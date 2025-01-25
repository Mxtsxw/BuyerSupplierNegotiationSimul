# communication/server.py
import socket
import json

class SocketServer:
    def __init__(self, host, port, handler):
        self.host = host
        self.port = port
        self.handler = handler

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            print(f"Server running on {self.host}:{self.port}")
            while True:
                client_socket, _ = server_socket.accept()
                with client_socket:
                    data = client_socket.recv(1024)
                    request = json.loads(data.decode('utf-8'))
                    response = self.handler(request)
                    client_socket.sendall(json.dumps(response).encode('utf-8'))
