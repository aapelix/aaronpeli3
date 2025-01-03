import socket
import pickle

class Network:
    def __init__(self, host='localhost', port=3000):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.client_id = None

    def connect(self):
        try:
            self.client.connect(self.addr)
            # Receive initial data including client ID
            initial_data = pickle.loads(self.client.recv(2048))
            self.client_id = initial_data["client_id"]
            print(f"Connected to server with ID: {self.client_id}")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(f"Network error: {e}")
            return None

    def close(self):
        self.client.close()