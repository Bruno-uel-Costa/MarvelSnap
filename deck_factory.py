# Arquivo: deck_factory.py
from card import Card
from deck_database import DECK_COMPOSITION, ULTRON_STONES # Added ULTRON_STONES import
from typing import List
# Importe as novas funções
from abilities import (
    ability_placeholder,
    ability_blade,
    ability_corvus_glaive,
    ability_jubilee,
    ability_ghost_rider,
    ability_gambit,
    ability_hela,
    ability_odin,
    ability_blink,
    ability_infinity_ultron,
    ability_legion # Added Legion's ability
)

# Mapeamento de nomes de cartas para suas funções de habilidade
ABILITY_MAPPING = {
    "Blade": ability_blade,
    "Corvus Glaive": ability_corvus_glaive,
    "Jubilee": ability_jubilee,
    "Ghost Rider": ability_ghost_rider,
    "Gambit": ability_gambit,
    "Hela": ability_hela,
    "Odin": ability_odin,
    "Blink": ability_blink,
    "Infinity Ultron": ability_infinity_ultron,
    "Gorr": ability_placeholder,
    "Legion": ability_legion, # Added Legion to mapping
    # Stones will default to ability_placeholder if not explicitly in ABILITY_MAPPING
    # Outras cartas como The Infinaut
    # continuarão usando ability_placeholder por enquanto.
}

# Store all prepared card objects in a lookup dictionary
PREPARED_CARDS_BY_ID = None

def get_prepared_card_definitions():
    global PREPARED_CARDS_BY_ID
    if PREPARED_CARDS_BY_ID is None:
        PREPARED_CARDS_BY_ID = {}
        # Main deck
        for card_data_dict in DECK_COMPOSITION:
            card_copy = card_data_dict.copy()
            card_name = card_copy['name']
            ability_func = ABILITY_MAPPING.get(card_name, ability_placeholder)
            card_copy['ability_function_obj'] = ability_func
            PREPARED_CARDS_BY_ID[card_copy['id']] = card_copy
        # Ultron Stones
        for stone_data_dict in ULTRON_STONES:
            stone_copy = stone_data_dict.copy()
            stone_name = stone_copy['name']
            ability_func = ABILITY_MAPPING.get(stone_name, ability_placeholder)
            stone_copy['ability_function_obj'] = ability_func
            PREPARED_CARDS_BY_ID[stone_copy['id']] = stone_copy

    return PREPARED_CARDS_BY_ID

# Call it once at module load to populate
get_prepared_card_definitions()

def create_card_from_prepared_data(card_id: int) -> Card:
    if PREPARED_CARDS_BY_ID is None:
        get_prepared_card_definitions() # Should already be populated by module load

    raw_data = PREPARED_CARDS_BY_ID.get(card_id) # Use .get() for safety
    if raw_data:
        card_obj = Card(
            id=raw_data['id'],
            name=raw_data['name'],
            cost=raw_data['cost'],
            power=raw_data['power'],
            ability_text=raw_data['ability_text'],
            is_complex_rng=raw_data.get('is_complex_rng', False),
            is_on_reveal=raw_data.get('is_on_reveal', False)
        )
        card_obj.ability_function = raw_data['ability_function_obj']
        return card_obj
    return None

def create_full_deck() -> List[Card]:
    card_list = []
    # Ensure definitions are loaded (should be by module import, but as a safeguard)
    if PREPARED_CARDS_BY_ID is None:
        get_prepared_card_definitions()

    for card_data_original in DECK_COMPOSITION: # Iterate over original DECK_COMPOSITION to get IDs for main deck
        card_id = card_data_original['id']
        card_instance = create_card_from_prepared_data(card_id)
        if card_instance:
            card_list.append(card_instance)
    return card_list
