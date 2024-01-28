import socket
import os
import sys
from multiprocessing import Process,Queue,Value
import time

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

def game(host, port, queue, play_shared):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print("JE SUIS CONNECTE")

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
        print("Je suis le player numéro :", numPlayer)
        time.sleep(0.1)
        val = queue.get()

        while play_shared.value:
            print("Je suis :", numPlayer, "et la valeur est :", val)
            while val != numPlayer:
                val = queue.get()
            
            # traitement
            if n_player == numPlayer:
                print("OUI :", n_player)
                queue.put(1)
                val = 1
                play_shared.value = False
            else:
                n = val + 1
                queue.put(n)
                val += 1
                print("SHEESH")
    except KeyboardInterrupt:
        print("Interruption du processus.")
    finally:
        client_socket.close()



if __name__ == "__main__":
    play_shared = Value('b', True)
    clear_terminal()
    HOST = "localhost"
    with create_socket(HOST, 20000) as client_socket:
        tab_data = receive(client_socket)
        nb_player = player(tab_data)
        send("N", nb_player, client_socket)
    
    time.sleep(1) # pour sync sinon serv socket pas encore ouvert avant de le rejoindre et erreur
    mq=Queue()
    mq.put(1)
    for _ in range(int(nb_player)):
        p = Process(target=game, args=(HOST, 20001,mq,play_shared,))
        p.start()
