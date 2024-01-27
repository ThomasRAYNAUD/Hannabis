import socket
import os
import sys

def receive(client_socket):
    data = client_socket.recv(1024)
    return decode(data)

def decode(message):
    # décode la trame pour en sortir tous les éléments et le mettre dans un tableau
    message_parts = message.decode('utf-8').split("|")
    return message_parts

def type(tab):
    # regarde le premier élément du tableau (= type) et en fonction prend une décision
    if tab[0] == "N":
        return tab[1]  # retourne le nombre de joueurs

def player(tab_data):
    verif = True
    while verif:
        try:
            val = int(input(tab_data[1]))
            print(val)
            if 2 <= val <= 5:
                verif=False
                return val
            else:
                print("Veuillez entrer un entier entre 2 et 5.")
        except ValueError:
                print("Veuillez entrer un entier entre 2 et 5.")

def send(type,mess,client_socket):
    # selon le type, un choix différent est fait = message envoyé différent
    if type == "N":  # demande le nombre de joueurs dans la partie
        chaine=str(mess)
        m = type + "|" + chaine
        print(m)
        client_socket.sendall(m.encode('utf-8'))
    if type == "P":
        m = type + "|" + mess
        client_socket.sendall(m.encode('utf-8'))
        
def clear_terminal():
     os.system('clear')

def create_socket(host, port):
    """
    Crée et retourne un objet socket connecté à l'adresse spécifiée.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

if __name__ == "__main__":
    HOST = "localhost"
    PORT = 26000

    with create_socket(HOST, PORT) as client_socket:
        tab_data = receive(client_socket)
        nb_player = player(tab_data)
        send("N", nb_player, client_socket)
        tab_data=receive(client_socket) # recoit tt le paquet -> tab_data contient le paquet de cartes mélangées
        send("P","Bien reçu paquet de cartes", client_socket)
        tab_data=tab_data[1::]
        print(tab_data)
        
        
# X * 5 -1