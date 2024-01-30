import multiprocessing
import os
import signal
import sys, socket, random, time

def clear_terminal():
    """Clears the terminal screen."""
    os.system('clear')

def handler(sig, frame):
    """Handler for SIGINT signal."""
    if sig == signal.SIGINT:
        print("Reçu SIGINT. Sortie...")
        sys.exit()

def create_server_socket(port,lis):
    """Creates a server socket and returns it."""
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

def nombrePlayer(serveur_socket):
    """Receives the number of players from the client."""
    try:
        send("N", serveur_socket,0) # Envoie un message au client pour lui demander le nombre de joueurs
        nbr_player = receive(serveur_socket) # Reçoit le nombre de joueurs
        return type(nbr_player) # Retourne le nombre de joueurs sous forme de Int
    except Exception as e:
        print(f"Erreur lors de la communication avec le client : {e}")
        return None

def type(tab):
    """Returns the type of the message received from the client."""
    if tab[0] == "N":
        return int(tab[1])
    if tab[0] == "P":
        return tab [1]

def send(type, serveur_socket,val):
    """Sends a message to the client."""
    if type == "N":
        m = type + "|" + "Combien de joueurs dans la partie ? "
        serveur_socket.sendall(m.encode('utf-8'))
    elif type == "P":
        m = "P" +"|"+ "|".join(map(str, val)) 
        serveur_socket.sendall(m.encode('utf-8'))
    elif type == "M":
        m = "M" +"|"+ "|".join(map(str, val)) 
        serveur_socket.sendall(m.encode('utf-8'))

def receive(serveur_socket):
    """Receives a message from the client."""
    data = serveur_socket.recv(1024)
    return decode(data)

def decode(message):
    """Decodes the message received from the client."""
    message_parts = message.decode('utf-8').split("|")
    return message_parts

def creer_jeu_de_cartes(nombre_joueurs):
    """Crée un jeu de cartes et le mélange."""
    # initialisation des couleurs
    couleurs = ["r", "b", "v", "j", "n"]
    # tirage aléatoire des couleurs
    couleurs_joueurs = random.sample(couleurs, k=nombre_joueurs) # tirer X couleurs aléatoire pour X player
    # initialisation des nombres
    nombres = [1, 2, 3, 4, 5]   
    cartes = []

    # création des cartes en fonction des couleurs et des nombres (nbr d'exemplaires précisés dans la règle)
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
    # mélange des cartes
    random.shuffle(cartes)
    #retourne le jeu de cartes mélangé [...,...,...]
    return cartes

def carte(pile,nbr_player):
    """Distribue les cartes aux joueurs."""
    limite=nbr_player*5
    debut=pile[:limite]
    fin=pile[limite:]
    return debut,fin # debut = jeu de cartes distribué aux joueurs, fin = pioche

def card_com(pile,serveur_socket):
    """Envoie les cartes aux joueurs."""
    try:
        send("P",serveur_socket,pile)
        
        
    except Exception as e:
        print(f"Erreur lors de la communication des piles : {e}")
        return None

def main(shared_array):
    """Main function."""
    
    clear_terminal()
    signal.signal(signal.SIGINT, handler)
    
    server_socket=create_server_socket(5000,1)
    nbr_player = nombrePlayer(server_socket) # n_player est le nombre de joueurs : Int
    shared_array[0]=3 
    shared_array[1]=3+nbr_player
    shared_array[2]=0
    shared_array[3]=0
    shared_array[4]=0
    shared_array[5]=0
    shared_array[6]=0
    # Création du jeu de cartes
    pile = creer_jeu_de_cartes(nbr_player) # pile est le jeu de cartes mélangé : List
    jeu, pioche = carte(pile, nbr_player) # jeu est le jeu de cartes distribué aux joueurs : List, pioche est la pioche : List
    
    card_com(jeu, server_socket)
    playing = True
    while playing:
        data = server_socket.recv(1024)
        message_parts = data.decode('utf-8').split("|")
        if message_parts[0] == "M" and len(pioche) > 0:
            jeu[int(message_parts[2])] = pioche[0]
            pioche.pop(0)
            send("M", server_socket, jeu)
        else :
            send("M", server_socket, "Null")
        # Ajoutez une condition pour sortir de la boucle
        if shared_array[0] <= 0:
            playing = False
