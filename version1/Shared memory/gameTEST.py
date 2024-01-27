import socket
from multiprocessing import shared_memory
import numpy as np

if __name__ == "__main__":
    
    HOST = "localhost"
    PORT = 6669
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        
        server_socket.listen(3)
        
        client_socket, address = server_socket.accept()
    
        a = np.array([1, 1, 2, 3, 5, 8])  
    
    
        shm = shared_memory.SharedMemory(name='MyMemory', create=True, size=a.nbytes)

        shared_array = np.ndarray(a.shape, dtype=a.dtype, buffer=shm.buf)
        
        shared_array[:] = a[:]

        mess = shm.name  

        print(mess)
        print("Tableau partagé (BEG) : ", shared_array)

        
        client_socket.sendall(mess.encode())
        conf = client_socket.recv(1024).decode()

        print("Tableau partagé (END) : ", shared_array)
        
        shm.close()
        shm.unlink()
