# abilities.py
from __future__ import annotations # Add this as the first line

import random
from typing import Optional, List, Dict, Any
from deck_database import ULTRON_STONES
# from card import Card # Remove or comment out this line
from deck_factory import create_card_from_prepared_data

def ability_placeholder(game_state, card: 'Card'): # Signature changed
    """Uma função vazia para cartas sem habilidade ou cuja habilidade não implementamos ainda."""
    pass

def ability_blade(game_state, card: 'Card'): # Signature changed
    """Ao Revelar: Descarta a carta mais à direita da sua mão."""
    hand = game_state.player.hand
    if hand:
        card_to_discard = hand[-1]
        game_state.player.move_card_to_discard(card_to_discard, simulation_mode=game_state.simulation_mode)


def ability_corvus_glaive(game_state, card: 'Card', resolved_outcomes_list: Optional[List[Dict[str, Any]]] = None): # Signature changed
    """Ao Revelar: Descarta 2 cartas da sua mão para ganhar +1 de Energia Máxima."""
    relevant_outcome = None
    if resolved_outcomes_list:
        for outcome_data in resolved_outcomes_list:
            if outcome_data.get('source_card_id') == card.id and \
               outcome_data.get('outcome_type') == 'CORVUS_DISCARD':
                relevant_outcome = outcome_data
                break

    cards_to_discard_instances = []
    if relevant_outcome and 'discarded_ids' in relevant_outcome:
        if not game_state.simulation_mode:
            print(f"CORVUS: Using pre-resolved discards: {relevant_outcome['discarded_ids']}")
        for cid in relevant_outcome['discarded_ids']:
            card_obj = game_state.player.find_card_in_hand(cid)
            if card_obj:
                cards_to_discard_instances.append(card_obj)
            elif not game_state.simulation_mode:
                print(f"CORVUS_WARNING: Pre-resolved discard ID {cid} not found in hand.")
    else:
        if not game_state.simulation_mode:
            print("CORVUS: No pre-resolved outcome found or no discarded_ids. Falling back to RNG.")
        hand = game_state.player.hand
        if len(hand) >= 2:
            cards_to_discard_instances = random.sample(hand, 2)
        elif len(hand) == 1:
            cards_to_discard_instances = [hand[0]]

    if cards_to_discard_instances:
        discarded_names = [c.name for c in cards_to_discard_instances]
        if not game_state.simulation_mode:
            print(f"CORVUS: Discarding {', '.join(discarded_names) if discarded_names else 'nothing'}.")
        for c_to_discard in list(cards_to_discard_instances):
            game_state.player.move_card_to_discard(c_to_discard, simulation_mode=game_state.simulation_mode)
    elif not game_state.simulation_mode:
        print("CORVUS: No cards to discard (either hand empty or pre-resolved specified none).")

    game_state.player.energy_max += 1
    if not game_state.simulation_mode:
        print("CORVUS: +1 de Energia Máxima concedido.")

