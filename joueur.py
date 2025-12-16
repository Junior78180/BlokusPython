from piece import Piece

COULEURS = {
    'bleu': '🔵',
    'jaune': '😑',
    'rouge': '🔴',
    'vert': '💚'
}


def creer_pieces():
    return [
        # Single block
        Piece([[1]], "I1"),

        # Two blocks
        Piece([[1, 1]], "I2"),

        # Three blocks
        Piece([[1, 1, 1]], "I3"),
        Piece([[1, 1], [1, 0]], "Coin3"),

        # Four blocks
        Piece([[1, 1, 1, 1]], "I4"),
        Piece([[1, 0, 0], [1, 1, 1]], "L4"),
        Piece([[1, 1, 1], [0, 1, 0]], "T4"),
        Piece([[1, 1], [1, 1]], "Carré4"),
        Piece([[0, 1], [1, 1], [1, 0]], "Z4"),

        # Five blocks
        Piece([[1, 1, 1, 1, 1]], "I5"),
        Piece([[1, 0, 0, 0], [1, 1, 1, 1]], "L5"),
        Piece([[1, 1, 0], [1, 1, 1]], "d5"),
        Piece([[1, 0, 1], [1, 1, 1]], "U5"),
        Piece([[1, 1, 1, 1], [0, 0, 1, 0]], "F5"),
        Piece([[1, 0, 0], [1, 1, 1], [1, 0, 0]], "T5"),
        Piece([[1, 1, 1], [1, 0, 0], [1, 0, 0]], "GrandL5"),
        Piece([[0, 0, 1], [0, 1, 1], [1, 1, 0]], "W5"),
        Piece([[0, 1, 1], [0, 1, 0], [1, 1, 0]], "Z5"),
        Piece([[0, 1, 1], [1, 1, 0], [0, 1, 0]], "ZX5"),
        Piece([[0, 1, 0], [1, 1, 1], [0, 1, 0]], "X5")
    ]


class Joueur:
    def __init__(self, nom, couleur, emoji=None, pieces=None):
        if couleur not in COULEURS:
            raise ValueError(f"Couleur invalide. Choisissez parmi : {list(COULEURS.keys())}")

        self.nom = nom
        self.couleur = couleur
        self.emoji = COULEURS[couleur] if emoji is None else emoji
        self.pieces = creer_pieces() if pieces is None else pieces

    def placer_piece_retirer_piece_inv(self, piece):
        if piece in self.pieces:
            self.pieces.remove(piece)
