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
        self.resolution_queue = []
        self.simulation_mode = False
        self.play_history: List['Card'] = [] # Histórico de cartas jogadas

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
                # print(f"ANALYZE_INFO: Using ANALYTICAL path for card {card_to_check.name} (ID: {move['card_id']}).")
                analytical_results = self.calculate_analytical_outcome(move)

                move_specific_outcomes_list = []
                for analytical_res_item in analytical_results:
                    if analytical_res_item['probability'] == 1.0:
                        move_specific_outcomes_list.append(analytical_res_item['outcome'])

                if move_specific_outcomes_list:
                    all_outcomes_data.append({
                        'move': move,
                        'outcomes': move_specific_outcomes_list,
                        'is_analytical': True,
                        'num_iterations_equivalent': 1
                    })

            else:
                # --- Monte Carlo Path (existing logic) ---
                # print(f"ANALYZE_INFO: Using MONTE CARLO path for card {card_to_check.name} (ID: {move['card_id']}).")
                current_move_monte_carlo_outcomes = []
                for _ in range(num_iterations):
                    game_copy = copy.deepcopy(self)
                    game_copy.simulation_mode = True # Ensure simulation mode for all operations on game_copy

                    # Pass the simulation_mode to play_card
                    played_card_instance_copy = game_copy.player.play_card(move['card_id'], simulation_mode=game_copy.simulation_mode)

                    if played_card_instance_copy:
                        game_copy.locations[move['location_index']].append(played_card_instance_copy)
                        if hasattr(played_card_instance_copy, 'ability_function') and callable(played_card_instance_copy.ability_function):
                            game_copy.resolution_queue.append((played_card_instance_copy.ability_function, played_card_instance_copy))

                        game_copy.process_resolution_queue()
                        game_copy.play_history.append(played_card_instance_copy)
                    else:
                        pass

                    if hasattr(game_copy, 'calculate_location_power'):
                        final_powers_tuple = tuple(game_copy.calculate_location_power(i, game_copy.locations) for i in range(len(game_copy.locations)))
                    else:
                        final_powers_tuple = tuple(sum(c.power for c in loc) for loc in game_copy.locations)
                    current_move_monte_carlo_outcomes.append(final_powers_tuple)

                if current_move_monte_carlo_outcomes:
                    all_outcomes_data.append({
                        'move': move,
                        'outcomes': current_move_monte_carlo_outcomes,
                        'is_analytical': False,
                        'num_iterations_equivalent': num_iterations
                    })

        # --- Aggregation Logic (handles mixed analytical/Monte Carlo inputs) ---
        final_results = {}

        for result_group in all_outcomes_data:
            move_card_name = result_group['move'].get('card_name', f"ID:{result_group['move']['card_id']}")
            move_str = f"Jogar {move_card_name} no L{result_group['move']['location_index']}"

            num_trials_for_this_move = len(result_group['outcomes'])

            if num_trials_for_this_move == 0: continue

            outcome_counts = Counter(result_group['outcomes'])

            for outcome, count in outcome_counts.items():
                if outcome not in final_results:
                    final_results[outcome] = {'probability': 0, 'actions': set()}

                prob_from_this_move = count / num_trials_for_this_move

                final_results[outcome]['probability'] += prob_from_this_move / len(possible_moves)
                final_results[outcome]['actions'].add(move_str)

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

    def calculate_analytical_outcome(self, move_details: dict) -> list:
        """
        Calculates the deterministic outcome of a simple move.
        move_details is expected to be like {'card_id': card_id, 'location_index': loc_idx, 'card_name': name}
        Returns a list containing a single outcome dictionary: [{'outcome': (L0,L1,L2), 'probability': 1.0}]
        """
        game_copy = copy.deepcopy(self)
        # Ensure the copy also operates in simulation mode if the original was, or set explicitly if needed.
        # For analytical outcomes triggered from analyze_next_turn_outcomes, self (original game) IS NOT in simulation_mode.
        # The game_copy made here should be for this specific analytical path, so its prints should be silenced.
        game_copy.simulation_mode = True


        card_id_to_play = move_details['card_id']
        location_to_play = move_details['location_index']

        # Execute the play on the copy
        # Player.play_card handles energy, hand removal, and returns the card instance
        played_card_instance = game_copy.player.play_card(card_id_to_play, simulation_mode=game_copy.simulation_mode)

        if not played_card_instance:
            # This should ideally not happen if possible_moves filters correctly.
            # This move path leads to no valid board change.
            # The calling function `analyze_next_turn_outcomes` will need to handle or filter out empty results.
            # print(f"ANALYTICAL_ERROR: Card ID {card_id_to_play} could not be played from hand in analytical calculation.")
            return []


        # Add card to location
        game_copy.locations[location_to_play].append(played_card_instance)

        # Add its ability to the resolution queue and process it
        if hasattr(played_card_instance, 'ability_function') and callable(played_card_instance.ability_function):
            game_copy.resolution_queue.append((played_card_instance.ability_function, played_card_instance))

        game_copy.process_resolution_queue() # Process deterministic abilities

        # Add to play_history
        game_copy.play_history.append(played_card_instance)


        # Calculate final powers
        # Using calculate_location_power
        if hasattr(game_copy, 'calculate_location_power'):
             final_powers_tuple = tuple(game_copy.calculate_location_power(i, game_copy.locations) for i in range(len(game_copy.locations)))
        else:
            # Fallback to simple sum if calculate_location_power is not yet implemented
            # print("ANALYTICAL_NOTE: Using simple power sum as calculate_location_power is not yet implemented.")
            final_powers_tuple = tuple(sum(c.power for c in loc) for loc in game_copy.locations)


        return [{'outcome': final_powers_tuple, 'probability': 1.0}]

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