def ability_jubilee(game_state, card_instance: 'Card', resolved_outcomes_list: Optional[List[Dict[str, Any]]] = None): # Signature changed
    """On Reveal: Add the top card of your deck to this location."""
    relevant_outcome = None
    if resolved_outcomes_list:
        for outcome_data in resolved_outcomes_list:
            if outcome_data.get('source_card_id') == card_instance.id and \
               outcome_data.get('outcome_type') == 'JUBILEE_PULL':
                relevant_outcome = outcome_data
                break

    pulled_card_instance = None

    if relevant_outcome and 'pulled_card_id' in relevant_outcome:
        pulled_card_id = relevant_outcome['pulled_card_id']
        if not game_state.simulation_mode:
            print(f"JUBILEE: Using pre-resolved pulled card ID: {pulled_card_id}")
        found_in_deck = False
        for i, card_in_deck in enumerate(game_state.player.deck):
            if card_in_deck.id == pulled_card_id:
                pulled_card_instance = game_state.player.deck.pop(i)
                found_in_deck = True
                break
        if not found_in_deck and not game_state.simulation_mode:
            print(f"JUBILEE_WARNING: Pre-resolved pulled card ID {pulled_card_id} not found in deck. Falling back to RNG.")
            pulled_card_instance = None # Force RNG path

    if not pulled_card_instance:
        if not game_state.player.deck:
            if not game_state.simulation_mode:
                print("JUBILEE: Baralho vazio, nenhuma carta para puxar (RNG path).")
            return
        if not game_state.simulation_mode:
            print("JUBILEE: No pre-resolved outcome or ID not in deck. Pulling card from top of deck (RNG path).")
        pulled_card_instance = game_state.player.deck.pop(0)

    if not pulled_card_instance:
        if not game_state.simulation_mode:
            print("JUBILEE_ERROR: Failed to select a card to pull.")
        return

    if not game_state.simulation_mode:
        print(f"JUBILEE: Puxou {pulled_card_instance.name} do baralho.")

    location_of_jubilee = None
    for loc_list in game_state.locations:
        if card_instance in loc_list:
            location_of_jubilee = loc_list
            break

    if location_of_jubilee is not None:
        if len(location_of_jubilee) < 4:
            location_of_jubilee.append(pulled_card_instance)
            if not game_state.simulation_mode:
                print(f"JUBILEE: {pulled_card_instance.name} adicionado(a) ao local de Jubilee.")
            if hasattr(pulled_card_instance, 'ability_function') and callable(pulled_card_instance.ability_function):
                game_state.resolution_queue.insert(0, (pulled_card_instance.ability_function, pulled_card_instance))
                if not game_state.simulation_mode:
                    print(f"JUBILEE: Habilidade de {pulled_card_instance.name} adicionada ao início da fila de resolução.")
        else:
            if not game_state.simulation_mode:
                print(f"JUBILEE: Local de Jubilee (onde {card_instance.name} está) está cheio. {pulled_card_instance.name} não pode ser adicionado.")
                print(f"JUBILEE: Movendo {pulled_card_instance.name} para o descarte pois o local está cheio.")
            game_state.player.discard_pile.append(pulled_card_instance)
    else:
        if not game_state.simulation_mode:
            print(f"ERRO JUBILEE: Não foi possível encontrar o local da carta Jubilee ({card_instance.name}). Card {pulled_card_instance.name} retorna ao topo do baralho.")
        game_state.player.deck.insert(0, pulled_card_instance)


