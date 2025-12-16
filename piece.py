import copy


class Piece:
    def __init__(self, forme, nom):
        self.forme = forme
        self.nom = nom

    def peut_placer(self, plateau, position):
        """Vérifie si la pièce peut être placée à la position donnée sur le plateau.

        Retourne True si la pièce tient dans les limites et que toutes les cases nécessaires
        sont libres ('▪️'), sinon False.
        """
        grille = plateau.plateau  # récupère la grille du plateau
        taille = plateau.taille_plateau  # récupère la taille du plateau
        x_pos, y_pos = position  # position où placer la pièce

        for r, row in enumerate(self.forme):
            for c, val in enumerate(row):
                if val:
                    x = x_pos + r
                    y = y_pos + c
                    if not (0 <= x < taille and 0 <= y < taille):
                        return False  # hors du plateau
                    if grille[x][y] != '▪️':
                        return False  # case déjà occupée
        return True

    def placer_piece(self, plateau, position, emoji):
        # Utilise la vérification avant de modifier la grille
        if not self.peut_placer(plateau, position):
            return False

        grille = plateau.plateau
        x_pos, y_pos = position
        symbole_util = emoji if emoji is not None else '▪️'
        for r, row in enumerate(self.forme):
            for c, val in enumerate(row):
                if val:
                    x = x_pos + r
                    y = y_pos + c
                    grille[x][y] = symbole_util

        return True

    def rotation_90(self):
        self.forme = [list(row) for row in zip(*self.forme[::-1])]

    def miroir(self):
        self.forme = [row[::-1] for row in self.forme]

    def clone(self):
        return copy.deepcopy(self)
