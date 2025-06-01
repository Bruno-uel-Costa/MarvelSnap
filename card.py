# Arquivo: card.py
from abilities import ability_placeholder
from typing import Callable # Certifique-se que Callable também está importado, se já não estiver

class Card:
    """
    Representa uma única carta no jogo, com todos os seus atributos estáticos.
    """
    # Imports foram movidos para o topo do arquivo.

    def __init__(self, id: int, name: str, cost: int, power: int, ability_text: str, is_complex_rng: bool = False, is_on_reveal: bool = False): # Added is_complex_rng and is_on_reveal
        """
        Inicializa uma nova instância de Carta.
        """
        self.id = id
        self.name = name
        self.cost = cost
        self.power = power
        self.ability_text = ability_text
        self.ability_function: Callable = ability_placeholder # Default, can be overridden by factory
        self.is_complex_rng = is_complex_rng
        self.is_on_reveal = is_on_reveal # Added for future step (Gorr)

    def __repr__(self) -> str:
        """
        Fornece uma representação textual clara do objeto Card, útil para depuração.
        Ex: Card(Blade, C:1, P:3)
        """
        return f"Card({self.name}, C:{self.cost}, P:{self.power})"
