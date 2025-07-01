from owlready2 import *
import Ontologia.OntoManager as OntoManager
from Ontologia.OntoManager import OntologyResource

onto = OntoManager.get_ontology_from_manager(OntologyResource.UPDATED_GAME)

def get_card_number(card):
    if hasattr(card, 'numeroCarta') and card.numeroCarta is not None:
        return card.numeroCarta
    return None

#Gestisce la pesca dal monte:
#la elimina dal mazzo della partita per inserirla nella mano del giocatore
def pesca_carta(player, game):
    monte = game.monte 
    card = monte.mazzo[0]
    monte.mazzo.remove(card)
    player.playerHand.mazzo.append(card)
     # Salva le modifiche all'ontologia
    OntoManager.salva_ontologia_init_game()

#Il giocatore scarta una carta: 
#elimina dalla mano del giocatore e la aggiunge alla pila degli scarti
def scarta_carta(player, card, game):
    player.playerHand.mazzo.remove(card)
    game.scarto.mazzo.append(card)
    card.cartaVisibile = False
    OntoManager.salva_ontologia_init_game()


#Permette al giocatore di calare una nuova canasta.
def apre_canasta(player, cards, save = False):
    #capire se tris o scala
    #istanziarla
    #associarla al giocatore

    semeScala = None
    skip = True
    isScala = False
    canasta = None
    for card in cards:
        #la carta diventa visibile per tutti
        card.cartaVisibile = True
        player.playerHand.mazzo.remove(card)
        #salta i Jolly
        if hasattr(card, 'seme'):
            if skip:
                skip = False
                semeScala = card.seme
            else:
                if semeScala == card.seme:
                    isScala = True
                    break

    if isScala:
        canasta = apre_scala(player, cards,semeScala)
    else:
        canasta = apre_tris(player, cards)
    
    if save:
        OntoManager.salva_ontologia_init_game()
    
    return canasta

def apre_canasta_test(player, cards):
    #capire se tris o scala
    #istanziarla
    #associarla al giocatore

    numeroCarta = None
    isScala = False
    canasta = None
    seme_scala =  None
    for card in cards:
        #la carta diventa visibile per tutti
        card.cartaVisibile = True
        #salta i Jolly
        if hasattr(card, 'numeroCarta'):
            if numeroCarta is None:
                numeroCarta = card.numeroCarta
            #da affinare, casi particolari (es. A,2,2)
            elif numeroCarta != card.numeroCarta:
                    isScala = True
                    seme_scala = card.seme

    if isScala:
        canasta = apre_scala(player, cards,seme_scala)
    else:
        canasta = apre_tris(player, cards)
    
    OntoManager.salva_ontologia_update_game()
    
    return canasta

#crea una nuova scala e la aggiunge al giocatore
def apre_scala(player, cards, seme):
    nuovaScala = onto.Scala("Scala_" + str(nScala)+ "_" + player.name)
    nScala = len(player.scala)
    nuovaScala.minValueScala = min(c.numeroCarta for c in cards)
    nuovaScala.maxValueScala = max(c.numeroCarta for c in cards)
    nuovaScala.semeScala = seme

    for card in cards:
        nuovaScala.hasCards.append(card)
        #aggiorna il punteggio del giocatore
        player.punteggioGiocatore += card.valoreCarta
        card.cartaVisibile = True
        player.playerHand.mazzo.remove(card)

    player.scala.append(nuovaScala)
    return nuovaScala

#crea una nuovo Tris e la aggiunge al giocatore
def apre_tris(player, cards):
    nTris = len(player.tris)
    nuovoTris = onto.Tris(f"Tris_" + str(nTris) + "_" + player.name)
    trisValue = None
    for card in cards:
        card.cartaVisibile = True
        player.playerHand.mazzo.remove(card)
        nuovoTris.hasCards.append(card)
        #aggiorna il punteggio del giocatore
        player.punteggioGiocatore += card.valoreCarta
        if hasattr(card, 'seme') and trisValue is None:
            trisValue = card.numeroCarta

    nuovoTris.trisValue = trisValue
    player.tris.append(nuovoTris)
    return nuovoTris

#permette al giocatore di aggiungere carte a un suo tris esistente sul tavolo, aggiornando il Tris.
def aggiunge_carte_tris(player, tris, cards_to_add, save = False): 
    for card in cards_to_add:
        tris.hasCards.append(card)
        player.playerHand.mazzo.remove(card)
        #aggiorna il punteggio del giocatore
        player.punteggioGiocatore += card.valoreCarta
        card.cartaVisibile = True
    if save: 
        OntoManager.salva_ontologia_init_game()
    return True


#permette al giocatore di aggiungere carte a una sua scala esistente sul tavolo, aggiornando la scala.
def aggiunge_carte_scala(player, target_scala, cards_to_add):

    for card in cards_to_add:
        # Aggiunge la carta alla scala nell'ontologia
        target_scala.hasCards.append(card)
        #  RimuovE la carta dalla mano del giocatore
        player.playerHand.mazzo.remove(card)
        #aggiorna il punteggio del giocatore
        player.punteggioGiocatore += card.valoreCarta
        # Rende la carta visibile (poichè è ora sul tavolo)
        card.cartaVisibile = True

    # In questa logica semplificata, contiamo solo le carte numerate "pure" per min/max,
    # TODO ma un CSP sarebbe necessario per assegnare correttamente il valore ai Jolly/Pinelle.
    all_numeric_cards_in_scala = [
        get_card_number(c) for c in target_scala.hasCards if get_card_number(c) is not None
    ]
    all_numeric_cards_in_scala = sorted(list(set(all_numeric_cards_in_scala))) 
    new_min_val = min(all_numeric_cards_in_scala)
    new_max_val = max(all_numeric_cards_in_scala)
    target_scala.minValueScala = new_min_val
    target_scala.maxValueScala = new_max_val

    OntoManager.salva_ontologia_init_game()

    return True


