from joueur import Joueur
from plateau import Plateau

if __name__ == "__main__":
    plateau = Plateau(10)
    plateau.afficher_tableau()

    joueurs = [
        Joueur("Joueur 1", couleur='bleu'),
        Joueur("Joueur 2", couleur='jaune'),
    ]

    joueur1 = joueurs[0]
    piece_a_placer = joueur1.pieces[5]  # Exemple : prendre la première pièce du joueur 1


    if piece_a_placer.placer_piece(plateau, (0, 0), joueur1.emoji):
        joueur1.placer_piece_retirer_piece_inv(piece_a_placer)
        print(f"{joueur1.nom} a placé une pièce.")

    plateau.afficher_tableau()
