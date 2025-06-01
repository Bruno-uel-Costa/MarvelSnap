# Arquivo: player.py
import random
from typing import List, Optional
from card import Card
from deck_factory import create_full_deck

class Player:
    """
    Representa o jogador, gerenciando seu baralho, mão, descarte e energia.
    """
    def __init__(self):
        self.deck: List[Card] = create_full_deck()
        random.shuffle(self.deck)  # O baralho começa embaralhado

        self.hand: List[Card] = []
        self.discard_pile: List[Card] = []

        self.energy_max: int = 0
        self.energy_current: int = 0

    def draw_cards(self, num_to_draw: int = 1):
        """
        Compra um número específico de cartas do topo do baralho para a mão.
        """
        for _ in range(num_to_draw):
            if self.deck:  # Verifica se o baralho não está vazio
                drawn_card = self.deck.pop(0) # Pega a primeira carta (topo do baralho)
                self.hand.append(drawn_card)

    def __repr__(self) -> str:
        """
        Representação textual do estado do jogador.
        """
        return (f"Mão ({len(self.hand)}): {self.hand}\n"
                f"Baralho ({len(self.deck)}): {len(self.deck)} cartas restantes\n"
                f"Descarte ({len(self.discard_pile)}): {self.discard_pile}")
