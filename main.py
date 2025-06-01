# Arquivo: main.py
from deck_factory import create_full_deck

if __name__ == "__main__":
    print("--- Verificando a montagem do baralho ---")

    # Cria o baralho
    my_deck = create_full_deck()

    # Verifica se temos 12 cartas
    print(f"Total de cartas no baralho: {len(my_deck)}")

    # Imprime cada carta para verificação visual
    print("\nLista de Cartas no Baralho:")
    for card in my_deck:
        print(f"- ID: {card.id}, {card}") # Usando o __repr__ que definimos
