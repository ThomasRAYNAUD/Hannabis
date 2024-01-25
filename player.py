import socket
import os

HOST = "localhost"
PORT = 25425
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))

    while True:
        data = client_socket.recv(2048)
        message = data.decode('utf-8')

        if not data:
            print("Connection closed by the server.")
            break

        print("Received echo:", message)
