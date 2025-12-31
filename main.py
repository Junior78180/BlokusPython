import os
import sys
import platform
import time

# Force l'encodage UTF-8 pour la sortie standard pour supporter les caractères spéciaux (■)
# Cela corrige l'erreur UnicodeEncodeError sur Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import readchar
from readchar import key


from joueur import Joueur
from plateau import Plateau

def clear_screen():
    """Efface le contenu du terminal"""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def afficher_interface(plateau, joueur, tour, joueurs_list, piece_en_cours=None, position=None, message=""):
    """Affiche le plateau, la liste des pièces et les scores."""
    clear_screen()
    
    # En-tête avec les scores
    header = f"--- Tour {tour} : {joueur.nom} ({joueur.emoji}) ---\n"
    scores_str = " | ".join([f"{j.nom}: {j.score}pts" for j in joueurs_list])
    print(header)
    print(f"Scores actuels : {scores_str}")
    print("-" * 60)

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
                        if plateau.plateau[x][y] == '\033[29m■\033[0m':
                            display_grid[x][y] = ghost_symbol
                        elif not symbole_valide:
                             display_grid[x][y] = ghost_symbol

    board_lines = ["Plateau de jeu :"]
    for row in display_grid:
        board_lines.append(" ".join(row))
    
    # 2. Préparation des lignes de la liste des pièces
    pieces_lines = ["Pièces disponibles :"]
    # On ajoute une ligne vide pour l'espacement si voulu, mais en tant qu'élément de liste
    pieces_lines.append("") 
    
    for i in range(0, len(joueur.pieces), 2):
        p1 = joueur.pieces[i]
        line_content = f"{i}: {p1.nom}"
        if i + 1 < len(joueur.pieces):
            p2 = joueur.pieces[i+1]
            line_content = f"{line_content:<20} {i+1}: {p2.nom}"
        pieces_lines.append(f"{' ' * 5} {line_content}")
        
    # 3. Affichage côte à côte (2 colonnes)
    max_lines = max(len(board_lines), len(pieces_lines))
    
    # Remplissage avec des lignes vides pour égaliser la hauteur
    board_lines += [""] * (max_lines - len(board_lines))
    pieces_lines += [""] * (max_lines - len(pieces_lines))

    
    for b_line, p_line in zip(board_lines, pieces_lines):
        print(f"{b_line}\t{p_line}")
        
    print("\n" + "="*40)
    if message:
        print(f"INFO: {message}")
    print("="*40)


