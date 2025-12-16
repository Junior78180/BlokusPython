class Piece:
    def __init__(self, forme, symbole):
        self.forme = forme  # Liste de tuples représentant les coordonnées des blocs de la pièce
        self.symbole = symbole  # Symbole pour représenter la pièce sur le tableau

    def placer(self, tableau, position):
        x_offset, y_offset = position
        for (x, y) in self.forme:
            tableau[y + y_offset][x + x_offset] = self.symbole