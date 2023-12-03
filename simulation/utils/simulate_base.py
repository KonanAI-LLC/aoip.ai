import argparse
import uuid
import time

from controllers.aws_controller import AwsController
from controllers.command_controller import CommandController
from controllers.ssh_controller import SSHController
from utils.constants import CommandGroups, Command, audio_files_command
from utils.logger import ContextLoggerAdapter, setup_logger


base_logger = None

def simulate(
        tracking_id,
        sender_region,
        receiver_region,
        sender_instance_type,
        receiver_instance_type,
        sender_instance_ami,
        receiver_instance_ami,
        sender_upload_bandwidth,
        sender_download_bandwidth,
        receiver_upload_bandwidth,
        receiver_download_bandwidth,
        src_audio_config,
        duration,
        s3_bucket_url
        ):


    base_logger = setup_logger(tracking_id)
    logger = ContextLoggerAdapter(base_logger, {"tracking_id": tracking_id})
    config = audio_files_command[src_audio_config]

    # implement delete logic ^

    ############ starting simulation ############

    logger.info("starting simulation")

    ############ create security key ############

    dir_path = "creds/"

    sender_key_name = f"key_simulation_sender_{tracking_id}"
    logger.info(f"creating sender security key {sender_key_name}")
    create_sender_key_msg = AwsController.aws_service.create_security_key(sender_region, sender_key_name, dir_path)
    logger.info(f"security key {sender_key_name} created. Msg: {create_sender_key_msg}")
    sender_key_path = dir_path + f"{sender_key_name}.pem"

    receiver_key_name = f"key_simulation_receiver_{tracking_id}"
    logger.info(f"creating receiver security key {receiver_key_name}")
    create_receiver_key_msg = AwsController.aws_service.create_security_key(receiver_region, receiver_key_name,
                                                                            dir_path)
    logger.info(f"security key {receiver_key_name} created. Msg: {create_receiver_key_msg}")
    receiver_key_path = dir_path + f"{receiver_key_name}.pem"

    ############ create security group ############

    sender_security_group_name = f"sg_simulation_sender_{tracking_id}"
    logger.info(f"creating sender security group {sender_security_group_name}")
    sender_security_group_id = AwsController.aws_service.create_security_group(sender_region,
                                                                               sender_security_group_name,
                                                                               "security group for simulation")
    logger.info(f"security group {sender_security_group_name} created. sg_id: {sender_security_group_id}")

    receiver_security_group_name = f"sg_simulation_receiver_{tracking_id}"
    logger.info(f"creating receiver security group {receiver_security_group_name}")
    receiver_security_group_id = AwsController.aws_service.create_security_group(receiver_region,
                                                                                 receiver_security_group_name,
                                                                                 "security group for simulation")
    logger.info(f"security group {receiver_security_group_name} created. sg_id: {receiver_security_group_id}")

    ############ create sender instance ############

    sender_instance_name = f"sender_instance_simulation_{tracking_id}"
    logger.info(f"creating sender instance {sender_instance_name}")
    sender_instance_id = AwsController.aws_service.create_ec2_instance(sender_region, sender_instance_type,
                                                                       sender_instance_name, sender_instance_ami, 8,
                                                                       sender_key_name, sender_security_group_id)
    logger.info(f"sender instance created {sender_instance_name}. Sender instance id: {sender_instance_id} ")

    time.sleep(5)

    logger.info(f"fetching sender instance details for {sender_instance_name}")
    sender_instance_details = AwsController.aws_service.get_ec2_instance_by_id(sender_instance_id, sender_region)
    sender_instance_public_ip = sender_instance_details['PublicIpAddress']
    logger.info(
        f"sender instance details for {sender_instance_name}. Public Ip: {sender_instance_public_ip}. Other details: {sender_instance_details}")

    # while loop to check status if instance is ready. Once ready, continue

    sender_instance_state = sender_instance_details['State']['Name']
    if sender_instance_state != 'running':
        logger.info(f"wait for sender instance to reach running status. Current status: {sender_instance_state}")

        while sender_instance_state != 'running':
            time.sleep(10)
            sender_instance_state = AwsController.aws_service.get_current_instance_status(sender_instance_id,
                                                                                          sender_region)
            logger.info(f"wait for sender instance to reach running status. Current status: {sender_instance_state}")

    ############ create receiver instance ############

    receiver_instance_name = f"receiver_instance_simulation_{tracking_id}"
    logger.info(f"creating receiver instance {receiver_instance_name}")
    receiver_instance_id = AwsController.aws_service.create_ec2_instance(receiver_region, receiver_instance_type,
                                                                         receiver_instance_name, receiver_instance_ami,
                                                                         8,
                                                                         receiver_key_name, receiver_security_group_id)
    logger.info(f"receiver instance created {receiver_instance_name}. receiver instance id: {receiver_instance_id} ")

    time.sleep(5)

    logger.info(f"fetching receiver instance details for {receiver_instance_name}")
    receiver_instance_details = AwsController.aws_service.get_ec2_instance_by_id(receiver_instance_id, receiver_region)
    receiver_instance_public_ip = receiver_instance_details['PublicIpAddress']
    logger.info(
            f"receiver instance details for {receiver_instance_name}. Public Ip: {receiver_instance_public_ip}. Other details: {receiver_instance_details}")

    # while loop to check status if instance is ready. Once ready, continue

    receiver_instance_state = receiver_instance_details['State']['Name']
    if receiver_instance_state != 'running':
        logger.info(f"wait for receiver instance to reach running status. Current status: {receiver_instance_state}")

        while receiver_instance_state != 'running':
            time.sleep(10)
            receiver_instance_state = AwsController.aws_service.get_current_instance_status(receiver_instance_id,
                                                                                            receiver_region)
            logger.info(
                f"wait for receiver instance to reach running status. Current status: {receiver_instance_state}")

    ############ setup sender instance ############

    logger.info(f"starting setup for sender instance {sender_instance_name}")
    sender_ssh_msg = SSHController.ssh_service.connect_ssh(sender_instance_public_ip, "ubuntu", sender_instance_name,
                                                           sender_key_path)
    logger.info(f"ssh success into {sender_ssh_msg}. Response: {sender_ssh_msg}")

    logger.info(f"running command SETUP_MACHINE into {sender_instance_name}")
    result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha",
                                                   CommandGroups.SETUP_MACHINE, None, non_blocking=False)
    logger.info(f"command SETUP_MACHINE success {sender_instance_name}. ")

    logger.info(f"running command WGET_FILES in {sender_instance_name} to get audio files")
    result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha", None,
                                                   config['wget'], non_blocking=False)
    logger.info(f"command WGET_FILES success {sender_instance_name}. ")

    logger.info(f"running command SOX_FILES in {sender_instance_name} to process audio files")
    result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha", None,
                                                   Command.SOX_PROCESS.format(
                                                           from_file=config['file_name'],
                                                           to_file=config['ffmpeg_file']
                                                           ), non_blocking=False)
    logger.info(f"command SOX_FILES success {sender_instance_name}. ")

    logger.info(f"running command START_VIRTUAL_MIC in {sender_instance_name} to start virtual mic")
    result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha",
                                                   CommandGroups.START_VIRTUAL_MIC, None, non_blocking=False)
    logger.info(f"command START_VIRTUAL_MIC success {sender_instance_name}. ")

    logger.info(f"running command WONDERSHAPER_UPLOAD_DOWNLOAD into {sender_instance_name}")
    result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha", None,
                                                   Command.WONDERSHAPER_UPLOAD_DOWNLOAD.format(
                                                       upload=sender_upload_bandwidth,
                                                       download=sender_download_bandwidth), non_blocking=False)
    logger.info(f"command WONDERSHAPER_UPLOAD_DOWNLOAD success {sender_instance_name}. ")

    logger.info(f"scp setup file to sender {sender_instance_name}")
    result = CommandController.ec2_service.scp(sender_instance_public_ip, sender_instance_name, "utils/sys_diag.sh", "/home/ubuntu/sys_diag.sh", True)
    logger.info(f"scp complete to sender {sender_instance_name}")

    logger.info(f"running command SYS_INFO into {sender_instance_name}")
    result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha", None, Command.SYS_INFO_SCRIPT, non_blocking=False)
    logger.info(f"command SYS_INFO success {sender_instance_name}. Result: {result}")

    ############ setup receiver instance ############

    logger.info(f"starting setup for receiver instance {receiver_instance_name}")
    receiver_ssh_msg = SSHController.ssh_service.connect_ssh(receiver_instance_public_ip, "ubuntu",
                                                             receiver_instance_name, receiver_key_path)
    logger.info(f"ssh success into {receiver_ssh_msg}. Response: {receiver_ssh_msg}")

    logger.info(f"running command SETUP_MACHINE into {receiver_instance_name}")
    result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha",
                                                   CommandGroups.SETUP_MACHINE, None, non_blocking=False)
    logger.info(f"command SETUP_MACHINE success {receiver_instance_name}. ")

    logger.info(f"running command WONDERSHAPER_UPLOAD_DOWNLOAD into {receiver_instance_name}")
    result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                   Command.WONDERSHAPER_UPLOAD_DOWNLOAD.format(
                                                       upload=receiver_upload_bandwidth,
                                                       download=receiver_download_bandwidth), non_blocking=False)
    logger.info(f"command WONDERSHAPER_UPLOAD_DOWNLOAD success {sender_instance_name}. ")

    logger.info(f"running command START_VIRTUAL_MIC in {receiver_instance_name} to start virtual mic")
    result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha",
                                                   CommandGroups.START_VIRTUAL_MIC, None, non_blocking=False)
    logger.info(f"command START_VIRTUAL_MIC success {receiver_instance_name}. ")

    logger.info(f"running command WONDERSHAPER_UPLOAD_DOWNLOAD into {receiver_instance_name}")
    result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                   Command.WONDERSHAPER_UPLOAD_DOWNLOAD.format(
                                                       upload=receiver_upload_bandwidth,
                                                       download=receiver_download_bandwidth), non_blocking=False)
    logger.info(f"command WONDERSHAPER_UPLOAD_DOWNLOAD success {sender_instance_name}. ")

    logger.info(f"scp setup file to sender {receiver_instance_name}")
    result = CommandController.ec2_service.scp(receiver_instance_public_ip, receiver_instance_name, "utils/sys_diag.sh", "/home/ubuntu/sys_diag.sh", True)
    logger.info(f"scp complete to sender {receiver_instance_name}")

    logger.info(f"running command SYS_INFO into {receiver_instance_name}")
    result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None, Command.SYS_INFO_SCRIPT, non_blocking=False)
    logger.info(f"command SYS_INFO success {receiver_instance_name}. Result: {result}")


    ############ call setup helper commands ############

    src_file = "/home/ubuntu/" + config['ffmpeg_file']
    record_file = "/home/ubuntu/" + config['record_file']
    record_ffmpeg_file = f"/home/ubuntu/record_{tracking_id}_{sender_region}_{receiver_region}_{src_audio_config}_{sender_instance_type}_{receiver_instance_type}_{sender_download_bandwidth}_kbps.wav"

    sender_pjsua_command = Command.PJSUA_TEST_CALLER.format(src_file=src_file,
                                                            caller_instance_public_ip=sender_instance_public_ip,
                                                            receiver_instance_public_ip=receiver_instance_public_ip)
    sender_pjsua_tmux_wrapper = Command.TMUX_WRAPPER_CALL.format(pjsua_command=sender_pjsua_command, tmux_name='mysession', tmux_name_2='mysession')

    receiver_pjsua_command = Command.PJSUA_TEST_RECEIVER.format(record_file=record_file,
                                                                receiver_instance_public_ip=receiver_instance_public_ip)
    receiver_pjsua_tmux_wrapper = Command.TMUX_WRAPPER_RECE.format(pjsua_command=receiver_pjsua_command, tmux_name='mysession', tmux_name_2='mysession')

    ############ create a receiver pjsua session ############

    logger.info(f"create a receiver pjsua session on receiver {receiver_instance_name}")
    result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                   receiver_pjsua_tmux_wrapper, non_blocking=False)
    logger.info(f"started a receiver pjsua session on receiver {receiver_instance_name}")

    ############ create a sender pjsua session ############

    logger.info(f"create a sender pjsua session on receiver {sender_instance_name}")
    result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha", None,
                                                   sender_pjsua_tmux_wrapper, non_blocking=False)
    logger.info(f"started a sender pjsua session on receiver {sender_instance_name}")

    ########### disconnect from sender ssh ###########

    logger.info(f"disconnect from ssh sender instance {sender_instance_name}")
    sender_ssh_msg = SSHController.ssh_service.disconnect_ssh_by_unique_id(sender_instance_name)
    logger.info(f"ssh disconnect success {sender_ssh_msg}. Response: {sender_ssh_msg}")

    ########### disconnect from receiver ssh ###########

    logger.info(f"disconnect from ssh receiver instance {receiver_instance_name}")
    sender_ssh_msg = SSHController.ssh_service.disconnect_ssh_by_unique_id(receiver_instance_name)
    logger.info(f"ssh disconnect success {receiver_instance_name}. Response: {sender_ssh_msg}")

    ############ wait for some time ############

    logger.info(f"Call in progress. Will be killed after {duration} seconds")

    time.sleep(duration)

    ############ ssh sender instance ############

    logger.info(f"ssh again into sender instance {sender_instance_name}")
    receiver_ssh_msg = SSHController.ssh_service.connect_ssh(sender_instance_public_ip, "ubuntu",
                                                             sender_instance_name, sender_key_path)
    logger.info(f"ssh success into {sender_ssh_msg}. Response: {sender_ssh_msg}")

    ############ ssh receiver instance ############

    logger.info(f"ssh again into receiver instance {receiver_instance_name}")
    receiver_ssh_msg = SSHController.ssh_service.connect_ssh(receiver_instance_public_ip, "ubuntu",
                                                             receiver_instance_name, receiver_key_path)
    logger.info(f"ssh success into {receiver_ssh_msg}. Response: {receiver_ssh_msg}")

    ############ kill caller pjsua session ############

    logger.info(f"kill sender pjsua session {sender_instance_name} after {duration} seconds")
    result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha", None,
                                                   Command.KILL_PJSUA, non_blocking=False)
    logger.info(f"command set for killing sender pjsua session {sender_instance_name}")

    ############ kill sender pjsua session ############

    logger.info(f"kill receiver pjsua session {receiver_instance_name} after {duration} seconds")
    result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                   Command.KILL_PJSUA, non_blocking=False)
    logger.info(f"command set for killing receiver pjsua session {receiver_instance_name}")

    ############ check the recorded audio and ffmpeg it ############

    logger.info(f"checking recorded audio and converting to readable wav format")
    result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                   Command.FFMPEG_PROCESS.format(record_file=record_file,
                                                                                 record_ffmpeg=record_ffmpeg_file),
                                                   non_blocking=False)

    ############ delete wondershaper eth0 ############
    #
    # logger.info(f"running command WONDERSHAPER_DELETE into {sender_instance_name}")
    # result = CommandController.ec2_service.execute(sender_instance_public_ip, sender_instance_name, "alpha", None,
    #                                                Command.WONDERSHAPER_DELETE, non_blocking=False)
    # logger.info(f"command WONDERSHAPER_UPLOAD_DOWNLOAD success {sender_instance_name}. ")

    logger.info(f"running command WONDERSHAPER_DELETE into {receiver_instance_name}")
    result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                   Command.WONDERSHAPER_DELETE, non_blocking=False)
    logger.info(f"command WONDERSHAPER_UPLOAD_DOWNLOAD success {receiver_instance_name}. ")


    ############ upload audio to s3 bucket ############
    logger.info(f"uploading wav file {record_ffmpeg_file} to s3 bucket {s3_bucket_url}")
    result = CommandController.ec2_service.execute(receiver_instance_public_ip, receiver_instance_name, "alpha", None,
                                                   Command.S3_UPLOAD.format(
                                                       from_path=record_ffmpeg_file,
                                                       to_path=s3_bucket_url), non_blocking=False)
    logger.info(f"uploaded wav file to {s3_bucket_url}")

    ############ delete instances ############
    logger.info(f"deleting sender instance {sender_instance_name}")
    result = AwsController.aws_service.delete_instance(sender_instance_id, sender_region)
    logger.info(f"deleted sender instance {sender_instance_name}")

    logger.info(f"deleting receiver instance {receiver_instance_name}")
    result = AwsController.aws_service.delete_instance(receiver_instance_id, receiver_region)
    logger.info(f"deleted receiver instance {receiver_instance_name}")

    ############ delete security groups ############
    logger.info(f"deleting sender security groups {sender_security_group_name}")
    result = AwsController.aws_service.delete_security_group(sender_region, sender_security_group_id)
    logger.info(f"deleted sender security groups {sender_security_group_name}")

    logger.info(f"deleting receiver security groups {receiver_security_group_name}")
    result = AwsController.aws_service.delete_security_group(receiver_region, receiver_security_group_id)
    logger.info(f"deleted receiver security groups {receiver_security_group_name}")

    ############ delete security keys ############
    logger.info(f"deleting sender security keys {sender_key_name}")
    result = AwsController.aws_service.delete_security_key(sender_region, sender_key_name, sender_key_path)
    logger.info(f"deleted sender security keys  {sender_key_name}")

    logger.info(f"deleting receiver security keys {receiver_key_name}")
    result = AwsController.aws_service.delete_security_key(receiver_region, receiver_key_name, receiver_key_path)
    logger.info(f"deleted receiver security keys {receiver_key_name}")

    ############ terminating simulation############

    logger.info(f"terminating simulation")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="This script helps you to perform an e2e data collection run.")

    parser.add_argument('--tracking_id', '--id', type=str, help='An id to track your simulation')
    parser.add_argument('--sender_region', '--sreg', type=str, required=True,
                        # choices=['us-east-1', 'us-west-1', 'eu-west-2', 'ap-south-1', 'ap-southeast-2'],
                        help='Sender region')
    parser.add_argument('--receiver_region', '--rreg', type=str, required=True,
                        # choices=['us-east-1', 'us-west-1', 'eu-west-2', 'ap-south-1', 'ap-southeast-2'],
                        help='Receiver region')
    parser.add_argument('--sender_instance_type', '--sins', type=str, default='t2.micro',
                        # choices=['t2.micro'],
                        help='Sender instance type')
    parser.add_argument('--receiver_instance_type', '--rins', type=str, default='t2.micro',
                        # choices=['t2.micro'],
                        help='Receiver instance type')
    parser.add_argument('--sender_instance_ami', '--sami', type=str,
                        # default='ami-053b0d53c279acc90',
                        # choices=['ami-053b0d53c279acc90'],
                        help='Sender instance ami id')
    parser.add_argument('--receiver_instance_ami', '--rami', type=str,
                        # default='ami-053b0d53c279acc90',
                        # choices=['ami-053b0d53c279acc90', 'ami-0310483fb2b488153'],
                        help='Receiver instance ami id')
    parser.add_argument('--sender_upload_bandwidth', '--subw', type=str, help='Sender upload bandwidth')
    parser.add_argument('--sender_download_bandwidth', '--sdbw', type=str, help='Sender download bandwidth')
    parser.add_argument('--receiver_upload_bandwidth', '--rubw', type=str, help='Receiver upload bandwidth')
    parser.add_argument('--receiver_download_bandwidth', '--rdbw', type=str, help='Receiver download bandwidth')
    parser.add_argument('--src_audio_config', '--src', type=str, required=True,
                        choices=['test_src_noisy', 'test_src_clean', 'train_src_noisy', 'train_src_clean'],
                        help='Source audio configuration')
    parser.add_argument('--duration', '--dur', type=int, required=True, help='Duration of call')
    parser.add_argument('--s3_bucket_url', '--s3', type=str, required=True, help='S3 storage url')

    # Test command
    # --sreg us-east-1 --rreg ap-southeast-2 --sins t2.micro --rins t2.micro --sami ami-053b0d53c279acc90 --rami ami-053b0d53c279acc90 --src test_src_clean --dur 20 --subw 500 --subw 500 --sdbw 500 --rubw 500 --rdbw 500

    # Parse the arguments
    args = parser.parse_args()

    # You can now use the parsed arguments in your script logic
    # print(f"Sender Region: {args.sender_region}")
    # print(f"Receiver Region: {args.receiver_region}")
    # print(f"Sender Instance Type: {args.sender_instance_type}")
    # print(f"Receiver Instance Type: {args.receiver_instance_type}")
    # print(f"Sender Instance AMI-ID: {args.sender_instance_ami}")
    # print(f"Receiver Instance AMI-ID: {args.receiver_instance_ami}")
    # print(f"Sender Upload Bandwidth: {args.sender_upload_bandwidth}")
    # print(f"Sender Download Bandwidth: {args.sender_download_bandwidth}")
    # print(f"Receiver Upload Bandwidth: {args.receiver_upload_bandwidth}")
    # print(f"Receiver Download Bandwidth: {args.receiver_download_bandwidth}")
    # print(f"Source Audio Configuration: {args.src_audio_config}")
    # print(f"Duration of call: {args.duration}")
    # print(f"S3 Bucket Url : {args.s3_bucket_url}")

    if not args.tracking_id:
        tracking_id = str(uuid.uuid4())
        # print(f"Tracking id: {tracking_id}")
    else:
        tracking_id = args.tracking_id

    simulate(tracking_id, args.sender_region, args.receiver_region, args.sender_instance_type,
             args.receiver_instance_type, args.sender_instance_ami, args.receiver_instance_ami,
             args.sender_upload_bandwidth, args.sender_download_bandwidth, args.receiver_upload_bandwidth,
             args.receiver_download_bandwidth, args.src_audio_config, args.duration, args.s3_bucket_url)