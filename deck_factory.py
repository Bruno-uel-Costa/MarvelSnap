# Arquivo: deck_factory.py
from card import Card
from deck_database import DECK_COMPOSITION
from typing import List

def create_full_deck() -> List[Card]:
    """
    Cria uma lista completa de objetos Card com base na composição do baralho.

    Returns:
        List[Card]: Uma lista contendo 12 instâncias de objetos Card.
    """
    return [Card(**card_data) for card_data in DECK_COMPOSITION]
