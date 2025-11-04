from owlready2 import *
from Ontologia.onto_save_manager import OntologyManager
import Ontologia.onto_access_util as onto_access_util
import Utils.CONST as CONST
import Utils.checks as checks


#carica l'ontologia (singleton)
def get_manager():
    if not hasattr(get_manager, "_manager"):
        get_manager._manager = OntologyManager()
    return get_manager._manager

def get_onto():
    if not hasattr(get_onto, "_onto"):
        manager = get_manager()
        get_onto._onto = manager.get_ontology_from_manager()
    return get_onto._onto

def get_game():
    return get_onto().Game.instances()[0]

def get_player_score(player):
	return player.punteggioGiocatore

def get_card_number(card):
	if hasattr(card, 'numeroCarta') and card.numeroCarta is not None:
		return card.numeroCarta
	return None

def get_player_known_cards(player):
	return [card for card in player.playerHand.mazzo if card.cartaNota ]

def get_player_unknown_cards(player):
	return [card for card in player.playerHand.mazzo if not card.cartaNota ]

def get_player_cards(player):
	return player.playerHand.mazzo

def get_player_melds(player):
	return player.scala

def get_player_tris(player):
	return player.tris

def reset_players_hands():
	mazzo = get_game().monte.mazzo
	for player in onto_access_util.get_player_list():
		mano = ( mazzo[:CONST.CardValues.NUM_CARDS_TO_DEAL.value])
		set_da_rimuovere = set(mano)
		lista_risultato = [
			elemento 
			for elemento in mazzo 
			if elemento not in set_da_rimuovere
		]
		get_game().monte.mazzo = lista_risultato
		player.playerHand.mazzo.extend(mano)

	get_manager().salva_ontologia_update_game()
	print("")

#restitusce le tuple della mano del giocatore
def get_players_card(player):
    return checks.get_tuple_from_cards(player.playerHand.mazzo)

#Gestisce la pesca dal monte:
#la elimina dal mazzo della partita per inserirla nella mano del giocatore
def pesca_carta(player):
	monte = get_game().monte 
	card = monte.mazzo[0]
	monte.mazzo.remove(card)
	player.playerHand.mazzo.append(card)
	 # Salva le modifiche all'ontologia
	get_manager().salva_ontologia_update_game()
	print("")

#Gestisce la pesca dagli scarti:
#svuota la pila degli scarti della partita 
#per inserirla nella mano del giocatore
def pesca_scarti(player):
	cards = get_game().scarto.mazzo[:]
	len_cards = len(cards)

	#le carte tornano non visibili
	for card in cards:
		card.cartaVisibile = False

	get_game().scarto.mazzo.clear()
	player.playerHand.mazzo.extend(cards)
	 # Salva le modifiche all'ontologia
	get_manager().salva_ontologia_update_game()
	return len_cards

#Il giocatore scarta una carta: 
#elimina dalla mano del giocatore e la aggiunge alla pila degli scarti

def scarta_carta(player, card_id):
	card = onto_access_util.get_card_from_id(card_id)
	player.playerHand.mazzo.remove(card)
	get_game().scarto.mazzo.append(card)
	card.cartaVisibile = True
	card.cartaNota = True
	get_manager().salva_ontologia_update_game()
	print("")

def chiudi_gioco(player, card_id):
	card = onto_access_util.get_card_from_id(card_id)
	player.playerHand.mazzo.remove(card)
	get_game().scarto.mazzo.append(card)
	card.cartaVisibile = True
	card.cartaNota = True
	add_points_chiusura(player)
	get_manager().salva_ontologia_update_game()

#crea una nuova scala e la aggiunge al giocatore
#restituisce il punteggio 
def apre_scala(player, cards):
	nScala = len(player.scala)
	nuovaScala = get_onto().Scala("Scala_" + str(nScala)+ "_" + player.name)
	nuovaScala.scalaId = len(get_onto().Scala.instances())
	nuovaScala.minValueScala = min(c[0] for c in cards if c[0] != -1)
	nuovaScala.maxValueScala = max(c[0] for c in cards if c[0] != -1)
	nuovaScala.isBurracoClosed = False

	#ignoro i jolly/pinelle per il seme della scala
	#sono sicuro della coerenza per i c
	for card in cards:
		if card[0] != CONST.CardValues.JOLLY_VALUE.value:
			nuovaScala.semeScala = next(s for s in get_onto().Seme.instances() if s.name == card[2])
			break

	partialScore = 0
	onto_cards = onto_access_util.get_cards_from_id_list([c[1] for c in cards])
	for card in onto_cards:
		nuovaScala.hasCards.append(card)
		#aggiorna il punteggio del giocatore
		partialScore += card.valoreCarta
		card.cartaVisibile = True
		card.cartaNota = True
		player.playerHand.mazzo.remove(card)

	player.punteggioGiocatore += partialScore
	nuovaScala.punteggioScala = partialScore
	player.scala.append(nuovaScala)

	player.scala = sorted(player.scala, key = sort_meld)

	#aggiungo i punti per il burraco se c'è
	#commentati in quanto per ora non è possibile 
	#scendere con una sola azione più di 5 carte 
	# per questioni di performance
	get_manager().salva_ontologia_update_game()
	return partialScore

