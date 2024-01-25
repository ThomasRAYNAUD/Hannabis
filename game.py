import random
import socket
import os
import signal
from multiprocessing import Process
import multiprocessing as mp
import sys
import select

# variables gloables : 


#
# Défintions des classes
#

"""carte = un tuple"""
Carte = (str, int)

"""pile de cartes d'une couleur spécifique"""
class Pile:
    def __init__(self, couleur): 
        self.couleur = couleur
        self.valeur = 0

"""joueur avec un nom et une liste de cartes"""
class Joueur:
    def __init__(self, nom, cartes):  
        Joueur.nom = nom
        Joueur.cartes = cartes


class Jetons:
    def __init__(self, nombre_de_joueurs):
        self.infos = 3 + nombre_de_joueurs
        self.fuse = 3

#
# Défintions des fonctions
# 

"""Un jeu de cartes est créé avec la fonction creer_jeu_de_cartes() --> appeler au début du jeu"""
def creer_jeu_de_cartes(nombre_joueurs):
    couleurs = ["r", "b", "v", "j", "n"]
    couleurs_joueurs = random.sample(couleurs, k=nombre_joueurs) # prend aléatoirement X couleurs, où X est le nbr de joueurs

    nombres = [1, 2, 3, 4, 5]
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
                cartes.append((couleur, nombre))

    # Mélanger aléatoirement les cartes
    random.shuffle(cartes)

    return cartes


def handler(sig, frame):

    if sig == signal.SIGINT:
        print("Received SIGINT. Exiting...")
        sys.exit()

def send(type):
    # selon le type, un choix différent est fait = message envoyé différent
    if type == "N":  # demande le nombre de joueurs dans la partie
        m = type + "|" + "Combien de joueurs dans la partie ? "
        client_socket.sendall(m.encode('utf-8'))

def decode(message):
    # décode la trame pour en sortir tous les éléments et le mettre dans un tableau
    message_parts = message.decode('utf-8').split("|")
    return message_parts

def type(tab):
    # regarde le premier élément du tableau (= type) et en fonction prend une décision
    if tab[0] == "N":
        return tab[1]  # retourne le nombre de joueurs

def receive():
    data = client_socket.recv(1024)
    return decode(data)

def nombrePlayer():
    try:
        send("N")
        tab_data = receive()
        return type(tab_data)
    except Exception as e:
        print(f"Erreur lors de la communication avec le client : {e}")
        return None

####### MAIN

if __name__ == "__main__":
    # appelle la fonction handle si SIGINT est reçu
    signal.signal(signal.SIGINT, handler)
    
    # Créer Socket
    HOST = "localhost"
    PORT = 25425
    # Configuration du socket du serveur, un seul process car une seule connection à maintenir dans le socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # régler problème d'adresse déjà utilisée
        server_socket.bind((HOST,PORT))
        server_socket.listen(1) # communique avec un seul process Player (orchestrateur)
        client_socket, address = server_socket.accept()
        with client_socket:
            print("Connected to client: ", address)
            print("Je demande le nombre de joueurs.")
            n_player=nombrePlayer()
            print("Le nombre de joueur est le suivant :",n_player)
            print(creer_jeu_de_cartes(int(n_player)))
            

    # Poser la question au process Player ("nbr de joueur ?")
    # met dans une varible globale