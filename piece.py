import copy


class Piece:
    def __init__(self, forme, nom):
        self.forme = forme
        self.nom = nom

    def peut_placer(self, plateau, position, joueur_emoji):
        """Vérifie si la pièce peut être placée selon les règles du Blokus.
        
        Règles :
        1. La pièce doit être dans les limites et sur des cases libres.
        2. La pièce NE DOIT PAS toucher une pièce de la même couleur par les arêtes (côtés).
        3. La pièce DOIT toucher une pièce de la même couleur par au moins un coin.
           EXCEPTION : Si c'est la première pièce de cette couleur sur le plateau, 
           elle doit recouvrir un des 4 coins du plateau.
        """
        grille = plateau.plateau
        taille = plateau.taille_plateau
        x_pos, y_pos = position

        coords_piece = []

        # 1. Vérification basique : Limites et cases occupées
        for r, row in enumerate(self.forme):
            for c, val in enumerate(row):
                if val:
                    x = x_pos + r
                    y = y_pos + c
                    if not (0 <= x < taille and 0 <= y < taille):
                        return False  # Hors du plateau
                    if grille[x][y] != '\033[29m■\033[0m':
                        return False  # Case déjà occupée
                    coords_piece.append((x, y))

        # Vérifier s'il y a déjà des pièces de cette couleur sur le plateau
        premier_tour = not any(joueur_emoji in ligne for ligne in grille)

        touche_coin_valide = False

        for px, py in coords_piece:
            # 2. Vérifier les arêtes (Haut, Bas, Gauche, Droite)
            # Si une arête touche une case de la même couleur -> INTERDIT
            voisins_aretes = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Haut, Bas, Gauche, Droite
            for dx, dy in voisins_aretes:
                nx, ny = px + dx, py + dy
                if 0 <= nx < taille and 0 <= ny < taille:
                    if grille[nx][ny] == joueur_emoji:
                        return False

            # 3. Vérifier les coins (Diagonales)
            # Si un coin touche une case de la même couleur -> BON
            voisins_coins = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dx, dy in voisins_coins:
                nx, ny = px + dx, py + dy
                if 0 <= nx < taille and 0 <= ny < taille:
                    if grille[nx][ny] == joueur_emoji:
                        touche_coin_valide = True

        if premier_tour:
            # Si c'est le premier tour, on doit occuper un coin du plateau (0,0), (0,max), (max,0), (max,max)
            coins_plateau = [(0, 0), (0, taille - 1), (taille - 1, 0), (taille - 1, taille - 1)]
            for cx, cy in coins_plateau:
                if (cx, cy) in coords_piece:
                    return True
            return False
        else:
            # Sinon, on doit obligatoirement toucher un coin d'une pièce de même couleur
            return touche_coin_valide

    def placer_piece(self, plateau, position, emoji):
        # Utilise la vérification avec les règles complètes
        if not self.peut_placer(plateau, position, emoji):
            return False

        grille = plateau.plateau
        x_pos, y_pos = position
        symbole_util = emoji if emoji is not None else '\033[29m■\033[0m'
        for r, row in enumerate(self.forme):
            for c, val in enumerate(row):
                if val:
                    x = x_pos + r
                    y = y_pos + c
                    grille[x][y] = symbole_util

        return True

    def rotation_90(self):
        # Inverse la liste et transpose
        self.forme = [list(row) for row in zip(*self.forme[::-1])]

    def miroir(self):
        # Inverse la liste
        self.forme = [row[::-1] for row in self.forme]

    def clone(self):
        return copy.deepcopy(self)
