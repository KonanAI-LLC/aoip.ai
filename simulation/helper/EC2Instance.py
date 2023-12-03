import boto3


class EC2Instance:

    def __init__(self, region: str, instance_type: str, instance_name: str, ami_id: str,
                 disk_size: int, ssh_key_name: str, security_group_id: str):
        self.region = region
        self.instance_type = instance_type
        self.instance_name = instance_name
        self.ami_id = ami_id
        self.disk_size = disk_size
        self.ssh_key_name = ssh_key_name
        self.security_group_id = security_group_id
        self.ec2 = boto3.client('ec2', region_name=self.region)
        self.exists = False

    def create_instance(self):
        self.instance_details = self.ec2.run_instances(
                ImageId=self.ami_id,
                MinCount=1,
                MaxCount=1,
                InstanceType=self.instance_type,
                KeyName=self.ssh_key_name,
                SecurityGroupIds=[self.security_group_id],
                BlockDeviceMappings=[
                    {
                        'DeviceName': '/dev/sda1',
                        'Ebs': {
                            'VolumeSize': self.disk_size,
                            },
                        },
                    ],
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': self.instance_name
                                }
                            ]
                        }
                    ]
                )
        return self.get_instance_id()

    def get_instance_id(self) -> str:
        self.instance_id = self.instance_details['Instances'][0]['InstanceId']
        return self.instance_id

    @staticmethod
    def get_current_instance_status(instance_id: str, region: str) -> str:
        """
        Returns the current status of the EC2 instance.
        """
        ec2_ = boto3.client('ec2', region_name=region)
        response = ec2_.describe_instance_status(InstanceIds=[instance_id])
        if not response['InstanceStatuses']:
            return "Instance not found."
        return response['InstanceStatuses'][0]['InstanceState']['Name']

    @staticmethod
    def delete_instance(instance_id: str, region: str):
        """
        Terminates the EC2 instance.
        """
        ec2_ = boto3.client('ec2', region_name=region)
        response = ec2_.terminate_instances(InstanceIds=[instance_id])
        return response['TerminatingInstances'][0]['CurrentState']['Name']

    @staticmethod
    def reboot_instance(instance_id: str, region: str):
        """
        Reboots the EC2 instance.
        """
        ec2_ = boto3.client('ec2', region_name=region)
        ec2_.reboot_instances(InstanceIds=[instance_id])
        return f"Reboot initiated for instance: {instance_id}"

    @staticmethod
    def get_instance_by_id(instance_id: str, region: str):
        ec2_ = boto3.client('ec2', region_name=region)
        response = ec2_.describe_instances(
                InstanceIds=[instance_id]
                )
        return response['Reservations'][0]['Instances'][0]