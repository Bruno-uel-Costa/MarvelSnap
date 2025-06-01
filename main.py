# Arquivo: main.py
from game_state import GameState

if __name__ == "__main__":
    # Cria uma nova instância do jogo
    game = GameState()

    # Inicia o jogo
    game.start_game()
    print(game)

    # Avança para o turno 2
    game.advance_to_next_turn()
    print(game)

    # Avança para o turno 3
    game.advance_to_next_turn()
    print(game)
