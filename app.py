# app.py
from flask import Flask, request, jsonify # Ensure 'request' is imported
from flask_cors import CORS # Add this line
import sys
import os

# Assuming game logic modules are accessible
# If your project structure is different (e.g., game logic in a sub-folder like 'game/'), adjust path.
# sys.path.append(os.path.join(os.path.dirname(__file__), 'your_game_logic_subfolder'))

from card import Card # For type checking if needed, though instances come from factory
from game_state import GameState
# Import the utility from deck_factory to create card instances correctly
from deck_factory import create_card_from_prepared_data, PREPARED_CARDS_BY_ID, get_prepared_card_definitions

app = Flask(__name__)
CORS(app) # Add this line to enable CORS for all routes and origins by default

# Ensure card definitions are loaded when app starts, if not already by deck_factory module import
if PREPARED_CARDS_BY_ID is None:
    get_prepared_card_definitions()


@app.route('/api/start_game', methods=['GET'])
def start_new_game():
    try:
        game = GameState()
        game.start_game()

        response_data = {
            "turn": game.turn,
            "current_energy": game.player.energy_current,
            "max_energy": game.player.energy_max,
            "hand_ids": [card.id for card in game.player.hand],
            "deck_ids": [card.id for card in game.player.deck],
            "deck_size": len(game.player.deck),
            "discard_ids": [card.id for card in game.player.discard_pile],
            "locations": [
                [card.id for card in loc] for loc in game.locations
            ],
            "play_history_ids": [card.id for card in game.play_history]
        }
        return jsonify(response_data), 200
    except Exception as e:
        # print(f"Error in /api/start_game: {e}") # Server-side log
        import traceback
        traceback.print_exc() # Server-side log
        return jsonify({"error": "An internal server error occurred during game start", "details": str(e)}), 500


@app.route('/api/execute_actions_and_analyze', methods=['POST'])
def execute_actions_and_analyze_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        current_game_state_dict = data.get('current_game_state')
        player_actions = data.get('player_actions', [])
        resolved_random_outcomes = data.get('resolved_random_outcomes', [])
        opponent_powers = data.get('opponent_powers', [0, 0, 0]) # Added opponent_powers extraction

        if not current_game_state_dict:
            return jsonify({"error": "Missing current_game_state"}), 400

        game = GameState(initial_state_dict=current_game_state_dict)
        # Server-side logging (optional)
        # print(f"EXEC_ACTIONS: Rehydrated GameState: Turn {game.turn}, Energy {game.player.energy_current}")
        # print(f"EXEC_ACTIONS: Hand: {[c.name for c in game.player.hand if c]}, Deck: {len(game.player.deck)} cards")
        # print(f"EXEC_ACTIONS: Actions: {player_actions}, Resolved RNG: {resolved_random_outcomes}")

        for action in player_actions:
            if action.get('type') == 'PLAY_CARD':
                card_id_to_play = action.get('card_id')
                location_idx_to_play = action.get('location_index')

                if card_id_to_play is None or location_idx_to_play is None:
                    # print(f"EXEC_ACTIONS_WARN: Invalid play action format: {action}")
                    continue

                # Player.play_card defaults simulation_mode=False, so server logs from it are possible
                played_card_instance = game.player.play_card(card_id_to_play)

                if played_card_instance:
                    if 0 <= location_idx_to_play < len(game.locations):
                        game.locations[location_idx_to_play].append(played_card_instance)
                        if hasattr(played_card_instance, 'ability_function') and callable(played_card_instance.ability_function):
                            game.resolution_queue.append((played_card_instance.ability_function, played_card_instance))
                        game.play_history.append(played_card_instance)
                        # print(f"EXEC_ACTIONS_INFO: Played {played_card_instance.name} to loc {location_idx_to_play}")
                    # else:
                        # print(f"EXEC_ACTIONS_ERROR: Invalid location index {location_idx_to_play} for card {played_card_instance.name}")
                        # This case should ideally be prevented by frontend or result in a client error.
                        # If it occurs, the card is consumed from hand but not placed, an inconsistent state.
                        pass # Assuming valid inputs for now post rehydration.
                # else:
                    # print(f"EXEC_ACTIONS_INFO: Play card ID {card_id_to_play} failed (player.play_card handles its own logging).")
                    pass

        game.process_resolution_queue(resolved_outcomes_for_turn=resolved_random_outcomes)

        game_state_after_actions_dict = {
            "turn": game.turn,
            "current_energy": game.player.energy_current,
            "max_energy": game.player.energy_max,
            "hand_ids": [card.id for card in game.player.hand],
            "deck_ids": [card.id for card in game.player.deck],
            "deck_size": len(game.player.deck),
            "discard_ids": [card.id for card in game.player.discard_pile],
            "locations": [[card.id for card in loc] for loc in game.locations],
            "play_history_ids": [card.id for card in game.play_history]
        }

        next_turn_analysis_results = game.analyze_next_turn_outcomes(opponent_powers=opponent_powers) # Pass opponent_powers

        return jsonify({
            "game_state_after_actions": game_state_after_actions_dict,
            "next_turn_analysis": { "top_10_outcomes": next_turn_analysis_results } # Modified line
        }), 200

    except Exception as e:
        # print(f"Error in /api/execute_actions_and_analyze: {e}") # Server-side log
        import traceback
        traceback.print_exc() # Server-side log
        return jsonify({"error": "An internal server error occurred during action execution/analysis", "details": str(e)}), 500


