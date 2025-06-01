# Arquivo: game_state.py
from player import Player
from typing import List
import random # Add this line
import copy  # Add this
from collections import Counter  # Add this

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
        self.simulation_mode = False # Add this flag

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
        Processa eventos na fila de Resolução até que ela esteja vazia.
        Esta é a chave para lidar com reações em cadeia (ex: Hela -> Ghost Rider).
        """
        if not self.simulation_mode:
            print("--- Processando Fila de Resolução ---")
        while self.resolution_queue:
            # Pega o próximo evento (uma função de habilidade) da fila
            event_function, card_instance = self.resolution_queue.pop(0)

            if not self.simulation_mode:
                print(f"EXECUTANDO: Habilidade de {card_instance.name}")
            # Executa a função da habilidade, passando o estado atual do jogo
            event_function(self, card_instance)

    # def run_full_simulation(self):
    #     """
    #     Executa uma simulação completa e aleatória de um jogo a partir do estado atual.
    #     """
    #     print("\n\n===== INICIANDO SIMULAÇÃO COMPLETA =====")
    #     self.start_game()
    #     print(self)
    #
    #     while self.turn <= 6:
    #         # Encontra todas as jogadas legais
    #         playable_cards = [card for card in self.player.hand if card.cost <= self.player.energy_current]
    #
    #         if playable_cards:
    #             # Escolhe uma carta e um local aleatórios
    #             card_to_play = random.choice(playable_cards)
    #             location_to_play = random.randint(0, 2)
    #
    #             print(f"SIMULAÇÃO T{self.turn}: Jogando {card_to_play.name} no local {location_to_play}")
    #
    #             # Joga a carta e adiciona sua habilidade à fila de resolução
    #             played_card_instance = self.player.play_card(card_to_play.id) # player.play_card handles energy and hand removal
    #             if played_card_instance:
    #                 self.locations[location_to_play].append(played_card_instance)
    #                 # Adiciona a função da habilidade e a instância da carta à fila
    #                 self.resolution_queue.append((played_card_instance.ability_function, played_card_instance))
    #
    #         else:
    #             print(f"SIMULAÇÃO T{self.turn}: Nenhuma jogada possível.")
    #
    #         # Processa todas as habilidades que foram acionadas
    #         self.process_resolution_queue()
    #
    #         if self.turn == 6: # Check if it's the end of the game
    #             break
    #
    #         # Avança para o próximo turno
    #         self.advance_to_next_turn() # This method increments turn, draws card, updates energy
    #         print(self) # Print game state at the start of the new turn
    #
    #     print("\n===== SIMULAÇÃO CONCLUÍDA =====")

    def analyze_next_turn_outcomes(self, num_iterations: int = 1000) -> list:
        """
        Analisa todas as jogadas possíveis para o turno atual e retorna os 10 resultados mais prováveis.
        """
        possible_moves = []
        for card_in_hand in self.player.hand:
            if card_in_hand.cost <= self.player.energy_current:
                for i in range(len(self.locations)):
                    if len(self.locations[i]) < 4:
                        possible_moves.append({'card_id': card_in_hand.id, 'location_index': i, 'card_name': card_in_hand.name})

        if not possible_moves:
            print("Nenhuma jogada legal possível neste turno.")
            return []

        all_outcomes_data = []
        for move in possible_moves:
            current_move_outcomes = []
            for _ in range(num_iterations):
                game_copy = copy.deepcopy(self)
                game_copy.simulation_mode = True # Set flag for silent abilities
                # Pass the simulation_mode to play_card
                played_card_instance_copy = game_copy.player.play_card(move['card_id'], simulation_mode=game_copy.simulation_mode)
                if played_card_instance_copy:
                    game_copy.locations[move['location_index']].append(played_card_instance_copy)
                    if hasattr(played_card_instance_copy, 'ability_function') and callable(played_card_instance_copy.ability_function):
                        game_copy.resolution_queue.append((played_card_instance_copy.ability_function, played_card_instance_copy))
                game_copy.process_resolution_queue() # process_resolution_queue needs to respect simulation_mode for abilities
                final_powers_tuple = tuple(sum(c.power for c in loc) for loc in game_copy.locations)
                current_move_outcomes.append(final_powers_tuple)
            all_outcomes_data.append({'move': move, 'outcomes': current_move_outcomes})

        # Agrega e calcula as probabilidades (as per prompt)
        final_results = {}
        # total_simulations = len(possible_moves) * num_iterations # Not used in prompt's final calc

        for result_group in all_outcomes_data:
            # Using card_name from possible_moves if available, else card_id
            move_card_name = result_group['move'].get('card_name', f"ID:{result_group['move']['card_id']}")
            move_str = f"Jogar {move_card_name} no L{result_group['move']['location_index']}"
            outcome_counts = Counter(result_group['outcomes'])

            for outcome, count in outcome_counts.items():
                if outcome not in final_results:
                    final_results[outcome] = {'probability': 0, 'actions': set()}

                prob_from_this_move = count / num_iterations # P(Outcome | This Specific Move)
                # This is P(Outcome) = Sum_M [ P(Outcome | M) * P(M) ] where P(M) = 1/len(possible_moves)
                final_results[outcome]['probability'] += prob_from_this_move / len(possible_moves)
                final_results[outcome]['actions'].add(move_str)

        # Formata e ordena os resultados finais (as per prompt)
        sorted_outcomes = sorted(
            [
                # Takes the first action encountered that can lead to this outcome.
                {'prob': data['probability'], 'outcome': out, 'action': list(data['actions'])[0] if data['actions'] else "N/A"}
                for out, data in final_results.items()
            ],
            key=lambda x: x['prob'],
            reverse=True
        )
        return sorted_outcomes[:10]
