import asyncio
import os
from os import path
import random
import argparse
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import librosa
import shutil

from controllers.aws_controller import AwsController
from controllers.command_controller import CommandController
from controllers.ssh_controller import SSHController
from utils.constants import AWSConstants, Command, CommandGroups
from utils.logger import ContextLoggerAdapter, setup_logger

class DynamicMixing:
    def __init__(self, source_data_dir, num_parallel_simulations, relay_data_dir, clean_data_dir, bandwidth, logger):
        self.source_data_dir = source_data_dir
        self.num_parallel_simulations = num_parallel_simulations
        self.relay_data_dir = relay_data_dir
        self.clean_data_dir = clean_data_dir
        self.bandwidth = bandwidth
        self.logger = logger
        self.EC2_SETUP_INFO = {}

    @staticmethod
    def get_wav_duration(filename):
        duration = librosa.get_duration(filename=filename)
        return duration

    async def process_audio_file_on_ec2(self, audio_file, ec2_idx):

        ec2_config = self.EC2_SETUP_INFO[ec2_idx]

        sender_instance_name = ec2_config['sender_instance_name']
        sender_instance_public_ip = ec2_config['sender_instance_public_ip']
        receiver_instance_name = ec2_config['receiver_instance_name']
        receiver_instance_public_ip = ec2_config['receiver_instance_public_ip']
        bandwidth = ec2_config['bandwidth']
        tracking_id = ec2_config['tracking_id']

        remote_home = '/home/ubuntu'

        src_audio_file_on_local = path.join(self.source_data_dir, audio_file)
        src_audio_file_on_sender = path.join(remote_home, audio_file)
        relay_audio_file_on_receiver = path.join(remote_home, f'relay_{audio_file}')
        relay_ffmpeg_audio_file_on_receiver = path.join(remote_home, f'ffmpeg_relay_{audio_file}')
        relay_audio_file_on_local = path.join(self.relay_data_dir, f'{audio_file}')
        clean_audio_file_on_local = path.join(self.clean_data_dir, f'{audio_file}')

        duration = int(self.get_wav_duration(src_audio_file_on_local) + 2)


        # SCP file

        self.logger.info(f"scp audio file {audio_file} to sender {sender_instance_name}")
        result = CommandController.ec2_service.scp(sender_instance_public_ip, sender_instance_name, src_audio_file_on_local, src_audio_file_on_sender, True)
        self.logger.info(f"scp complete to sender {sender_instance_name}")

        # put wondershaper

        self.logger.info(f"running command WONDERSHAPER_UPLOAD_DOWNLOAD into {sender_instance_name}")
        result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha", None,
                                                       Command.WONDERSHAPER_UPLOAD_DOWNLOAD.format(
                                                           upload=bandwidth,
                                                           download=bandwidth), non_blocking=False)
        self.logger.info(f"command WONDERSHAPER_UPLOAD_DOWNLOAD success {sender_instance_name}. {result}")

        # put wondershaper

        self.logger.info(f"running command WONDERSHAPER_UPLOAD_DOWNLOAD into {receiver_instance_name}")
        result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                       Command.WONDERSHAPER_UPLOAD_DOWNLOAD.format(
                                                           upload=bandwidth,
                                                           download=bandwidth), non_blocking=False)
        self.logger.info(f"command WONDERSHAPER_UPLOAD_DOWNLOAD success {receiver_instance_name}. {result}")

        sender_pjsua_command = Command.PJSUA_TEST_CALLER.format(src_file=src_audio_file_on_sender,
                                                                caller_instance_public_ip=sender_instance_public_ip,
                                                                receiver_instance_public_ip=receiver_instance_public_ip)
        tmux_uuid = str(uuid.uuid4())
        sender_pjsua_tmux_wrapper = Command.TMUX_WRAPPER_CALL.format(pjsua_command=sender_pjsua_command, tmux_name=tmux_uuid, tmux_name_2=tmux_uuid)

        receiver_pjsua_command = Command.PJSUA_TEST_RECEIVER.format(record_file=relay_audio_file_on_receiver,
                                                                    receiver_instance_public_ip=receiver_instance_public_ip)
        receiver_pjsua_tmux_wrapper = Command.TMUX_WRAPPER_RECE.format(pjsua_command=receiver_pjsua_command, tmux_name=tmux_uuid, tmux_name_2=tmux_uuid)

        ############ create a receiver pjsua session ############

        self.logger.info(f"create a receiver pjsua session on receiver {receiver_instance_name}")
        result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                       receiver_pjsua_tmux_wrapper, non_blocking=False)
        self.logger.info(f"started a receiver pjsua session on receiver {receiver_instance_name} {result}")

        ############ create a sender pjsua session ############

        self.logger.info(f"create a sender pjsua session on receiver {sender_instance_name}")
        result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha", None,
                                                       sender_pjsua_tmux_wrapper, non_blocking=False)
        self.logger.info(f"started a sender pjsua session on receiver {sender_instance_name} {result}")

        ############ wait for some time ############

        self.logger.info(f"Call in progress. Will be killed after {duration} seconds")

        await asyncio.sleep(duration)    # Simulates the job being processed in the EC2 instance.

        ############ kill caller pjsua session ############

        self.logger.info(f"kill sender pjsua session {sender_instance_name} after {duration} seconds")
        result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha", None,
                                                       Command.KILL_PJSUA, non_blocking=False)
        self.logger.info(f"command set for killing sender pjsua session {sender_instance_name} {result}")

        ############ kill sender pjsua session ############

        self.logger.info(f"kill receiver pjsua session {receiver_instance_name} after {duration} seconds")
        result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                       Command.KILL_PJSUA, non_blocking=False)
        self.logger.info(f"command set for killing receiver pjsua session {receiver_instance_name} {result}")

        ############ check the recorded audio and ffmpeg it ############

        self.logger.info(f"checking recorded audio and converting to readable wav format")
        result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                       Command.FFMPEG_PROCESS.format(record_file=relay_audio_file_on_receiver,
                                                                                     record_ffmpeg=relay_ffmpeg_audio_file_on_receiver),
                                                       non_blocking=False)
        self.logger.info(f"fmmpeg process output {result}")
        ############ delete wondershaper sender ############

        self.logger.info(f"running command WONDERSHAPER_DELETE into {receiver_instance_name}")
        result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                       Command.WONDERSHAPER_DELETE, non_blocking=False)
        self.logger.info(f"command WONDERSHAPER_UPLOAD_DOWNLOAD success {receiver_instance_name}. {result}")


       ############ delete wondershaper receiver ############

        self.logger.info(f"running command WONDERSHAPER_DELETE into {receiver_instance_name}")
        result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                       Command.WONDERSHAPER_DELETE, non_blocking=False)
        self.logger.info(f"command WONDERSHAPER_UPLOAD_DOWNLOAD success {receiver_instance_name}. {result}")

        # SCP file

        self.logger.info(f"scp final relayed file from {receiver_instance_name} to local")
        result = CommandController.ec2_service.scp(receiver_instance_public_ip, receiver_instance_name, relay_audio_file_on_local, relay_ffmpeg_audio_file_on_receiver, False)
        self.logger.info(f"scp complete to sender {receiver_instance_name}")

        self.logger.info(f"copy clean audio to data folder")
        shutil.copyfile(src_audio_file_on_local, clean_audio_file_on_local)

        self.logger.info(f"EC2 instance {ec2_idx} processed file {audio_file}")

    def on_job_complete(self, ec2_id, result):
        self.logger.info(result)
        self.EC2_SETUP_INFO[ec2_id]['available'] = True

    async def schedule_jobs(self):

        files = [file for file in os.listdir(self.source_data_dir) if file.endswith('.wav')]
        random.shuffle(files)

        pending_jobs = set()

        while files or pending_jobs:
            for idx in self.EC2_SETUP_INFO.keys():
                if self.EC2_SETUP_INFO[idx]['available'] and files:
                    self.EC2_SETUP_INFO[idx]['available'] = False
                    file_name = files.pop()
                    job = asyncio.create_task(self.process_audio_file_on_ec2(file_name, idx))
                    job.add_done_callback(lambda future: self.on_job_complete(idx, future.result()))
                    pending_jobs.add(job)

            if pending_jobs:
                done, pending_jobs = await asyncio.wait(pending_jobs, return_when=asyncio.FIRST_COMPLETED)

        print("All jobs have been processed.")

    def setup_EC2(self, config):

        tracking_id = config['tracking_id']

        sender_instance_ami = config['sender_config'][0]
        sender_region = config['sender_config'][1]
        sender_instance_type = config['sender_config'][2]

        receiver_instance_ami = config['receiver_config'][0]
        receiver_region = config['receiver_config'][1]
        receiver_instance_type = config['receiver_config'][2]

        ############ create security key ############

        dir_path = "creds/"

        sender_key_name = f"key_simulation_sender_{tracking_id}"
        self.logger.info(f"creating sender security key {sender_key_name}")
        create_sender_key_msg = AwsController.aws_service.create_security_key(sender_region, sender_key_name, dir_path)
        self.logger.info(f"security key {sender_key_name} created. Msg: {create_sender_key_msg}")
        sender_key_path = dir_path + f"{sender_key_name}.pem"

        receiver_key_name = f"key_simulation_receiver_{tracking_id}"
        self.logger.info(f"creating receiver security key {receiver_key_name}")
        create_receiver_key_msg = AwsController.aws_service.create_security_key(receiver_region, receiver_key_name,
                                                                                dir_path)
        self.logger.info(f"security key {receiver_key_name} created. Msg: {create_receiver_key_msg}")
        receiver_key_path = dir_path + f"{receiver_key_name}.pem"

        ############ create security group ############

        sender_security_group_name = f"sg_simulation_sender_{tracking_id}"
        self.logger.info(f"creating sender security group {sender_security_group_name}")
        sender_security_group_id = AwsController.aws_service.create_security_group(sender_region,
                                                                                   sender_security_group_name,
                                                                                   "security group for simulation")
        self.logger.info(f"security group {sender_security_group_name} created. sg_id: {sender_security_group_id}")

        receiver_security_group_name = f"sg_simulation_receiver_{tracking_id}"
        self.logger.info(f"creating receiver security group {receiver_security_group_name}")
        receiver_security_group_id = AwsController.aws_service.create_security_group(receiver_region,
                                                                                     receiver_security_group_name,
                                                                                     "security group for simulation")
        self.logger.info(f"security group {receiver_security_group_name} created. sg_id: {receiver_security_group_id}")

        ############ create sender instance ############

        sender_instance_name = f"sender_instance_simulation_{tracking_id}"
        self.logger.info(f"creating sender instance {sender_instance_name}")
        sender_instance_id = AwsController.aws_service.create_ec2_instance(sender_region, sender_instance_type,
                                                                           sender_instance_name, sender_instance_ami, 8,
                                                                           sender_key_name, sender_security_group_id)
        self.logger.info(f"sender instance created {sender_instance_name}. Sender instance id: {sender_instance_id} ")

        time.sleep(5)

        self.logger.info(f"fetching sender instance details for {sender_instance_name}")
        sender_instance_details = AwsController.aws_service.get_ec2_instance_by_id(sender_instance_id, sender_region)
        sender_instance_public_ip = sender_instance_details['PublicIpAddress']
        self.logger.info(
                f"sender instance details for {sender_instance_name}. Public Ip: {sender_instance_public_ip}. Other details: {sender_instance_details}")

        # while loop to check status if instance is ready. Once ready, continue

        sender_instance_state = sender_instance_details['State']['Name']
        if sender_instance_state != 'running':
            self.logger.info(f"wait for sender instance to reach running status. Current status: {sender_instance_state}")

            while sender_instance_state != 'running':
                time.sleep(10)
                sender_instance_state = AwsController.aws_service.get_current_instance_status(sender_instance_id,
                                                                                              sender_region)
                self.logger.info(f"wait for sender instance to reach running status. Current status: {sender_instance_state}")

        ############ create receiver instance ############

        receiver_instance_name = f"receiver_instance_simulation_{tracking_id}"
        self.logger.info(f"creating receiver instance {receiver_instance_name}")
        receiver_instance_id = AwsController.aws_service.create_ec2_instance(receiver_region, receiver_instance_type,
                                                                             receiver_instance_name, receiver_instance_ami,
                                                                             8,
                                                                             receiver_key_name, receiver_security_group_id)
        self.logger.info(f"receiver instance created {receiver_instance_name}. receiver instance id: {receiver_instance_id} ")

        time.sleep(5)

        self.logger.info(f"fetching receiver instance details for {receiver_instance_name}")
        receiver_instance_details = AwsController.aws_service.get_ec2_instance_by_id(receiver_instance_id, receiver_region)
        receiver_instance_public_ip = receiver_instance_details['PublicIpAddress']
        self.logger.info(
                f"receiver instance details for {receiver_instance_name}. Public Ip: {receiver_instance_public_ip}. Other details: {receiver_instance_details}")

        # while loop to check status if instance is ready. Once ready, continue

        receiver_instance_state = receiver_instance_details['State']['Name']
        if receiver_instance_state != 'running':
            self.logger.info(f"wait for receiver instance to reach running status. Current status: {receiver_instance_state}")

            while receiver_instance_state != 'running':
                time.sleep(10)
                receiver_instance_state = AwsController.aws_service.get_current_instance_status(receiver_instance_id,
                                                                                                receiver_region)
                self.logger.info(
                        f"wait for receiver instance to reach running status. Current status: {receiver_instance_state}")

        ############ setup sender instance ############

        self.logger.info(f"starting setup for sender instance {sender_instance_name}")
        sender_ssh_msg = SSHController.ssh_service.connect_ssh(sender_instance_public_ip, "ubuntu", sender_instance_name,
                                                               sender_key_path)
        self.logger.info(f"ssh success into {sender_ssh_msg}. Response: {sender_ssh_msg}")

        self.logger.info(f"running command START_VIRTUAL_MIC in {sender_instance_name} to start virtual mic")
        result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha",
                                                       CommandGroups.START_VIRTUAL_MIC, None, non_blocking=False)
        self.logger.info(f"command START_VIRTUAL_MIC success {sender_instance_name}. {result}")


        ############ setup receiver instance ############
        self.logger.info(f"starting setup for receiver instance {receiver_instance_name}")
        receiver_ssh_msg = SSHController.ssh_service.connect_ssh(receiver_instance_public_ip, "ubuntu",
                                                                 receiver_instance_name, receiver_key_path)
        self.logger.info(f"ssh success into {receiver_ssh_msg}. Response: {receiver_ssh_msg}")

        self.logger.info(f"running command START_VIRTUAL_MIC in {receiver_instance_name} to start virtual mic")
        result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha",
                                                       CommandGroups.START_VIRTUAL_MIC, None, non_blocking=False)
        self.logger.info(f"command START_VIRTUAL_MIC success {receiver_instance_name}. {result} ")

        ########### save all info ##################
        self.EC2_SETUP_INFO[config['idx']] = {
            'sender_region': sender_region,
            'sender_instance_name': sender_instance_name,
            'sender_instance_public_ip': sender_instance_public_ip,
            'sender_instance_id': sender_instance_id,
            'sender_security_group_name': sender_security_group_name,
            'sender_security_group_id': sender_security_group_id,
            'sender_key_name': sender_key_name,
            'sender_key_path': sender_key_path,

            'receiver_region': receiver_region,
            'receiver_instance_name': receiver_instance_name,
            'receiver_instance_public_ip': receiver_instance_public_ip,
            'receiver_instance_id': receiver_instance_id,
            'receiver_security_group_name': receiver_security_group_name,
            'receiver_security_group_id': receiver_security_group_id,
            'receiver_key_name': receiver_key_name,
            'receiver_key_path': receiver_key_path,

            'bandwidth': config['bandwidth'],
            'tracking_id': tracking_id,
            'available': True
            }

    def terminate_EC2(self, ec2_idx):

        ec2_config = self.EC2_SETUP_INFO[ec2_idx]

        sender_instance_name = ec2_config['sender_instance_name']
        sender_instance_id = ec2_config['sender_instance_id']
        sender_security_group_name = ec2_config['sender_security_group_name']
        sender_key_name = ec2_config['sender_key_name']
        sender_region = ec2_config['sender_region']
        sender_security_group_id = ec2_config['sender_security_group_id']
        sender_key_path = ec2_config['sender_key_path']

        receiver_instance_name = ec2_config['receiver_instance_name']
        receiver_instance_id = ec2_config['receiver_instance_id']
        receiver_security_group_name = ec2_config['receiver_security_group_name']
        receiver_key_name = ec2_config['receiver_key_name']
        receiver_region = ec2_config['receiver_region']
        receiver_key_path = ec2_config['receiver_key_path']
        receiver_security_group_id = ec2_config['receiver_security_group_id']

        ############ delete instances ############
        self.logger.info(f"deleting sender instance {sender_instance_name}")
        result = AwsController.aws_service.delete_instance(sender_instance_id, sender_region)
        self.logger.info(f"deleted sender instance {sender_instance_name} ")

        self.logger.info(f"deleting receiver instance {receiver_instance_name}")
        result = AwsController.aws_service.delete_instance(receiver_instance_id, receiver_region)
        self.logger.info(f"deleted receiver instance {receiver_instance_name}")

        ############ delete security groups ############
        self.logger.info(f"deleting sender security groups {sender_security_group_name}")
        result = AwsController.aws_service.delete_security_group(sender_region, sender_security_group_id)
        self.logger.info(f"deleted sender security groups {sender_security_group_name}")

        self.logger.info(f"deleting receiver security groups {receiver_security_group_name}")
        result = AwsController.aws_service.delete_security_group(receiver_region, receiver_security_group_id)
        self.logger.info(f"deleted receiver security groups {receiver_security_group_name}")

        ############ delete security keys ############
        self.logger.info(f"deleting sender security keys {sender_key_name}")
        result = AwsController.aws_service.delete_security_key(sender_region, sender_key_name, sender_key_path)
        self.logger.info(f"deleted sender security keys  {sender_key_name}")

        self.logger.info(f"deleting receiver security keys {receiver_key_name}")
        result = AwsController.aws_service.delete_security_key(receiver_region, receiver_key_name, receiver_key_path)
        self.logger.info(f"deleted receiver security keys {receiver_key_name}")

    def setup_simulations(self):
        simulations = {}

        idx = 0
        self.logger.info("Generate simulation configs")

        while idx != self.num_parallel_simulations:
            simulations[idx] = {
                'sender_config': random.choice(AWSConstants.REGIONS_CONFIG),
                'receiver_config': random.choice(AWSConstants.REGIONS_CONFIG),
                'tracking_id': str(uuid.uuid4()),
                'bandwidth': self.bandwidth,
                'idx': idx
                }
            idx += 1

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.setup_EC2, simulations[idx]) for idx in simulations.keys()]

            for future in as_completed(futures):
                try:
                    result = future._state
                except Exception as exc:
                    self.logger.info(f"EC2 create futures Exception {exc}. State {result}")
                else:
                    self.logger.info(f"EC2 create futures state {result}.")

            self.logger.info("All EC2 instances have been set up.")

    def destroy_simulations(self):

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.terminate_EC2, idx) for idx in self.EC2_SETUP_INFO.keys()]

            for future in as_completed(futures):
                try:
                    result = future._state
                except Exception as exc:
                    self.logger.info(f"EC2 create futures Exception {exc}. State {result}")
                else:
                    self.logger.info(f"EC2 create futures state {result}.")

            self.logger.info("All EC2 instances have been deleted.")

    def run(self):

        self.logger.info("Setup Simulations")
        self.setup_simulations()

        self.logger.info("Run jobs")
        asyncio.run(self.schedule_jobs())

        self.logger.info("Delete simulations")
        self.destroy_simulations()


def main(args):
    base_logger = setup_logger("dynamic mixing")
    logger = ContextLoggerAdapter(base_logger, {"tracking_id": "dynamic mixing"})

    dynamic_mixer = DynamicMixing(args.source_data_dir, args.num_parallel_simulations, args.relay_data_dir, args.clean_data_dir, args.bandwidth, logger)
    dynamic_mixer.run()

    logger.info("Finish")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Relay audio files over VOIP using EC2 instances in multiple regions")
    parser.add_argument('--source_data_dir', '--src_dir', type=str, help='The directory that contains the data')
    parser.add_argument('--num_parallel_simulations', '--num', type=int, help='The number of simulations to run in parallel')
    parser.add_argument('--relay_data_dir', '--relay_dir', type=str, help='The directory where to store the relay data')
    parser.add_argument('--clean_data_dir', '--clean_dir', type=str, help='The directory where to store the clean data')
    parser.add_argument('--bandwidth', '--bw', type=int, default=100, help='The bandwidth to be used for the experiment')

    args = parser.parse_args()
    main(args)