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

def ability_gambit(game_state, card):
    """Ao Revelar: Descarta uma carta da sua mão para destruir uma carta inimiga aleatória."""
    if game_state.player.hand:
        # Descarta uma carta aleatória da própria mão
        card_to_discard = random.choice(game_state.player.hand)
        # game_state.player.hand.remove(card_to_discard) # move_card_to_discard will handle this
        game_state.player.move_card_to_discard(card_to_discard) # Use the existing method
        print(f"GAMBIT: Descartou {card_to_discard.name} da mão.")
        # Nota do Maestro: A lógica de destruir carta inimiga será adicionada quando
        # implementarmos um estado para o oponente. Por enquanto, o descarte é o principal.
    else:
        print("GAMBIT: Habilidade falhou (sem cartas na mão para descartar).")

def ability_hela(game_state, card): # 'card' is Hela instance
    """Ao Revelar: Ressuscita cartas de custos diferentes da pilha de descarte."""
    # Lei nº 2: O "Snapshot" de Estado
    # Create a copy of the discard pile to iterate over, as it will be modified.
    snapshot_discard_pile = list(game_state.player.discard_pile)

    if not snapshot_discard_pile:
        print("HELA: Pilha de descarte vazia. Nenhuma carta para ressuscitar.")
        return

    cards_to_resurrect_final = [] # Renamed to avoid conflict with loop var

    # Agrupa por custo e seleciona uma carta aleatória de cada custo
    cards_by_cost = {}
    for c_snap in snapshot_discard_pile: # Renamed loop var
        if c_snap.cost not in cards_by_cost:
            cards_by_cost[c_snap.cost] = []
        cards_by_cost[c_snap.cost].append(c_snap)

    for cost, available_cards_at_cost in cards_by_cost.items(): # Renamed loop vars
        if available_cards_at_cost: # Ensure there are cards for this cost
            chosen_card_for_cost = random.choice(available_cards_at_cost) # Renamed
            cards_to_resurrect_final.append(chosen_card_for_cost)

    if not cards_to_resurrect_final:
        print("HELA: Nenhuma carta elegível para ressurreição após filtrar por custo.")
        return

    print(f"HELA: Selecionou {len(cards_to_resurrect_final)} cartas para ressuscitar: {[c.name for c in cards_to_resurrect_final]}.")

    for c_res in cards_to_resurrect_final:
        # Encontra um local aleatório com espaço (max 4 cards per location)
        available_locations_indices = [i for i, loc in enumerate(game_state.locations) if len(loc) < 4]

        if available_locations_indices:
            loc_index = random.choice(available_locations_indices)

            # Remove do descarte real (game_state.player.discard_pile)
            # Check if card is still in actual discard pile (it should be, as we iterated snapshot)
            if c_res in game_state.player.discard_pile:
                game_state.player.discard_pile.remove(c_res)
                game_state.locations[loc_index].append(c_res)
                print(f"HELA: Ressuscitou {c_res.name} no local {loc_index}.")

                # Adiciona a habilidade da carta ressuscitada à fila de resolução (INÍCIO)
                if hasattr(c_res, 'ability_function') and callable(c_res.ability_function):
                    game_state.resolution_queue.insert(0, (c_res.ability_function, c_res))
                    print(f"HELA: Habilidade de {c_res.name} adicionada ao início da fila de resolução.")
                else:
                    print(f"HELA: {c_res.name} não tem uma função de habilidade configurada.")
            else:
                # This might happen if a card was selected from snapshot but somehow removed from actual discard pile by another effect
                # before Hela got to it. For current single-player simulation, less likely.
                print(f"HELA: AVISO - {c_res.name} não encontrado na pilha de descarte no momento da ressurreição (possivelmente já ressuscitado por outra Hela ou efeito).")
        else:
            print(f"HELA: Nenhum local com espaço disponível para {c_res.name}.")
            # Card remains in discard if no space. Or decide if it should be put back to hand/deck, or lost.
            # For now, it just means it's not resurrected.

def ability_odin(game_state, card): # 'card' is the Odin instance
    """Ao Revelar: Repete as habilidades 'Ao Revelar' de suas outras cartas aqui."""
    odin_location_index = -1
    # Find Odin's location
    for i, loc_list in enumerate(game_state.locations): # Renamed loc to loc_list
        if card in loc_list: # 'card' is the Odin instance
            odin_location_index = i
            break

    if odin_location_index != -1:
        # Pega todas as outras cartas no local do Odin.
        # Create a snapshot of other cards in case their abilities modify the location's content.
        other_cards_in_location_snapshot = [c for c in game_state.locations[odin_location_index] if c.id != card.id]

        if not other_cards_in_location_snapshot:
            print(f"ODIN: Nenhuma outra carta no local {odin_location_index} para reativar.")
            return

        print(f"ODIN: Reativando {len(other_cards_in_location_snapshot)} habilidades no local {odin_location_index}: {[c.name for c in other_cards_in_location_snapshot]}.")

        # Adiciona as habilidades delas à fila de resolução (INÍCIO)
        # Iterate in reverse of play order? Or specified order? The prompt implies just adding them.
        # Adding to front of queue means they happen before other pending global events,
        # and in the order they are added (so last one added is first to execute from this batch).
        # To maintain original play order effect, one might add them in played order, or reverse.
        # For now, following prompt: add to front.
        for other_card_instance in other_cards_in_location_snapshot: # Renamed loop var
            if hasattr(other_card_instance, 'ability_function') and callable(other_card_instance.ability_function):
                game_state.resolution_queue.insert(0, (other_card_instance.ability_function, other_card_instance))
                print(f"ODIN: Habilidade de {other_card_instance.name} adicionada ao início da fila de resolução.")
            else:
                print(f"ODIN: {other_card_instance.name} não tem uma função de habilidade configurada.")
    else:
        # This should ideally not happen if Odin was played correctly.
        print(f"ERRO ODIN: Não foi possível encontrar o local da carta Odin ({card.name}).")
