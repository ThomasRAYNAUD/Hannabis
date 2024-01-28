# Hannabis

Développement du jeu Hannabi (version simplifiée). 
Dans les codes suivants, il est nécessaire d'exécuter dans un premier temps le server/game puis le client.

```bash
#Installer python3 pour lancer les codes suivants (sur Linux [Debian/Ubuntu]) :
sudo apt-get install python3
```

## Dossier "Shared_Memory" :
> Contient deux codes, utilisés afin de réaliser des tests sur l'accès à une shared memory des deux côtés (client-serveur) :
- Serveur.py : créé une shared memory
- client.py : accès à la shared memory

Il est nécessaire d'installer :
```bash
pip install numpy
```
## Dossier "main" :
> Contient deux codes, utilisés afin de jouer en signalant les cartes de ses équipiers :
- game.py : ditribue cartes
- player.py : permet aux joueurs d'intéragir chacun leur tour

Il n'est pas nécessaire d'installer des paquets supplémentaires.

## Dossier "mainAndSharedMemory" :
> Contient les deux codes fusionnés
- game.py
- player.py

## Lancer les scripts : 
Afin de lancer les scripts, il faut dans un premier temps cloner le dépot github : 
```bash
git clone https://github.com/ThomasRAYNAUD/Hannabis.git
cd ./Hannabis
cd [dossier voulu]
python3 ./script.py      #lancer un script
```
