# Echo server
import socket
from multiprocessing import Process
import signal
import sys

def handler(sig, frame):
    if sig == signal.SIGINT:
        sys.exit()


def traitement_client(client_socket,address) :
    with client_socket:
        print("Connected to client: ", address)
        data = client_socket.recv(1024)
        print("Message reçu : ",data.decode())
        while len(data):
            client_socket.sendall(data)
            data = client_socket.recv(1024)        
            print(data)
        print("Disconnecting from client: ", address)

HOST = "localhost"
PORT = 6666
nbr_client=5
signal.signal(signal.SIGINT, handler)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(nbr_client)
    while True:
        client_socket, address = server_socket.accept()
        p = Process(target=traitement_client, args=(client_socket,address,))
        p.start()


#recoit connection entrante puis créé processus -> appel de fonction pour le traitement ...
# sudo systemctl restart NetworkManager