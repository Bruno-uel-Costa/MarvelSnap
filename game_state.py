# Arquivo: game_state.py
import random
import copy
from collections import Counter
from typing import List, Tuple, Optional, Dict, Any, TYPE_CHECKING # Added Tuple

from player import Player
from deck_factory import create_card_from_prepared_data # Removed create_full_deck as Player handles its own deck init now

if TYPE_CHECKING:
    from card import Card


class GameState:
    """
    A classe mestre que contém todo o estado de um jogo em um determinado momento.
    """
    def __init__(self, initial_state_dict: Optional[Dict[str, Any]] = None):
        self.player: Player
        self.turn: int = 0
        self.locations: List[List['Card']] = [[], [], []]
        self.resolution_queue: list = []
        self.play_history: List['Card'] = []
        self.simulation_mode: bool = False # Ensure this is always initialized

        if initial_state_dict:
            self.player = Player() # Player init creates a full deck by default. We override its contents.

            self.turn = initial_state_dict.get('turn', 1)
            self.player.energy_current = initial_state_dict.get('current_energy', 0)
            self.player.energy_max = initial_state_dict.get('max_energy', 0)

            hand_ids = initial_state_dict.get('hand_ids', [])
            self.player.hand = [card for card_id in hand_ids if (card := create_card_from_prepared_data(card_id)) is not None]

            discard_ids = initial_state_dict.get('discard_ids', [])
            self.player.discard_pile = [card for card_id in discard_ids if (card := create_card_from_prepared_data(card_id)) is not None]

            deck_ids = initial_state_dict.get('deck_ids', [])
            self.player.deck = [card for card_id in deck_ids if (card := create_card_from_prepared_data(card_id)) is not None]
            # Note: Deck order is preserved from deck_ids. No shuffle here.

            locations_data = initial_state_dict.get('locations', [[], [], []])
            self.locations = []
            for loc_ids_list in locations_data:
                self.locations.append([card for card_id in loc_ids_list if (card := create_card_from_prepared_data(card_id)) is not None])

            while len(self.locations) < 3:
                self.locations.append([])
            self.locations = self.locations[:3]

            play_history_ids = initial_state_dict.get('play_history_ids', [])
            self.play_history = [card for card_id in play_history_ids if (card := create_card_from_prepared_data(card_id)) is not None]

            self.resolution_queue = [] # Start with an empty queue for a rehydrated state

        else:
            # Default initialization (new game)
            self.player = Player()
            self.turn = 0
            self.locations = [[], [], []]
            self.resolution_queue = []
            self.play_history = []
            # self.player.energy_max and self.player.energy_current will be set by start_game

    def start_game(self):
        """
        Prepara o estado inicial do jogo no turno 1.
        (Assumes self.player is already initialized with a deck from __init__)
        """
        self.turn = 1
        self.player.draw_cards(3)
        self.player.energy_max = 1
        self.player.energy_current = 1
        self.play_history = []
        self.resolution_queue = []
        self.locations = [[], [], []] # Ensure locations are reset for a new game
        print("--- Jogo Iniciado (Turno 1 via GameState.start_game) ---")

    def advance_to_next_turn(self):
        """
        Avança o jogo para o próximo turno.
        """
        if self.turn >= 7:
            print(f"GAMESTATE_INFO: Tentativa de avançar além do turno {self.turn}.")
            return

        self.turn += 1
        print(f"\n--- Iniciando Turno {self.turn} (via GameState.advance_to_next_turn) ---")
        self.player.draw_cards(1)
        self.player.energy_max = min(self.turn, 6)
        self.player.energy_current = self.player.energy_max
        self.resolution_queue = [] # Clear queue at start of natural turn

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

    def process_resolution_queue(self, resolved_outcomes_for_turn: Optional[List[Dict[str, Any]]] = None):
        """
        Processa eventos na fila de resolução.
        'resolved_outcomes_for_turn': A list of user-provided outcomes for specific RNG events this turn.
        """
        if resolved_outcomes_for_turn is None:
            resolved_outcomes_for_turn = []

        if not self.simulation_mode:
            print("--- Processando Fila de Resolução ---")

        while self.resolution_queue:
            event_function, card_instance = self.resolution_queue.pop(0)

            if not self.simulation_mode:
                print(f"EXECUTANDO: Habilidade de {card_instance.name} (ID: {card_instance.id})")

            # Pass game_state, card_instance, and the list of resolved_outcomes_for_turn
            event_function(self, card_instance, resolved_outcomes_for_turn)

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

    def analyze_next_turn_outcomes(self, opponent_powers: List[int], num_iterations: int = 1000) -> list:
        """
        Analisa todas as jogadas possíveis para o turno atual, calcula uma pontuação de avaliação
        contra os poderes do oponente fornecidos, e retorna as jogadas classificadas por pontuação média.
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

        all_outcomes_data = [] # This list will store groups of outcomes, whether analytical or simulated

        # Create a temporary lookup for card objects in hand by ID
        cards_in_hand_map = {card.id: card for card in self.player.hand}

        for move in possible_moves:
            card_to_check = cards_in_hand_map.get(move['card_id'])

            if not card_to_check:
                # print(f"ANALYZE_ERROR: Card with ID {move['card_id']} not found in hand map during hybrid check.")
                continue # Skip this move if card instance can't be found

            if not card_to_check.is_complex_rng:
                # --- Analytical Path ---
                analytical_path_scores = self.calculate_analytical_outcome(move, opponent_powers)

                if analytical_path_scores: # If not empty (i.e., play was valid)
                    all_outcomes_data.append({
                        'move': move,
                        'scores': analytical_path_scores,
                        'is_analytical': True
                    })

            else:
                # --- Monte Carlo Path ---
                current_move_monte_carlo_scores = []
                for _ in range(num_iterations):
                    game_copy = copy.deepcopy(self)
                    game_copy.simulation_mode = True

                    played_card_instance_copy = game_copy.player.play_card(move['card_id'], simulation_mode=game_copy.simulation_mode)

                    final_powers_tuple = None
                    if played_card_instance_copy:
                        game_copy.locations[move['location_index']].append(played_card_instance_copy)
                        if hasattr(played_card_instance_copy, 'ability_function') and callable(played_card_instance_copy.ability_function):
                            game_copy.resolution_queue.append((played_card_instance_copy.ability_function, played_card_instance_copy))

                        game_copy.process_resolution_queue()
                        game_copy.play_history.append(played_card_instance_copy)

                        # Calculate powers after all effects for this iteration
                        if hasattr(game_copy, 'calculate_location_power'):
                            final_powers_tuple = tuple(game_copy.calculate_location_power(i, game_copy.locations) for i in range(len(game_copy.locations)))
                        else:
                            final_powers_tuple = tuple(sum(c.power for c in loc) for loc in game_copy.locations)
                    else:
                        # If card play failed, use current board state for power calculation (likely unchanged or minimally changed)
                        # Or consider this an invalid path for this iteration (score could be -infinity or skip)
                        # For now, calculate power on the current (mostly unchanged) game_copy state.
                        if hasattr(game_copy, 'calculate_location_power'):
                            final_powers_tuple = tuple(game_copy.calculate_location_power(i, game_copy.locations) for i in range(len(game_copy.locations)))
                        else:
                            final_powers_tuple = tuple(sum(c.power for c in loc) for loc in game_copy.locations)

                    eval_score = self._calculate_evaluation_score(final_powers_tuple, opponent_powers)
                    current_move_monte_carlo_scores.append(eval_score)

                if current_move_monte_carlo_scores:
                    all_outcomes_data.append({
                        'move': move,
                        'scores': current_move_monte_carlo_scores,
                        'is_analytical': False
                    })

        # --- New Aggregation and Sorting Logic ---
        aggregated_move_evaluations = []

        for move_outcome_group in all_outcomes_data:
            move_details = move_outcome_group['move']
            scores_for_this_move = move_outcome_group['scores']

            if not scores_for_this_move:
                continue

            average_score_for_move = sum(scores_for_this_move) / len(scores_for_this_move)

            move_card_name = move_details.get('card_name', f"ID:{move_details['card_id']}")
            action_str = f"Jogar {move_card_name} no L{move_details['location_index']}"

            aggregated_move_evaluations.append({
                'action': action_str,
                'average_score': average_score_for_move
                # Optionally, could also include:
                # 'num_simulations': len(scores_for_this_move),
                # 'is_analytical': move_outcome_group['is_analytical']
            })

        # Sort the moves by their average_score in descending order
        sorted_moves_by_score = sorted(
            aggregated_move_evaluations,
            key=lambda x: x['average_score'],
            reverse=True
        )

        return sorted_moves_by_score[:10] # Return top 10 best moves by average score

    def calculate_analytical_outcome(self, move_details: dict, opponent_powers_for_eval: List[int]) -> List[int]:
        """
        Calculates the deterministic outcome of a simple move and returns its evaluation score.
        move_details is expected to be like {'card_id': card_id, 'location_index': loc_idx, 'card_name': name}
        Returns a list containing a single score, or an empty list if the move is invalid.
        """
        game_copy = copy.deepcopy(self)
        game_copy.simulation_mode = True # Ensure silent operations

        card_id_to_play = move_details['card_id']
        location_to_play = move_details['location_index']

        played_card_instance = game_copy.player.play_card(card_id_to_play, simulation_mode=game_copy.simulation_mode)

        if not played_card_instance:
            return [] # No score if play failed

        game_copy.locations[location_to_play].append(played_card_instance)

        if hasattr(played_card_instance, 'ability_function') and callable(played_card_instance.ability_function):
            game_copy.resolution_queue.append((played_card_instance.ability_function, played_card_instance))

        game_copy.process_resolution_queue()
        game_copy.play_history.append(played_card_instance)

        if hasattr(game_copy, 'calculate_location_power'):
             final_powers_tuple = tuple(game_copy.calculate_location_power(i, game_copy.locations) for i in range(len(game_copy.locations)))
        else:
            final_powers_tuple = tuple(sum(c.power for c in loc) for loc in game_copy.locations)

        eval_score = self._calculate_evaluation_score(final_powers_tuple, opponent_powers_for_eval)
        return [eval_score] # Return a list containing the single score

    def calculate_location_power(self, location_index: int, all_locations_cards: list) -> int:
        """
        Calculates the total power of cards in a specific location.
        Includes dynamic power calculation for Gorr.
        'all_locations_cards' is the full list of lists of cards, e.g., self.locations or a copy.
        """
        if not (0 <= location_index < len(all_locations_cards)):
            # print(f"CALC_POWER_ERROR: Invalid location_index {location_index}")
            return 0

        current_location_cards = all_locations_cards[location_index]
        total_power = 0

        # Check for Gorr and calculate his power first if he's in this location
        gorr_present_in_location = None
        for card_instance in current_location_cards:
            if card_instance.name == "Gorr":
                gorr_present_in_location = card_instance
                break # Found Gorr

        gorr_dynamic_power = 0
        if gorr_present_in_location:
            on_reveal_count = 0
            for loc_list in all_locations_cards: # Iterate through all cards in all locations
                for card_in_any_loc in loc_list:
                    # Accessing is_on_reveal attribute which should be set from deck_database
                    if hasattr(card_in_any_loc, 'is_on_reveal') and card_in_any_loc.is_on_reveal:
                        # Gorr should not count himself if he were mistakenly tagged as on_reveal
                        if card_in_any_loc.name != "Gorr": # Make sure Gorr doesn't count himself
                             on_reveal_count += 1

            gorr_dynamic_power = -1 + (2 * on_reveal_count) # Gorr's base power is -1
            # print(f"GORR_DEBUG: Gorr found. On-reveal count: {on_reveal_count}. Gorr dynamic power: {gorr_dynamic_power}")

        # Sum powers of cards in the current location
        for card_instance in current_location_cards:
            if card_instance.name == "Gorr":
                total_power += gorr_dynamic_power
            else:
                total_power += card_instance.power

        return total_power

    def _calculate_evaluation_score(self, player_final_powers: Tuple[int, int, int], opponent_powers: List[int]) -> int:
        """
        Calculates the evaluation score based on the 'Victory Margin'.
        Score = sum(player_power[i] - opponent_power[i]) for the three locations.
        """
        if len(player_final_powers) != 3:
            # print(f"EVAL_SCORE_ERROR: player_final_powers length is {len(player_final_powers)}, expected 3.")
            return -999
        if len(opponent_powers) != 3:
            # print(f"EVAL_SCORE_ERROR: opponent_powers length is {len(opponent_powers)}, expected 3.")
            return -999

        victory_margin_score = 0
        for i in range(3): # Iterate through the three locations
            victory_margin_score += (player_final_powers[i] - opponent_powers[i])

        return victory_margin_score
