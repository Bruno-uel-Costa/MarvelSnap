# app.py

from flask import Flask, request, jsonify
import sys
import os

# Assuming app.py is in the root, and other game logic is also in root.
# If modules are in a sub-folder, sys.path adjustments might be needed, e.g.:
# sys.path.append(os.path.join(os.path.dirname(__file__), 'your_subfolder_name'))

from card import Card
from deck_database import DECK_COMPOSITION, ULTRON_STONES
from game_state import GameState
from player import Player
# deck_factory is needed for ABILITY_MAPPING in create_card_instance_from_id
from deck_factory import ABILITY_MAPPING, ability_placeholder

app = Flask(__name__)

# Combine DECK_COMPOSITION and ULTRON_STONES for a full card lookup
ALL_CARDS_RAW_DATA = DECK_COMPOSITION + ULTRON_STONES
ALL_CARDS_LOOKUP_BY_ID = {card_data['id']: card_data for card_data in ALL_CARDS_RAW_DATA}

def create_card_instance_from_id(card_id):
    if card_id in ALL_CARDS_LOOKUP_BY_ID:
        card_data = ALL_CARDS_LOOKUP_BY_ID[card_id]

        card_obj = Card(
            id=card_data['id'],
            name=card_data['name'],
            cost=card_data['cost'],
            power=card_data['power'],
            ability_text=card_data['ability_text'],
            is_complex_rng=card_data.get('is_complex_rng', False),
            is_on_reveal=card_data.get('is_on_reveal', False)
        )
        # Assign the correct ability function after instantiation
        card_obj.ability_function = ABILITY_MAPPING.get(card_obj.name, ability_placeholder)
        return card_obj
    return None


@app.route('/analyze', methods=['POST'])
def analyze_game_state():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        hand_ids = data.get('hand_ids', [])
        discard_ids = data.get('discard_ids', [])
        location1_ids = data.get('location1_ids', [])
        location2_ids = data.get('location2_ids', [])
        location3_ids = data.get('location3_ids', [])

        current_energy = data.get('current_energy')
        max_energy = data.get('max_energy')
        current_turn = data.get('current_turn')
        # Optional: play_history_ids for cards like Blink, though this might be complex to manage from UI
        # play_history_ids = data.get('play_history_ids', [])

        if current_energy is None or max_energy is None or current_turn is None:
            return jsonify({"error": "Missing energy or turn information"}), 400

        game = GameState()

        game.player.hand = [create_card_instance_from_id(id) for id in hand_ids if create_card_instance_from_id(id) is not None]
        game.player.discard_pile = [create_card_instance_from_id(id) for id in discard_ids if create_card_instance_from_id(id) is not None]

        game.locations[0] = [create_card_instance_from_id(id) for id in location1_ids if create_card_instance_from_id(id) is not None]
        game.locations[1] = [create_card_instance_from_id(id) for id in location2_ids if create_card_instance_from_id(id) is not None]
        game.locations[2] = [create_card_instance_from_id(id) for id in location3_ids if create_card_instance_from_id(id) is not None]

        game.player.energy_current = int(current_energy)
        game.player.energy_max = int(max_energy)
        game.turn = int(current_turn)

        # game.play_history = [create_card_instance_from_id(id) for id in play_history_ids if create_card_instance_from_id(id) is not None]

        all_known_card_ids = set(hand_ids + discard_ids + location1_ids + location2_ids + location3_ids)
        # Filter the default deck to remove known cards. This is a simplification.
        # A more robust system would have the UI send the exact deck contents or manage deck creation differently.
        initial_deck_ids = [card.id for card in game.player.deck] # Get IDs from default shuffled deck
        unique_deck_ids_after_removal = [id for id in initial_deck_ids if id not in all_known_card_ids]

        # To preserve the original deck's shuffle order as much as possible while removing known cards:
        temp_deck = []
        seen_ids_in_new_deck = set()
        for card in game.player.deck: # Iterate through the original shuffled deck
            if card.id not in all_known_card_ids and card.id not in seen_ids_in_new_deck:
                temp_deck.append(card)
                seen_ids_in_new_deck.add(card.id)
        game.player.deck = temp_deck

        top_outcomes = game.analyze_next_turn_outcomes()

        return jsonify(top_outcomes)

    except Exception as e:
        print(f"Error in /analyze: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) # debug=False for production/testing without auto-reload issues
