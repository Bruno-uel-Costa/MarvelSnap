# Arquivo: card.py

class Card:
    """
    Representa uma única carta no jogo, com todos os seus atributos estáticos.
    """
    # Adicionado para compatibilidade com type hinting e abilities.py
    from typing import Callable
    from abilities import ability_placeholder # Importa um placeholder para habilidade

    def __init__(self, id: int, name: str, cost: int, power: int, ability_text: str, ability_function: Callable = ability_placeholder):
        """
        Inicializa uma nova instância de Carta.

        Args:
            id (int): Um identificador único para a carta (de 1 a 12).
            name (str): O nome da carta (ex: "Blade").
            cost (int): O custo de energia da carta.
            power (int): O poder base da carta.
            ability_text (str): A descrição completa da habilidade da carta.
            ability_function (Callable): A função que implementa a habilidade da carta.
        """
        self.id = id
        self.name = name
        self.cost = cost
        self.power = power
        self.ability_text = ability_text
        self.ability_function = ability_function # Adicionado para armazenar a função da habilidade

    def __repr__(self) -> str:
        """
        Fornece uma representação textual clara do objeto Card, útil para depuração.
        Ex: Card(Blade, C:1, P:3)
        """
        return f"Card({self.name}, C:{self.cost}, P:{self.power})"
