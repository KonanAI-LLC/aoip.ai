from flask import Blueprint, request

from services.aws_service import AwsService


class AwsController:
    aws_controller = Blueprint('aws', __name__, url_prefix='/aws')
    aws_service = AwsService()

    @staticmethod
    @aws_controller.route('/create-instance', methods=['POST'])
    def create_instance():
        if request.method == 'POST':
            data = request.get_json()
            region = data.get('region')
            instance_type = data.get('instance_type')
            instance_name = data.get('instance_name')
            ami_id = data.get('ami_id')
            disk_size = data.get('disk_size')
            ssh_key_name = data.get('ssh_key_name')
            security_group_id = data.get('security_group_id')
            instance_id = AwsController.aws_service.create_ec2_instance(region, instance_type, instance_name, ami_id, disk_size,
                                                                        ssh_key_name,
                                                                        security_group_id)
            return {'message': 'Instance Created Successfully', 'instance_id': instance_id}, 201

    @staticmethod
    @aws_controller.route('/get-instance', methods=['POST'])
    def get_instance():
        if request.method == 'POST':
            data = request.get_json()
            instance_id = data.get('instance_id')
            region = data.get('region')
            details = AwsController.aws_service.get_ec2_instance_by_id(instance_id, region)
            return {'message': 'Retrieved', 'details': details}, 201

    @staticmethod
    @aws_controller.route('/get-instance-status', methods=['POST'])
    def get_instance_status():
        if request.method == 'POST':
            data = request.get_json()
            instance_id = data.get('instance_id')
            region = data.get('region')
            instance_status = AwsController.aws_service.get_current_instance_status(instance_id, region)
            return {'message': 'Retrieved', 'instance_status': instance_status}, 201

    @staticmethod
    @aws_controller.route('/delete-instance', methods=['POST'])
    def delete_instance():
        if request.method == 'POST':
            data = request.get_json()
            instance_id = data.get('instance_id')
            region = data.get('region')
            details = AwsController.aws_service.get_ec2_instance_by_id(instance_id, region)
            return {'message': 'Retrieved', 'details': details}, 201

    @staticmethod
    @aws_controller.route('/reboot-instance', methods=['POST'])
    def reboot_instance():
        if request.method == 'POST':
            data = request.get_json()
            instance_id = data.get('instance_id')
            region = data.get('region')
            details = AwsController.aws_service.get_ec2_instance_by_id(instance_id, region)
            return {'message': 'Retrieved', 'details': details}, 201

    @staticmethod
    @aws_controller.route('/create-security-group', methods=['POST'])
    def create_security_group():
        if request.method == 'POST':
            data = request.get_json()
            region = data.get('region')
            name = data.get('name')
            description = data.get('description')
            security_group_id = AwsController.aws_service.create_security_group(region, name, description)
            return {
                       'message': 'Security group Created Successfully',
                       'security_group_id': security_group_id
                       }, 201

    @staticmethod
    @aws_controller.route('/delete-security-group', methods=['POST'])
    def delete_security_group():
        if request.method == 'POST':
            data = request.get_json()
            region = data.get('region')
            sg_id = data.get('sg_id')
            security_group_id = AwsController.aws_service.delete_security_group(region, sg_id)
            return {
                       'message': 'Security group deleted Successfully',
                       'security group id': security_group_id
                       }, 201

    @staticmethod
    @aws_controller.route('/create-key', methods=['POST'])
    def create_security_key():
        if request.method == 'POST':
            data = request.get_json()
            region = data.get('region')
            name = data.get('name')
            dir_path = data.get('dir_path')
            created_name = AwsController.aws_service.create_security_key(region, name, dir_path)
            return {'message': created_name, 'key_name': name}, 201

    @staticmethod
    @aws_controller.route('/delete-key', methods=['POST'])
    def delete_security_key():
        if request.method == 'POST':
            data = request.get_json()
            region = data.get('region')
            name = data.get('name')
            created_name = AwsController.aws_service.delete_security_key(region, name)
            return {'message': created_name, 'key_name': name}, 201