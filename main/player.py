import sys, signal, os, socket, time
import threading
from multiprocessing import Process, Pipe, Array,Semaphore
import sysv_ipc

nbr_player = None
tab_data = []
playing = True
player_ready = threading.Event()

def clear_terminal():
    """Clears the terminal screen."""
    os.system('clear')

def handler(sig, frame):
    """Handler for SIGINT signal."""
    if sig == signal.SIGINT:
        print("Reçu SIGINT. Sortie...")
        sys.exit(1)

def create_socket(host, port):
    """Creates a client socket and returns it."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

def receive(client_socket):
    """Receives a message from the server."""
    data = client_socket.recv(1024)
    return decode(data)

def decode(message):
    """Decodes the message received from the client."""
    message_parts = message.decode('utf-8').strip().split("|")
    return message_parts

def player(tab_data_2):
    """Asks the player how many players will be in the game."""
    global nbr_player
    while True:
        try:
            val = int(input(tab_data_2[1]))
            if 2 <= val <= 5:
                nbr_player = val
                player_ready.set()  # Indiquer que le nombre de joueurs est prêt
                return val
            else:
                print("Veuillez entrer un entier entre 2 et 5.")
        except ValueError:
            print("Veuillez entrer un entier entre 2 et 5.")

def send(type, mess, client_socket):
    """Sends a message to the server."""
    if type == "N":
        chaine = str(mess)
        m = type + "|" + chaine
        client_socket.sendall(m.encode('utf-8'))
    if type == "P":
        m = type + "|" + mess
        client_socket.sendall(m.encode('utf-8'))
    if type == "M":
        m = type + "|" + mess
        client_socket.sendall(m.encode('utf-8'))
            
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
    """afficher les cartes du joueur"""
    numPlayer = numPlayer + 1
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

def play(_, nbr_player, deck, shared_array, newstdin2, semaphore):
    """expliquer comment jouer"""
    sys.stdin = newstdin2
    key = 128
    mq = sysv_ipc.MessageQueue(key)
    numPlayer = _
    indice=""
    global playing
    while playing:
        semaphore.acquire()  # Acquérir le sémaphore avant d'accéder à la section critique
        for _ in range(mq.current_messages):
            message, t = mq.receive()
            message2 = message.decode('utf-8')
            message2 = message2.split("|")
            sender_player = message2[0]
            if t==1 and int(sender_player) == (numPlayer+1):
                indice += "\n" + "- " + str(message2[1])
            elif t==1:
                mq.send(message)  # on renvoie le message au joueur suivant si pas pour lui
            elif t==6:
                deck=message2[:]     
        try:
            print(deck)
            compteur = 0
            if shared_array[2]==5:
                compteur+=1
            if shared_array[3]==5:
                compteur+=1
            if shared_array[4]==5:
                compteur+=1
            if shared_array[5]==5:
                compteur+=1
            if shared_array[6]==5:
                compteur+=1
            if compteur==nbr_player:
                print("Bravo ! Vous avez gagné !")
                playing=False
                sys.exit(1)
            print("C'est à vous de jouer player " + str(numPlayer + 1) + " !")
            print("Vous avez " + str(shared_array[0]) + " token fuse.")
            print("Vous avez " + str(shared_array[1]) + " token informations.")
            for i in range(2, 7): # de (2) à (7-1)
                if deck[i] != 0:
                    if i == 2:
                        print("Vous avez " + str(shared_array[i]) + ": cartes vertes.")
                    elif i == 3:
                        print("Vous avez " + str(shared_array[i]) + ": cartes jaunes.")
                    elif i == 4:
                        print("Vous avez " + str(shared_array[i]) + ": cartes bleues.")
                    elif i == 5:
                        print("Vous avez " + str(shared_array[i]) + ": cartes rouges.")
                    elif i == 6:
                        print("Vous avez " + str(shared_array[i]) + ": cartes noires.")
            print("Les cartes de vos collègues sont les suivantes :")
            show_card(deck, numPlayer)
            time.sleep(0.1)  # import time
            if indice != "":
                print("Les informations que vous avez reçu sont les suivantes :", indice)
            message = f"Joueur {numPlayer+1} : Voulez-vous donner une information [1] ou jouer une carte [2] ? "
            user_input = input(message)
            while not check_input(user_input):
                user_input = input("Entrez un nombre (1 ou 2) : ")
            if user_input == "1":
                if shared_array[1] > 0:
                    information(nbr_player, numPlayer, deck,mq)
                else:
                    print("Vous n'avez plus d'informations à donner.")
            elif user_input == "2":
                deck=jouer_carte(numPlayer, deck, shared_array)
                # recoit le nouveau tableau qu'il faut transmettre aux autres players
                time.sleep(0.1)
        finally:
            # tjrs renvoyer son tab_data
            print("Le joueur " + str(numPlayer + 1) + " a joué !")
            tab_bis="|".join(deck)
            mq.send(type = 6, message = tab_bis)
            print("Joueur suivant !")
            time.sleep(2)  # import time
            clear_terminal()
            semaphore.release()  # Libérer le sémaphore après utilisation
        time.sleep(0.1)

def jouer_carte(numPlayer, deck, shared_array):
    """jouer une carte"""
    numPlayer = (numPlayer + 1)
    valid_input = False
    while not valid_input:
        try:
            message = f"Quelle carte voulez-vous jouer ? "
            user_input = input(message)
            user_input = int(user_input)
            if 1 <= user_input <= 5:
                valid_input = True
            else:
                print("Erreur : Entrée invalide. Veuillez choisir une carte différente.")
        except ValueError:
            print("Erreur : Veuillez entrer un nombre valide.")
        return sortir_carte(user_input,numPlayer,deck,shared_array)
        
    
    # comparer sa carte avec la carte du dessus de la pile dans la shared memory
    
def sortir_carte(num_carte,numPlayer,deck,shared_array):
    """expliquer comment sortir une carte"""
    global playing
    key = 128
    mq = sysv_ipc.MessageQueue(key)
    i=5*(numPlayer-1)
    j=i+num_carte
    valid=True
    print("La carte que vous décidez de jouer : ",deck[j-1])
    while deck[j-1] == "N":
        print("Vous n'avez pas de carte à cet emplacement (pioche vide) !")
        
        try:
            num2 = int(input("Veuillez choisir une autre carte (entrez un nombre) : "))
            if 0 < num2 < 6:
                j = i + num2
            else:
                print("Choix de carte invalide. Veuillez choisir un nombre entre 1 et 5.")
        except ValueError: # gestion d'erreru si lettre
            print("Veuillez entrer un nombre valide.")

    print("La carte que vous décidez de jouer : ",deck[j-1])
    
    carte = deck[j-1]
    if carte[0] == 'b':
        if int(carte[1]) == (shared_array[4] + 1):
            shared_array[4] += 1
            valid=False
            print("Bravo ! Vous avez joué une carte bleue !")
    elif carte[0] == 'j':
        if int(carte[1]) == (shared_array[3]+1):
            shared_array[3] += 1
            valid=False
            print("Bravo ! Vous avez joué une carte jaune !")
    elif carte[0] == 'v':
        if int(carte[1]) == (shared_array[2]+1):
            shared_array[2] += 1
            valid=False
            print("Bravo ! Vous avez joué une carte verte !")
    elif carte[0] == 'n':
        if int(carte[1]) == (shared_array[6]+1):
            shared_array[6] += 1
            valid=False
            print("Bravo ! Vous avez joué une carte noire !")
    elif carte[0] == 'r':
        if int(carte[1]) == (shared_array[5]+1):
            shared_array[5] += 1
            valid=False
            print("Bravo ! Vous avez joué une carte rouge !")
    if valid :
        print("Flûte alors tu perds une vie !")
        shared_array[0] -= 1
        if shared_array[0] < 0:
            print("Vous avez perdu !")
            playing=False

    # demande une nouvelle carte au serveur 
    message="M|"+str(numPlayer)+"|"+str(num_carte-1)
    mq.send(message, type = 5)
    message,t = mq.receive(type = 5)
    # recoit la nouvelle carte, la met dans le tableau
    if message.decode('utf-8')!="Null":
        deck[j-1]=message.decode('utf-8')
        return deck
    else:
        print("La pioche est vide !")
        deck[j-1]=""
        
def information(nbr_player, numPlayer, deck,mq):
    """expliquer comment donner une information"""
    numPlayer = numPlayer + 1
    valid_input = False
    while not valid_input:
        try:
            message = f"Tu veux dire une information à quel joueur ? "
            user_input = input(message)
            user_input = int(user_input)

            if 1 <= user_input <= nbr_player and user_input != numPlayer:
                show_select(deck, user_input)
                valid_input = True
            else:
                print("Erreur : Entrée invalide. Veuillez choisir un joueur différent.")
        except ValueError:
            print("Erreur : Veuillez entrer un nombre valide.")
    # que veux-tu dévoiler ?
    valid_input = False
    while not valid_input:
        try:
            carte = f"Que veux-tu dévoiler (bleu, rouge,...,1, 2...)  ? "
            print(carte)
            user_input2 = input()
            ind = find_indices(deck, user_input2, user_input)
            valid_input = True
            mess = str(user_input) + "|" + ind
            mq.send(mess.encode('utf-8'))
        except ValueError:
            print("Erreur : Veuillez entrer une valeur valide.")

def find_indices(cards, criterion,numPlayer):
    """expliquer comment trouver les indices"""
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
    """expliquer comment afficher les cartes du joueur"""
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

def sock():
    """Main function of the client."""
    key = 128
    mq = sysv_ipc.MessageQueue(key)
    global nbr_player, tab_data, playing
    HOST = "localhost"
    with create_socket(HOST, 5000) as client_socket:
        tab_data = receive(client_socket)
        nbr_player = player(tab_data)
        send("N", nbr_player, client_socket)
        tab_data = receive(client_socket)
        tab_data = tab_data[1:]
        while playing:
            message,t=mq.receive(type = 5)
            message=message.decode('utf-8')
            message=message.split("|")
            message_bis=str(message[1])+"|"+str(message[2])
            # message est un tuple -> "M|"+str(numPlayer)+"|"+str(num_carte-1)
            send("M",message_bis,client_socket) # on renvoie le message au serveur
            #send("M",message_bis,client_socket)
            message2 = receive(client_socket) # message recoit le split de ce qu'il a recu
            # à renvoyer au joueur qui nous a demandé une carte message[1]
            if message2:
                mq.send(type=5, message=message2[1])

def main(shared_array, newstdin):
    """Main function."""
    sys.stdin = newstdin
    clear_terminal()
    signal.signal(signal.SIGINT, handler)
    key = 128
    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
    thread = threading.Thread(target=sock, args=())
    thread.start()
    print("Bienvenue dans Hanabi !")
        
    # Attendre que le nombre de joueurs soit prêt
    player_ready.wait()

    # Maintenant que nbr_player n'est plus None, on peut créer le sémaphore
    semaphore = Semaphore(value=1)  # Initialiser le sémaphore avec une valeur de 1

    time.sleep(1)  # import time

    process_list = []
    newstdin2 = os.fdopen(os.dup(sys.stdin.fileno()))
    for _ in range(int(nbr_player)):
        p = Process(target=play, args=(_, nbr_player, tab_data, shared_array, newstdin2, semaphore,))
        p.start()
        process_list.append(p)
    for process in process_list:
        process.join()
    thread.join()
    mq.remove()
    
if __name__ == "__main__":
    """Entry point."""
    main(Array('i', range(5)), sys.stdin)
