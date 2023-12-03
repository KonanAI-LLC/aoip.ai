from flask import Blueprint, request

from services.call_service import CallService


class CallController:
    call_controller = Blueprint('call', __name__)
    call_service = CallService()

    @staticmethod
    @call_controller.route('/start-call', methods=['POST'])
    def create_instance():
        if request.method == 'POST':
            data = request.get_json()
            tmux_name = data.get('tmux_name')
            wav_file_location = data.get('wav_file_location')
            codec = data.get('codec')
            ip_addr = data.get('ip_addr')
            receiver_ip_addr = data.get('receiver_ip_addr')
            CallController.call_service.start_call(tmux_name, wav_file_location, codec, ip_addr, receiver_ip_addr)
            return {'message': 'Call initiated successfully'}, 201

    @staticmethod
    @call_controller.route('/receive-call', methods=['POST'])
    def get_instance():
        if request.method == 'POST':
            data = request.get_json()
            tmux_name = data.get('tmux_name')
            record_file_location = data.get('record_file_location')
            ip_addr = data.get('ip_addr')
            CallController.call_service.receive_call(tmux_name, record_file_location, ip_addr)
            return {'message': 'Retrieved'}, 201