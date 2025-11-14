import random
from datetime import datetime
from Ontologia.onto_save_manager import OntologyManager
from Utils.logger import SingletonLogger 


#carica l'ontologia (singleton)
def get_onto():
    return OntologyManager().get_onto()

def get_manager():
    return OntologyManager()

#ritorna la carta dato l'id
def get_card_from_id(id):
    onto = get_onto()
    return onto.search(type = onto.Card, idCarta = id)[0]

#ritorna la carta dato l'id
def get_meld_from_id(id):
    onto = get_onto()
    return onto.search(type = onto.Scala, scalaId = id)[0]

#ritorna il tris dato l'id
def get_tris_from_id(id):
    onto = get_onto()
    return onto.search(type = onto.Tris, trisId = id)[0]

#ritorna la carta dato l'id
def get_cards_from_id_list(id_list):
    onto = get_onto()
    return [onto.search(type=onto.Card, idCarta=i)[0] for i in id_list]

#ritorna le carte note
def get_unknown_cards():
    onto = get_onto()
    return onto.search(type = onto.Card, cartaNota = False)

#ritorna la lista dei giocatori
def get_player_list():
    onto = get_onto()
    return onto.Player.instances()

#ritorna l'istanza del giocatore con quel nome
def get_player_by_name(nome):
    onto = get_onto()
    return onto.search(type = onto.Player, nomeGiocatore = nome)[0]

#ritorna l'istanza del giocatore con quel nome
def get_player_by_id(idPlayer):
    onto = get_onto()
    return onto.search(type = onto.Player, idGiocatore = idPlayer)[0]

#ritorna la carta dato l'id
def get_seme_by_name(find_name):
    onto = get_onto()
    return onto.search(type=onto.Seme, name = find_name)[0]


#aggiorna il valore di partita.turnOf
def set_turnOf_by_id_player(player_id):
    onto = get_onto()
    onto.Game.instances()[0].turnOf = get_player_by_id(player_id)
    get_manager().salva_ontologia_update_game()

#ritorna l'istanza di tutte le carte dell'ontologia
def get_all_cards():
    onto = get_onto()
    return list(onto.Card.instances())

#ritorna il monte da cui pescare
def get_monte():
    onto = get_onto()
    return onto.Game.instances()[0].monte.mazzo

#ritorna il monte degli scarti
def get_scarti():
    onto = get_onto()
    return onto.Game.instances()[0].scarto.mazzo

# check sulle scale/tris
def isBurraco(canasta):
    return len(canasta.hasCards) >= 7

def has_jolly_or_pinella_clean(canasta):
    onto = get_onto()
    cards = list(canasta.hasCards)

    if any(isinstance(c, onto.Jolly) for c in cards):
        return True
    
    # Se non è una Scala basta una Pinella
    if not isinstance(canasta, onto.Scala):
        return any(isinstance(c, (onto.Pinella)) for c in cards)

    seme_scala = canasta.semeScala
    pinellas = [c for c in cards if isinstance(c, onto.Pinella)]

    # Caso: due pinelle 
    if len(pinellas) == 2:
        return True

    # Caso: una sola pinella
    if len(pinellas) == 1 and is_continous(cards):
        p = pinellas[0]
        # se dello stesso seme
        if getattr(p, "numeroCarta", None) == 2 and getattr(p, "seme", None) == seme_scala:
            # Deve esserci il 3 dello stesso seme
            has_three_same_suit = any(
                getattr(c, "numeroCarta", None) == 3 and getattr(c, "seme", None) == seme_scala
                for c in cards
            )
            if has_three_same_suit:
                return False

    # In tutti gli altri casi basta la presenza di un Jolly
    return True


def is_continous(canasta):
    lista_carte = sorted(canasta, key=lambda x: x.numeroCarta)
    # Controlla che ogni carta successiva abbia numero consecutivo
    old_num = lista_carte[0].numeroCarta
    jolly_used = False
    for card in lista_carte[1:]:
        gap = card.numeroCarta - old_num
        if gap == 1:
            old_num = card.numeroCarta
        elif gap == 2 and not jolly_used:
            jolly_used = True
            old_num = card.numeroCarta
        else:
            return False
    return True
""" 
    for prev, curr in zip(lista_carte, lista_carte[1:]):
        if curr.numeroCarta != prev.numeroCarta + 1:
            return False
    return True """

def isBurracoPulito(canasta):
    return isBurraco(canasta) and not has_jolly_or_pinella_clean(canasta)

def remove_jolly_pinella(lista_carte):
    onto = get_onto()
    return [card for card in lista_carte if not isinstance(card, (onto.Jolly, onto.Pinella))]

def reset_deck():
    # pulisco le mani dei giocatori per iniziare un nuovo round
    onto = get_onto()
    for player in onto.Player.instances():
            player.playerHand.mazzo.clear()

    # pulisco il monte da cui raccogliere e gli scarti
    monte = get_monte()
    scarti = get_scarti()
    monte.clear()
    scarti.clear()

    # mischio le carte
    all_cards_in_ontology = list(get_all_cards())
    random.seed(int(datetime.now().strftime("%S%f")))
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
    get_manager().salva_ontologia_update_game()
    get_manager().salva_ontologia_init_game()


def add_discarded_cards_to_pickup():
    onto = get_onto()
    scarti = onto.Game.instances()[0].scarto.mazzo
    log = SingletonLogger().get_logger()
    #log.info(f"  [add_discarded_to_pickup PRE - [SCARTI] ------> {onto.Game.instances()[0].scarto.mazzo}]")
    #log.info(f"  [add_discarded_to_pickup PRE - [MONTE]  ------> {onto.Game.instances()[0].monte.mazzo}]")

    onto.Game.instances()[0].monte.mazzo = scarti[:len(scarti) - 1]
    set_da_rimuovere = set(onto.Game.instances()[0].monte.mazzo)
    lista_risultato = [
        elemento 
        for elemento in scarti 
        if elemento not in set_da_rimuovere
    ]
    onto.Game.instances()[0].scarto.mazzo = lista_risultato
    #log.info(f"  [add_discarded_to_pickup POST - [SCARTI] ------> {onto.Game.instances()[0].scarto.mazzo}]")
    #log.info(f"  [add_discarded_to_pickup POST - [MONTE]  ------> {onto.Game.instances()[0].monte.mazzo}]")

    get_manager().salva_ontologia_update_game()
    
def scarica_ontologia():
    get_manager().scarica_ontologia()