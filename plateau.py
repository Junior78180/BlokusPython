class Plateau:
    def __init__(self, taille=10):
        self.taille_plateau = taille
        self.plateau = [['▪️' for _ in range(taille)] for _ in range(taille)]

    def afficher_tableau(self):
        print("Tableau actuel :")
        a = 0
        for ligne in self.plateau:
            print(f"{ligne}")
            x = len(ligne)
            a += x
        print(f"Nombre total de cases : {a}")