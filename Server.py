import asyncio
import json

# --------------------
# Placement de pièce
# --------------------
def placerPiece(x, y, grille):
    bloc_L = [
        [1, 0, 0],
        [1, 1, 1]
    ]

    for i in range(len(bloc_L)):
        for j in range(len(bloc_L[0])):
            # Vérification des limites
            if 0 <= y+i < len(grille) and 0 <= x+j < len(grille[0]):
                if bloc_L[i][j] == 1:
                    grille[y+i][x+j] = 1
    return grille

def convert(x):
    lettres = "ABCDEFGHIJ"
    if x in lettres:
        return lettres.index(x) + 10
    return int(x)

async def handle_client(reader, writer):
    while True:
        data = await reader.read(1024)
        if not data:
            break

        grille = json.loads(data.decode())
        print("Grille reçue :")
        for row in grille:
            print(row)

        # input NON bloquant
        s = await asyncio.to_thread(input, "Coordonnées (x,y) : ")
        try:
            x, y = map(int, s.split(","))
        except ValueError:
            print("Format invalide")
            continue

        grille = placerPiece(x, y, grille)

        writer.write(json.dumps(grille).encode())
        await writer.drain()

        print("Grille renvoyée")

async def main():
    server = await asyncio.start_server(
        handle_client, '127.0.0.1', 8888
    )

    print("Serveur en écoute sur 127.0.0.1:8888")

    async with server:
        await server.serve_forever()

asyncio.run(main())

