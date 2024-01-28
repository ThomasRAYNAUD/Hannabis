import random
import socket
import os
import signal
import time
import sys
from multiprocessing import Process
import multiprocessing

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

def send(type, serveur_socket,val):
    if type == "N":
        m = type + "|" + "Combien de joueurs dans la partie ? "
        serveur_socket.sendall(m.encode('utf-8'))
    elif type == "P":
        m = "P" +"|"+ "|".join(map(str, val)) # valide : envoie bien ce qu'il faut
        print(m)
        serveur_socket.sendall(m.encode('utf-8'))
    elif type == "E":
        m = "E" +"|"+ val # envoie le numéro de player au Px
        serveur_socket.sendall(m.encode('utf-8'))

def receive(serveur_socket):
    data = serveur_socket.recv(1024)
    return decode(data)

def decode(message):
    message_parts = message.decode('utf-8').split("|")
    return message_parts

def type(tab):
    if tab[0] == "N":
        return tab[1]
    if tab[0] == "P":
        return tab [1]

def nombrePlayer(serveur_socket):
    try:
        send("N", serveur_socket,0)
        tab_data = receive(serveur_socket)
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
            serveur_socket, address = server_socket.accept()
            print("Connecté au client :", address)
            return serveur_socket
    except Exception as e:
        print(f"Erreur lors de la création du socket : {e}")
        sys.exit()

def card_com(pile,serveur_socket):
    try:
        send("P",serveur_socket,pile)
        tab_data = receive(serveur_socket)
        return type(tab_data)
    except Exception as e:
        print(f"Erreur lors de la communication des piles : {e}")
        return None

def carte(pile,player):
    limite=player*5
    debut=pile[:limite]
    fin=pile[limite:]
    return debut,fin

def ecoute(client_socket, address, jeu):
    with client_socket:
        global play
        print("Connected to client:", address)
        with num.get_lock():
            player = str(num.value)
            num.value += 1
        try:
            print("VOILA")
            send("E", client_socket, player)
            # while play:
            print("J'envoie jeu de carte au player :",player)
            time.sleep(0.1)  # import time
            message_recu_P = card_com(jeu, client_socket)
            print(message_recu_P)
            
        except Exception as e:
            print(f"Erreur lors de la communication avec le client : {e}")
            return None


if __name__ == "__main__":
    clear_terminal()
    signal.signal(signal.SIGINT, handler)
    serveur_socket = create_server_socket(20000, 1)
    n_player = nombrePlayer(serveur_socket)
    n_player = int(n_player)
    print("Le nombre de joueurs est le suivant :", n_player)
    pile = creer_jeu_de_cartes(n_player)
    print(pile)
    jeu, pioche = carte(pile, n_player)
    print(jeu)
    print("Voici la pioche :", pioche)
    serveur_socket.close()

    # FIN DU PREMIER SOCKET POUR INITIALISER LA CONNEXION AVEC PLAYER
    #
    # DEBUT SECOND SOCKET POUR COMMUNIQUER AVEC Px
    num = multiprocessing.Value('d', 1)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket_px:
        server_socket_px.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket_px.bind(("localhost", 20001))
        server_socket_px.listen(n_player)
        while True:
            client_socket_px, address_px = server_socket_px.accept()
            p = Process(target=ecoute, args=(client_socket_px, address_px, jeu,))
            p.start()
            
            
            
            
    """while play:
        val=queue.get()
        print(val)
        while val != numPlayer:
            val=queue.get()
            #pass
        #traitement
        if n_player==numPlayer:
            queue.put(1)
            val=1
        else :
            n=val+1
            queue.put(n)
            val+=1"""
