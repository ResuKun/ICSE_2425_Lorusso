from owlready2 import *
import Ontologia.onto_save_manager as onto_save_manager
import Ontologia.onto_access_util as onto_access_util
import Utils.CONST as CONST
import CSP.checks as checks

onto = onto_save_manager.get_ontology_from_manager()
game = onto.Game.instances()[0]

def get_player_score(player):
	return player.punteggioGiocatore

def get_card_number(card):
	if hasattr(card, 'numeroCarta') and card.numeroCarta is not None:
		return card.numeroCarta
	return None

def get_player_known_cards(player):
	return [card for card in player.playerHand.mazzo if card.cartaNota ]

def get_player_unknown_cards(player):
	return [card for card in player.playerHand.mazzo if card.cartaNota == False ]

def get_player_cards(player):
	return player.playerHand.mazzo

def get_player_melds(player):
	return player.scala

def get_player_tris(player):
	return player.tris

def reset_players_hands():
	monte = onto_access_util.get_monte()
	for player in onto_access_util.get_player_list():
		mano, monte = (
			monte[:CONST.CardValues.NUM_CARDS_TO_DEAL.value],
			monte[CONST.CardValues.NUM_CARDS_TO_DEAL.value:])
		player.playerHand.mazzo.extend(mano)
	onto_save_manager.salva_ontologia_update_game()

#restitusce le tuple della mano del giocatore
def get_players_card(player):
    return checks.get_tuple_from_card(player.playerHand.mazzo)

#Gestisce la pesca dal monte:
#la elimina dal mazzo della partita per inserirla nella mano del giocatore
def pesca_carta(player):
	monte = game.monte 
	card = monte.mazzo[0]
	monte.mazzo.remove(card)
	player.playerHand.mazzo.append(card)
	 # Salva le modifiche all'ontologia
	onto_save_manager.salva_ontologia_update_game()

#Gestisce la pesca dagli scarti:
#svuota la pila degli scarti della partita 
#per inserirla nella mano del giocatore
def pesca_scarti(player):
	cards = game.scarto.mazzo[:]
	len_cards = len(cards)

	#le carte tornano non visibili
	for card in cards:
		card.cartaVisibile = False

	game.scarto.mazzo.clear()
	player.playerHand.mazzo.extend(cards)
	 # Salva le modifiche all'ontologia
	onto_save_manager.salva_ontologia_update_game()
	return len_cards

#Il giocatore scarta una carta: 
#elimina dalla mano del giocatore e la aggiunge alla pila degli scarti

def scarta_carta(player, card_id):
	card = onto_access_util.get_card_from_id(card_id)
	player.playerHand.mazzo.remove(card)
	game.scarto.mazzo.append(card)
	card.cartaVisibile = True
	card.cartaNota = True
	onto_save_manager.salva_ontologia_update_game()

def chiudi_gioco(player, card_id):
	card = onto_access_util.get_card_from_id(card_id)
	player.playerHand.mazzo.remove(card)
	game.scarto.mazzo.append(card)
	card.cartaVisibile = True
	card.cartaNota = True
	add_points_chiusura(player)
	onto_save_manager.salva_ontologia_update_game()

#crea una nuova scala e la aggiunge al giocatore
#restituisce il punteggio 
def apre_scala(player, cards):
	nScala = len(player.scala)
	nuovaScala = onto.Scala("Scala_" + str(nScala)+ "_" + player.name)
	nuovaScala.minValueScala = min(c.numeroCarta for c in cards)
	nuovaScala.maxValueScala = max(c.numeroCarta for c in cards)

	#ignoro i jolly/pinelle per il seme della scala
	#sono sicuro della coerenza per i c
	for card in cards:
		if hasattr(card, 'seme'):
			seme = card.seme
			break

	nuovaScala.semeScala = seme

	partialScore = 0
	for card in cards:
		nuovaScala.hasCards.append(card)
		#aggiorna il punteggio del giocatore
		partialScore += card.valoreCarta
		card.cartaVisibile = True
		card.cartaNota = True
		player.playerHand.mazzo.remove(card)

	player.punteggioGiocatore += partialScore
	player.scala.append(nuovaScala)

	#aggiungo i punti per il burraco se c'è
	#commentati in quanto per ora non è possibile 
	#scendere con una sola azione più di 5 carte 
	# per questioni di performance
	#partialScore += add_points_burraco(nuovaScala, player)
	#partialScore += add_points_chiusura(player)
	onto_save_manager.salva_ontologia_update_game()
	return partialScore

#crea una nuovo Tris e la aggiunge al giocatore
def apre_tris(player, cards):
	nTris = len(player.tris)
	nuovoTris = onto.Tris(f"Tris_" + str(nTris) + "_" + player.name)
	trisValue = None

	partialScore = 0
	for card in cards:
		card.cartaVisibile = True
		card.cartaNota = True
		player.playerHand.mazzo.remove(card)
		nuovoTris.hasCards.append(card)
		#aggiorna il punteggio del giocatore
		partialScore += card.valoreCarta
		if hasattr(card, 'seme') and trisValue is None:
			trisValue = card.numeroCarta

	player.punteggioGiocatore += partialScore
	nuovoTris.trisValue = trisValue
	player.tris.append(nuovoTris)

	#aggiungo i punti per il burraco se c'è
	#commentati in quanto per ora non è possibile 
	#scendere con una sola azione più di 5 carte 
	# per questioni di performance
	#partialScore += add_points_burraco(nuovaScala, player)
	#partialScore += add_points_chiusura(player)
	onto_save_manager.salva_ontologia_update_game()
	return partialScore

#permette al giocatore di aggiungere carte a un suo tris esistente sul tavolo, aggiornando il Tris.
def aggiunge_carta_tris(player, tris, card):
	partialScore = card.valoreCarta
	tris.hasCards.append(card)
	player.playerHand.mazzo.remove(card)
	#aggiorna il punteggio del giocatore
	player.punteggioGiocatore += card.valoreCarta
	card.cartaVisibile = True
	card.cartaNota = True
		
	#aggiungo i punti per il burraco se c'è
	partialScore += add_points_burraco(tris, player)
	partialScore += add_points_chiusura(player)

	onto_save_manager.salva_ontologia_update_game()
	return partialScore


#permette al giocatore di aggiungere carte a una sua scala esistente sul tavolo, aggiornando la scala.
def aggiunge_carta_scala(player, target_scala, card):

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
	partialScore += add_points_chiusura(player)
	onto_save_manager.salva_ontologia_update_game()
	return partialScore


def add_points_burraco(canasta, player):
	points = 0
	if onto_access_util.isBurracoPulito(canasta):
		points = 200
	elif onto_access_util.isBurraco(canasta):
		points = 100
	player.punteggioGiocatore += points
	return points

def add_points_chiusura(player):
	partialScore = 0 if len(player.playerHand.mazzo) == 0 else 100
	player.punteggioGiocatore += partialScore
	return partialScore