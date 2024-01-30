from multiprocessing import Process, Value, Array
import game
import player
import os,sys
import signal

memory_size=100

def handler(sig, frame):
    """Handler for SIGINT signal."""
    if sig == signal.SIGINT:
        print("Reçu SIGINT. Sortie...")
        os.system('ipcrm -Q 128') # Supprime la file de message -> appuie sur "CTRL + C" clear la file
        sys.exit(1)

if __name__ == "__main__":
    newstdin = os.fdopen(os.dup(sys.stdin.fileno()))
    signal.signal(signal.SIGINT, handler)
    shared_array = Array('i', memory_size)
    game_process = Process(target=game.main, args=(shared_array,))
    game_process.start()
    player_process = Process(target=player.main, args=(shared_array,newstdin,))
    player_process.start()
    player_process.join()
