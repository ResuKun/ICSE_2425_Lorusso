import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "aipython"))

import copy
from owlready2 import *
import random
from csp_card_resolver import can_create_csp_scala, can_update_csp_scala
from playerAction import apre_canasta
import Ontologia.OntoManager as OntoManager

def remove_jolly_pinella(lista_carte):
    onto = OntoManager.get_ontology_from_manager()
    return [card for card in lista_carte if not isinstance(card, (onto.Jolly, onto.Pinella))]

def get_card_value_sum(lista_carte):
    sum = 0
    for carta in lista_carte:
        sum += carta.valoreCarta
    return sum

def mischia_carte(da_mischiare):
    all_cards_in_ontology = list(da_mischiare.mazzo)
    random.shuffle(all_cards_in_ontology)
    return all_cards_in_ontology

def passa_turno(partita):
    current_player = partita.turnOf
    all_players = list(partita.players) # Converte in lista per poter usare l'indice
    for player in all_players:
        if player != current_player:
            partita.turnOf = player
            break
    OntoManager.salva_ontologia_init_game()


#restituisce una rappresentazione compatta e descrittiva 
#dello stato attuale della partita dal punto di vista del player
def stato_della_partita(player, game):

    player_hand = frozenset(card.name for card in player.playerHand.mazzo)
    player_hand_value = get_card_value_sum(player.playerHand.mazzo)
    player_score = player.punteggioGiocatore

    scale_in_gioco = frozenset(
        frozenset((c.name for c in scala.hasCards) for scala in player_tmp.scala) for player_tmp in game.players
    )

    tris_in_gioco = frozenset(
        frozenset((c.name for c in tris.hasCards) for tris in player_tmp.tris) for player_tmp in game.players
    )
   
    scarto_in_gioco = frozenset(
        frozenset(c.name for c in scarti.hasCards) for scarti in game.scarto.mazzo
    )

    monte = len(game.monte.mazzo)

   # Restituisce una tupla di tutti questi elementi hashable
    stato_partita = (
        player_hand,
        player_hand_value,
        player_score,
        scale_in_gioco,
        tris_in_gioco,
        scarto_in_gioco,
        monte
    )
    
    return stato_partita

#simula una azione
def simulate_action(game, player, action, cards = None):
    stato = copy.deepcopy(stato_della_partita(player, game))

    if action.name == "scarta":
        stato.player_hand.remove(action.cards.name)
        stato.player_hand_value = get_card_value_sum(player.playerHand.mazzo)
        stato.scarto_in_gioco.append(cards.name)

    elif action.name == "pesca":
        card = stato.monte.pop(0)
        stato.player_hand.append(card)

    elif action.name == "calare_scala":
        if can_create_csp_scala(cards):
            nuovaScala = apre_canasta(player, cards)
            #!!! FARE ATTENZIONE -- controllare che player sia  aggiornato dopo apre_canasta
            stato.player_hand = frozenset(card.name for card in player.playerHand.mazzo)
            stato.player_hand_value = get_card_value_sum(player.playerHand.mazzo)
            stato.player_score = player.punteggioGiocatore
            stato.scale_in_gioco.append(nuovaScala)

    elif action.name == "update_scala":
        #!! RIPRENDERE DA QUI TODO
        #  '°-°  idiota, il CSP ti fornisce anche la soluzione, quindi la scala a cui attaccarlo, tienilo a 
        if can_update_csp_scala(cards):
            #nuovoTris = aggiunge_carte_scala(player, cards)
            #!!! FARE ATTENZIONE -- controllare che player sia  aggiornato dopo apre_canasta
            stato.player_hand = frozenset(card.name for card in player.playerHand.mazzo)
            stato.player_hand_value = get_card_value_sum(player.playerHand.mazzo)
            stato.player_score = player.punteggioGiocatore
            #stato.scale_in_gioco.append(nuovoTris)