@app.route('/api/advance_turn_and_analyze', methods=['POST'])
def advance_turn_and_analyze_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        current_game_state_dict = data.get('current_game_state_at_turn_end') # Modified key
        opponent_powers = data.get('opponent_powers', [0, 0, 0]) # Added opponent_powers extraction
        if not current_game_state_dict:
            return jsonify({"error": "Missing current_game_state_at_turn_end"}), 400

        # 1. Rehydrate GameState from current_game_state_dict
        game = GameState(initial_state_dict=current_game_state_dict)
        # print(f"DEBUG advance_turn: Rehydrated GameState: Turn {game.turn}, Energy {game.player.energy_current}")

        # 2. Call GameState.advance_to_next_turn()
        game.advance_to_next_turn() # Increments turn, draws card, resets energy
        # print(f"DEBUG advance_turn: Advanced to Turn {game.turn}. New energy: {game.player.energy_current}")


        # Serialize new_turn_game_state (state after advancing)
        new_turn_game_state_dict = {
            "turn": game.turn,
            "current_energy": game.player.energy_current,
            "max_energy": game.player.energy_max,
            "hand_ids": [card.id for card in game.player.hand],
            "deck_ids": [card.id for card in game.player.deck],
            "deck_size": len(game.player.deck),
            "discard_ids": [card.id for card in game.player.discard_pile],
            "locations": [[card.id for card in loc] for loc in game.locations],
            "play_history_ids": [card.id for card in game.play_history]
        }
        # print(f"DEBUG advance_turn: New turn game state: {new_turn_game_state_dict}")


        # 3. Call analyze_next_turn_outcomes() for this new turn.
        # print(f"DEBUG advance_turn: Calling analyze_next_turn_outcomes for newly advanced Turn {game.turn}")
        current_turn_analysis_results = game.analyze_next_turn_outcomes(opponent_powers=opponent_powers) # Pass opponent_powers
        # print(f"DEBUG advance_turn: Analysis for current new turn: {current_turn_analysis_results}")


        return jsonify({
            "new_turn_game_state": new_turn_game_state_dict,
            "current_turn_analysis": current_turn_analysis_results
        }), 200

    except Exception as e:
        # print(f"Error in /api/advance_turn_and_analyze: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred during turn advancement/analysis", "details": str(e)}), 500


@app.route('/api/get_next_turn_analysis', methods=['POST'])
def get_next_turn_analysis_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        current_game_state_dict = data.get('current_game_state')
        opponent_powers = data.get('opponent_powers', [0, 0, 0]) # Added opponent_powers extraction
        if not current_game_state_dict:
            return jsonify({"error": "Missing current_game_state"}), 400

        # Rehydrate GameState
        game = GameState(initial_state_dict=current_game_state_dict)
        # print(f"DEBUG get_next_turn_analysis: Rehydrated GameState: Turn {game.turn}, Energy {game.player.energy_current}")

        # Call analyze_next_turn_outcomes()
        analysis_results = game.analyze_next_turn_outcomes(opponent_powers=opponent_powers) # Pass opponent_powers
        # print(f"DEBUG get_next_turn_analysis: Analysis results: {analysis_results}")

        return jsonify({
            "top_10_outcomes": analysis_results
        }), 200

    except Exception as e:
        # print(f"Error in /api/get_next_turn_analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred during analysis", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
