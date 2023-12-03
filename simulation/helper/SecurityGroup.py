import boto3


class SecurityGroup:

    def __init__(self, region: str, security_group_name: str, description: str):
        self.region = region
        self.security_group_name = security_group_name
        self.description = description
        self.ec2 = boto3.client('ec2', region_name=self.region)
        self.exists = False

    def create_security_group(self):
        response = self.ec2.describe_security_groups(
                Filters=[
                    dict(Name='group-name', Values=[self.security_group_name])
                    ]
                )

        if not response['SecurityGroups']:
            self.sg_id = self.ec2.create_security_group(
                    GroupName=self.security_group_name,
                    Description=self.description
                    )['GroupId']
        else:
            self.sg_id = response['SecurityGroups'][0]['GroupId']
            self.exists = True

    def add_rules_to_security_group(self):
        self.ec2.authorize_security_group_ingress(
                GroupName=self.security_group_name,
                IpPermissions=[
                    {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                    {'IpProtocol': '-1', 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                    {'IpProtocol': 'udp', 'FromPort': 3000, 'ToPort': 9000, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
                    ]
                )

    @staticmethod
    def delete_security_group(region, sg_id):
        ec2_ = boto3.client('ec2', region_name=region)
        try:
            ec2_.delete_security_group(GroupId=sg_id)
            print(f"Security Group {sg_id} deleted successfully!")
        except Exception as e:
            print(f"Error deleting security group {sg_id}: {str(e)}")

    @staticmethod
    def get_security_group_by_id(sg_id, region):
        ec2_ = boto3.client('ec2', region_name=region)
        try:
            response = ec2_.describe_security_groups(
                    GroupIds=[sg_id]
                    )
            if response['SecurityGroups']:
                sg_details = response['SecurityGroups'][0]
                return sg_details
            else:
                print(f"No Security Group found with the ID {sg_id}")
                return None
        except Exception as e:
            print(f"Error fetching details for security group with ID {sg_id}: {str(e)}")
            return None