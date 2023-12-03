import asyncio
import os
import subprocess
import argparse

from utils.dynamic_mixing import DynamicMixing
from utils.logger import ContextLoggerAdapter, setup_logger


def remove_last_path(path_):
    return "/".join(path_.split("/")[:-1])


def make_training_config(
    training_voip_config_path ,
    train_noisy_path          ,
    test_noisy_path           ):

    train_noisy_path = remove_last_path(train_noisy_path)
    test_noisy_path = remove_last_path(test_noisy_path)
    training_voip_config_text = """
    #!/bin/bash

    dset:
      train: {}
      valid: {}
      test: {}
      noisy_json:
      noisy_dir:
      matching: dns
      eval_every: 1
    """.format(
        train_noisy_path,
        test_noisy_path,
        test_noisy_path
    )

    with open(training_voip_config_path, "w") as f:
        f.write(training_voip_config_text)


def make_training_runner(
    training_voip_runner_path ,
    training_voip_config_path ,
    learning_rate             ,
    acoustic_loss_weight      ,
    stft_loss_weight          ,
    epochs                    ,
    num_workers               ,
    batch_size                ,
    continue_pretrained       ,
    continue_from             ,
    checkpoints_dir             ,
    ddp                       ):

    descripton = training_voip_config_path.split("/")[-1].split(".")[-2]

    dset                = descripton
    acoustic_loss       = "False" if acoustic_loss_weight == 0 else "True"
    acoustic_loss_only  = "False"
    stft_loss           = "False" if stft_loss_weight == 0 else "True"
    ac_loss_weight      = acoustic_loss_weight
    acoustic_model_path = "/content/lld-estimation-model_12mse_14mae.pt"

    training_voip_runner_text = """
    #!/bin/bash

    python train.py            \
        continue_pretrained={} \
        continue_from={}       \
        dset={}                \
        acoustic_loss={}       \
        acoustic_loss_only={}  \
        stft_loss={}           \
        ac_loss_weight={}      \
        stft_loss_weight={}    \
        hydra.run.dir={} \
        lr={}                  \
        epochs={}              \
        num_workers={}         \
        num_prints=1           \
        batch_size={}          \
        acoustic_model_path={} \
        ddp={} $@
    """.format(
        continue_pretrained ,
        continue_from       ,
        dset                ,
        acoustic_loss       ,
        acoustic_loss_only  ,
        stft_loss           ,
        ac_loss_weight      ,
        stft_loss_weight    ,
        checkpoints_dir     ,
        learning_rate       ,
        epochs              ,
        num_workers         ,
        batch_size          ,
        acoustic_model_path ,
        ddp                 )

    with open(training_voip_runner_path, "w") as f:
        f.write(training_voip_runner_text)


def make_clean_noisy_jsons(
    train_noisy_path          ,
    test_noisy_path           ,
    test_clean_path  ):

  os.system(f"python -m denoiser.audio {train_noisy_path} > {remove_last_path(train_noisy_path)}/noisy.json")
  os.system(f"python -m denoiser.audio {test_noisy_path} > {remove_last_path(test_noisy_path)}/noisy.json")
  os.system(f"python -m denoiser.audio {test_clean_path} > {remove_last_path(test_noisy_path)}/clean.json")


