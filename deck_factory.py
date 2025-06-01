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
    ability_ghost_rider
) # Modify this import block

# Mapeamento de nomes de cartas para suas funções de habilidade
ABILITY_MAPPING = {
    "Blade": ability_blade,
    "Corvus Glaive": ability_corvus_glaive, # Add this
    "Jubilee": ability_jubilee,           # Add this
    "Ghost Rider": ability_ghost_rider,   # Add this
    # As outras cartas continuarão usando o placeholder por enquanto
}

def create_full_deck() -> List[Card]: # Ensure List is imported from typing
    card_list = []
    for card_data in DECK_COMPOSITION:
        card = Card(**card_data)
        # Atribui a função de habilidade correta com base no nome
        card.ability_function = ABILITY_MAPPING.get(card.name, ability_placeholder)
        card_list.append(card)
    return card_list
