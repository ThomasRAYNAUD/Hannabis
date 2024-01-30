# Hannabis

Développement du jeu Hannabi (version simplifiée). 
Pour les codes suivant, il faut exécuter "start.py" et de s'assurer que game.py et "player.py" sont dans le même répertoire.

Dans un premier temps, il est nécessaire d'installer python3. Notre code est fonctionnel sur python3.8 :

```bash
#Installer python3 pour lancer les codes suivants (sur Linux [Debian/Ubuntu]) :
sudo apt-get install python3
```

## Dossier "main" :
> Contient deux codes, utilisés afin de jouer au jeu :
- **start.py** : contient la shared memory et permet de lancer les deux scripts suivants :
  - **game.py** : communique avec les players afin de gérer la pioche.
  - **player.py** : s'occupe de créer les différents processus de joueurs.

## Lancer les scripts : 
Afin de lancer les scripts, il faut dans un premier temps cloner le dépot github : 
```bash
git clone https://github.com/ThomasRAYNAUD/Hannabis.git
cd ./Hannabis
cd ./main
python3 ./start.py  #lancer le jeu
```