def train_demucs(train_noisy_data_dir, test_clean_data_dir, test_noisy_data_dir, mix_epoch_frequency, continue_pretrained, continue_from, running_checkpoints_dir ):

    training_runner_path = train_noisy_data_dir + ".yaml"
    learning_rate        = 3e-4
    acoustic_loss_weight = 0.0
    stft_loss_weight     = 1.0
    num_workers          = 2
    batch_size           = 20
    ddp                  = 1

    training_voip_config_path = "/content/TAPLoss-master/Demucs/denoiser/conf/dset/" + training_runner_path.split("/")[-1]

    make_training_config(
            training_voip_config_path,
            train_noisy_data_dir,
            test_noisy_data_dir)

    make_clean_noisy_jsons(
            train_noisy_data_dir,
            test_noisy_data_dir,
            test_clean_data_dir
            )

    make_training_runner(
            train_noisy_data_dir,
            training_voip_config_path,
            learning_rate,
            acoustic_loss_weight,
            stft_loss_weight,
            mix_epoch_frequency,
            num_workers,
            batch_size,
            continue_pretrained,
            continue_from,
            running_checkpoints_dir,
            ddp
            )

    os.environ["TRAINING_RUNNER_PATH"] = training_runner_path

    # Ensure that the script has executable permissions
    subprocess.run(['chmod', '+x', training_runner_path])

    # Run the bash script
    result = subprocess.run([training_runner_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check the result
    if result.returncode == 0:
        print('Script ran successfully.')
        print('Output:', result.stdout)
    else:
        print('Script failed.')
        print('Error:', result.stderr)

def run_dynamic_mixer(dynamic_mixer):
    dynamic_mixer.run()

async def dynamic_mix_demucs(args):

    relay_data_dir = (args.train_noisy_data_dir[-1] if args.train_noisy_data_dir.endswith("/") else  args.train_noisy_data_dir) + "_relay"
    os.mkdir(relay_data_dir)
    running_checkpoints_dir = "/content/checkpoints"

    bandwidth = 100

    base_logger = setup_logger("demucs dynamic mixing")
    logger = ContextLoggerAdapter(base_logger, {"tracking_id": "demucs dynamic mixing"})

    dynamic_mixer = DynamicMixing(
            args.train_noisy_data_dir,
            args.num_parallel_simulations,
            relay_data_dir,
            bandwidth,
            logger
            )

    # Use run_in_executor to run the run method asynchronously
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_dynamic_mixer, dynamic_mixer)

    train_noisy_data_dir = args.train_noisy_data_dir
    test_clean_data_dir = args.test_clean_data_dir
    test_noisy_data_dir = args.test_noisy_data_dir
    total_epochs = args.total_epochs
    mix_epoch_frequency = args.mix_epoch_frequency

    for epoch in range(0, total_epochs, mix_epoch_frequency):

        archive_checkpoints_dir = f"/content/checkpoints_archive_{epoch}"

        if epoch == 0:
            train_demucs(
                train_noisy_data_dir,
                test_clean_data_dir,
                test_noisy_data_dir,
                mix_epoch_frequency,
                "dns64",
                "",
                running_checkpoints_dir
                )

        else:
            train_demucs(
                relay_data_dir,
                test_clean_data_dir,
                test_noisy_data_dir,
                mix_epoch_frequency,
                "",
                f"{archive_checkpoints_dir}/checkpoint.th",
                running_checkpoints_dir
                )

            os.rename(relay_data_dir, f"{relay_data_dir}_archive_{epoch+mix_epoch_frequency}")
            os.mkdir(relay_data_dir)

        os.rename(running_checkpoints_dir, f"/content/checkpoints_archive_{epoch+mix_epoch_frequency}")

    logger.info("Finish")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Relay audio files over VOIP using EC2 instances in multiple regions")

    parser.add_argument('--train_noisy_data_dir', '--train_noisy_dir', type=str, help='The directory that contains the noisy training data')
    parser.add_argument('--test_clean_data_dir', '--test_clean_dir', type=str, help='The directory that contains the clean test data')
    parser.add_argument('--test_noisy_data_dir', '--test_noisy_dir', type=str, help='The directory that contains the noisy test data')
    parser.add_argument('--num_parallel_simulations', '--num', type=int, help='The number of simulations to run in parallel')
    parser.add_argument('--total_epochs', '--epochs', type=int, help='The number of total epochs to run')
    parser.add_argument('--mix_epoch_frequency', '--mix_epochs', type=int, help='The number of epoch to run after mix')

    args = parser.parse_args()

    asyncio.run(dynamic_mix_demucs(args))