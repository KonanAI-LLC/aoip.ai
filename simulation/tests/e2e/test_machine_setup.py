import uuid
import time

def test_setup_machine(test_logger, create_key, delete_key, create_security_group, delete_security_group, create_aws_instance, get_aws_instance, get_aws_instance_status, delete_aws_instance, ssh_into_instance, run_given_command_group, base_url, region, run_given_command_non_blocking, scp_to_local):

    return
    delete_key_var, delete_sg_var, delete_caller_var, delete_receiver_var = False, False, False, False
    def cleanup():
        if delete_key_var:
            logger.info(f"deleting security key {key_name}")
            status_code, response = delete_key(region, key_name)
            logger.info(f"deleted security key {key_name}")

        if delete_sg_var:
            logger.info(f"deleting security group {sg_id}")
            status_code, response = delete_security_group(region, sg_id)
            logger.info(f"deleted security group {sg_id}")

        if delete_caller_var:
            logger.info(f"deleting caller instance {caller_instance_id}")
            status_code, response = delete_aws_instance(region, caller_instance_id)
            logger.info(f"deleted caller instance {caller_instance_id}")

        if delete_receiver_var:
            logger.info(f"deleting receiver instance {caller_instance_id}")
            status_code, response = delete_aws_instance(region, receiver_instance_id)
            logger.info(f"deleted receiver instance {caller_instance_id}")

    test_id = str(uuid.uuid4())
    logger = test_logger(test_id)

    ############ starting e2e test ############

    logger.info("starting e2e test")

    ############ create security key ############

    key_name = f"key_e2e_test_{test_id}"
    dir_path = "creds/"

    logger.info(f"creating security key {key_name}")
    status_code, response = create_key(region, key_name, dir_path)

    if status_code != 201:
        logger.info(f"Failed to create security key. status_code: {status_code}. Response: {response}")
        cleanup()
        return
    else:
        delete_key_var = True

    logger.info(f"security key {key_name} created. Response: {response}")
    key_path = dir_path + f"{key_name}.pem"

    ############ create security group ############

    security_group_name = f"sg_e2e_test_{test_id}"

    logger.info(f"creating security group {security_group_name}")
    status_code, sg_response = create_security_group(region, security_group_name, "security group for e2e test")

    if status_code != 201:
        logger.info(f"Failed to create security group. status_code: {status_code}. Response: {sg_response}")
        cleanup()
        return
    else:
        delete_sg_var = True
    logger.info(f"security group {security_group_name} created. Response: {sg_response}")
    sg_id = sg_response["security_group_id"]

    ############ create caller instance ############

    caller_instance_name = f"instance_caller_e2e_test_{test_id}"

    logger.info(f"creating caller instance {caller_instance_name}")
    status_code, instance_response = create_aws_instance(
            region, "t2.micro", caller_instance_name, "ami-053b0d53c279acc90", 8, key_name, sg_id)

    if status_code != 201:
        logger.info(f"Failed to create caller instance. status_code: {status_code}. Response: {instance_response}")
        cleanup()
        return
    else:
        delete_caller_var = True

    logger.info(f"caller instance created {caller_instance_name}. status_code: {status_code}. Response: {instance_response} ")
    caller_instance_id = instance_response['instance_id']

    time.sleep(5)

    logger.info(f"fetching instance details for {caller_instance_name}")
    status_code, instance_details = get_aws_instance(region, caller_instance_id)
    if status_code != 201:
        logger.info(f"Failed to create caller instance. status_code: {status_code}. Response: {instance_details}")
        cleanup()
        return

    caller_instance_public_ip = instance_details['details']['PublicIpAddress']

    logger.info(f"instance details for {caller_instance_name}. Public Ip: {caller_instance_public_ip}. Other details: {instance_details}")

    # while loop to check status if instance is ready. Once ready, continue

    caller_instance_state = instance_details['details']['State']['Name']
    if caller_instance_state != 'running':
        logger.info(f"wait for caller instance to reach running status. Current status: {caller_instance_state}")

        while caller_instance_state != 'running':
            time.sleep(5)
            status_code, instance_details = get_aws_instance_status(region, caller_instance_id)
            caller_instance_state = instance_details['instance_status']
            logger.info(f"wait for caller instance to reach running status. Current status: {caller_instance_state}")

    ############ create receiver instance ############

    receiver_instance_name = f"instance_receiver_e2e_test_{test_id}"

    logger.info(f"creating receiver instance {receiver_instance_name}")
    status_code, instance_response = create_aws_instance(
            region, "t2.micro", receiver_instance_name, "ami-053b0d53c279acc90", 8, key_name, sg_id)

    if status_code != 201:
        logger.info(f"Failed to create receiver instance. status_code: {status_code}. Response: {instance_response}")
        cleanup()
        return
    else:
        delete_receiver_var = True

    logger.info(f"receiver instance created {receiver_instance_name}. status_code: {status_code}. Response: {instance_response} ")
    receiver_instance_id = instance_response['instance_id']

    time.sleep(5)

    logger.info(f"fetching instance details for {receiver_instance_name}")
    status_code, instance_details = get_aws_instance(region, receiver_instance_id)
    if status_code != 201:
        logger.info(f"Failed to create receiver instance. status_code: {status_code}. Response: {instance_details}")
        cleanup()
        return

    receiver_instance_public_ip = instance_details['details']['PublicIpAddress']

    logger.info(f"instance details for {receiver_instance_name}. Public Ip: {receiver_instance_public_ip}. Other details: {instance_details}")

    # while loop to check status if instance is ready. Once ready, continue

    receiver_instance_state = instance_details['details']['State']['Name']
    if receiver_instance_state != 'running':
        logger.info(f"wait for receiver instance to reach running status. Current status: {receiver_instance_state}")

        while receiver_instance_state != 'running':
            time.sleep(5)
            status_code, instance_details = get_aws_instance_status(region, receiver_instance_id)
            receiver_instance_state = instance_details['instance_status']
            logger.info(f"wait for receiver instance to reach running status. Current status: {receiver_instance_state}")

    ############ setup caller instance ############

    logger.info(f"starting setup for caller instance {caller_instance_name}")

    time.sleep(15)

    logger.info(f"trying ssh into {caller_instance_name}")
    status_code, ssh_response = ssh_into_instance(caller_instance_name, caller_instance_public_ip, "ubuntu", key_path)

    if status_code != 200:
        logger.info(f"Failed to ssh into caller instance. status_code: {status_code}. Response: {ssh_response}")
        cleanup()
        return

    logger.info(f"ssh success into {caller_instance_name}. Response: {ssh_response}")

    logger.info(f"running command SETUP_MACHINE into {caller_instance_name}")
    status_code, setup_response = run_given_command_group(caller_instance_name, "caller_instance", "SETUP_MACHINE")

    if status_code != 200:
        logger.info(f"Failed to run command SETUP_MACHINE into caller instance. status_code: {status_code}. Response: {setup_response}")
        cleanup()
        return

    logger.info(f"command SETUP_MACHINE success {caller_instance_name}. status_code: {status_code}. Response: {setup_response['message']}")

    logger.info(f"running command WGET_E2E_FILES in {caller_instance_name} to get test audio files")
    wget_response = run_given_command_group(caller_instance_name, "caller_instance", "WGET_E2E_FILES")

    if status_code != 200:
        logger.info(f"Failed to run command WGET_E2E_FILES into caller instance. status_code: {status_code}. Response: {wget_response}")
        cleanup()
        return

    logger.info(f"command WGET_E2E_FILES success in {caller_instance_name}")

    logger.info(f"running command SOX_FILES in {caller_instance_name} to get test audio files")
    wget_response = run_given_command_group(caller_instance_name, "caller_instance", "SOX_PROCESS")

    if status_code != 200:
        logger.info(f"Failed to run command SOX_PROCESS into caller instance. status_code: {status_code}. Response: {wget_response}")
        cleanup()
        return

    logger.info(f"command SOX_PROCESS success in {caller_instance_name}")

    logger.info(f"running command START_VIRTUAL_MIC in {caller_instance_name} to setup virtual mic")
    mic_response = run_given_command_group(caller_instance_name, "caller_instance", "START_VIRTUAL_MIC")

    if status_code != 200:
        logger.info(
            f"Failed to run command START_VIRTUAL_MIC into caller instance. status_code: {status_code}. Response: {mic_response}")
        cleanup()
        return

    logger.info(f"command START_VIRTUAL_MIC success in {caller_instance_name} to setup virtual mic")

    ############ setup receiver instance ############

    logger.info(f"starting setup for receiver instance {receiver_instance_name}")

    time.sleep(15)

    logger.info(f"trying ssh into {receiver_instance_name}")
    status_code, ssh_response = ssh_into_instance(receiver_instance_name, receiver_instance_public_ip, "ubuntu", key_path)

    if status_code != 200:
        logger.info(f"Failed to ssh into receiver instance. status_code: {status_code}. Response: {ssh_response}")
        cleanup()
        return

    logger.info(f"ssh success into {receiver_instance_name}. Response: {ssh_response}")

    logger.info(f"running command SETUP_MACHINE into {receiver_instance_name}")
    status_code, setup_response = run_given_command_group(receiver_instance_name, "receiver_instance", "SETUP_MACHINE")

    if status_code != 200:
        logger.info(f"Failed to run command SETUP_MACHINE into receiver instance. status_code: {status_code}. Response: {setup_response}")
        cleanup()
        return

    logger.info(f"command SETUP_MACHINE success {receiver_instance_name}. status_code: {status_code}. Response: {setup_response['message']}")

    logger.info(f"running command START_VIRTUAL_MIC in {receiver_instance_name} to setup virtual mic")
    mic_response = run_given_command_group(receiver_instance_name, "receiver_instance", "START_VIRTUAL_MIC")

    if status_code != 200:
        logger.info(
            f"Failed to run command START_VIRTUAL_MIC into receiver instance. status_code: {status_code}. Response: {mic_response}")
        cleanup()
        return

    logger.info(f"command START_VIRTUAL_MIC success in {receiver_instance_name} to setup virtual mic")

    src_file = "/home/ubuntu/src_clean_converted.wav"
    record_file = "/home/ubuntu/src_relay_record.wav"
    record_ffmpeg_file = "/home/ubuntu/src_relay_record_ffmpeg.wav"

    ############ helper commands ############


    PJSUA_TEST_CALLER = f"cd /home/ubuntu/pjproject-2.13/pjsip-apps/bin && ./pjsua-x86_64-unknown-linux-gnu --use-cli --auto-play --play-file {src_file} --local-port=5061 --no-vad --ip-addr {caller_instance_public_ip} --stun-srv=stun.l.google.com:19302 --duration=10 sip:{receiver_instance_public_ip}:5061"
    TMUX_WRAPPER_CALL = f"tmux new-session -d -s mysession && tmux send-keys -t mysession '{PJSUA_TEST_CALLER}' C-m"

    PJSUA_TEST_RECEIVER = f"cd /home/ubuntu/pjproject-2.13/pjsip-apps/bin && ./pjsua-x86_64-unknown-linux-gnu --use-cli --auto-answer 200 --auto-rec --rec-file {record_file} --local-port=5061 --ip-addr {receiver_instance_public_ip} --stun-srv=stun.l.google.com:19302"
    TMUX_WRAPPER_RECE = f"tmux new-session -d -s mysession && tmux send-keys -t mysession '{PJSUA_TEST_RECEIVER}' C-m"

    KILL_PJSUA = "ps -aux | grep pjsua | grep -v grep | awk '{print $2}' | xargs kill -9"

    ############ create a receiver pjsua session ############

    logger.info(f"create a receiver pjsua session on receiver {receiver_instance_name}")
    status_code, receiver_pjsua_command = run_given_command_group(receiver_instance_name, "receiver_instance", None, TMUX_WRAPPER_RECE)

    if status_code != 200:
        logger.info(
            f"Failed to run command PJSUA_TEST_RECEIVER into receiver instance. status_code: {status_code}. Response: {receiver_pjsua_command}")
        cleanup()
        return

    logger.info(f"started session on pjsua reciever instance.status_code: {status_code}. Response: {receiver_pjsua_command}")

    ############ create a caller pjsua session ############

    logger.info(f"create a caller pjsua session on receiver {caller_instance_name} and attempt a call to receiver")
    status_code, caller_pjsua_command = run_given_command_group(caller_instance_name, "caller_instance", None, TMUX_WRAPPER_CALL)

    if status_code != 200:
        logger.info(
                f"Failed to run command PJSUA_TEST_CALLER into caller instance. status_code: {status_code}. Response: {caller_pjsua_command}")
        cleanup()
        return

    logger.info(
        f"started session on pjsua reciever instance.status_code: {status_code}. Response: {receiver_pjsua_command}")

    ############ wait for some time ############

    logger.info(f"Call in progress. Will be killed after 20seconds")

    time.sleep(20)

    ############ kill caller pjsua session ############

    logger.info(f"kill caller pjsua session {caller_instance_name}")

    status_code, kill_caller_pjsua_command = run_given_command_group(caller_instance_name, "caller_instance", None, KILL_PJSUA)

    if status_code != 200:
        logger.info(
                f"Failed to run command KILL_PJSUA into caller instance. status_code: {status_code}. Response: {kill_caller_pjsua_command}")
        cleanup()
        return

    logger.info(
        f"Killed pjsua session on pjsua caller instance.status_code: {status_code}. Response: {kill_caller_pjsua_command}")


    ############ kill receiver pjsua session ############

    logger.info(f"kill receiver pjsua session {receiver_instance_name}")

    status_code, kill_receiver_pjsua_command = run_given_command_group(receiver_instance_name, "receiver_instance", None, KILL_PJSUA)

    if status_code != 200:
        logger.info(
                f"Failed to run command KILL_PJSUA into receiver instance. status_code: {status_code}. Response: {kill_receiver_pjsua_command}")
        cleanup()
        return

    logger.info(
            f"Killed pjsua session on pjsua receiver instance.status_code: {status_code}. Response: {kill_receiver_pjsua_command}")

    ############ check the recorded audio and ffmpeg it ############

    FFMPEG_PROCESS = f"ffmpeg -i {record_file} -acodec pcm_s16le -ac 1 -ar 16000 {record_ffmpeg_file}"
    SOXI_FILE = f"soxi {record_ffmpeg_file}"

    logger.info(f"checking recorded audio and converting to readable wav format")

    status_code, ffmpeg_response = run_given_command_group(receiver_instance_name, "receiver_instance", None, f"{FFMPEG_PROCESS} && {SOXI_FILE}")

    if status_code != 200:
        logger.info(
                f"Failed to run command FFMPEG_PROCESS into receiver instance. status_code: {status_code}. Response: {ffmpeg_response}")
        cleanup()
        return

    logger.info(f"audio processing complete for recorded audio. status_code: {status_code}. Response: {ffmpeg_response}")

    ############ scp the recorded audio ############

    local_wav_path = "tests/e2e_test_recorded_audio.wav"
    logger.info(f"scp the recorded audio")
    status_code, scp_response = scp_to_local(receiver_instance_name, receiver_instance_public_ip, record_ffmpeg_file, local_wav_path)
    if status_code != 200:
        logger.info(
                f"Failed to run command FFMPEG_PROCESS into receiver instance. status_code: {status_code}. Response: {ffmpeg_response}")
        cleanup()
        return
    logger.info(f"scp complete for recorded audio. status_code: {status_code}. Response: {scp_response}")


    ############ delete all aws resources ############

    logger.info(f"deleting all aws resources")
    cleanup()

    ############ delete all aws resources ############

    logger.info(f"terminating e2e test")
