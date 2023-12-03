class AWSConstants:
    AMI_ID = "ami-053b0d53c279acc90"
    REGIONS_CONFIG = ami_ids = [
        ["ami-0f2b6f057e0b94d5f", "us-east-1", "t2.micro"],
        ["ami-0fc034eec6ebb0a2f", "us-east-2", "t2.micro"],
        ["ami-0dd46a9bd78933b59", "us-west-1", "t2.micro"],
        ["ami-0b0b696130ccae67a", "us-west-2", "t2.micro"],
        ["ami-06c953f35606c6cab", "af-south-1", "t3.micro"],
        ["ami-0b7f75070a9af5ccc", "ap-east-1", "t3.micro"],
        ["ami-039a3748ec7d927ea", "ap-south-1", "t2.micro"],
        ["ami-0cd432cfa44d54635", "ap-south-2", "t3.micro"],
        ["ami-048cf2b6094a8ddea", "ap-southeast-1", "t2.micro"],
        ["ami-08e2b80da2d1a26ba", "ap-southeast-2", "t2.micro"],
        ["ami-07cbd8baed4031a0b", "ap-southeast-3", "t3.micro"],
        ["ami-0b2d79b35cb407633", "ap-southeast-4", "t3.micro"],
        ["ami-03ede0e542255afab", "ap-northeast-1", "t2.micro"],
        ["ami-0194a3a85274df403", "ap-northeast-2", "t2.micro"],
        ["ami-0e3e14659906088ee", "ap-northeast-3", "t2.micro"],
        ["ami-061a9d1cbe679774f", "ca-central-1", "t2.micro"],
        ["ami-0503973bb9fd5bf9d", "eu-central-1", "t2.micro"],
        ["ami-08a393a6f1ae935ae", "eu-central-2", "t3.micro"],
        ["ami-06f9d95eb36b09c6d", "eu-west-1", "t2.micro"],
        ["ami-0289906f3a1cc9f6e", "eu-west-2", "t2.micro"],
        ["ami-033fffd5768abc474", "eu-west-3", "t2.micro"],
        ["ami-0f0fa2dc7875970ae", "eu-south-1", "t3.micro"],
        ["ami-01068005c34dbbeaa", "eu-south-2", "t3.micro"],
        ["ami-083e5cd2c4794ba06", "eu-north-1", "t3.micro"],
        ["ami-00d907c0f0dd4cea8", "me-south-1", "t3.micro"],
        ["ami-0bc3f735ec926ac10", "il-central-1", "t3.micro"],
        ["ami-0dbe45934592daa1d", "sa-east-1", "t2.micro"]
    ]



class Command:
    TMUX_START = "tmux new -s {name}"
    TMUX_ATTACH = "tmux attach -s {name}"
    TMUX_DETACH = "tmux detach -s {name}"

    # can also add codec using --add-codec {codec}
    PJSUA_CALLER = "./pjsua-x86_64-unknown-linux-gnu --use-cli --auto-play --play-file {wav_file_location} --local-port=5061 --no-vad  --ip-addr {ip_addr} --stun-srv=stun.l.google.com:19302 --add-codec opus"

    PJSUA_RECEIVER = "./pjsua-x86_64-unknown-linux-gnu --use-cli --auto-answer 200 --auto-rec --rec-file {record_location} --local-port=5061 --ip-addr {ip_addr} --stun-srv=stun.l.google.com:19302 --add-codec opus"
    PJSUA_CALL = "call new sip:{receiver_ip}"

    PJSUA_TEST_CALLER = "cd /home/ubuntu/pjproject-2.13/pjsip-apps/bin && ./pjsua-x86_64-unknown-linux-gnu --use-cli --auto-play --play-file {src_file} --local-port=5061 --no-vad --ip-addr {caller_instance_public_ip} --stun-srv=stun.l.google.com:19302 sip:{receiver_instance_public_ip}:5061"
    TMUX_WRAPPER_CALL = "tmux new-session -d -s {tmux_name} && tmux send-keys -t {tmux_name_2} '{pjsua_command}' C-m"

    PJSUA_TEST_RECEIVER = "cd /home/ubuntu/pjproject-2.13/pjsip-apps/bin && ./pjsua-x86_64-unknown-linux-gnu --use-cli --auto-answer 200 --auto-rec --rec-file {record_file} --local-port=5061 --ip-addr {receiver_instance_public_ip} --stun-srv=stun.l.google.com:19302"
    TMUX_WRAPPER_RECE = "tmux new-session -d -s {tmux_name} && tmux send-keys -t {tmux_name_2} '{pjsua_command}' C-m"

    WGET_SRC_NOISY = "wget -q https://cmu.box.com/shared/static/3k2ryls3zxk5yvht8oo27v7tky7axxdc.wav --content-disposition --show-progress"
    WGET_SRC_NOISY_TRAIN = "wget -q https://cmu.box.com/shared/static/sd7okbt7c78kluouqbs3umi5dlj8nugh.wav --content-disposition --show-progress"
    WGET_SRC_CLEAN = "wget -q https://cmu.box.com/shared/static/lfczes67q0vo05m3kxp5q0wowo86uxav.wav --content-disposition --show-progress"

    SOX_PROCESS = "sox {from_file} -b 16 {to_file}"

    UPDATE_UBUNTU = "sudo apt-get update -y"
    UPGRADE_UBUNTU = "sudo apt-get upgrade -y"
    SETUP_LIBASOUND = "sudo apt-get install -y build-essential libasound2-dev"
    INSTALL_SOX = "sudo apt install sox -y"
    INSTALL_FFMPEG = "sudo apt install ffmpeg -y"
    INSTALL_WONDERSHAPER = "sudo apt install wondershaper -y"
    INSTALL_AWS_CLI = "sudo apt  install awscli -y"

    DOWNLOAD_PJSUA = "wget https://github.com/pjsip/pjproject/archive/refs/tags/2.13.tar.gz"
    TAR_PJSUA = "tar -xvf 2.13.tar.gz"
    CD_PJSUA = "cd /home/ubuntu/pjproject-2.13/ && "
    MAKE_PJSUA_CONFIGURE = "./configure"
    MAKE_PJSUA_MAKE_DEP = "make dep"
    MAKE_PJSUA_MAKE = "make"
    MAKE_PJSUA_SUDO_MAKE_INSTALL = "sudo make install"
    SLEEP_COMMAND = "sleep {duration} && "
    KILL_PJSUA = "pids=$(ps -aux | grep pjsua | grep -v grep | awk '{print $2}') && [[ ! -z \"$pids\" ]] && echo $pids | xargs kill -9 || echo \"No pjsua processes found.\""

    PULSEAUDIO_INSTALL = "sudo apt-get install pulseaudio -y"
    MAKE_PJSUA_WITH_PULSEAUDIO = "./configure --with-pulseaudio"

    PULSEAUDIO_START = "pulseaudio --start"
    VIRTUAL_SPEAKER_SETUP = "pactl load-module module-null-sink sink_name=VIRTUAL-SPEAKER sink_properties=device.description=VIRTUAL-SPEAKER"
    VIRTUAL_SPEAKER_MONITOR = "pactl load-module module-remap-source source_name=Remap-Source master=VIRTUAL-SPEAKER.monitor"

    FFMPEG_PROCESS = "ffmpeg -i {record_file} -acodec pcm_s16le -ac 1 -ar 16000 {record_ffmpeg}"

    WONDERSHAPER_UPLOAD_DOWNLOAD = "sudo wondershaper eth0 {upload} {download} && sudo wondershaper ens5 {upload} {download}"
    WONDERSHAPER_DELETE = "sudo wondershaper clear eth0 && sudo wondershaper clear ens5"

    CHANGE_DIRECTORY = "cd"
    BIN_FOLDER = "cd /home/ubuntu/pjproject-2.13/pjsip-apps/bin"

    S3_UPLOAD = "export AWS_SECRET_ACCESS_KEY=<> && export AWS_ACCESS_KEY_ID=<> && aws s3 cp {from_path} {to_path}"
    SYS_INFO_SCRIPT = "chmod +x sys_diag.sh && ./sys_diag.sh"