if __name__ == "__main__":
    plateau = Plateau(5)
    clear_screen()
    try:
        nb_joueurs_input = input("Nombre de joueurs (2 à 4) [defaut 2]: ")
        nb_joueurs = int(nb_joueurs_input) if nb_joueurs_input.strip() else 2
    except ValueError:
        nb_joueurs = 2

    if nb_joueurs < 2: nb_joueurs = 2
    if nb_joueurs > 4: nb_joueurs = 4

    couleurs_dispo = [('bleu', 'Joueur 1'), ('jaune', 'Joueur 2'), ('rouge', 'Joueur 3'), ('vert', 'Joueur 4')]
    joueurs = []
    for i in range(nb_joueurs):
        c, nom_defaut = couleurs_dispo[i]
        joueurs.append(Joueur(nom_defaut, couleur=c))

    tour = 1
    au_tour_de = 0
    actifs = list(range(len(joueurs)))

    while tour < 100 and actifs:
        if not actifs:
            break

        joueur_idx = actifs[au_tour_de % len(actifs)]
        joueur = joueurs[joueur_idx]

        if joueur.skip:
            if joueur_idx in actifs:
                actifs.remove(joueur_idx)
            if actifs and au_tour_de >= len(actifs):
                au_tour_de = 0
                tour += 1
            continue

        # Vérification automatique : Plus de pièces ou bloqué
        bloque = False
        raison = ""
        if not joueur.pieces:
            raison = f"{joueur.nom} a terminé (toutes les pièces posées) !"
            bloque = True
        elif not joueur.a_un_coup_possible(plateau):
            raison = f"{joueur.nom} est bloqué et ne peut plus jouer !"
            bloque = True
        
        if bloque:
            print(f"\n" + "=" * 40)
            print(f"INFO: {raison}")
            print(f"=" * 40)
            joueur.skip = True
            if joueur_idx in actifs:
                actifs.remove(joueur_idx)

            time.sleep(2)
            
            if actifs and au_tour_de >= len(actifs):
                au_tour_de = 0
                tour += 1
            continue

        tour_termine = False
        msg = "" 

        while not tour_termine:
            afficher_interface(plateau, joueur, tour, joueurs, message=msg)
            msg = "" 

            print(f"\nTour de {joueur.nom}: Choisissez une pièce (tapez le numéro et Entrée)")
            choix = input("> ")

            try:
                choix_piece_idx = int(choix)
                if not (0 <= choix_piece_idx < len(joueur.pieces)):
                    raise ValueError
                piece_originale = joueur.pieces[choix_piece_idx]
                piece_a_manipuler = piece_originale.clone()
            except (ValueError, IndexError):
                msg = "Numéro de pièce invalide."
                continue

            # Boucle de manipulation
            x, y = 0, 0
            placement_reussi = False
            
            while not placement_reussi:
                afficher_interface(plateau, joueur, tour, joueurs, piece_a_manipuler, (x, y), message=msg)
                msg = "" 
                
                print(f"Pièce: {piece_a_manipuler.nom} | Position: ({x}, {y})")
                print("Flèches ou ZQSD: déplacer | r: pivoter | m: miroir | Entrée: valider | c: changer pièce")

                k = readchar.readkey()

                if k in (key.UP, 'z', 'Z'):
                    x = max(0, x - 1)
                elif k in (key.DOWN, 's', 'S'):
                    x = min(plateau.taille_plateau - 1, x + 1)
                elif k in (key.LEFT, 'q', 'Q'):
                    y = max(0, y - 1)
                elif k in (key.RIGHT, 'd', 'D'):
                    y = min(plateau.taille_plateau - 1, y + 1)
                elif k in ('r', 'R'):
                    piece_a_manipuler.rotation_90()
                elif k in ('m', 'M'):
                    piece_a_manipuler.miroir()
                elif k in ('c', 'C'):
                    break 
                elif k == key.ENTER or k == '\r' or k == '\n':
                    if piece_a_manipuler.placer_piece(plateau, (x, y), joueur.emoji):
                        joueur.placer_piece_retirer_piece_inv(piece_originale)
                        msg = f"Pièce placée en ({x}, {y})."
                        placement_reussi = True
                        tour_termine = True
                    else:
                        msg = "Placement invalide (règles Blokus non respectées)."
            
        # Gestion de fin de tour
        if joueur.skip:
            # Si le joueur a été exclu, on n'incrémente pas au_tour_de (car décalage de liste)
            if actifs and au_tour_de >= len(actifs):
                au_tour_de = 0
                tour += 1
        else:
            au_tour_de += 1
            if actifs and au_tour_de >= len(actifs):
                au_tour_de = 0
                tour += 1
        
        if not actifs:
            break

    clear_screen()
    print("="*40)
    print("FIN DE LA PARTIE")
    print("="*40)
    print("Plateau final :")
    for row in plateau.plateau:
        print(" ".join(row))
    
    print("\n--- CLASSEMENT FINAL ---")
    joueurs_tries = sorted(joueurs, key=lambda j: j.score, reverse=True)
    
    for i, j in enumerate(joueurs_tries):
        print(f"{i+1}. {j.nom} : {j.score} points")

    if joueurs_tries[0].score == joueurs_tries[1].score:
        # Si 2 membres on le même nombre alors 3 est compris dedans aussi
        gagnant = None
        print(f"\n🏆 Égalité {joueurs_tries[0].score} points ! 🏆")
    else:
        gagnant = joueurs_tries[0]
        print(f"\n🏆 Le gagnant est {gagnant.nom} avec {gagnant.score} points ! 🏆")
