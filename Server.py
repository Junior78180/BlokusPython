import asyncio
import json
import os
import platform
import sys

# Ensure we can import from current directory
sys.path.append('.')

from plateau import Plateau
from Joueur import Joueur


# Helper to serialize/deserialize
def piece_to_dict(p):
    """
    converts a piece to a dictionary
    :param p:
    :return: forme et nom de la piece
    """
    return {"forme": p.forme, "nom": p.nom}

def joueur_to_dict(j):
    """
    converts a player to a dictionary to send to client
    :param j:
    :return: nom, couleur, emoji, score, pieces, skip du joueur
    """
    return {
        "nom": j.nom,
        "couleur": j.couleur,
        "emoji": j.emoji,
        "score": j.score,
        "pieces": [piece_to_dict(p) for p in j.pieces],
        "skip": j.skip
    }

def clear_screen():
    """Efface le contenu du terminal"""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

class BlokusServer:
    """
    Class Blokus Server
    """
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.clients = {} # writer -> player_index
        self.writers = []
        self.plateau = Plateau(20)
        self.joueurs = []
        self.colors_available = [('bleu', 'Joueur 1'), ('jaune', 'Joueur 2'), ('rouge', 'Joueur 3'), ('vert', 'Joueur 4')]
        self.game_started = False
        self.current_player_idx = 0
        self.lock = asyncio.Lock()
        self.logs = []

    def log(self, message):
        """
        Affiche un message dans la console du serveur
        :param message:
        :return: le message
        """
        self.logs.append(message)
        if len(self.logs) > 8:
            self.logs.pop(0)
        
        if self.game_started:
            self.render_game()
        else:
            print(message)

    def render_game(self):
        """
        Permet l'affichage de l'interface du serveur
        :return:
        """
        clear_screen()
        print("=== SERVEUR BLOKUS - PARTIE EN COURS ===")
        
        # Scores
        scores_str = " | ".join([f"{j.nom}: {j.score}pts" for j in self.joueurs])
        print(f"Scores: {scores_str}")
        
        # Tour
        if self.joueurs and self.game_started:
            c_player = self.joueurs[self.current_player_idx]
            print(f"Tour actuel: {c_player.nom} ({c_player.emoji})")
        
        print("-" * 40)
        # Plateau
        for row in self.plateau.plateau:
            print(" ".join(row))
        print("-" * 40)
        
        # Logs
        print("Logs récents:")
        for l in self.logs:
            print(f"> {l}")

    async def broadcast(self, message):
        """
        Envoie un message à tous les clients connectés
        :param message:
        :return: le message
        """
        # Log info messages to server console
        if isinstance(message, dict) and message.get("type") == "info":
            self.log(message["message"])

        for w in self.writers:
            try:
                w.write((json.dumps(message) + "\n").encode())
                await w.drain()
            except:
                pass

    async def send_to(self, writer, message):
        """
        Envoie un message à un client spécifique
        :param writer:
        :param message:
        :return: le message
        """
        try:
            writer.write((json.dumps(message) + "\n").encode())
            await writer.drain()
        except:
            pass

    async def handle_client(self, reader, writer):
        """
        Gère la connexion d'un client
        :param reader:
        :param writer:
        :return:
        """
        addr = writer.get_extra_info('peername')
        self.log(f"Connexion de {addr}")

        if self.game_started:
            await self.send_to(writer, {"type": "error", "message": "Partie déjà commencée"})
            writer.close()
            return

        if len(self.joueurs) >= 4:
            await self.send_to(writer, {"type": "error", "message": "Serveur plein"})
            writer.close()
            return

        async with self.lock:
            color, name = self.colors_available[len(self.joueurs)]
            new_player = Joueur(name, color)
            self.joueurs.append(new_player)
            self.writers.append(writer)
            player_idx = len(self.joueurs) - 1
            self.clients[writer] = player_idx

        self.log(f"Joueur {name} ({color}) connecté.")
        await self.send_to(writer, {"type": "welcome", "player_idx": player_idx, "color": color, "name": name})
        
        # Notify others
        await self.broadcast({"type": "info", "message": f"{name} a rejoint la partie. ({len(self.joueurs)}/4)"})

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                
                try:
                    msg = json.loads(data.decode())
                except:
                    continue

                if msg["type"] == "start":
                    if self.clients[writer] == 0:
                        if len(self.joueurs) >= 2:
                            await self.start_game()
                        else:
                            await self.send_to(writer, {"type": "error", "message": "Il faut au moins 2 joueurs."})
                
                elif msg["type"] == "move":
                    if not self.game_started:
                        continue
                    await self.process_move(writer, msg)
                
                elif msg["type"] == "skip":
                    if not self.game_started:
                        continue
                    if self.clients[writer] == self.current_player_idx:
                         self.joueurs[self.current_player_idx].skip = True
                         self.log(f"{self.joueurs[self.current_player_idx].nom} passe son tour (skip).")
                         await self.next_turn()

        except Exception as e:
            self.log(f"Erreur avec {addr}: {e}")
        finally:
            self.log(f"Déconnexion de {addr}")
            writer.close()

    async def start_game(self):
        """
        Démarre la partie
        :return:
        """
        async with self.lock:
            if self.game_started: return
            self.game_started = True
            self.current_player_idx = 0
        
        self.log("La partie commence !")
        await self.broadcast({"type": "game_start"})
        await self.send_game_state()

    async def send_game_state(self):
        """
        Envoie l'état de la partie au client
        :return:
        """
        state = {
            "type": "state",
            "plateau": self.plateau.plateau,
            "tour": self.current_player_idx,
            "joueurs": [joueur_to_dict(j) for j in self.joueurs]
        }
        await self.broadcast(state)
        # Force render on server side
        self.render_game()

    async def process_move(self, writer, msg):
        """
        Effectue le mouvement envoyé par le client
        :param writer:
        :param msg:
        :return:
        """
        player_idx = self.clients[writer]
        if player_idx != self.current_player_idx:
            await self.send_to(writer, {"type": "error", "message": "Ce n'est pas votre tour"})
            return

        joueur = self.joueurs[player_idx]
        piece_idx = msg.get("piece_idx")
        x = msg.get("x")
        y = msg.get("y")
        
        if piece_idx is None or not (0 <= piece_idx < len(joueur.pieces)):
             await self.send_to(writer, {"type": "error", "message": "Pièce invalide"})
             return

        piece_originale = joueur.pieces[piece_idx]
        piece_to_place = None

        forme_recue = msg.get("forme")
        if forme_recue:
            # Verify that forme_recue is a valid transformation
            variants = []
            p = piece_originale.clone()
            for m in [False, True]:
                p_m = p.clone()
                if m: p_m.miroir()
                for r in range(4):
                    p_r = p_m.clone()
                    for _ in range(r):
                        p_r.rotation_90()
                    variants.append(p_r.forme)
            
            if forme_recue in variants:
                piece_to_place = piece_originale.clone()
                piece_to_place.forme = forme_recue
            else:
                 await self.send_to(writer, {"type": "error", "message": "Forme de pièce invalide (triche ?)"})
                 return
        else:
            # Fallback
            rotations = msg.get("rotations", 0)
            do_miroir = msg.get("miroir", False)
            
            piece_to_place = piece_originale.clone()
            if do_miroir:
                piece_to_place.miroir()
            for _ in range(rotations):
                piece_to_place.rotation_90()

        if piece_to_place.placer_piece(self.plateau, (x, y), joueur.emoji):
            joueur.placer_piece_retirer_piece_inv(piece_originale)
            self.log(f"{joueur.nom} a placé {piece_originale.nom} en ({x},{y})")
            await self.next_turn()
        else:
            await self.send_to(writer, {"type": "error", "message": "Placement invalide (règles Blokus)"})

    async def next_turn(self):
        """
        Passe au joueur suivant
        :return:
        """
        active_players = [j for j in self.joueurs if not j.skip and j.pieces]
        
        if not active_players:
             await self.broadcast({"type": "game_over", "joueurs": [joueur_to_dict(j) for j in self.joueurs]})
             self.game_started = False
             self.log("Partie terminée !")
             return

        start_idx = self.current_player_idx
        loop_count = 0
        while loop_count < len(self.joueurs):
            self.current_player_idx = (self.current_player_idx + 1) % len(self.joueurs)
            j = self.joueurs[self.current_player_idx]
            loop_count += 1
            
            if not j.pieces:
                j.skip = True
            
            if not j.skip:
                if not j.a_un_coup_possible(self.plateau):
                    j.skip = True
                    await self.broadcast({"type": "info", "message": f"{j.nom} est bloqué!"})
                else:
                    break
        
        if all(p.skip or not p.pieces for p in self.joueurs):
             await self.broadcast({"type": "game_over", "joueurs": [joueur_to_dict(j) for j in self.joueurs]})
             self.game_started = False
             self.log("Partie terminée !")
             return

        await self.send_game_state()

    async def start(self):
        """
        Démarre le serveur
        :return:
        """
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        self.log(f"Serveur démarré sur {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    server = BlokusServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        pass
