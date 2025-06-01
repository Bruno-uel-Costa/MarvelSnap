DECK_COMPOSITION = [
    {'id': 1, 'name': 'Blade', 'cost': 1, 'power': 3, 'ability_text': 'On Reveal: Discard the rightmost card from your hand.', 'is_on_reveal': True},
    {'id': 2, 'name': 'Gambit', 'cost': 3, 'power': 3, 'ability_text': 'On Reveal: Discard a card from your hand to destroy a random enemy card.', 'is_on_reveal': True},
    {'id': 3, 'name': 'Corvus Glaive', 'cost': 3, 'power': 5, 'ability_text': 'On Reveal: Discard 2 cards from your hand to get +1 Max Energy.', 'is_on_reveal': True},
    {'id': 4, 'name': 'Jubilee', 'cost': 4, 'power': 1, 'ability_text': 'On Reveal: Add the top card of your deck to this location.', 'is_complex_rng': True, 'is_on_reveal': True},
    {'id': 5, 'name': 'Ghost Rider', 'cost': 4, 'power': 3, 'ability_text': 'On Reveal: Bring back one of your discarded cards to this location.', 'is_complex_rng': True, 'is_on_reveal': True},
    {'id': 6, 'name': 'Blink', 'cost': 5, 'power': 7, 'ability_text': 'On Reveal: Swap the last card you played with a card that costs more from your deck.', 'is_complex_rng': True, 'is_on_reveal': True},
    {'id': 7, 'name': 'Legion', 'cost': 5, 'power': 7, 'ability_text': 'On Reveal: Replace each other location with this one.', 'is_on_reveal': True},
    {'id': 8, 'name': 'Infinity Ultron', 'cost': 5, 'power': 8, 'ability_text': "On Reveal: Add 2 of Ultron’s Stones to your hand.", 'is_complex_rng': True, 'is_on_reveal': True},
    {'id': 9, 'name': 'Gorr', 'cost': 6, 'power': -1, 'ability_text': 'Ongoing: +2 Power for EACH On Reveal card in play.'}, # is_on_reveal is False (it's Ongoing)
    {'id': 10, 'name': 'Hela', 'cost': 6, 'power': 6, 'ability_text': 'On Reveal: For each different Cost among them, resurrect a card you discarded to a random location.', 'is_complex_rng': True, 'is_on_reveal': True},
    {'id': 11, 'name': 'Odin', 'cost': 6, 'power': 8, 'ability_text': 'On Reveal: Repeat the On Reveal abilities of your other cards here.', 'is_complex_rng': True, 'is_on_reveal': True},
    {'id': 12, 'name': 'The Infinaut', 'cost': 6, 'power': 20, 'ability_text': 'If you played a card last turn, you can’t play this.'} # is_on_reveal is False
]
