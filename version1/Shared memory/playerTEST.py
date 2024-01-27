import socket
from multiprocessing import shared_memory
import numpy as np
import time
import signal
import sys

def signal_handler(signal, frame):
    print("Interruption manuelle détectée. Libération des ressources...")
    existing_shm.close()
    sys.exit(0)

import multiprocessing.resource_tracker as resource_tracker

def remove_shm_from_resource_tracker():

    def fix_register(name, rtype):
        if rtype == "shared_memory":
            return
        return resource_tracker._resource_tracker.register(name, rtype)

    resource_tracker.register = fix_register

    def fix_unregister(name, rtype):
        if rtype == "shared_memory":
            return
        return resource_tracker._resource_tracker.unregister(name, rtype)

    resource_tracker.unregister = fix_unregister

    if "shared_memory" in resource_tracker._CLEANUP_FUNCS:
        del resource_tracker._CLEANUP_FUNCS["shared_memory"]

# Appel de la fonction pour appliquer le monkey-patch
remove_shm_from_resource_tracker()


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 6669

    # Configurer le gestionnaire de signal pour capturer SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        data = str(client_socket.recv(10240).decode())
        print("Nom de la shared memory reçu : ", data) 
        remove_shm_from_resource_tracker()

        existing_shm = shared_memory.SharedMemory(name=data)
        
        shared_array = np.ndarray((6,), dtype=np.int64, buffer=existing_shm.buf)
        print(shared_array)
        shared_array[2] = 666
        m = "18"
        client_socket.sendall(m.encode())
        
        # La libération des ressources se fait maintenant dans le gestionnaire de signal
        time.sleep(10)  # import time

        client_socket.close()
