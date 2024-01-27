import socket
from multiprocessing import shared_memory
import numpy as np
import time

if __name__ == "__main__":
    HOST = "localhost"
    PORT = 6669
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # init serveur
        client_socket.connect((HOST, PORT))
        data = str(client_socket.recv(10240).decode())
        # il a reçu le nom de la shared memory (si pas de nom def il reçoit @ memoire ?)
        print("Nom du la shared memory reçu : ",data) 
        existing_shm = shared_memory.SharedMemory(name=data)
        shared_array = np.ndarray((6,), dtype=np.int64, buffer=existing_shm.buf)
        print(shared_array)
        shared_array[2] = 666
        m = "18"
        client_socket.sendall(m.encode())
        
        del shared_array
        existing_shm.close()
        existing_shm.unlink()

        time.sleep(10)  # import time

        client_socket.close()