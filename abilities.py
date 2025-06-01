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
        game_state.player.move_card_to_discard(card_to_discard, simulation_mode=game_state.simulation_mode)

# Nota do Maestro: Por enquanto, implementaremos apenas a do Blade.
# As outras podem usar o 'placeholder'.

def ability_corvus_glaive(game_state, card):
    """Ao Revelar: Descarta 2 cartas da sua mão para ganhar +1 de Energia Máxima."""
    hand = game_state.player.hand
    if len(hand) >= 2:
        # Escolhe 2 cartas aleatórias e únicas da mão para descartar
        cards_to_discard = random.sample(hand, 2)
        if not game_state.simulation_mode:
            print(f"CORVUS: Descartando {cards_to_discard[0].name} e {cards_to_discard[1].name}")
        for c_to_discard in cards_to_discard:
            game_state.player.move_card_to_discard(c_to_discard, simulation_mode=game_state.simulation_mode)
    elif len(hand) == 1:
        card_to_discard_single = hand[0]
        if not game_state.simulation_mode:
            print(f"CORVUS: Descartando {card_to_discard_single.name}")
        game_state.player.move_card_to_discard(card_to_discard_single, simulation_mode=game_state.simulation_mode)

    game_state.player.energy_max += 1
    if not game_state.simulation_mode:
        print("CORVUS: +1 de Energia Máxima concedido.")

def ability_jubilee(game_state, card): # 'card' is the instance of Jubilee
    """Ao Revelar: Adiciona a carta do topo do seu baralho a este local."""
    deck = game_state.player.deck
    if deck:
        pulled_card = deck.pop(0) # Get the top card
        if not game_state.simulation_mode:
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
            if not game_state.simulation_mode:
                print(f"JUBILEE: {pulled_card.name} adicionado(a) ao local de Jubilee.")
            if hasattr(pulled_card, 'ability_function') and callable(pulled_card.ability_function):
                game_state.resolution_queue.insert(0, (pulled_card.ability_function, pulled_card))
                if not game_state.simulation_mode:
                    print(f"JUBILEE: Habilidade de {pulled_card.name} adicionada ao início da fila de resolução.")
            else:
                if not game_state.simulation_mode:
                    print(f"JUBILEE: {pulled_card.name} não tem uma função de habilidade configurada.")
        else:
            if not game_state.simulation_mode:
                print(f"ERRO JUBILEE: Não foi possível encontrar o local da carta Jubilee ({card.name}).")
    else:
        if not game_state.simulation_mode:
            print("JUBILEE: Baralho vazio, nenhuma carta para puxar.")

def ability_ghost_rider(game_state, card): # 'card' is the instance of Ghost Rider
    """Ao Revelar: Traz de volta uma de suas cartas descartadas para este local."""
    discard_pile = game_state.player.discard_pile
    if discard_pile:
        card_to_resurrect = random.choice(discard_pile)
        if not game_state.simulation_mode:
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
            if not game_state.simulation_mode:
                print(f"GHOST RIDER: {card_to_resurrect.name} ressuscitado(a) para o local de Ghost Rider.")
            if hasattr(card_to_resurrect, 'ability_function') and callable(card_to_resurrect.ability_function):
                game_state.resolution_queue.insert(0, (card_to_resurrect.ability_function, card_to_resurrect))
                if not game_state.simulation_mode:
                    print(f"GHOST RIDER: Habilidade de {card_to_resurrect.name} adicionada ao início da fila de resolução.")
            else:
                if not game_state.simulation_mode:
                    print(f"GHOST RIDER: {card_to_resurrect.name} não tem uma função de habilidade configurada.")
        else:
            if not game_state.simulation_mode:
                print(f"ERRO GHOST RIDER: Não foi possível encontrar o local da carta Ghost Rider ({card.name}).")
    else:
        if not game_state.simulation_mode:
            print("GHOST RIDER: Pilha de descarte vazia, nenhuma carta para ressuscitar.")

