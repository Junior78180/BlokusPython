plateau = [['0' for _ in range(20)] for _ in range(20)]



def afficher_tableau():
    print("Tableau actuel :")
    a = 0
    for ligne in plateau:
        print(f"{ligne}")
        x = len(ligne)
        a += x
    print(f"Nombre total de cases : {a}")

afficher_tableau()