class CommandGroups:
    SETUP_MACHINE = [
        Command.UPDATE_UBUNTU,
        Command.UPGRADE_UBUNTU,
        Command.SETUP_LIBASOUND,
        Command.INSTALL_SOX,
        Command.INSTALL_FFMPEG,
        Command.INSTALL_AWS_CLI,
        Command.INSTALL_WONDERSHAPER,
        Command.DOWNLOAD_PJSUA,
        Command.TAR_PJSUA,
        Command.CD_PJSUA + Command.MAKE_PJSUA_CONFIGURE,
        Command.CD_PJSUA + Command.MAKE_PJSUA_MAKE_DEP,
        Command.CD_PJSUA + Command.MAKE_PJSUA_MAKE,
        Command.CD_PJSUA + Command.MAKE_PJSUA_SUDO_MAKE_INSTALL,
        Command.PULSEAUDIO_INSTALL,
        Command.CD_PJSUA + Command.MAKE_PJSUA_WITH_PULSEAUDIO,
        Command.CD_PJSUA + Command.MAKE_PJSUA_MAKE_DEP,
        Command.CD_PJSUA + Command.MAKE_PJSUA_MAKE,
        Command.CD_PJSUA + Command.MAKE_PJSUA_SUDO_MAKE_INSTALL,
        ]

    WGET_SOURCE_FILES = [
        Command.WGET_SRC_CLEAN,
        Command.WGET_SRC_NOISY
        ]

    WGET_E2E_FILES = [
        Command.WGET_SRC_CLEAN,
        Command.WGET_SRC_NOISY
        ]

    START_VIRTUAL_MIC = [
        Command.PULSEAUDIO_START,
        Command.VIRTUAL_SPEAKER_SETUP,
        Command.VIRTUAL_SPEAKER_MONITOR
        ]

    SOX_PROCESS = [
        Command.SOX_PROCESS
        ]

    #
    # MAKE_A_CALL = [
    #     Command.BIN_FOLDER,
    #     Command.PJSUA_CALLER,
    #     Command.PJSUA_CALL
    #     ]
    #
    # RECEIVE_A_CALL = [
    #     Command.BIN_FOLDER,
    #     Command.PJSUA_RECEIVER
    #     ]


audio_files_command = {
    'test_src_noisy': {
        'wget': Command.WGET_SRC_NOISY,
        'file_name': 'src_noisy.wav',
        'ffmpeg_file': 'src_noisy_converted.wav',
        'record_file':'src_noisy_record.wav'
        },
    'test_src_clean': {
        'wget': Command.WGET_SRC_CLEAN,
        'file_name': 'src_clean.wav',
        'ffmpeg_file': 'src_clean_converted.wav',
        'record_file':'src_clean_record.wav'
        },
    'train_src_noisy': {
        'wget': Command.WGET_SRC_NOISY_TRAIN,
        'file_name': 'train_noisy_1200.wav',
        'ffmpeg_file': 'src_noisy_train_converted.wav',
        'record_file':'src_noisy_train_record.wav'
        },
    'train_src_clean': {
        'wget': Command.WGET_SRC_CLEAN
        }
    }
