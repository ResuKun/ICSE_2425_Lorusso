from Ontologia.onto_save_manager import OntologyManager, OntologyResource
from Ontologia.onto_access_util import get_card_by_rank, get_card_by_rank_seme
import itertools
from functools import lru_cache
from enum import Enum

from Utils.logger import SingletonLogger 

# VEDERE tabella excel per i dettagli
# # https://docs.google.com/spreadsheets/d/1DjnS8H3UblTrA0DteEcYRw28aSgxtK5EV7Ahtghl_rc/edit?gid=405700369#gid=405700369

# pick_up_action_id = 0
# pick_up_discard_action_id = 1
# discard_action_id = 2 - 109
# close_game_action_id = 110 - 217
# open_tris_action_id = 218 - 4921
# open_meld_action_id = 4922 - 9641
# update_tris_action_id = 9642 - 9761
# update_meld_action_id = 9762 - 9921
# close_game_by_judge = 9922

class ActionIndexes(Enum):
    PICK_UP_ACTION_ID = ['pick_up_action_id', 0]
    PICK_UP_DISCARD_ACTION_ID = ['pick_up_discard_action_id', 1]
    DISCARD_ACTION_ID = ['discard_action_id', 2] 
    # 110 - 217
    CLOSE_GAME_ACTION_ID = ['close_game_action_id', 110]
    # 218 - 4921
    OPEN_TRIS_ACTION_ID = ['open_tris_action_id', 218]
    # 4922 - 9641
    OPEN_MELD_ACTION_ID = ['open_meld_action_id', 4922]
    # 9642 - 9761
    UPDATE_TRIS_ACTION_ID = ['update_tris_action_id', 9642]
    # 9762 - 9921
    UPDATE_MELD_ACTION_ID = ['update_meld_action_id', 9762]
    # 9922
    CLOSE_GAME_JUDGE_ACTION_ID = ['close_game_judge_action_id', 9922]
    # Vedere Excel per mappatura dettagliata

#Creazione della mappatura delle azioni
# in cache senza doverlo leggere da file o ricalcolare
@lru_cache(maxsize=1)
def get_map_actions():
    arr = create_mapping()
    result = {ActionIndexes.PICK_UP_ACTION_ID.value[0]: 0, ActionIndexes.PICK_UP_DISCARD_ACTION_ID.value[0]: 1 }

    for index in range(2, len(arr)):
        result[tuple(arr[index])] = index

    return result

#Creazione della mappatura delle azioni
# in cache senza doverlo leggere da file o ricalcolare
@lru_cache(maxsize=1)
def create_mapping():
    #log = SingletonLogger().get_logger()
    #res = OntologyResource.CARD
    #manager = OntologyManager()
    #manager.reload_file_name()
    #onto = manager.get_ontology_from_manager(res)
    onto = OntologyManager().get_onto()

    action_ids = [
        "pick_up_action_id",
        "pick_up_discard_action_id"
    ]
    # da fondere poi con action_ids, 
    # in maniera tale da non dover ciclare più volte
    close_game_arr = []
    
    cards = onto.Card.instances()
    cards = sorted(cards, key=lambda p: ( p.idCarta))
    #for card in cards:
    for index in range(0, len(cards)):
        #discard
        card = cards[index]
        action_ids.append(["discard_action_id", card.idCarta])
        
        #costruisco gli array di chiusura di gioco e di creazione delle scale
        #commentato per semplicità di scrittura tramite id_carta
        #if not isinstance(card, (onto.Jolly, onto.Pinella)):
        # close_game
        close_game_arr.append(["close_game_action_id", card.idCarta])

    # aggiungo le azioni di CHIUSURA
    action_ids.extend(close_game_arr)

    crazy_cards = [card.idCarta for card in cards if isinstance(card, (onto.Jolly, onto.Pinella))]

    # open_tris
    create_tris_arr = _generate_tris(crazy_cards)
    # aggiungo le azioni di APERTURA TRIS
    action_ids.extend(create_tris_arr)

    # open_meld
    create_meld_arr = _generate_melds(crazy_cards, onto)
    # aggiungo le azioni di APERTURA SCALE
    action_ids.extend(create_meld_arr)

    # update_tris
    update_tris_arr = _generate_update_tris()
    # aggiungo le azioni di UPDATE TRIS
    action_ids.extend(update_tris_arr)

    # update_meld
    update_meld_arr = _generate_update_meld()
    # aggiungo le azioni di UPDATE MELD
    action_ids.extend(update_meld_arr)

    # aggiungo l'azione di CLOSE GAME BY JUDGE
    action_ids.append(["close_game_judge_action_id", card.idCarta])

    #log.info(action_ids)
    return action_ids


