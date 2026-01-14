import asyncio
import json
import sys
import os
import platform

import readchar
from readchar import key

from piece import Piece
from plateau import Plateau

def clear_screen():
    """
    Efface le contenu du terminal
    :return:
    """
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def get_piece_lines(index, piece_data, emoji):
    """Génère les lignes de texte pour afficher une pièce (nom + forme)"""
    shape_lines = []
    for row in piece_data["forme"]:
        line = "".join([emoji + " " if cell else "  " for cell in row])
        shape_lines.append(line)
    
    header = f"{index}: {piece_data['nom']}"
    lines = []
    
    if shape_lines:
        lines.append(f"{header:<14} {shape_lines[0]}")
        for sl in shape_lines[1:]:
            lines.append(f"{' ' * 14} {sl}")
    else:
        lines.append(header)
    return lines

class BlokusClient:
    """
    Class Blokus Client
    """
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.my_idx = -1
        self.my_color = ""
        self.my_name = ""
        self.game_state = None
        self.running = True

    async def connect(self):
        """
        Établit une connexion au serveur
        :return:
        """
        print(f"Tentative de connexion à {self.host}:{self.port}...")
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        except Exception as e:
            print(f"Impossible de se connecter au serveur: {e}")
            return False
        return True

    async def send(self, message):
        """
        Envoie un message au serveur
        :param message:
        :return:
        """
        self.writer.write((json.dumps(message) + "\n").encode())
        await self.writer.drain()

    async def receive_loop(self):
        """
        Réception des messages du serveur en boucle
        :return:
        """
        while self.running:
            try:
                data = await self.reader.readline()
                if not data:
                    print("Connexion perdue avec le serveur.")
                    self.running = False
                    break
                
                msg = json.loads(data.decode())
                await self.handle_message(msg)
            except Exception as e:
                print(f"Erreur réception: {e}")
                self.running = False
                break

    async def handle_message(self, msg):
        """
        Gère les messages reçus du serveur
        :param msg:
        :return:
        """
        mtype = msg.get("type")
        
        if mtype == "welcome":
            self.my_idx = msg["player_idx"]
            self.my_color = msg["color"]
            self.my_name = msg["name"]
            print(f"Connecté en tant que {self.my_name} ({self.my_color})")
            print("En attente d'autres joueurs... (Appuyez sur 's' pour démarrer si vous êtes le joueur 1)")

        elif mtype == "info":
            print(f"INFO: {msg['message']}")

        elif mtype == "error":
            print(f"ERREUR: {msg['message']}")

        elif mtype == "game_start":
            print("La partie commence !")

        elif mtype == "state":
            self.game_state = msg
            # If it's not my turn, render the game state as is
            if self.game_state["tour"] != self.my_idx:
                self.render_interface()

        elif mtype == "game_over":
            self.game_state["joueurs"] = msg["joueurs"]
            self.render_interface()
            print("\nPARTIE TERMINÉE !")
            joueurs = msg["joueurs"]
            joueurs_tries = sorted(joueurs, key=lambda j: j["score"], reverse=True)
            for i, j in enumerate(joueurs_tries):
                print(f"{i+1}. {j['nom']} : {j['score']} points")
            print("=" * 40 + "\n")
            if joueurs_tries[0]['score'] != joueurs_tries[1]['score']:
                print(f"Le gagnant est {joueurs_tries[0]['nom']} avec {joueurs_tries[0]['score']} points ! \nFélicitations !")
            else : print(f"Égalité entre les joueurs !")
            print("\n", "=" * 40)
            self.running = False

    def render_interface(self, piece_en_cours=None, position=None, message=""):
        """
        Affiche l'interface du client
        :param piece_en_cours:
        :param position:
        :param message:
        :return: l'interface de la partie
        """
        if not self.game_state: return
        
        clear_screen()
        
        plateau_grid = self.game_state["plateau"]
        joueurs_data = self.game_state["joueurs"]
        tour = self.game_state["tour"]
        current_player_data = joueurs_data[tour]
        
        # Header
        header = f"--- Tour {tour} : {current_player_data['nom']} ({current_player_data['emoji']}) ---\n"
        scores_str = " | ".join([f"{j['nom']}: {j['score']}pts" for j in joueurs_data])
        print(header)
        print(f"Scores actuels : {scores_str}")
        print("-" * 60)

        # Prepare grid display
        display_grid = [row[:] for row in plateau_grid]
        
        # Ghost piece
        if piece_en_cours and position:
            x_pos, y_pos = position
            # Create temp objects for validation
            temp_plateau = Plateau(len(plateau_grid))
            temp_plateau.plateau = plateau_grid 
            
            my_emoji = joueurs_data[self.my_idx]['emoji']
            
            symbole_valide = piece_en_cours.peut_placer(temp_plateau, position, my_emoji)
            ghost_symbol = my_emoji if symbole_valide else 'X'
            
            for r, row in enumerate(piece_en_cours.forme):
                for c, val in enumerate(row):
                    if val:
                        x, y = x_pos + r, y_pos + c
                        if 0 <= x < len(display_grid) and 0 <= y < len(display_grid[0]):
                            if plateau_grid[x][y] == '\033[29m■\033[0m': # Empty cell
                                display_grid[x][y] = ghost_symbol
                            elif not symbole_valide:
                                display_grid[x][y] = ghost_symbol 

        board_lines = ["Plateau de jeu :"]
        for row in display_grid:
            board_lines.append(" ".join(row))
        
        # Pieces list (Show my pieces)
        target_player_idx = self.my_idx
        target_player = joueurs_data[target_player_idx]
        
        pieces_lines = [f"Vos pièces ({target_player['nom']}) :", ""]

        # Configuration de l'affichage en colonnes
        cols = 5  # Nombre de colonnes de pièces
        col_width = 20  # Largeur d'une colonne

        shape_piece = target_player['emoji']

        for i in range(0, len(target_player["pieces"]), cols):
            batch = []
            for j in range(cols):
                if i + j < len(target_player["pieces"]):
                    batch.append((i + j, target_player["pieces"][i + j]))

            batch_lines = [get_piece_lines(idx, p, shape_piece) for idx, p in batch]

            if not batch_lines:
                continue

            max_h = max(len(lines) for lines in batch_lines)

            # Harmonisation de la hauteur
            for lines in batch_lines:
                lines += [""] * (max_h - len(lines))

            # Construction des lignes
            for r in range(max_h):
                row_str = " " * 3
                for lines in batch_lines:
                    row_str += f"{lines[r]:<{col_width}}"
                pieces_lines.append(row_str)  # end of line
            pieces_lines.append("")

        # Side by side
        max_lines = max(len(board_lines), len(pieces_lines))
        board_lines += [""] * (max_lines - len(board_lines))
        pieces_lines += [""] * (max_lines - len(pieces_lines))
        
        for b_line, p_line in zip(board_lines, pieces_lines):
            print(f"{b_line}\t{p_line}")
            
        print("\n" + "="*40)
        if message:
            print(f"INFO: {message}")
        print("="*40)

    async def input_loop(self):
        """
        Réception des entrées du client en boucle
        :return:
        """
        print("Attente du démarrage... (Si vous êtes Joueur 1, tapez 's' pour lancer)")
        
        while self.running:
            if self.game_state and self.game_state["tour"] == self.my_idx:
                await self.play_turn()
            else:
                if self.my_idx == 0 and self.game_state is None:
                    cmd = await asyncio.to_thread(input, "")
                    if cmd.strip().lower() == 's':
                        await self.send({"type": "start"})
                else:
                    await asyncio.sleep(0.5)

    async def play_turn(self):
        """
        Affiche l'interface et récupère la saisie de pièce du joueur
        :return:
        """
        self.render_interface(message="C'est à votre tour ! Choisissez une pièce (numéro)")
        
        try:
            # 1. Select piece
            s = await asyncio.to_thread(input, "> ")
            if not s.strip(): return
            
            # Vérification de la saisie
            try:
                piece_idx = int(s)
            except ValueError:
                self.render_interface(message="Numéro invalide")
                await asyncio.sleep(1)
                return

            my_pieces = self.game_state["joueurs"][self.my_idx]["pieces"]
            if not (0 <= piece_idx < len(my_pieces)):
                self.render_interface(message="Index de pièce invalide")
                await asyncio.sleep(1)
                return

            # Création de l'objet Piece
            p_data = my_pieces[piece_idx]
            piece_obj = Piece(p_data["forme"], p_data["nom"])
            
            # 2. Place piece
            x, y = 0, 0
            
            confirmed = False
            msg = ""
            
            # Boucle afin de confirmer le placement de la pièce du joueur
            while not confirmed:
                self.render_interface(piece_en_cours=piece_obj, position=(x, y), message=msg or "ZQSD: Bouger | R: Rotation | M: Miroir | Entrée: Valider | C: Annuler")
                msg = ""
                
                k = await asyncio.to_thread(readchar.readkey)
                
                board_size = len(self.game_state["plateau"])
                
                if k in ('z', 'Z', key.UP): x = max(0, x - 1)
                elif k in ('s', 'S', key.DOWN): x = min(board_size - 1, x + 1)
                elif k in ('q', 'Q', key.LEFT): y = max(0, y - 1)
                elif k in ('d', 'D', key.RIGHT): y = min(board_size - 1, y + 1)
                elif k in ('r', 'R'): 
                    piece_obj.rotation_90()
                elif k in ('m', 'M'): 
                    piece_obj.miroir()
                elif k in ('c', 'C'):
                    return # Cancel move selection
                elif k == '\r' or k == '\n':
                    confirmed = True
            
            # Send move with the transformed shape
            await self.send({
                "type": "move",
                "piece_idx": piece_idx,
                "x": x,
                "y": y,
                "forme": piece_obj.forme # Send the actual shape after transformations
            })
            
            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Erreur tour: {e}")

async def main():
    # Demande de l'IP au démarrage
    print("=== BLOKUS CLIENT ===")
    target_ip = input("Entrez l'IP du serveur (laisser vide pour localhost) : ").strip()
    if not target_ip:
        target_ip = '127.0.0.1'
        
    client = BlokusClient(host=target_ip)
    if await client.connect():
        await asyncio.gather(
            client.receive_loop(),
            client.input_loop()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
