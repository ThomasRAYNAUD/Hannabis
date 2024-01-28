import socket
import os
import sys
from multiprocessing import Process, Value, Queue
from multiprocessing import shared_memory
import time
import numpy as np
import multiprocessing.resource_tracker as resource_tracker
import signal
from multiprocessing import Lock
import signal
from multiprocessing import Process, shared_memory
import threading
import queue
import multiprocessing


shared_memory_lock = threading.Lock() # pour accéder à la shared memory mettre un lock

def receive(client_socket):
    data = client_socket.recv(1024)
    return decode(data)

def decode(message):
    message_parts = message.decode('utf-8').split("|")
    return message_parts

def type(tab):
    if tab[0] == "N":
        return tab[1]

def player(tab_data):
    verif = True
    while verif:
        try:
            val = int(input(tab_data[1]))
            print(val)
            if 2 <= val <= 5:
                verif = False
                return val
            else:
                print("Veuillez entrer un entier entre 2 et 5.")
        except ValueError:
            print("Veuillez entrer un entier entre 2 et 5.")

def send(type, mess, client_socket):
    if type == "N":
        chaine = str(mess)
        m = type + "|" + chaine
        print(m)
        client_socket.sendall(m.encode('utf-8'))
    if type == "P":
        m = type + "|" + mess
        client_socket.sendall(m.encode('utf-8'))

def clear_terminal():
    os.system('clear')

def create_socket(host, port):
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

