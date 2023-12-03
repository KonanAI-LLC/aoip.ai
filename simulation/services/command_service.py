from services.ssh_service import SSHService
from utils.constants import CommandGroups

import time
class CommandService:

    def __init__(self):
        self.ssh_service = SSHService()

    def execute(self, public_ip, unique_id, tmux_name, command_group, command, non_blocking=False):

        if unique_id:
            client = self.ssh_service.get_connection_by_unique_id(unique_id)
        elif public_ip:
            client = self.ssh_service.get_connection_by_public_ip(public_ip)
        else:
            return "One of unique_id or public_ip is required"

        commands = []

        if command_group and isinstance(command_group, list) and len(command_group) > 0:
            commands = command_group
        elif command_group and hasattr(CommandGroups, command_group):
            commands = CommandGroups.__dict__.get(command_group)
        elif command:
            if isinstance(command, list):
                commands = command
            elif isinstance(command, str):
                commands = [command]
        else:
            return "No command to execute."

        # if tmux_name:
        #     commands.insert(0, Command.TMUX_ATTACH.format(name=tmux_name))
        #     commands.append(Command.TMUX_DETACH.format(name=tmux_name))

        if non_blocking:
            return self.execute_commands_non_blocking(client, commands)
        return self.execute_commands(client, commands)

    def execute_commands(self, client, command_group):
        stdin, stdout, stderr = [], [], []
        for command in command_group:
            try:
                time.sleep(2)
                # print(f"executing {command}")
                start_time = time.time()

                stdin_, stdout_, stderr_ = client.get('ssh_connection').client.exec_command(command)
                stdout.append([command, stdout_.read().decode()])
                stderr.append([command, stderr_.read().decode()])
                end_time = time.time()
                elapsed_time = end_time - start_time
                # print(f"executed in {elapsed_time:.2f} seconds.")

            except Exception as e:
                print("Exception while executing command {} ", command)

        return stdin, stdout, stderr

    def execute_commands_non_blocking(self, client, command_group):
        for command in command_group:
            try:
                print(f"executing non-blocking {command}")
                client.get('ssh_connection').client.exec_command(command)
            except Exception as e:
                print("Exception while executing command {} : {}", command, e)

        return "executed non-blocking command"

    def scp(self, public_ip, unique_id, remote_path, local_path, reverse=False):
        if unique_id:
            client = self.ssh_service.get_connection_by_unique_id(unique_id)
        elif public_ip:
            client = self.ssh_service.get_connection_by_public_ip(public_ip)
        else:
            return "One of unique_id or public_ip is required"

        scp = client.get('ssh_connection').client.open_sftp()
        try:
            if reverse:
                scp.put(remote_path, local_path)
            else:
                scp.get(local_path, remote_path)
            scp.close()
        except Exception as e:
            return f"Exception while performing scp from {remote_path} to {local_path}: {e}"

        return f"performed scp from {remote_path} to {local_path}"