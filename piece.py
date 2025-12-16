class Piece:
    def __init__(self, forme, nom):
        self.forme = forme
        self.nom = nom

    def placer_piece(self, plateau, position, emoji):
        grille = plateau.plateau # récupère la grille du plateau
        taille = plateau.taille_plateau # récupère la taille du plateau
        x_pos, y_pos = position # position où placer la pièce

        for r, row in enumerate(self.forme):
            for c, val in enumerate(row):
                if val:
                    x = x_pos + r
                    y = y_pos + c
                    if not (0 <= x < taille and 0 <= y < taille):
                        return False  # hors du plateau
                    if grille[x][y] != '⬜':
                        return False  # case déjà occupée

        symbole_util = emoji if emoji is not None else '⬜'
        for r, row in enumerate(self.forme):
            for c, val in enumerate(row):
                if val:
                    x = x_pos + r
                    y = y_pos + c
                    grille[x][y] = symbole_util

        return True