def game(host, port, play_shared,newstdin,queue):
    
    """
    variables : 
    - client_socket : socket du client                          | pas SM
    - numPlayer : le numéro de joueur                           | pas SM
    - n_player : le nombre de joueurs dans la partie ~ à verif  | pas SM
    - tab_data : les cartes des joueurs dans la liste           | en Shared Memory
    - queue
    
    
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    try:
        numPlayer = receive(client_socket)
        print(numPlayer)
        print("Je suis prêt à recevoir les cartes !")
        tab_data = receive(client_socket)
        send("P", "Bien reçu paquet de cartes", client_socket)
        tab_data = tab_data[1:]
        print(tab_data)
        numPlayer = int(float(numPlayer[1]))
        n_player = len(tab_data) / 5
        n_player=int(float(n_player))
        time.sleep(0.1)
        # queue partagée entre les threads
        thread=threading.Thread(target=jeu,args=(numPlayer,n_player,play_shared,newstdin,tab_data,queue))
        thread.start()
        thread.join()
    except KeyboardInterrupt:
        print("Interruption du processus.")
    finally: 
        client_socket.close()
def jeu(numPlayer, n_player, play_shared, newstdin, tab_data, queue):
    val = 1
    indice = ""
    tour = 1
    while True:
        while val != numPlayer:
            # Si l'élément 1 de queue.get() est égal à mon numéro de thread
            t = queue.get()  # Mettre dans une variable ce que l'on reçoit pour un traitement ultérieur
            if isinstance(t, int):  # Vérifier si t est un entier
                val = t
                continue
            else:
                elements = t.split("|")
                if int(elements[0]) != numPlayer:
                    continue
                else:
                    indice += "     -     " + elements[1] 
                    continue
   
            # Recevoir le paquet de cartes par la queue aussi
        #
        print("A mon tour de jouer, je suis", numPlayer, ". Au total il y a joueurs :", n_player)
        ask(tab_data, newstdin, n_player, numPlayer, indice)
        #
        if n_player == numPlayer:
            for i in range(n_player):
                queue.put(1)
            val = 1
            # fonctionne pas -> play_shared.value = False > change que en local au process et pas dans tout le programme
        else:
            n = val + 1
            time.sleep(2)
            val += 1
            for i in range(n_player):
                queue.put(val)
            print("N vaut :", val)
    # montre les cartes sauf les siennes
    # demande ce que veut faire
            # poupées russes
            # envoie le résultat de ce qu'il veut faire par la queue
    
def ask(tab_data, newstdin, n_player, numPlayer, indice):
    sys.stdin = newstdin
    clear_terminal()
    print("Mes indices :")
    print(indice)
    print("Voici les cartes de tes collègues !")
    show_card(tab_data, numPlayer)
    message = f"Joueur {numPlayer} : Voulez-vous donner une information [1] ou jouer une carte [2] ?"
    print(message)
    user_input = input()
    while not check_input(user_input):
        user_input = input("Entrez un nombre (1 ou 2) : ")
    if user_input == "1":
        information(n_player, numPlayer, tab_data)
    elif user_input==2:
        jouer_carte()
        time.sleep(3)
        
def remove_shm_from_resource_tracker(): # patch bug python3
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

def reconize(card):
    if card[0]=="b":
        a = 2
        return a
    elif card[0]=="v":
        a = 3
        return a
    elif card[0]=="n":
        a = 4
        return a
    elif card[0]=="r":
        a = 5
        return a
    elif card[0]=="j":
        a = 6
        return a
    else:
        print("mauvaise carte")


def jouer_carte():
    with shared_memory_lock:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        signal.signal(signal.SIGINT, signal_handler)
        try:
            client_socket.connect(("localhost", 20002))
            data = str(client_socket.recv(10240).decode())
            remove_shm_from_resource_tracker()
            existing_shm = shared_memory.SharedMemory(name=data)
            shared_array = np.ndarray((7,), dtype=np.int64, buffer=existing_shm.buf)
            print("Tableau partagé (avant jouer_carte) :", shared_array)
            card = "r1"
            a = reconize(card)
            if int(shared_array[a]) + 1 == int(card[1]):
                print("Bravo !")
                print("La pile a été mise à jour :", card)
                shared_array[a] = shared_array[a] + 1
                print("Tableau partagé (après jouer_carte) :", shared_array)
            else:
                shared_array[0] = shared_array[0] - 1
                print("Oups... tu perds un jeton fuse, il en reste : ", shared_array[0])
        finally:
            # Fermer la connexion et libérer la mémoire partagée
            client_socket.close()
            existing_shm.close()

        return shared_array

def use_infos():
    with shared_memory_lock:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        signal.signal(signal.SIGINT, signal_handler)
        try:
            client_socket.connect(("localhost", 20002))
            data = str(client_socket.recv(10240).decode())
            remove_shm_from_resource_tracker()
            existing_shm = shared_memory.SharedMemory(name=data)
            shared_array = np.ndarray((7,), dtype=np.int64, buffer=existing_shm.buf)
            shared_array[1] = shared_array[1] - 1
            print("Tu as utilisé un jeton info, il n'en reste plus que :", shared_array[1])
        finally:
            # Fermer la connexion et libérer la mémoire partagée
            client_socket.close()
            existing_shm.close()

        return shared_array


def information(n_player, numPlayer, tab_data):
    valid_input = False
    use_infos() # retirer un jeton de la shared memory
    while not valid_input:
        try:
            message = f"Tu veux dire une information à quel joueur ?"
            print(message)
            user_input = input()
            user_input = int(user_input)

            if 1 <= user_input <= n_player and user_input != numPlayer:
                show_select(tab_data, user_input)
                valid_input = True
            else:
                print("Erreur : Entrée invalide. Veuillez choisir un joueur différent.")
        except ValueError:
            print("Erreur : Veuillez entrer un nombre valide.")
    # que veux-tu dévoiler ?
    valid_input = False
    while not valid_input:
        try:
            carte = f"Que veux-tu dévoiler (bleu, rouge,...,1, 2...)  ?"
            print(carte)
            user_input2 = input()
            ind = find_indices(tab_data, user_input2, user_input)
            valid_input = True
            mess = str(user_input) + "|" + ind
            queue.put(mess)
        except ValueError:
            print("Erreur : Veuillez entrer une valeur valide.")
    
# ... (le reste du code reste inchangé)

def find_indices(cards, criterion,numPlayer):
    indices = []

    if criterion=="bleu":
        criterion="b"
    elif criterion=="jaune":
        criterion="j"
    elif criterion=="vert":
        criterion="v"
    elif criterion=="noir":
        criterion="n"
    elif criterion=="rouge":
        criterion="r"

    i = (numPlayer - 1) * 5
    j = (numPlayer * 5) - 1
    indices = []

    for k, card in enumerate(cards[i:j + 1]):
        if criterion in card:
            indices.append(i + k)
    new=[]
    if criterion=="b":
        criterion="bleue"
    elif criterion=="j":
        criterion="jaune"
    elif criterion=="v":
        criterion="verte"
    elif criterion=="n":
        criterion="noire"
    elif criterion=="r":
        criterion="rouge"
    for v in indices:
        if numPlayer != 1:
            new.append((v+1)-((numPlayer-1)*5))
        else:
            new.append(v+1)
    
    message = f"Tu as une carte {criterion} à l'indice {new}"
    
    return message

def show_select(tab,numPlayer):
    i = (numPlayer-1)*5
    j = (numPlayer*5)-1
    y=0
    while i <= j:
        color = get_color(tab[i])
        card_info = f"{color} {tab[i][1:]}"
        print(f"| {chr(65 +y):2} - {card_info}", end=' | ')
        i+=1
        y+=1
    print("")


def get_color(card_value):
    """
    convertir une lettre en une couleur -> pour le première élément de la chaine de caractère (b1 -> bleu)
    """
    color_mapping = {
        'b': 'bleu',
        'r': 'rouge',
        'j': 'jaune',
        'v': 'vert',
        'n': 'noir'
    }
    color_letter = card_value[0]
    return color_mapping.get(color_letter, 'unknown')

def show_card(pile, numPlayer):
    """ 
    Montrer les cartes de ses collègues mais pas les siennes -> fonctionne, à ajouter si temps : 
        - dessin des cartes avec couleurs
    """
    i = (numPlayer - 1) * 5
    j = min(numPlayer * 5, len(pile))
    
    k = 0
    p = 1
    
    while k < len(pile):
        if k % 5 == 0 and k != 0:
            print("")
            p += 1
        if i <= k < j:
            print(end=" ")
        else:
            color = get_color(pile[k])
            card_info = f"{color} {pile[k][1:]}"
            print(f"|  {card_info:18}", end=' ') #{chr(65 + k):2} -
            if (k + 1) % 5 == 0:
                print(f"  < Tas du joueur {p}", end=' ')
        k += 1
        
    print("")

def check_input(input_str):
    """
    Vérifier que l'entrée utilisateur est 1 ou 2 -> ne pas oublier de convertir
    """
    try:    
        num = int(input_str)
        if num == 1 or num == 2:
            return True
        else:
            return False
    except ValueError:
        return False

def signal_handler(signum, frame):
    print("Signal INT reçu. Fermeture propre du programme.")
    
    # Terminer tous les processus enfants de manière plus robuste
    for process in multiprocessing.active_children():
        os.kill(process.pid, signal.SIGTERM)
    
    sys.exit(0)



if __name__ == "__main__":
    play_shared = Value('b', True)
    signal.signal(signal.SIGINT, signal_handler)
    clear_terminal()
    HOST = "localhost"
    with create_socket(HOST, 20000) as client_socket:
        tab_data = receive(client_socket)
        nb_player = player(tab_data)
        send("N", nb_player, client_socket)
    queue=Queue()
    time.sleep(1) # pour sync sinon serv socket pas encore ouvert avant de le rejoindre et erreur
    newstdin = os.fdopen(os.dup(sys.stdin.fileno()))
    for _ in range(int(nb_player)):
        p = Process(target=game, args=(HOST, 20001,play_shared,newstdin,queue,))
        p.start()
        p.join