def ability_gambit(game_state, card):
    """Ao Revelar: Descarta uma carta da sua mão para destruir uma carta inimiga aleatória."""
    if game_state.player.hand:
        card_to_discard = random.choice(game_state.player.hand)
        game_state.player.move_card_to_discard(card_to_discard, simulation_mode=game_state.simulation_mode)
        if not game_state.simulation_mode:
            print(f"GAMBIT: Descartou {card_to_discard.name} da mão.")
    else:
        if not game_state.simulation_mode:
            print("GAMBIT: Habilidade falhou (sem cartas na mão para descartar).")

def ability_hela(game_state, card): # 'card' is Hela instance
    """Ao Revelar: Ressuscita cartas de custos diferentes da pilha de descarte."""
    # Lei nº 2: O "Snapshot" de Estado
    # Create a copy of the discard pile to iterate over, as it will be modified.
    snapshot_discard_pile = list(game_state.player.discard_pile)

    if not snapshot_discard_pile:
        if not game_state.simulation_mode:
            print("HELA: Pilha de descarte vazia. Nenhuma carta para ressuscitar.")
        return

    cards_to_resurrect_final = []

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
        if not game_state.simulation_mode:
            print("HELA: Nenhuma carta elegível para ressurreição após filtrar por custo.")
        return

    if not game_state.simulation_mode:
        print(f"HELA: Selecionou {len(cards_to_resurrect_final)} cartas para ressuscitar: {[c.name for c in cards_to_resurrect_final]}.")

    for c_res in cards_to_resurrect_final:
        available_locations_indices = [i for i, loc in enumerate(game_state.locations) if len(loc) < 4]

        if available_locations_indices:
            loc_index = random.choice(available_locations_indices)

            # Remove do descarte real (game_state.player.discard_pile)
            # Check if card is still in actual discard pile (it should be, as we iterated snapshot)
            if c_res in game_state.player.discard_pile:
                game_state.player.discard_pile.remove(c_res)
                game_state.locations[loc_index].append(c_res)
                if not game_state.simulation_mode:
                    print(f"HELA: Ressuscitou {c_res.name} no local {loc_index}.")

                if hasattr(c_res, 'ability_function') and callable(c_res.ability_function):
                    game_state.resolution_queue.insert(0, (c_res.ability_function, c_res))
                    if not game_state.simulation_mode:
                        print(f"HELA: Habilidade de {c_res.name} adicionada ao início da fila de resolução.")
                else:
                    if not game_state.simulation_mode:
                        print(f"HELA: {c_res.name} não tem uma função de habilidade configurada.")
            else:
                if not game_state.simulation_mode:
                    print(f"HELA: AVISO - {c_res.name} não encontrado na pilha de descarte no momento da ressurreição (possivelmente já ressuscitado por outra Hela ou efeito).")
        else:
            if not game_state.simulation_mode:
                print(f"HELA: Nenhum local com espaço disponível para {c_res.name}.")

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
            if not game_state.simulation_mode:
                print(f"ODIN: Nenhuma outra carta no local {odin_location_index} para reativar.")
            return

        if not game_state.simulation_mode:
            print(f"ODIN: Reativando {len(other_cards_in_location_snapshot)} habilidades no local {odin_location_index}: {[c.name for c in other_cards_in_location_snapshot]}.")

        for other_card_instance in other_cards_in_location_snapshot:
            if hasattr(other_card_instance, 'ability_function') and callable(other_card_instance.ability_function):
                game_state.resolution_queue.insert(0, (other_card_instance.ability_function, other_card_instance))
                if not game_state.simulation_mode:
                    print(f"ODIN: Habilidade de {other_card_instance.name} adicionada ao início da fila de resolução.")
            else:
                if not game_state.simulation_mode:
                    print(f"ODIN: {other_card_instance.name} não tem uma função de habilidade configurada.")
    else:
        if not game_state.simulation_mode:
            print(f"ERRO ODIN: Não foi possível encontrar o local da carta Odin ({card.name}).")
