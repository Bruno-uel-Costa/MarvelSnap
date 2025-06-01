# Arquivo: main.py
from game_state import GameState
# Assuming Card and other necessary classes are indirectly imported via GameState if needed
# or directly if main.py manipulates cards for setup (which it doesn't here).

if __name__ == "__main__":
    # Configura um cenário de teste específico
    game = GameState()
    game.start_game() # Initializes deck, player draws 3, turn 1, 1 energy

    # Advance to Turn 2
    # advance_to_next_turn increments turn, player draws 1, energy_max = turn, energy_current = energy_max
    game.advance_to_next_turn() # Turn 2, player has 4 cards, 2 energy

    # Advance to Turn 3
    game.advance_to_next_turn() # Turn 3, player has 5 cards, 3 energy

    # Advance to Turn 4 for more energy and playable options
    print("\n--- Avançando para o Turno 4 ---")
    game.advance_to_next_turn() # Turn 4, player has 6 cards (usually), 4 energy

    # Vamos forçar a mão para ter uma jogada interessante
    # (Jules, você pode ajustar isso para testar diferentes cenários)
    # For this test, we'll rely on the random draw.
    # If specific cards are needed in hand for a targeted test,
    # one might need to temporarily modify Player __init__ or add a debug method
    # to set hand, e.g., game.player.hand = [Card(id=1, ...), Card(id=4, ...)]
    # For now, we proceed with the drawn hand.

    print("--- Estado Inicial para Análise (Turno 4) ---")
    print(game) # This will print game state including hand, energy, etc.

    print("\n--- Analisando Outcomes do Próximo Turno... ---")
    # Using default num_iterations=1000, can be overridden: game.analyze_next_turn_outcomes(num_iterations=500)
    top_outcomes = game.analyze_next_turn_outcomes()

    print("\n--- Top 10 Resultados Mais Prováveis ---")
    if not top_outcomes:
        print("Nenhuma jogada possível ou nenhum resultado consistente encontrado.")
    else:
        for i, result in enumerate(top_outcomes):
            prob_percent = result['prob'] * 100
            # outcome is a tuple of powers (L0, L1, L2)
            outcome_powers = result['outcome']
            action = result['action'] # The example action string
            print(f"{i+1}. Prob: {prob_percent:.2f}% | Resultado (L0,L1,L2): {outcome_powers} | Via: {action}")