def ability_ghost_rider(game_state, card_instance: 'Card', resolved_outcomes_list: Optional[List[Dict[str, Any]]] = None): # Signature changed
    """On Reveal: Bring back one of your discarded cards to this location."""
    relevant_outcome = None
    if resolved_outcomes_list:
        for outcome_data in resolved_outcomes_list:
            if outcome_data.get('source_card_id') == card_instance.id and \
               outcome_data.get('outcome_type') == 'GHOST_RIDER_CHOICE':
                relevant_outcome = outcome_data
                break

    card_to_resurrect_id = None
    card_to_resurrect_instance = None

    if relevant_outcome and 'resurrected_id' in relevant_outcome:
        card_to_resurrect_id = relevant_outcome['resurrected_id']
        if not game_state.simulation_mode:
            print(f"GHOST RIDER: Using pre-resolved resurrected ID: {card_to_resurrect_id}")
        for card_in_discard in game_state.player.discard_pile:
            if card_in_discard.id == card_to_resurrect_id:
                card_to_resurrect_instance = card_in_discard
                break
        if not card_to_resurrect_instance and not game_state.simulation_mode:
            print(f"GHOST RIDER_WARNING: Pre-resolved resurrected ID {card_to_resurrect_id} not found in discard pile. Falling back to RNG.")
            card_to_resurrect_id = None

    if not card_to_resurrect_instance:
        if not game_state.player.discard_pile:
            if not game_state.simulation_mode:
                print("GHOST RIDER: Pilha de descarte vazia, nenhuma carta para ressuscitar (RNG path).")
            return
        if not game_state.simulation_mode:
            print("GHOST RIDER: No pre-resolved outcome or ID invalid/not found. Choosing random card from discard (RNG path).")
        card_to_resurrect_instance = random.choice(game_state.player.discard_pile)

    if not card_to_resurrect_instance:
        if not game_state.simulation_mode:
            print("GHOST RIDER_ERROR: Failed to select a card to resurrect.")
        return

    if not game_state.simulation_mode:
        print(f"GHOST RIDER: Attempting to resurrect {card_to_resurrect_instance.name}.")
    game_state.player.discard_pile.remove(card_to_resurrect_instance)

    location_of_ghost_rider = None
    for loc_list in game_state.locations:
        if card_instance in loc_list:
            location_of_ghost_rider = loc_list
            break

    if location_of_ghost_rider is not None:
        if len(location_of_ghost_rider) < 4:
            location_of_ghost_rider.append(card_to_resurrect_instance)
            if not game_state.simulation_mode:
                print(f"GHOST RIDER: {card_to_resurrect_instance.name} ressuscitado(a) para o local de Ghost Rider.")
            if hasattr(card_to_resurrect_instance, 'ability_function') and callable(card_to_resurrect_instance.ability_function):
                game_state.resolution_queue.insert(0, (card_to_resurrect_instance.ability_function, card_to_resurrect_instance))
                if not game_state.simulation_mode:
                    print(f"GHOST RIDER: Habilidade de {card_to_resurrect_instance.name} adicionada ao início da fila de resolução.")
        else: # Location is full
            if not game_state.simulation_mode:
                print(f"GHOST RIDER: Local de Ghost Rider (onde {card_instance.name} está) está cheio. {card_to_resurrect_instance.name} não pode ser adicionado.")
                print(f"GHOST RIDER: Movendo {card_to_resurrect_instance.name} de volta para o descarte pois o local está cheio.")
            game_state.player.discard_pile.append(card_to_resurrect_instance) # Return to discard
    else:
        if not game_state.simulation_mode:
            print(f"ERRO GHOST RIDER: Não foi possível encontrar o local da carta Ghost Rider ({card_instance.name}). Card {card_to_resurrect_instance.name} retorna ao descarte.")
        game_state.player.discard_pile.append(card_to_resurrect_instance) # Return to discard

def ability_gambit(game_state, card: 'Card', resolved_outcomes_list: Optional[List[Dict[str, Any]]] = None): # Signature changed
    """Ao Revelar: Descarta uma carta da sua mão para destruir uma carta inimiga aleatória."""
    # TODO: Adapt Gambit for pre-resolved outcomes (which card is discarded, which enemy is destroyed) if needed.
    if game_state.player.hand:
        card_to_discard = random.choice(game_state.player.hand)
        game_state.player.move_card_to_discard(card_to_discard, simulation_mode=game_state.simulation_mode)
        if not game_state.simulation_mode:
            print(f"GAMBIT: Descartou {card_to_discard.name} da mão.")
    else:
        if not game_state.simulation_mode:
            print("GAMBIT: Habilidade falhou (sem cartas na mão para descartar).")

def ability_hela(game_state, card: 'Card', resolved_outcomes_list: Optional[List[Dict[str, Any]]] = None): # Signature changed
    """Ao Revelar: Ressuscita cartas de custos diferentes da pilha de descarte."""
    # TODO: Adapt Hela for pre-resolved outcomes (which card per cost is chosen) if needed.
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
                    game_state.resolution_queue.insert(0, (c_res.ability_function, c_res)) # Queue as 2-tuple
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

