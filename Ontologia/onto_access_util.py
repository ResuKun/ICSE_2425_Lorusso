import random
from Ontologia.onto_save_manager import OntologyManager


#carica l'ontologia (singleton)
def get_onto():
    if not hasattr(get_onto, "_onto"):
        manager = OntologyManager()
        get_onto._manager = manager
        get_onto._onto = manager.get_ontology_from_manager()
    return get_onto._onto,get_onto._manager

#ritorna la carta dato l'id
def get_card_from_id(id):
    onto,_ = get_onto()
    return onto.search(type = onto.Card, idCarta = id)[0]

#ritorna la carta dato l'id
def get_meld_from_id(id):
    onto,_ = get_onto()
    return onto.search(type = onto.Scala, scalaId = id)[0]

#ritorna il tris dato l'id
def get_tris_from_id(id):
    onto,_ = get_onto()
    return onto.search(type = onto.Tris, trisId = id)[0]

#ritorna la carta dato l'id
def get_cards_from_id_list(id_list):
    onto,_ = get_onto()
    return [onto.search(type=onto.Card, idCarta=i)[0] for i in id_list]

#ritorna le carte note
def get_unknown_cards():
    onto,_ = get_onto()
    return onto.search(type = onto.Card, cartaNota = False)

#ritorna la lista dei giocatori
def get_player_list():
    onto,_ = get_onto()
    return onto.Player.instances()

#ritorna l'istanza del giocatore con quel nome
def get_player_by_name(nome):
    onto,_ = get_onto()
    return onto.search(type = onto.Player, nomeGiocatore = nome)[0]

#ritorna l'istanza del giocatore con quel nome
def get_player_by_id(idPlayer):
    onto,_ = get_onto()
    return onto.search(type = onto.Player, idGiocatore = idPlayer)[0]

#ritorna la carta dato l'id
def get_seme_by_name(find_name):
    onto,_ = get_onto()
    return onto.search(type=onto.Seme, name = find_name)[0]


#aggiorna il valore di partita.turnOf
def set_turnOf_by_id_player(player_id):
    onto,manager = get_onto()
    onto.Game.instances()[0].turnOf = get_player_by_id(player_id)
    manager.salva_ontologia_update_game()

#ritorna l'istanza di tutte le carte dell'ontologia
def get_all_cards():
    onto,_ = get_onto()
    return list(onto.Card.instances())

#ritorna il monte da cui pescare
def get_monte():
    onto,_ = get_onto()
    return onto.Game.instances()[0].monte.mazzo

#ritorna il monte degli scarti
def get_scarti():
    onto,_ = get_onto()
    return onto.Game.instances()[0].scarto.mazzo

# check sulle scale/tris
def isBurraco(canasta):
    return len(canasta.hasCards) >= 7

def has_jolly_or_pinella(canasta):
    onto,_ = get_onto()
    return any(isinstance(card, (onto.Jolly, onto.Pinella)) for card in canasta.hasCards)

def has_jolly_or_pinella_clean(canasta):
    onto,_ = get_onto()
    result = False
    if(isinstance(canasta, onto.Scala)):
        seme = canasta.semeScala
        if any(isinstance(card, (onto.Pinella)) for card in canasta.hasCards):
            for card in canasta.hasCards:
                if card.numeroCarta == 2:
                    if seme == card.seme:
                        if is_continous():
                            pass
        elif any(isinstance(card, (onto.Jolly)) for card in canasta.hasCards):
            pass
    return result

def is_continous(canasta):
    lista_carte = sorted(canasta, key=lambda x: x.numeroCarta)
    for card in lista_carte:
        if old_num is None:
            old_num = card.numeroCarta
        else:
            if (old_num + 1) < card.numeroCarta:
                return False
            else: 
                old_num = old_num + 1
    return True


def isBurracoPulito(canasta):
    return isBurraco(canasta) and not has_jolly_or_pinella(canasta)

def remove_jolly_pinella(lista_carte):
    onto,_ = get_onto()
    return [card for card in lista_carte if not isinstance(card, (onto.Jolly, onto.Pinella))]

def reset_deck():
    # pulisco le mani dei giocatori per iniziare un nuovo round
    onto, manager = get_onto()

    for player in onto.Player.instances():
            player.playerHand.mazzo.clear()

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
    manager.salva_ontologia_update_game()
