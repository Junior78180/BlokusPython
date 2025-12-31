import random

from piece import Piece

COULEURS = {
    'bleu': '\033[34m■\033[0m',
    'jaune': '\033[33m■\033[0m',
    'rouge': '\033[31m■\033[0m',
    'vert': '\033[32m■\033[0m'
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
        Piece([[1, 1, 1, 1], [0, 0, 1, 0]], "Y5"),
        Piece([[1, 0, 0], [1, 1, 1], [1, 0, 0]], "T5"),
        Piece([[1, 1, 1], [1, 0, 0], [1, 0, 0]], "GrandL5"),
        Piece([[0, 0, 1, 1], [1, 1, 1, 0]], "PetitZ5"),
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
        self.skip = False  # Si True, le joueur est exclu pour le reste de la partie
        self.score = 0

    def placer_piece_retirer_piece_inv(self, piece):
        if piece in self.pieces:
            # Calcul des points de la pièce posée (nombre de carrés)
            points_piece = sum(sum(row) for row in piece.forme)
            self.score += points_piece
            self.pieces.remove(piece)
            
            # Bonus si toutes les pièces sont posées
            if not self.pieces:
                self.score += 15
                # Petit bonus supplémentaire si la dernière pièce était le I1 (carré 1)
                if points_piece == 1:
                    self.score += 5

    def a_un_coup_possible(self, plateau):
        """Retourne True s'il existe au moins un placement possible pour une des pièces du joueur"""
        for piece in self.pieces:
            # parcourir toutes les positions du plateau
            for x in range(plateau.taille_plateau):
                for y in range(plateau.taille_plateau):
                    if piece.peut_placer(plateau, (x, y), self.emoji):
                        return True
        return False

    def trouver_placement_possible(self, plateau):
        """Renvoie (piece, (x,y)) pour le premier placement possible trouvé, ou None si aucun"""

        pieces = self.pieces[:]
        random.shuffle(pieces)  # Mélanger les pièces pour varier les placements

        for piece in pieces:
            piece_originale = piece

            for miroir in [False, True]:
                for rotation in range(4):
                    piece_test = piece_originale.clone()

                    if miroir:
                        piece_test.miroir()

                    for _ in range(rotation):
                        piece_test.rotation_90()

                    positions = [
                        (x, y)
                        for x in range(plateau.taille_plateau)
                        for y in range(plateau.taille_plateau)
                    ]
                    random.shuffle(positions)  # Mélanger les positions pour varier les placements

                    for pos in positions:
                        if piece_test.peut_placer(plateau, pos, self.emoji):
                            return piece_originale, pos
        return None
