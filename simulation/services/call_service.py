from services.command_service import CommandService
from utils.constants import Command


class CallService:

    def __init__(self):
        self.command_service = CommandService()

    def start_call(self, tmux_name, wav_file_location, codec, ip_addr, receiver_ip_addr):
        command = [Command.PJSUA_CALLER.format(wav_file_location=wav_file_location, codec=codec, ip_addr=ip_addr),
                   Command.PJSUA_CALL.format(receiver_ip_addr)]
        return self.command_service.execute(ip_addr, None, tmux_name, command, None)

    def receive_call(self, tmux_name, record_file_location, ip_addr):
        command = [Command.PJSUA_RECEIVER.format(record_location=record_file_location, ip_addr=ip_addr)]
        return self.command_service.execute(ip_addr, None, tmux_name, command, None)