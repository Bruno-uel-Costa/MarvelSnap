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

    def find_card_in_hand(self, card_id: int) -> Optional[Card]:
        """Encontra uma carta na mão pelo seu ID."""
        for card in self.hand:
            if card.id == card_id:
                return card
        return None

    def play_card(self, card_id: int, simulation_mode: bool = False) -> Optional[Card]:
        """
        Tenta jogar uma carta da mão. Verifica se há energia suficiente.
        Se for bem-sucedido, remove a carta da mão e retorna o objeto Card.
        """
        card_to_play = self.find_card_in_hand(card_id)
        if not card_to_play:
            if not simulation_mode: # Check the passed parameter
                print(f"ERRO: Carta com ID {card_id} não encontrada na mão.")
            return None

        if self.energy_current >= card_to_play.cost:
            self.energy_current -= card_to_play.cost
            self.hand.remove(card_to_play)
            if not simulation_mode: # Check the passed parameter
                print(f"JOGADA: {card_to_play.name} jogado(a).")
            return card_to_play
        else:
            if not simulation_mode: # Check the passed parameter
                print(f"ERRO: Energia insuficiente para jogar {card_to_play.name}. Requer {card_to_play.cost}, disponível {self.energy_current}.")
            return None

    def move_card_to_discard(self, card_to_discard: Card, simulation_mode: bool = False):
        """
        Move uma carta específica da mão para a pilha de descarte.
        """
        if card_to_discard in self.hand:
            self.hand.remove(card_to_discard)
            self.discard_pile.append(card_to_discard)
            if not simulation_mode:
                print(f"DESCARTE: {card_to_discard.name} movido(a) para o descarte.")
        else:
            if not simulation_mode:
                print(f"AVISO: Tentativa de descartar {card_to_discard.name}, que não está na mão.")
