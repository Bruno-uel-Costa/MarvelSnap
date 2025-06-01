# Arquivo: deck_factory.py
from card import Card
from deck_database import DECK_COMPOSITION
from typing import List
from abilities import ability_placeholder, ability_blade # Add this line

# Mapeamento de nomes de cartas para suas funções de habilidade
ABILITY_MAPPING = {
    "Blade": ability_blade,
    # Adicionaremos outras cartas aqui no futuro
}

def create_full_deck() -> List[Card]: # Ensure List is imported from typing
    card_list = []
    for card_data in DECK_COMPOSITION:
        card = Card(**card_data)
        # Atribui a função de habilidade correta com base no nome
        card.ability_function = ABILITY_MAPPING.get(card.name, ability_placeholder)
        card_list.append(card)
    return card_list
