# Arquivo: abilities.py
import random # Add this line if not present

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

def ability_corvus_glaive(game_state, card):
    """Ao Revelar: Descarta 2 cartas da sua mão para ganhar +1 de Energia Máxima."""
    hand = game_state.player.hand
    if len(hand) >= 2:
        # Escolhe 2 cartas aleatórias e únicas da mão para descartar
        cards_to_discard = random.sample(hand, 2)
        print(f"CORVUS: Descartando {cards_to_discard[0].name} e {cards_to_discard[1].name}")
        # Usa um loop para garantir que as cartas sejam movidas corretamente
        # Need to iterate over a copy if modifying the list (hand) via move_card_to_discard
        # However, move_card_to_discard operates on game_state.player.hand directly.
        # The random.sample already gives us the specific card objects.
        for c_to_discard in cards_to_discard: # Use a different variable name to avoid confusion with 'card' parameter
            game_state.player.move_card_to_discard(c_to_discard)
    elif len(hand) == 1:
        # Se só tiver 1 carta, descarta ela
        card_to_discard_single = hand[0] # Use a different variable name
        print(f"CORVUS: Descartando {card_to_discard_single.name}")
        game_state.player.move_card_to_discard(card_to_discard_single)
    # else: if hand is empty, no discard occurs

    # A rampa de energia acontece independentemente do descarte
    game_state.player.energy_max += 1
    print("CORVUS: +1 de Energia Máxima concedido.")

def ability_jubilee(game_state, card): # 'card' is the instance of Jubilee
    """Ao Revelar: Adiciona a carta do topo do seu baralho a este local."""
    deck = game_state.player.deck
    if deck:
        pulled_card = deck.pop(0) # Get the top card
        print(f"JUBILEE: Puxou {pulled_card.name} do baralho.")

        # Encontra o local onde a Jubilee (the 'card' instance) está
        # This is important to ensure the pulled card goes to the same location as Jubilee.
        location_of_jubilee = None
        for loc_list in game_state.locations:
            if card in loc_list: # 'card' is the Jubilee instance that triggered this ability
                location_of_jubilee = loc_list
                break

        if location_of_jubilee is not None:
            location_of_jubilee.append(pulled_card)
            print(f"JUBILEE: {pulled_card.name} adicionado(a) ao local de Jubilee.")
            # Adiciona a habilidade da carta puxada ao INÍCIO da fila de resolução
            # Ensure the pulled_card has an ability_function attribute
            if hasattr(pulled_card, 'ability_function') and callable(pulled_card.ability_function):
                game_state.resolution_queue.insert(0, (pulled_card.ability_function, pulled_card))
                print(f"JUBILEE: Habilidade de {pulled_card.name} adicionada ao início da fila de resolução.")
            else:
                # This case should ideally not happen if all cards have a default placeholder
                print(f"JUBILEE: {pulled_card.name} não tem uma função de habilidade configurada.")
        else:
            # This should not happen if Jubilee was played correctly and is on a location.
            print(f"ERRO JUBILEE: Não foi possível encontrar o local da carta Jubilee ({card.name}).")
    else:
        print("JUBILEE: Baralho vazio, nenhuma carta para puxar.")

def ability_ghost_rider(game_state, card): # 'card' is the instance of Ghost Rider
    """Ao Revelar: Traz de volta uma de suas cartas descartadas para este local."""
    discard_pile = game_state.player.discard_pile
    if discard_pile:
        # Escolhe uma carta aleatória da pilha de descarte
        card_to_resurrect = random.choice(discard_pile)
        print(f"GHOST RIDER: Tentando ressuscitar {card_to_resurrect.name}.")

        # Remove do descarte
        game_state.player.discard_pile.remove(card_to_resurrect) # More direct way to remove

        # Encontra o local onde o Ghost Rider (the 'card' instance) está
        location_of_ghost_rider = None
        for loc_list in game_state.locations:
            if card in loc_list: # 'card' is the Ghost Rider instance
                location_of_ghost_rider = loc_list
                break

        if location_of_ghost_rider is not None:
            location_of_ghost_rider.append(card_to_resurrect)
            print(f"GHOST RIDER: {card_to_resurrect.name} ressuscitado(a) para o local de Ghost Rider.")
            # Adiciona a habilidade da carta ressuscitada ao INÍCIO da fila de resolução
            if hasattr(card_to_resurrect, 'ability_function') and callable(card_to_resurrect.ability_function):
                game_state.resolution_queue.insert(0, (card_to_resurrect.ability_function, card_to_resurrect))
                print(f"GHOST RIDER: Habilidade de {card_to_resurrect.name} adicionada ao início da fila de resolução.")
            else:
                print(f"GHOST RIDER: {card_to_resurrect.name} não tem uma função de habilidade configurada.")
        else:
            # This should not happen if Ghost Rider was played correctly.
            print(f"ERRO GHOST RIDER: Não foi possível encontrar o local da carta Ghost Rider ({card.name}).")
    else:
        print("GHOST RIDER: Pilha de descarte vazia, nenhuma carta para ressuscitar.")