def _generate_melds(matte_list, onto):
    create_meld_arr = []

    all_semes = [seme_name.name for seme_name in onto.Seme.instances()]
    
    # Ciclare per SEME
    for seme in all_semes:
        # Ciclare per SEQUENZA (11 in totale)
        cache = {}
        for index in range(1,12):
            copies = []
            for copies_index in range(0,3):
                card_index = index + copies_index
                if card_index in cache:
                    copies.append(cache[card_index])
                else:
                    card = [carta.idCarta for carta in get_card_by_rank_seme(seme, card_index)]
                    copies.append(card)
                    cache[card_index] = card

            copies_R1 = copies[0]
            copies_R2 = copies[1]
            copies_R3 = copies[2]
                
            # --- SCALE PURE ---
            # itertools.product per generare tutte le terne incrociate (2 x 2 x 2 = 8)
            for cards_list in itertools.product(copies_R1, copies_R2, copies_R3):
                create_meld_arr.append(["open_meld_action_id", cards_list])

            # SCALE CON MATTA
            for remaining_cards in itertools.product(copies_R1, copies_R2):
                for matta in matte_list:
                    if matta != remaining_cards[0] and matta != remaining_cards[1]:
                        meld = (remaining_cards[0], remaining_cards[1], matta)
                        create_meld_arr.append(["open_meld_action_id", meld])

            for remaining_cards in itertools.product(copies_R1, copies_R3):
                for matta in matte_list: 
                    if matta != remaining_cards[0] and matta != remaining_cards[1]:
                        meld = (remaining_cards[0], matta, remaining_cards[1])
                        create_meld_arr.append(["open_meld_action_id", meld])

        copies_R1 = cache[12]
        copies_R2 = cache[13]
        for remaining_cards in itertools.product(copies_R1, copies_R2):
                for matta in matte_list: 
                    meld = (remaining_cards[0], remaining_cards[1], matta)
                    create_meld_arr.append(["open_meld_action_id", meld])

    # Il totale di create_meld_arr dovrebbe essere (11 seq * 4 semi * 152 comb/seq) = 6688
    return create_meld_arr


def _generate_tris(matte_list):
    tris_arr = []
    tris_arr.extend(_generate_single_tris_combination(1, matte_list))
    for index in range(3,14):
        tris_arr.extend(_generate_single_tris_combination(index, matte_list))
    return tris_arr


def _generate_single_tris_combination(number, matte_list):
    tris_arr = []
    cards = [p.idCarta for p in get_card_by_rank(number)]
    # itertools.product per generare tutte le terne incrociate (2 x 2 x 2 = 8)
    for cards_list in itertools.combinations(cards, 3):
        tris_arr.append(["open_tris_action_id", cards_list])

    # TRIS CON MATTA 
    for coppia in itertools.combinations(cards, 2):
        for matta in matte_list: # 12 Matte (4 Jolly + 8 Pinelle)
            # la matta è SEMPRE ULTIMA, da tenere in conto
            meld = (coppia[0], coppia[1], matta)
            tris_arr.append(["open_tris_action_id", meld])

    return tris_arr


# in base alla tipologia di tris e alla sua lunghezza
def _generate_update_tris():
    tris_udpate_arr = []
    # A 3/7 - 8/13(K)
    tris_card_values = [5, 15, 10]
    added_card_values = [5, 15, 10, 20, 30]

    # tris pulito
    # per ogni "tipologia" di Tris
    for tris_value in tris_card_values:
        # considero da il totale di carte finale ( da 3 a 7+)
        for tris_len in range(3, 8):
            # valore della carta che sto aggiungendo
            for card_value in added_card_values:
                tris_type = (0, tris_len, tris_value, card_value)
                tris_udpate_arr.append(["update_tris_action_id", tris_type])

    # se ha già una matta, non considero le carte matte da aggiungere
    for tris_value in tris_card_values:
        for tris_len in range(3, 8):
            for card_value in tris_card_values:
                tris_type = (1, tris_len, tris_value, card_value)
                tris_udpate_arr.append(["update_tris_action_id", tris_type])

    return tris_udpate_arr


# in base alla tipologia di carta che si sta aggiungendo
#  e alla lunghezza della scala
def _generate_update_meld():
    meld_udpate_arr = []
    # 3/7 - 8/13(K) - A - 2 - Jolly
    meld_card_values = [5, 10, 15, 20, 30]
    # 3/7 - 8/13(K) - A
    clean_card_values = [5, 10, 15]
    #              Come     Quando    Fuori   Piove
    seme_carta = ["Cuori", "Quadri", "Fiori","Picche"]
    # 0 scala pulita, 1 scala sporca

    for seme in seme_carta:
        # per ogni "tipologia" di carta che si sta aggiungendo
        for value in meld_card_values:
            # considero da il totale di carte finale ( da 3 a 7+)
            for index in range(3, 8):
                meld_type = (0, seme, index, value)
                meld_udpate_arr.append(["update_meld_action_id", meld_type])
    
    for seme in seme_carta:
        for value in clean_card_values:
            for mel_len in range(3, 8):
                meld_type = (1, seme, mel_len, value)
                meld_udpate_arr.append(["update_meld_action_id", meld_type])

    return meld_udpate_arr