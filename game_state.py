# Arquivo: game_state.py
from player import Player
from typing import List

class GameState:
    """
    A classe mestre que contém todo o estado de um jogo em um determinado momento.
    """
    def __init__(self):
        self.player = Player()
        self.turn = 0
        # Por enquanto, representaremos os 3 locais como listas de cartas.
        # Mais tarde, isso pode se tornar uma classe 'Location' mais complexa.
        self.locations: List[List] = [[], [], []]

    def start_game(self):
        """
        Prepara o estado inicial do jogo no turno 1.
        """
        self.turn = 1
        self.player.draw_cards(3) # Compra inicial
        self.player.energy_max = 1
        self.player.energy_current = 1
        print("--- Jogo Iniciado (Turno 1) ---")

    def advance_to_next_turn(self):
        """
        Avança o jogo para o próximo turno.
        """
        if self.turn >= 6:
            print("O jogo já terminou.")
            return

        self.turn += 1
        print(f"\n--- Iniciando Turno {self.turn} ---")
        self.player.draw_cards(1) # Compra do turno
        self.player.energy_max = self.turn
        self.player.energy_current = self.turn

    def play_card(self, card_id: int, location_index: int):
        """
        Lida com a ação de um jogador de jogar uma carta em um local.
        """
        # Validação do índice do local
        if not 0 <= location_index < len(self.locations):
            print(f"ERRO: Local inválido: {location_index}. Escolha entre 0, 1 ou 2.")
            return

        played_card = self.player.play_card(card_id)

        if played_card:
            self.locations[location_index].append(played_card)
            # Nota do Maestro: Futuramente, este é o local onde a lógica
            # para ativar as habilidades "Ao Revelar" será invocada.
            # Por agora, apenas colocamos a carta no campo.

    def __repr__(self) -> str:
        """
        Representação textual completa do estado do jogo.
        """
        header = f"====== ESTADO DO JOGO | TURNO {self.turn} | ENERGIA: {self.player.energy_current}/{self.player.energy_max} ======"
        player_state = str(self.player)
        locations_state = f"Locais: {self.locations}" # Adicionar esta linha
        return f"{header}\n{player_state}\n{locations_state}\n" # Modificar esta linha
