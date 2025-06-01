# Arquivo: deck_factory.py
from card import Card
from deck_database import DECK_COMPOSITION
from typing import List
# Importe as novas funções
from abilities import (
    ability_placeholder,
    ability_blade,
    ability_corvus_glaive,
    ability_jubilee,
    ability_ghost_rider,
    ability_gambit,  # Add this
    ability_hela,    # Add this
    ability_odin,    # Add this
    ability_blink,   # Added Blink's ability
    ability_infinity_ultron # Added Infinity Ultron's ability
)

# Mapeamento de nomes de cartas para suas funções de habilidade
ABILITY_MAPPING = {
    "Blade": ability_blade,
    "Corvus Glaive": ability_corvus_glaive,
    "Jubilee": ability_jubilee,
    "Ghost Rider": ability_ghost_rider,
    "Gambit": ability_gambit,  # Add this
    "Hela": ability_hela,      # Add this
    "Odin": ability_odin,      # Add this
    "Blink": ability_blink,    # Added Blink to mapping
    "Infinity Ultron": ability_infinity_ultron, # Added Infinity Ultron mapping
    "Gorr": ability_placeholder, # Explicitly mapped Gorr
    # Outras cartas como Legion, The Infinaut
    # continuarão usando ability_placeholder por enquanto.
}

def create_full_deck() -> List[Card]: # Ensure List is imported from typing
    card_list = []
    for card_data in DECK_COMPOSITION:
        card = Card(**card_data)
        # Atribui a função de habilidade correta com base no nome
        card.ability_function = ABILITY_MAPPING.get(card.name, ability_placeholder)
        card_list.append(card)
    return card_list
