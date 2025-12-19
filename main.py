import os
import sys
import platform
import readchar # already installed
from readchar import key


from joueur import Joueur
from plateau import Plateau

def clear_screen():
    """Efface le contenu du terminal"""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def afficher_interface(plateau, joueur, tour, piece_en_cours=None, position=None, message=""):
    """Affiche le plateau et la liste des pièces côte à côte."""
    clear_screen()
    print(f"--- Tour {tour} : {joueur.nom} ({joueur.emoji}) ---\n")

    # 1. Préparation des lignes du plateau
    display_grid = [row[:] for row in plateau.plateau]
    
    if piece_en_cours and position:
        x_pos, y_pos = position
        symbole_valide = piece_en_cours.peut_placer(plateau, position, joueur.emoji)
        ghost_symbol = joueur.emoji if symbole_valide else 'X'
        
        for r, row in enumerate(piece_en_cours.forme):
            for c, val in enumerate(row):
                if val:
                    x, y = x_pos + r, y_pos + c
                    if 0 <= x < plateau.taille_plateau and 0 <= y < plateau.taille_plateau:
                        if display_grid[x][y] == '▪️':
                            display_grid[x][y] = ghost_symbol

    board_lines = ["Plateau de jeu :"]
    for row in display_grid:
        board_lines.append(" ".join(row))
    
    # 2. Préparation des lignes de la liste des pièces
    pieces_lines = ["Pièces disponibles :"]
    for i, p in enumerate(joueur.pieces):
        pieces_lines.append(f"{i}: {p.nom}")
        
    # 3. Affichage côte à côte
    max_lines = max(len(board_lines), len(pieces_lines))
    
    # Remplissage avec des lignes vides pour égaliser la hauteur
    board_lines += [""] * (max_lines - len(board_lines))
    pieces_lines += [""] * (max_lines - len(pieces_lines))

    col_width = 35 
    
    for b_line, p_line in zip(board_lines, pieces_lines):
        # On utilise une tabulation pour séparer visuellement, c'est souvent plus robuste avec les emojis
        print(f"{b_line} \t {p_line}")

    print("\n" + "="*40)
    if message:
        print(f"INFO: {message}")
    print("="*40)


if __name__ == "__main__":
    plateau = Plateau(20)
    couleurs = ["bleu", "jaune", "rouge", "vert"]
    nb_joueurs = int(input("Nombre de joueurs (2 à 4) : "))

    while nb_joueurs < 2 or nb_joueurs > 4:
        nb_joueurs = int(input("Veuillez entrer un nombre valide entre 2 et 4 : "))

    joueurs = [
        Joueur(f"Joueur {i + 1}", couleur=couleurs[i])
        for i in range(nb_joueurs)
    ]

    tour = 1
    au_tour_de = 0
    actifs = list(range(len(joueurs)))

    while tour < 100 and actifs:
        if not actifs:
            break

        joueur_idx = actifs[au_tour_de % len(actifs)]
        joueur = joueurs[joueur_idx]

        if joueur.skip:
            print(f"{joueur.nom} a passé son tour et est exclu")
            au_tour_de += 1
            continue

        tour_termine = False
        msg = "" # Message à afficher en bas de l'interface

        while not tour_termine:
            # Affichage de l'interface de sélection
            afficher_interface(plateau, joueur, tour, message=msg)
            msg = "" # Reset du message après affichage

            choix = input(f"\nTour de {joueur.nom}: Choisissez une pièce (numéro), ou 's' pour passer: ")

            if choix.lower() == 's':
                joueur.skip = True
                if joueur_idx in actifs:
                    actifs.remove(joueur_idx)
                msg = f"{joueur.nom} passe son tour et est exclu"
                tour_termine = True
                continue

            try:
                choix_piece_idx = int(choix)
                piece_originale = joueur.pieces[choix_piece_idx]
                piece_a_manipuler = piece_originale.clone()
            except (ValueError, IndexError):
                msg = "Entrée invalide, Veuillez choisir un numéro de pièce valide"
                continue

            # Boucle de manipulation de la pièce avec les flèches
            x, y = 0, 0
            placement_reussi = False
            
            # On centre la pièce au début si possible
            # x, y = 0, 0 est le coin haut gauche par défaut

            while not placement_reussi:
                afficher_interface(plateau, joueur, tour, piece_a_manipuler, (x, y), message=msg)
                msg = "" # Reset message
                
                print(f"Pièce: {piece_a_manipuler.nom} | Position: ({x}, {y})")
                print("Commandes: [Flèches] déplacer | [r] pivoter | [Entrée] placer | [c] retour choix")

                k = readchar.readkey()

                if k in (key.UP, 'z'):
                    x = max(0, x - 1)
                elif k in (key.DOWN, 's'):
                    x = min(plateau.taille_plateau - 1, x + 1)
                elif k in (key.LEFT, 'q'):
                    y = max(0, y - 1)
                elif k in (key.RIGHT, 'd'):
                    y = min(plateau.taille_plateau - 1, y + 1)
                elif k == 'r':
                    piece_a_manipuler.rotation_90()
                elif k == 'c':
                    break  # Retourne à la sélection de pièce
                elif k == key.ENTER:
                    if piece_a_manipuler.placer_piece(plateau, (x, y), joueur.emoji):
                        joueur.placer_piece_retirer_piece_inv(piece_originale)
                        msg = f"Pièce {piece_a_manipuler.nom} placée en ({x}, {y})"
                        placement_reussi = True
                        tour_termine = True
                    else:
                        msg = "Placement impossible ! Vérifiez les règles (coins, arêtes, limites)"
            
        au_tour_de += 1
        if au_tour_de >= len(actifs):
            au_tour_de = 0
            tour += 1

    clear_screen()
    # Affichage final
    print("Plateau final :")
    for row in plateau.plateau:
        print(" ".join(row))
    print("\nFin de la partie")