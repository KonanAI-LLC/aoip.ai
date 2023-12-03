import pytest


@pytest.fixture
def create_key(api_client, base_url):
    def _create_key(region, name, dir_path):
        endpoint = f'{base_url}/aws/create-key'
        data = {
            "region": region,
            "name": name,
            "dir_path": dir_path
            }
        response = api_client.post(endpoint, json=data)
        return response.status_code, response.json()

    return _create_key


@pytest.fixture
def delete_key(api_client, base_url):
    def _delete_key(region, name):
        endpoint = f'{base_url}/aws/delete-key'
        data = {
            "region": region,
            "name": name
            }
        response = api_client.post(endpoint, json=data)
        return response.json()

    return _delete_key


@pytest.fixture
def create_security_group(api_client, base_url):
    def _create_security_group(region, name, description):
        endpoint = f'{base_url}/aws/create-security-group'
        data = {
            "region": region,
            "name": name,
            "description": description
            }
        response = api_client.post(endpoint, json=data)
        return response.status_code, response.json()

    return _create_security_group


@pytest.fixture
def delete_security_group(api_client, base_url):
    def _delete_security_group(region, sg_id):
        endpoint = f'{base_url}/aws/delete-security-group'
        data = {
            "region": region,
            "sg_id": sg_id,
            }
        response = api_client.post(endpoint, json=data)
        return response.json()

    return _delete_security_group


@pytest.fixture
def create_aws_instance(api_client, base_url):
    def _create_aws_instance(region, instance_type, instance_name, ami_id, disk_size, ssh_key_name, security_group_id):
        endpoint = f'{base_url}/aws/create-instance'
        data = {
            "region": region,
            "instance_type": instance_type,
            "instance_name": instance_name,
            "ami_id": ami_id,
            "disk_size": disk_size,
            "ssh_key_name": ssh_key_name,
            "security_group_id": security_group_id
            }
        response = api_client.post(endpoint, json=data)
        return response.status_code, response.json()

    return _create_aws_instance


@pytest.fixture
def get_aws_instance(api_client, base_url):
    def _get_aws_instance(region, instance_id):
        endpoint = f'{base_url}/aws/get-instance'
        data = {
            "region": region,
            "instance_id": instance_id
            }
        response = api_client.post(endpoint, json=data)
        return response.status_code, response.json()

    return _get_aws_instance


@pytest.fixture
def get_aws_instance_status(api_client, base_url):
    def _get_aws_instance_status(region, instance_id):
        endpoint = f'{base_url}/aws/get-instance-status'
        data = {
            "region": region,
            "instance_id": instance_id
            }
        response = api_client.post(endpoint, json=data)
        return response.status_code, response.json()

    return _get_aws_instance_status


@pytest.fixture
def delete_aws_instance(api_client, base_url):
    def _delete_aws_instance(region, instance_id):
        endpoint = f'{base_url}/aws/delete-instance'
        data = {
            "region": region,
            "instance_id": instance_id
            }
        response = api_client.post(endpoint, json=data)
        return response.status_code, response.json()

    return _delete_aws_instance


@pytest.fixture
def ssh_into_instance(api_client, base_url):
    def _ssh_into_instance(unique_id, public_ip, username, key_file):
        endpoint = f'{base_url}/ssh/connect-ssh'
        data = {
            "unique_id": unique_id,
            "public_ip": public_ip,
            "username": username,
            "key_file": key_file
            }
        response = api_client.post(endpoint, json=data)
        return response.status_code, response.json()

    return _ssh_into_instance


@pytest.fixture
def run_given_command_group(api_client, base_url):
    def _run_given_command(unique_id, tmux_name, command_group, command=""):
        endpoint = f'{base_url}/command/run-command'
        data = {
            "unique_id": unique_id,
            "tmux_name": tmux_name,
            "command_group": command_group,
            "command": command,
            "non_blocking": False
            }
        response = api_client.post(endpoint, json=data)
        return response.status_code, response.json()

    return _run_given_command


@pytest.fixture
def run_given_command_non_blocking(api_client, base_url):
    def _run_given_command(unique_id, tmux_name, command):
        endpoint = f'{base_url}/command/run-command'
        data = {
            "unique_id": unique_id,
            "tmux_name": tmux_name,
            "command": command,
            "non_blocking": True
            }
        response = api_client.post(endpoint, json=data)
        return response.status_code, response.json()

    return _run_given_command

@pytest.fixture
def scp_to_local(api_client, base_url):
    def _scp_to_local(unique_id, public_ip, remote_path, local_path):
        endpoint = f'{base_url}/command/scp-command'
        data = {
            "unique_id": unique_id,
            "public_ip": public_ip,
            "remote_path": remote_path,
            "local_path": local_path
            }

        response = api_client.post(endpoint, json=data)
        return response.status_code, response.json()
    return _scp_to_local