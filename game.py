import random
import socket
import os
import signal
from multiprocessing import Process
import multiprocessing as mp
import sys


Carte = (str, int)

class Pile:
    def __init__(self, couleur): 
        self.couleur = couleur
        self.valeur = 0


class Joueur:
    def __init__(Joueur, nom, cartes):  
        Joueur.nom = nom
        Joueur.cartes = cartes
class Jetons:
    def __init__(self, nombre_de_joueurs):
        self.infos = 3 + nombre_de_joueurs
        self.fuse = 3

def creer_jeu_de_cartes():
    couleurs = ["r", "b", "v", "j", "n"]
    nombres = [1, 2, 3, 4, 5]
    cartes = []

    for couleur in couleurs:
        for nombre in nombres:
            if nombre == 1:
                nb_exemplaires = 3
            elif 2 <= nombre <= 4:
                nb_exemplaires = 2
            else:
                nb_exemplaires = 1
            for _ in range(nb_exemplaires):
                cartes.append((couleur, nombre))

    return cartes


def tirer_mains_des_joueurs(nombre_de_joueurs, jeu_de_cartes):
    return {
        f"Joueur {i+1}": Joueur(f"Joueur {i+1}", random.sample(jeu_de_cartes, 5))
        for i in range(nombre_de_joueurs)
    }

cartes = creer_jeu_de_cartes()
print(cartes)

nombre_de_joueurs = 2
jetons = Jetons(nombre_de_joueurs)

couleurs = ["R", "B", "V", "J", "N"]
piles_couleurs = {couleur: Pile(couleur) for couleur in couleurs[:nombre_de_joueurs]}

joueurs = tirer_mains_des_joueurs(nombre_de_joueurs, cartes)

for joueur, info in joueurs.items():
    print(f"{info.nom} :")
    for carte in info.cartes:
        print(f"Carte : {carte[0]} - Numéro : {carte[1]}")

print("Piles Couleurs :")
for pile in piles_couleurs.values():
    print(f"{pile.couleur}, {pile.valeur}")


print("Jetons disponibles :")
print("Jetons Fuse :", jetons.fuse, "\nJetons Infos :", jetons.infos)

HOST = "localhost"
PORT = 25425

def handler(sig, frame):

    if sig == signal.SIGINT:
        print("Received SIGINT. Exiting...")
        sys.exit()

def connection(client_socket, address, joueurs):
    with client_socket:
        print(f"Connected to client: {address}")

        for joueur, info in joueurs.items():
            data = f"Joueur {info.nom} : {info.cartes}\n"
            client_socket.send(data.encode('utf-8'))
            print(data)
        client_socket.send(b"FIN")

        print(f"Disconnecting from client: {address}")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    
    # Configuration du socket du serveur
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ADDR = (HOST, PORT)
        server_socket.bind(ADDR)
        server_socket.listen(1)
        print(f"Server is listening on {HOST}:{PORT}")

        while True:
            print("Waiting for a connection...")
            client_socket, address = server_socket.accept()
            p = Process(target=connection, args=(client_socket, address, joueurs))
            p.start()


"""""
METTRE LES JETONS DANS UNE SHARED MEMORY ET AJOUTER UN LOCK
nombre de joueur = nombre de couleur
3 jetons infos + 3 jetons fusions
donner une info  = jetons_informations -1
carte joué si la couleur existe pas ou le numéro (si carte joué est 5 = +1 jetons_informations)
si pas de carte joué -> pioche une carte
sinon jeton_fusions-1
fin du jeu si : plus de jetons fusion ou tous les piles ont été faites 

construire la pile de 1 à 5. première équipe qui finit sa pile de couleur a gagné

faire 2 processes : 

un process jeu  : il contient la pioche, gestion des cartes, suivi des piles 
un process player : connecté avec les autres joueurs et le process jeu. Il communique aux autres processes ses cartes et ses jetons.
Interaction avec le process jeu sur un tread différent que les autres.

definir les types

MESSAGE QUEUE ENTRE LES PROCESS ENFANTS ET SOCKET ENTRE PLAYER PROCESS ET GAME PROCESS
le socket envoie au player qui lui va redistribuer aux joueurs la trame envoyée
socketclient.py
"""