import os.path

import boto3

from data.aws_repository import AwsRepository
from helper.EC2Instance import EC2Instance
from helper.SecurityGroup import SecurityGroup


class AwsService:

    def __init__(self):
        self.aws_repo = AwsRepository()

    def add_user(self, name, email):
        self.aws_repo.add_user(name, email)

    def create_security_group(self, region, name, description):
        security_group = SecurityGroup(region, name, description)
        security_group.create_security_group()

        if not security_group.exists:
            security_group.add_rules_to_security_group()
        return security_group.sg_id

    def delete_security_group(self, region, sg_id):
        info = SecurityGroup.delete_security_group(region, sg_id)
        return info

    def get_security_group_by_id(self, sg_id, region):
        info = SecurityGroup.get_security_group_by_id(sg_id, region)
        return info

    def create_ec2_instance(self, region, instance_type, instance_name, ami_id, disk_size, ssh_key_name, security_group_id):
        ec2_instance = EC2Instance(region, instance_type, instance_name, ami_id, disk_size, ssh_key_name, security_group_id)
        instance_id = ec2_instance.create_instance()
        return instance_id

    def get_ec2_instance_by_id(self, instance_id, region):
        ec = EC2Instance.get_instance_by_id(instance_id, region)
        return ec

    def get_current_instance_status(self, instance_id, region):
        status = EC2Instance.get_current_instance_status(instance_id, region)
        return status

    def delete_instance(self, instance_id, region):
        status = EC2Instance.delete_instance(instance_id, region)
        return status

    def reboot_instance(self, instance_id, region):
        status = EC2Instance.reboot_instance(instance_id, region)
        return status

    def create_security_key(self, region, name, dir_path):
        ec2 = boto3.client('ec2', region_name=region)
        keys = ec2.describe_key_pairs().get('KeyPairs', [])
        if any(key['KeyName'] == name for key in keys):
            return f"Key pair with name {name} already exists."

        key_pair = ec2.create_key_pair(KeyName=name)
        private_key = key_pair['KeyMaterial']

        path = os.path.join(dir_path, f'{name}.pem')
        with open(path, 'w') as file:
            file.write(private_key)

        return f"Key pair created and stored in {path}"

    def delete_security_key(self, region, name, path=None):
        ec2 = boto3.client('ec2', region_name=region)
        try:
            # Attempt to delete the key pair with the provided name
            ec2.delete_key_pair(KeyName=name)

            # Optionally, remove the local pem file if it exists
            if path:
                import os
                pem_file_path = path
                if os.path.exists(pem_file_path):
                    os.remove(pem_file_path)
                    return f"Key pair {name} deleted and local file {path} removed."

            return f"Key pair {name} deleted successfully."
        except Exception as e:
            return f"Error deleting key pair {name}: {str(e)}"