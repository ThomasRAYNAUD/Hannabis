import socket
from multiprocessing import shared_memory
import numpy as np

if __name__ == "__main__":
    
    # Paramètres du serveur
    HOST = "localhost"
    PORT = 6669
    
    # Création du socket serveur
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(3)
    client_socket, address = server_socket.accept()
    
    # Crée un tableau numpy initial avec des données
    a = np.array([1, 1, 2, 3, 5, 8])  
    
    # Crée un objet SharedMemory nommé 'MyMemory' pour partager le tableau 'a'
    # 'create=True' indique de créer la mémoire partagée si elle n'existe pas déjà
    # 'size=a.nbytes' spécifie la taille de la mémoire partagée en octets
    shm = shared_memory.SharedMemory(name='MyMemory', create=True, size=a.nbytes)

    # Crée un tableau 'shared_array' qui utilise la mémoire partagée pour stocker les données de 'a'
    shared_array = np.ndarray(a.shape, dtype=a.dtype, buffer=shm.buf)
    
    """
    > a.shape: Récupère la forme (dimensions) du tableau initial a -> la forme du tableau est la même que initial
    > a.dtype: Récupère le type de données du tableau initial a -> aussi int si int dans a
    > shm.buf: Donne accès au tampon mémoire partagée de l'objet SharedMemory -> buffer def sur SharedMemory
    """


    # Copie les données de 'a' dans 'shared_array'
    shared_array[:] = a[:]

    # Récupère le nom de la mémoire partagée (normalement, c'est le nom généré automatiquement)
    mess = shm.name  

    # Affiche le nom de la mémoire partagée et l'état initial du tableau partagé
    print(mess)
    print("Tableau partagé (BEG) : ", shared_array)

    
    # Envoi du nom de la mémoire partagée au client
    client_socket.sendall(mess.encode())
    conf = client_socket.recv(1024).decode()

    print("Tableau partagé (END) : ", shared_array)
    
    # Libération de la mémoire partagée
    # Libération de la mémoire partagée
    del shared_array # pas fermer shm -> sinon leak de data
    shm.close()
    shm.unlink()


    
    # Fermeture du socket serveur
    server_socket.close()
