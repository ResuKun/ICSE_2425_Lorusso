import random
import Ontologia.onto_save_manager as onto_save_manager
onto = onto_save_manager.get_ontology_from_manager()


#ritorna la carta dato l'id
def get_card_from_id(id):
    return onto.search(type = onto.Card, idCarta = id)[0]

#ritorna le carte note
def get_unknown_cards():
    return onto.search(type = onto.Card, cartaNota = False)

#ritorna la lista dei giocatori
def get_player_list():
    return onto.Player.instances()

#ritorna l'istanza del giocatore con quel nome
def get_player_by_name(nome):
    return onto.search(type = onto.Player, nomeGiocatore = nome)[0]

#aggiorna il valore di partita.turnOf
def set_turn_of(player):
    onto.partita.turnOf = player
    onto_save_manager.salva_ontologia_update_game()

#ritorna l'istanza di tutte le carte dell'ontologia
def get_all_cards():
    return list(onto.Card.instances())

#ritorna il monte da cui pescare
def get_monte():
    return onto.partita.monte.mazzo

#ritorna il monte degli scarti
def get_scarti():
    return onto.partita.scarto.mazzo

# check sulle scale/tris
def isBurraco(canasta):
    return len(canasta.hasCards) >= 7

def has_jolly_or_pinella(canasta):
	return any(isinstance(card, (onto.Jolly, onto.Pinella)) for card in canasta.hasCards)

def isBurracoPulito(canasta):
    return isBurraco(canasta) and not has_jolly_or_pinella(canasta)

def remove_jolly_pinella(lista_carte):
	return [card for card in lista_carte if not isinstance(card, (onto.Jolly, onto.Pinella))]

def reset_deck():
    # pulisco le mani dei giocatori per iniziare un nuovo round
    for player in onto.players:
        player.playerHand.clear()

    # pulisco il monte da cui raccogliere e gli scarti
    monte = get_monte()
    scarti = get_scarti()
    monte.clear()
    scarti.clear()

    # mischio le carte
    all_cards_in_ontology = list(get_all_cards())
    random.shuffle(all_cards_in_ontology)

    # le rendo di nuovo non visibile e/o note 
    # e le aggiungo al mazzo
    for card in all_cards_in_ontology:
        card.cartaVisibile = False
        card.cartaNota = False
        monte.append(card)

    primo_scarto = monte[0]
    primo_scarto.cartaVisibile = True
    primo_scarto.cartaNota = True
    scarti.append(primo_scarto)
    monte.remove(primo_scarto)
    onto_save_manager.salva_ontologia_update_game()
