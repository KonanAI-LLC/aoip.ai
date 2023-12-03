from helper.SSHConnection import SSHConnection
from helper.Singleton import Singleton
import random
import time

class SSHService(Singleton):

    def __init__(self):
        self.connections = {}

    def connect_ssh(self, public_ip, username, unique_id, key_file):
        max_retries = 10
        delay = 10  # Initial delay in seconds

        for attempt in range(1, max_retries + 1):
            try:
                if unique_id in self.connections:
                    return False, "SSH connection already exists."

                conn = SSHConnection(unique_id, public_ip, username, key_file)
                conn.connect()

                self.connections[unique_id] = {
                    "public_ip": public_ip,
                    "username": username,
                    "unique_id": unique_id,
                    "key_file": key_file,
                    "ssh_connection": conn
                }
                # print(f"SSH connection {unique_id} created successfully on attempt {attempt}.")
                return True, f"SSH connection {unique_id} created successfully."

            except Exception as e:
                # print(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    sleep_time = ((2 ** attempt) - 1) * delay + (random.randint(0, 1000) / 1000.0)
                    # print(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    # print("SSH connection failed after maximum number of retries.")
                    raise Exception("SSH could not work after 10 retries")


    def disconnect_ssh_by_unique_id(self, unique_id):
        if unique_id in self.connections:
            self.connections[unique_id]["ssh_connection"].disconnect()
            del self.connections[unique_id]
            return True, f"SSH connection with id {unique_id} removed successfully."
        else:
            return False, f"SSH connection with id {unique_id} does not exist."

    def disconnect_ssh_by_public_ip(self, public_ip):
        for unique_id, connection_info in list(self.connections.items()):
            if connection_info["public_ip"] == public_ip:
                connection_info["ssh_connection"].disconnect()
                del self.connections[unique_id]
                return True, f"SSH connection with id {unique_id} removed successfully."
        return False, f"No SSH connection for public IP {public_ip} found."

    def get_connection_by_unique_id(self, unique_id):
        return self.connections.get(unique_id, None)

    def get_connection_by_public_ip(self, public_ip):
        for connection_info in self.connections.values():
            if connection_info["public_ip"] == public_ip:
                return connection_info
        return None

    def get_all_connections(self):
        return {unique_id: {
            "public_ip": conn_info["public_ip"],
            "username": conn_info["username"],
            "key_file": conn_info["key_file"],
            "status": "connected" if conn_info["ssh_connection"].is_connected() else "disconnected"
            }
            for unique_id, conn_info in self.connections.items()}

    def disconnect_all_ssh(self):
        for conn_info in self.connections.values():
            conn_info["ssh_connection"].disconnect()
        self.connections = {}
        return "All SSH connections removed successfully."

    def is_active_ssh(self, unique_id):
        conn = self.get_connection_by_unique_id(unique_id)
        if not conn:
            return False
        return conn["ssh_connection"].is_connected()