def ability_odin(game_state, card: 'Card'): # Signature changed
    """Ao Revelar: Repete as habilidades 'Ao Revelar' de suas outras cartas aqui."""
    # Odin's re-triggering doesn't involve new RNG from Odin itself.
    # It re-triggers other abilities, which will correctly receive the
    # resolved_outcomes_list from the current process_resolution_queue context.
    odin_location_index = -1
    for i, loc_list in enumerate(game_state.locations):
        if card in loc_list:
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
                game_state.resolution_queue.insert(0, (other_card_instance.ability_function, other_card_instance)) # Queue as 2-tuple
                if not game_state.simulation_mode:
                    print(f"ODIN: Habilidade de {other_card_instance.name} adicionada ao início da fila de resolução.")
            else:
                if not game_state.simulation_mode:
                    print(f"ODIN: {other_card_instance.name} não tem uma função de habilidade configurada.")
    else:
        if not game_state.simulation_mode:
            print(f"ERRO ODIN: Não foi possível encontrar o local da carta Odin ({card.name}).")

def ability_blink(game_state, card: 'Card', resolved_outcomes_list: Optional[List[Dict[str, Any]]] = None): # Signature changed
    """
    On Reveal: Swap the last card you played with a card that costs more from your deck.
    """
    # TODO: Adapt Blink for pre-resolved outcomes (which card from deck, if multiple eligible) if needed.
    if not game_state.play_history:
        if not game_state.simulation_mode:
            print("BLINK: Play history is empty. Blink's ability fizzles.")
        return

    target_card_played_instance = game_state.play_history[-1]

    if not game_state.simulation_mode:
        print(f"BLINK: Targeting {target_card_played_instance.name} (last card in play history).")

    target_location_list = None
    target_location_index = -1
    original_index_in_location = -1

    for i, loc_list in enumerate(game_state.locations):
        if target_card_played_instance in loc_list:
            target_location_list = loc_list
            target_location_index = i
            original_index_in_location = loc_list.index(target_card_played_instance)
            break

    if target_location_list is None:
        if not game_state.simulation_mode:
            print(f"BLINK: Target card {target_card_played_instance.name} not found in any location (perhaps already moved?). Ability fizzles.")
        return

    eligible_deck_cards = [c for c in game_state.player.deck if c.cost > target_card_played_instance.cost]

    if not eligible_deck_cards:
        if not game_state.simulation_mode:
            print(f"BLINK: No card found in deck costing more than {target_card_played_instance.name} (Cost: {target_card_played_instance.cost}). Ability fizzles.")
        return

    card_from_deck = random.choice(eligible_deck_cards)
    if not game_state.simulation_mode:
        print(f"BLINK: Selected {card_from_deck.name} (Cost: {card_from_deck.cost}) from deck to swap with {target_card_played_instance.name}.")

    target_location_list.remove(target_card_played_instance)
    if not game_state.simulation_mode:
        print(f"BLINK: Removed {target_card_played_instance.name} from location {target_location_index}.")

    game_state.player.deck.remove(card_from_deck)
    if not game_state.simulation_mode:
        print(f"BLINK: Removed {card_from_deck.name} from deck.")

    if original_index_in_location != -1 and original_index_in_location <= len(target_location_list): # Use <= to allow insert at end
         target_location_list.insert(original_index_in_location, card_from_deck)
    else:
        target_location_list.append(card_from_deck)
    if not game_state.simulation_mode:
        print(f"BLINK: Added {card_from_deck.name} to location {target_location_index}.")

    if hasattr(card_from_deck, 'ability_function') and callable(card_from_deck.ability_function):
        game_state.resolution_queue.insert(0, (card_from_deck.ability_function, card_from_deck)) # Queue as 2-tuple
        if not game_state.simulation_mode:
            print(f"BLINK: Queued ability of {card_from_deck.name}.")

    game_state.player.deck.append(target_card_played_instance)
    random.shuffle(game_state.player.deck)
    if not game_state.simulation_mode:
        print(f"BLINK: Returned {target_card_played_instance.name} to deck and shuffled.")

