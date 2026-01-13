# Blokus Python

Ce projet est une implémentation du jeu de société **Blokus** en Python, jouable directement dans le terminal.  
Il propose deux modes de jeu : **local** (sur une seule machine) et **réseau** (client-serveur).

## But du jeu

Le but est de placer le maximum de ses pièces sur le plateau. Chaque pièce posée rapporte des points en fonction de sa taille (nombre de carrés).

Le jeu se termine quand plus aucun joueur ne peut poser de pièce. Le joueur avec le score le plus élevé gagne.

## Règles de placement

1.  **Première pièce** : Chaque joueur doit commencer dans un coin du plateau.
2.  **Pièces suivantes** : Chaque nouvelle pièce doit toucher au moins une autre pièce de la même couleur par un **coin**.
3.  **Interdictions** :
    *   Deux pièces de la même couleur ne peuvent pas se toucher par un **côté**.
    *   On ne peut pas recouvrir une pièce déjà posée.

## Modes de jeu

### 1. Mode Local (Solo)

Jouez à plusieurs sur le même ordinateur en passant le clavier.

*   **Lancer le jeu** :
    ```bash
    py main.py
    ```
*   Suivez les instructions pour choisir le nombre de joueurs (2 à 4).

### 2. Mode Réseau (Client-Serveur)

Jouez avec des amis sur différents ordinateurs via le réseau local.

#### Étape 1 : Lancer le Serveur
Une personne doit lancer le serveur qui hébergera la partie.
```bash
py Server.py
```
*   Le serveur attendra une connexion de 2 à 4 joueurs.

#### Étape 2 : Lancer les Clients
Chaque joueur (y compris celui qui héberge le serveur s'il veut jouer) doit lancer son client.
```bash
py Client.py
```
*   Par défaut, le client se connecte à `127.0.0.1` (localhost).
*   Pour jouer sur le réseau, modifiez l'adresse IP dans `Client.py` (`host='VOTRE_IP_LOCALE'`).

#### Étape 3 : Démarrer la partie
*   Une fois que tous les joueurs sont connectés, le **Joueur 1** (le premier connecté) doit appuyer sur `s` (pour start) dans son terminal client pour lancer la partie.

## Contrôles (Identiques pour les deux modes)

*   **Sélection** : Tapez le numéro de la pièce et validez avec `Entrée`.
*   **Déplacement** : Flèches directionnelles ou `ZQSD`.
*   **Rotation** : Touche `r`.
*   **Miroir** : Touche `m`.
*   **Valider** : Touche `Entrée`.
*   **Annuler/Changer** : Touche `c`.

#### Si la pièce est `x` alors elle n'est pas plaçable.

## Aperçu (Mode Réseau)

![Démonstration du jeu en mode Client-Serveur](BlokusAlexisMatthew.gif)

## Prérequis

*   Python 3.x
*   Bibliothèque `readchar` (pour bouger les pièces):
    ```bash
    pip install readchar
    ```
