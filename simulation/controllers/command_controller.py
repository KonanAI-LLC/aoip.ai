from flask import Blueprint, request

from services.command_service import CommandService


class CommandController:
    command_controller = Blueprint('ec2', __name__, url_prefix='/command')
    ec2_service = CommandService()

    @staticmethod
    @command_controller.route('/run-command', methods=['POST'])
    def run_command_on_ec2():
        data = request.get_json()

        public_ip = data.get('public_ip')
        unique_id = data.get('unique_id')
        tmux_name = data.get('tmux_name')
        command_group = data.get('command_group')
        command = data.get('command')
        non_blocking = data.get('non_blocking', False)

        result = CommandController.ec2_service.execute(public_ip, unique_id, tmux_name, command_group, command, non_blocking)

        return {
                   'message': 'Command run successfully',
                    'output': result
                   }, 200


    @staticmethod
    @command_controller.route('/scp-command', methods=['POST'])
    def scp_command_on_ec2():
        data = request.get_json()

        public_ip = data.get('public_ip')
        unique_id = data.get('unique_id')
        from_path = data.get('from_path')
        to_path = data.get('to_path')
        reverse = data.get('reverse')

        result = CommandController.ec2_service.scp(public_ip, unique_id, from_path, to_path, reverse)

        return {
                   'message': 'SCP run successfully',
                    'output': result
                   }, 200

