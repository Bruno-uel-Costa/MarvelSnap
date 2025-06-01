# Arquivo: main.py
from game_state import GameState

if __name__ == "__main__":
    # Cria uma nova instância do jogo
    game = GameState()

    # Inicia o jogo
    game.start_game()

    # Avança para o turno 3
    game.advance_to_next_turn()
    game.advance_to_next_turn()
    print("--- ESTADO ANTES DA JOGADA (TURNO 3) ---")
    print(game)

    # Nota do Maestro: No seu teste anterior, a carta 'Blade' (ID: 1)
    # estava na mão no turno 3. Vamos simular jogá-la.
    # Se a carta não estiver na mão devido à aleatoriedade,
    # o teste de erro de 'carta não encontrada' será ativado.

    # Modificação: Encontrar uma carta jogável na mão
    playable_card_found = False
    card_to_play_id = -1
    if game.player.hand: # Verificar se a mão não está vazia
        for card_in_hand in game.player.hand:
            if game.player.energy_current >= card_in_hand.cost:
                card_to_play_id = card_in_hand.id
                playable_card_found = True
                break

    if playable_card_found:
        print(f"\n--- TENTANDO JOGAR CARTA (ID {card_to_play_id}) NO LOCAL 0 ---")
        game.play_card(card_id=card_to_play_id, location_index=0)
    else:
        print("\n--- NENHUMA CARTA JOGÁVEL ENCONTRADA NA MÃO COM A ENERGIA ATUAL ---")

    print("\n--- ESTADO APÓS A TENTATIVA DE JOGADA ---")
    print(game)