#crea una nuovo Tris e la aggiunge al giocatore
from Utils.logger import SingletonLogger 
def apre_tris(player, tuple_cards):
	log = SingletonLogger().get_logger()
	nTris = len(player.tris)
	nuovoTris = get_onto().Tris(f"Tris_" + str(nTris) + "_" + player.name)
	nuovoTris.trisId = len(get_onto().Tris.instances())
	trisValue = None
	
	cards = onto_access_util.get_cards_from_id_list([x[1] for x in tuple_cards])

	partialScore = 0
	for card in cards:
		card.cartaVisibile = True
		card.cartaNota = True
		player.playerHand.mazzo.remove(card)
		nuovoTris.hasCards.append(card)
		#aggiorna il punteggio del giocatore
		partialScore += card.valoreCarta
		log.info(f" {card.name} -{card.valoreCarta} ----> partialScore ----> {partialScore}")
		if hasattr(card, 'seme') and trisValue is None:
			trisValue = card.numeroCarta

	player.punteggioGiocatore += partialScore
	nuovoTris.trisValue = trisValue
	nuovoTris.isTrisClosed = False
	nuovoTris.punteggioTris = partialScore
	log.info(f"FINAL partialScore ----> {partialScore}")

	player.tris.append(nuovoTris)

	#aggiungo i punti per il burraco se c'è
	#commentati in quanto per ora non è possibile 
	#scendere con una sola azione più di 5 carte 
	# per questioni di performance
	get_manager().salva_ontologia_update_game()
	return partialScore

#permette al giocatore di aggiungere carte a un suo tris esistente sul tavolo, aggiornando il Tris.
def aggiunge_carta_tris(player, tris_id, card_id):
	tris = onto_access_util.get_tris_from_id(tris_id)
	card = onto_access_util.get_card_from_id(card_id)
	partialScore = card.valoreCarta
	tris.hasCards.append(card)
	player.playerHand.mazzo.remove(card)
	#aggiorna il punteggio del giocatore
	player.punteggioGiocatore += card.valoreCarta
	card.cartaVisibile = True
	card.cartaNota = True
		
	#aggiungo i punti per il burraco se c'è
	partialScore += add_points_tris(tris, player)
	tris.punteggioTris += partialScore
	get_manager().salva_ontologia_update_game()
	return partialScore


#permette al giocatore di aggiungere carte a una sua scala esistente sul tavolo, aggiornando la scala.
def aggiunge_carta_scala(player, scala_id, card_id):
	card = onto_access_util.get_card_from_id(card_id)
	target_scala = onto_access_util.get_meld_from_id(scala_id)
	partialScore = card.valoreCarta
	# Aggiunge la carta alla scala nell'ontologia
	target_scala.hasCards.append(card)
	#  Rimuove la carta dalla mano del giocatore
	player.playerHand.mazzo.remove(card)
	#aggiorna il punteggio del giocatore
	player.punteggioGiocatore += partialScore
	# Rende la carta visibile (poichè è ora sul tavolo)
	card.cartaVisibile = True
	card.cartaNota = True

	card_number = [ get_card_number(c) for c in target_scala.hasCards if get_card_number(c) is not None ]
	target_scala.minValueScala = min(card_number)
	target_scala.maxValueScala = max(card_number)

	#aggiungo i punti per il burraco se c'è
	partialScore += add_points_burraco(target_scala, player)
	target_scala.punteggioScala += partialScore
	get_manager().salva_ontologia_update_game()
	return partialScore


def add_points_burraco(canasta, player):
	points = 0
	if not canasta.isBurracoClosed:
		if onto_access_util.isBurracoPulito(canasta):
			points = 200
			canasta.isBurracoClosed = True
		elif onto_access_util.isBurraco(canasta):
			points = 100
			canasta.isBurracoClosed = True
		player.punteggioGiocatore += points
	return points

def add_points_tris(canasta, player):
	points = 0
	if not canasta.isTrisClosed:
		if onto_access_util.isBurracoPulito(canasta):
			points = 200
			canasta.isTrisClosed = True
		elif onto_access_util.isBurraco(canasta):
			points = 100
			canasta.isBurraco = True
		player.punteggioGiocatore += points
	return points

def add_points_chiusura(player):
	partialScore = 0 if len(player.playerHand.mazzo) == 0 else 100
	player.punteggioGiocatore += partialScore
	return partialScore

def sort_meld(card):
	if card.numeroCarta != None:
		return card.numeroCarta
	return -1