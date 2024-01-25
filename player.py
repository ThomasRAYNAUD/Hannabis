import socket
import os

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

def send(type,nb_player):
    # selon le type, un choix différent est fait = message envoyé différent
    if type == "N":  # demande le nombre de joueurs dans la partie
        chaine=str(nb_player)
        m = type + "|" + chaine
        print(m)
        client_socket.sendall(m.encode('utf-8'))

if __name__ == "__main__":
    HOST = "localhost"
    PORT = 25425
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        tab_data = receive(client_socket)
        nb_player=player(tab_data)
        send("N",nb_player)
# La suite du code ici après que vous ayez obtenu une valeur valide