from flask import Blueprint, jsonify, request

from services.ssh_service import SSHService


class SSHController:
    ssh_controller = Blueprint('ssh', __name__, url_prefix='/ssh')
    ssh_service = SSHService()

    @staticmethod
    @ssh_controller.route('/connect-ssh', methods=['POST'])
    def connect_ssh():
        data = request.get_json()
        unique_id = data.get('unique_id')
        public_ip = data.get('public_ip')
        username = data.get('username')
        key_file = data.get('key_file')
        response = SSHController.ssh_service.connect_ssh(public_ip, username, unique_id, key_file)
        return jsonify({'message': response})

    @staticmethod
    @ssh_controller.route('/disconnect-ssh', methods=['POST'])
    def disconnect_ssh():
        data = request.get_json()
        unique_id = data.get('unique_id')
        public_ip = data.get('public_ip')
        if unique_id:
            response = SSHController.ssh_service.disconnect_ssh_by_unique_id(unique_id)
        elif public_ip:
            response = SSHController.ssh_service.disconnect_ssh_by_public_ip(public_ip)
        else:
            response = "Must provide either 'unique_id' or 'public_ip'."
        return jsonify({'message': response})

    @staticmethod
    @ssh_controller.route('/get-all-ssh', methods=['GET'])
    def get_all_ssh():
        connections = SSHController.ssh_service.get_all_connections()
        return jsonify(connections)

    @staticmethod
    @ssh_controller.route('/disconnect-all-ssh', methods=['GET'])
    def disconnect_all_ssh():
        response = SSHController.ssh_service.disconnect_all_ssh()
        return jsonify({'message': response})

    @staticmethod
    @ssh_controller.route('/is-active-ssh', methods=['POST'])
    def is_active_ssh():
        data = request.get_json()
        unique_id = data.get('unique_id')
        return jsonify({'message': SSHController.ssh_service.is_active_ssh(unique_id)})