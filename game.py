import random
import socket
import os
import signal
from multiprocessing import Process
import multiprocessing as mp
import sys
# Définition du type Carte
Carte = (str, int)

# Définition du type PileCouleur
class Pile:
    def __init__(self, couleur):
        self.couleur = couleur
        self.valeur = 0

# Définition du type Joueur
class Joueur:
    def __init__(Joueur, nom, cartes):
        Joueur.nom = nom
        Joueur.cartes = cartes
        

# Définition du type Jetons
class Jetons:
    def __init__(self, nombre_de_joueurs):
        self.infos = 3 + nombre_de_joueurs
        self.fuse = 3

# Fonction pour créer un jeu de cartes avec un nombre spécifié de couleurs
def creer_jeu_de_cartes(n):
    couleurs = ["Rouge", "Bleu", "Vert", "Jaune", "Noir"][:n]
    nombres = [1, 2, 3, 4, 5]
    return [(couleur, nombre) for couleur in couleurs for nombre in nombres]

# Fonction pour tirer aléatoirement 5 cartes pour chaque joueur
def tirer_mains_des_joueurs(nombre_de_joueurs):
    jeu_de_cartes = creer_jeu_de_cartes(nombre_de_joueurs)
    return {
        f"Joueur {i+1}": Joueur(f"Joueur {i+1}", random.sample(jeu_de_cartes, 5))
        for i in range(nombre_de_joueurs)
    }

# Nombre de joueurs
nombre_de_joueurs = 3
jetons = Jetons(nombre_de_joueurs)

# Création des piles de couleurs
couleurs = ["Rouge", "Bleu", "Vert", "Jaune", "Noir"]
piles_couleurs = {couleur: Pile(couleur) for couleur in couleurs[:nombre_de_joueurs]}

# Tirer les mains des joueurs
joueurs = tirer_mains_des_joueurs(nombre_de_joueurs)

# Affichage des mains des joueurs et incrémentation des piles de couleurs
for joueur, info in joueurs.items():
    print(f"{info.nom} :")
    for carte in info.cartes:
        print(f"Carte : {carte[0]} - Numéro : {carte[1]}")

print("Piles Couleurs :")
for pile in piles_couleurs.values():
    print(f"  Couleur : {pile.couleur} - État : {pile.valeur}")

print("Jetons disponibles :")
print("Jetons Fuse :", jetons.fuse, "\nJetons Infos :", jetons.infos)

HOST = "localhost"
PORT = 25425

def handler(sig, frame):
    # Gestionnaire pour SIGINT (Ctrl+C)
    if sig == signal.SIGINT:
        print("Received SIGINT. Exiting...")
        sys.exit()

def connection(client_socket, address):
    # Fonction pour gérer la connexion avec un client
    with client_socket:
        print("Connected to client:", address)
        try:
            while True:
                    for carte in info.cartes:
                        data = f"Carte : {carte[0]} - Numéro : {carte[1]}"
                        client_socket.send(data.encode('utf-8'))
                    if not data:
                        break
                    client_socket.sendall(data)
        except (socket.error, BrokenPipeError):
            pass  # Gestion des erreurs de connexion

        print("Disconnecting from client:", address)

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
            # Attente d'une nouvelle connexion
            print("Waiting for a connection...")
            client_socket, address = server_socket.accept()

            # Création d'un processus pour gérer la connexion avec le client
            p = Process(target=connection, args=(client_socket, address))
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