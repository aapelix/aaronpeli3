import socket
import pickle
import threading
import time

class GameServer:
    def __init__(self, host='localhost', port=5000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()

        self.players = {}  # {client_id: {'position': (x,y), 'animation': state}}
        self.player_count = 0

        print(f"Server started on {host}:{port}")

    def handle_client(self, conn, client_id):
        while True:
            try:
                data = pickle.loads(conn.recv(2048))
                if not data:
                    break

                # Update this player's state
                self.players[client_id] = data

                # Send everyone's state back to this client
                conn.send(pickle.dumps(self.players))
            except:
                break

        print(f"Lost connection to client {client_id}")
        del self.players[client_id]
        conn.close()

    def run(self):
        while True:
            conn, addr = self.server.accept()
            self.player_count += 1
            client_id = self.player_count

            self.players[client_id] = {
                'position': (400, 300),
                'animation': 'idle'
            }

            thread = threading.Thread(target=self.handle_client, args=(conn, client_id))
            thread.daemon = True
            thread.start()

            print(f"New connection from {addr}, assigned ID: {client_id}")