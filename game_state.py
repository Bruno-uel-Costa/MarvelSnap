# Arquivo: game_state.py
from player import Player
from typing import List
import random # Add this line

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
        self.resolution_queue = [] # Add this line

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

    def process_resolution_queue(self):
        """
        Processa eventos na fila de resolução até que ela esteja vazia.
        Esta é a chave para lidar com reações em cadeia (ex: Hela -> Ghost Rider).
        """
        print("--- Processando Fila de Resolução ---")
        while self.resolution_queue:
            # Pega o próximo evento (uma função de habilidade) da fila
            event_function, card_instance = self.resolution_queue.pop(0)

            print(f"EXECUTANDO: Habilidade de {card_instance.name}")
            # Executa a função da habilidade, passando o estado atual do jogo
            event_function(self, card_instance)

    def run_full_simulation(self):
        """
        Executa uma simulação completa e aleatória de um jogo a partir do estado atual.
        """
        print("\n\n===== INICIANDO SIMULAÇÃO COMPLETA =====")
        self.start_game()
        print(self)

        while self.turn <= 6:
            # Encontra todas as jogadas legais
            playable_cards = [card for card in self.player.hand if card.cost <= self.player.energy_current]

            if playable_cards:
                # Escolhe uma carta e um local aleatórios
                card_to_play = random.choice(playable_cards)
                location_to_play = random.randint(0, 2)

                print(f"SIMULAÇÃO T{self.turn}: Jogando {card_to_play.name} no local {location_to_play}")

                # Joga a carta e adiciona sua habilidade à fila de resolução
                played_card_instance = self.player.play_card(card_to_play.id) # player.play_card handles energy and hand removal
                if played_card_instance:
                    self.locations[location_to_play].append(played_card_instance)
                    # Adiciona a função da habilidade e a instância da carta à fila
                    self.resolution_queue.append((played_card_instance.ability_function, played_card_instance))

            else:
                print(f"SIMULAÇÃO T{self.turn}: Nenhuma jogada possível.")

            # Processa todas as habilidades que foram acionadas
            self.process_resolution_queue()

            if self.turn == 6: # Check if it's the end of the game
                break

            # Avança para o próximo turno
            self.advance_to_next_turn() # This method increments turn, draws card, updates energy
            print(self) # Print game state at the start of the new turn

        print("\n===== SIMULAÇÃO CONCLUÍDA =====")
