import random
import socket
import os
import signal
import time
import sys

def creer_jeu_de_cartes(nombre_joueurs):
    couleurs = ["r", "b", "v", "j", "n"]
    couleurs_joueurs = random.sample(couleurs, k=nombre_joueurs) # tirer X couleurs aléatoire pour X player

    nombres = [1, 2, 3, 4, 5]  # Donne les numéros de cartes possibles
    cartes = []

    for couleur in couleurs_joueurs:
        for nombre in nombres:
            if nombre == 1:
                nb_exemplaires = 3
            elif 2 <= nombre <= 4:
                nb_exemplaires = 2
            else:
                nb_exemplaires = 1
            for _ in range(nb_exemplaires):
                cartes.append(couleur + str(nombre))

    random.shuffle(cartes)

    return cartes

def handler(sig, frame):
    if sig == signal.SIGINT:
        print("Reçu SIGINT. Sortie...")
        sys.exit()

def clear_terminal():
     os.system('clear')

def send(type, client_socket,val):
    if type == "N":
        m = type + "|" + "Combien de joueurs dans la partie ? "
        client_socket.sendall(m.encode('utf-8'))
        print("etes")
    elif type == "P":
        m = "P" +"|"+ "|".join(map(str, val)) # valide : envoie bien ce qu'il faut
        client_socket.sendall(m.encode('utf-8'))

def receive(client_socket):
    data = client_socket.recv(1024)
    return decode(data)

def decode(message):
    message_parts = message.decode('utf-8').split("|")
    return message_parts

def type(tab):
    if tab[0] == "N":
        return tab[1]
    if tab[0] == "P":
        return tab [1]

def nombrePlayer(client_socket):
    try:
        send("N", client_socket,0)
        tab_data = receive(client_socket)
        return type(tab_data)
    except Exception as e:
        print(f"Erreur lors de la communication avec le client : {e}")
        return None

def create_server_socket(port,lis):
    HOST = "localhost"
    PORT=port
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen(lis)
            print("En attente de connexion...")
            client_socket, address = server_socket.accept()
            print("Connecté au client :", address)
            return client_socket
    except Exception as e:
        print(f"Erreur lors de la création du socket : {e}")
        sys.exit()

def card_com(pile,client_socket):
    try:
        send("P",client_socket,pile)
        tab_data = receive(client_socket)
        return type(tab_data)
    except Exception as e:
        print(f"Erreur lors de la communication des piles : {e}")
        return None


if __name__ == "__main__":
    clear_terminal()
    signal.signal(signal.SIGINT, handler)
    client_socket = create_server_socket(26000,1)
    n_player = nombrePlayer(client_socket)
    nbr_player=int(n_player)
    print("Le nombre de joueurs est le suivant :", n_player)
    pile=creer_jeu_de_cartes(nbr_player)
    ret_P=card_com(pile,client_socket)
    print(ret_P)
    client_socket.close()