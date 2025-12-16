import random

from joueur import Joueur
from plateau import Plateau

if __name__ == "__main__":
    plateau = Plateau(10)
    plateau.afficher_tableau()

    joueurs = [
        Joueur("Joueur 1 b", couleur='bleu'),
        Joueur("Joueur 2 j", couleur='jaune')
        #, Joueur("Joueur 3 r", couleur='rouge'),
        # Joueur("Joueur 4 v", couleur='vert')
    ]

    tour = 1
    au_tour_de = 0 # Indice du joueur dont c'est le tour

    # Liste des indices des joueurs actifs
    actifs = [i for i in range(len(joueurs))]

    while tour < 100 and actifs:
        # Si plus aucun joueur actif, on sort
        if not actifs:
            break

        # Réduire au tour de joueur s'il a été exclu
        if au_tour_de not in actifs:
            au_tour_de = actifs[0]

        joueur_idx = au_tour_de
        joueur = joueurs[joueur_idx]

        print(f"C'est le tour du {joueur.nom} (Tour {tour})")

        if joueur.skip:
            print(f"{joueur.nom} est en skip et est exclu pour le reste de la partie.")
            # Passer au joueur suivant actif
            pos = actifs.index(joueur_idx)
            au_tour_de = actifs[(pos + 1) % len(actifs)]
            continue

        # Forcer le joueur à jouer une pièce si possible
        placement = joueur.trouver_placement_possible(plateau)
        if placement is not None:
            piece_a_placer, position_voulue = placement
            if piece_a_placer.placer_piece(plateau, position_voulue, joueur.emoji):
                joueur.placer_piece_retirer_piece_inv(piece_a_placer)
                print(f"{joueur.nom} a placé la pièce {piece_a_placer.nom} en {position_voulue}.")
                print(f"Pièces restantes pour {joueur.nom} : {[piece.nom for piece in joueur.pieces]}")
            else:
                print(f"Pièces restantes pour {joueur.nom} : {[piece.nom for piece in joueur.pieces]}")
                print(f"Échec inattendu lors du placement de {piece_a_placer.nom}.")
        else:
            # Aucun placement possible -> on exclut le joueur pour le reste de la partie
            joueur.skip = True
            if joueur_idx in actifs:
                actifs.remove(joueur_idx)
            print(f"{joueur.nom} ne peut plus jouer et est exclu pour le reste de la partie.")

        plateau.afficher_tableau()

        # Avancer au joueur actif suivant
        if joueur_idx in actifs:
            pos = actifs.index(joueur_idx)
            au_tour_de = actifs[(pos + 1) % len(actifs)]
            # augmenter le numéro de tour quand on revient au premier joueur
            tour += 1 if au_tour_de == actifs[0] else 0
        else:
            # si joueur a été retiré, commencer par le même index dans la liste actifs
            au_tour_de = actifs[0] if actifs else 0

    print("Fin de la partie (tour limit atteint ou plus de joueurs actifs)")