def ability_infinity_ultron(game_state, card_instance: 'Card', resolved_outcomes_list: Optional[List[Dict[str, Any]]] = None): # Signature changed
    """On Reveal: Add 2 of Ultron’s Stones to your hand."""
    relevant_outcome = None
    if resolved_outcomes_list:
        for outcome_data in resolved_outcomes_list:
            if outcome_data.get('source_card_id') == card_instance.id and \
               outcome_data.get('outcome_type') == 'ULTRON_STONES':
                relevant_outcome = outcome_data
                break

    stone_ids_to_add = []
    if relevant_outcome and 'generated_stone_ids' in relevant_outcome:
        if not game_state.simulation_mode:
            print(f"ULTRON: Using pre-resolved stones: {relevant_outcome['generated_stone_ids']}")
        stone_ids_to_add = relevant_outcome['generated_stone_ids']
        if len(stone_ids_to_add) != 2 and not game_state.simulation_mode:
             print(f"ULTRON_WARNING: Pre-resolved outcome provided {len(stone_ids_to_add)} stones, expected 2. Using as is.")
    else:
        if not game_state.simulation_mode:
            print("ULTRON: No pre-resolved outcome. Generating stones with RNG.")
        if len(ULTRON_STONES) < 2:
            if not game_state.simulation_mode:
                print("INFINITY_ULTRON: Not enough unique stones defined.")
            return # Return early if not enough stones to pick from
        selected_stone_data_list = random.sample(ULTRON_STONES, 2)
        stone_ids_to_add = [sd['id'] for sd in selected_stone_data_list]

    added_stone_names = []
    for stone_id in stone_ids_to_add:
        new_stone_card = create_card_from_prepared_data(stone_id)
        if new_stone_card:
            game_state.player.hand.append(new_stone_card)
            added_stone_names.append(new_stone_card.name)
        elif not game_state.simulation_mode:
            print(f"ULTRON_ERROR: Could not create stone card for ID {stone_id}")

    if added_stone_names:
        if not game_state.simulation_mode:
            print(f"INFINITY_ULTRON: Added {', '.join(added_stone_names)} to hand.")
    elif not game_state.simulation_mode:
        print("INFINITY_ULTRON: No stones added to hand.")

def ability_legion(game_state, card_instance: 'Card'): # Signature changed
    """
    On Reveal: Replace each other location with this one.
    """
    legion_location_index = -1
    legion_actual_location_list = None

    for i, loc_list in enumerate(game_state.locations):
        if card_instance in loc_list:
            legion_location_index = i
            legion_actual_location_list = loc_list
            break

    if legion_location_index == -1 or legion_actual_location_list is None:
        if not game_state.simulation_mode:
            print(f"LEGION_ERROR: Could not find Legion ({card_instance.name}) in any location.")
        return

    if not game_state.simulation_mode:
        print(f"LEGION: Activated at location {legion_location_index}. Its content: {[c.name for c in legion_actual_location_list]}")

    card_ids_in_legion_location = [c.id for c in legion_actual_location_list]

    for i in range(len(game_state.locations)):
        if i == legion_location_index:
            continue

        removed_cards_from_loc_i = game_state.locations[i][:]
        if removed_cards_from_loc_i and not game_state.simulation_mode:
            print(f"LEGION: Removing cards {[c.name for c in removed_cards_from_loc_i]} from location {i}.")

        game_state.locations[i] = []

        new_cards_for_location_i = []
        for card_id_to_copy in card_ids_in_legion_location:
            new_card_copy = create_card_from_prepared_data(card_id_to_copy)
            if new_card_copy:
                new_cards_for_location_i.append(new_card_copy)
            elif not game_state.simulation_mode:
                print(f"LEGION_ERROR: Could not create card copy for ID {card_id_to_copy} for location {i}")

        game_state.locations[i].extend(new_cards_for_location_i)
        if not game_state.simulation_mode:
            print(f"LEGION: Location {i} now mirrors Legion's location with cards: {[c.name for c in game_state.locations[i]]}")
