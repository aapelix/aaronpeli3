import socket
import pickle
import threading
import os



class GameServer:
    def __init__(self, host='0.0.0.0'):
        port = int(os.getenv('PORT', default=5000))

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()

        self.players = {}  # {client_id: {'position': (x,y), 'animation': state}}
        self.player_count = 0

        print(f"Server started on {host}:{port}")

    def handle_client(self, conn, client_id):
        print(f"Starting to handle client {client_id}")
        while True:
            try:
                data = pickle.loads(conn.recv(2048))
                if not data:
                    break

                # Update this player's state
                self.players[client_id] = data

                # Send everyone's state back to this client
                conn.send(pickle.dumps(self.players))
            except Exception as e:
                print(f"Error handling client {client_id}: {e}")
                break

        print(f"Lost connection to client {client_id}")
        if client_id in self.players:
            del self.players[client_id]
        conn.close()

    def run(self):
        print("Server is running and waiting for connections...")
        while True:
            try:
                conn, addr = self.server.accept()
                self.player_count += 1
                client_id = self.player_count

                self.players[client_id] = {
                    'position': (400, 300),
                    'animation': 'idle'
                }

                print(f"New connection from {addr}, assigned ID: {client_id}")

                # Send the client their ID
                conn.send(pickle.dumps({"client_id": client_id}))

                thread = threading.Thread(target=self.handle_client, args=(conn, client_id))
                thread.daemon = True
                thread.start()

            except Exception as e:
                print(f"Error accepting connection: {e}")
                continue


if __name__ == "__main__":
    try:
        server = GameServer()
        server.run()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    except Exception as e:
        print(f"Server error: {e}")
