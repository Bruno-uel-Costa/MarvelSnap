# Arquivo: abilities.py

def ability_placeholder(game_state, card):
    """Uma função vazia para cartas sem habilidade ou cuja habilidade não implementamos ainda."""
    pass

def ability_blade(game_state, card):
    """Ao Revelar: Descarta a carta mais à direita da sua mão."""
    hand = game_state.player.hand
    if hand:
        card_to_discard = hand[-1] # A última carta da lista é a mais à direita
        game_state.player.move_card_to_discard(card_to_discard)

# Nota do Maestro: Por enquanto, implementaremos apenas a do Blade.
# As outras podem usar o 'placeholder'.
