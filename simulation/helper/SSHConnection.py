import paramiko


class SSHConnection:

    def __init__(self, unique_id, public_ip, username, key_file):
        self.unique_id = unique_id
        self.public_ip = public_ip
        self.username = username
        self.key_file = key_file
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        self.client.connect(hostname=self.public_ip, username=self.username, key_filename=self.key_file)

    def disconnect(self):
        self.client.close()

    def is_connected(self):
        try:
            self.client.exec_command("ls", timeout=5)
            return True
        except:
            return False