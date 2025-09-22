from owlready2 import *
import Ontologia.onto_save_manager as onto_save_manager
import Ontologia.onto_access_util as onto_access_util
import Utils.CONST as CONST

onto = onto_save_manager.get_ontology_from_manager()
game = onto.Game.instances()[0]

def get_player_score(player):
	return player.punteggioGiocatore

def get_card_number(card):
	if hasattr(card, 'numeroCarta') and card.numeroCarta is not None:
		return card.numeroCarta
	return None


def reset_players_hands():
	monte = onto_access_util.get_monte()
	for player in onto_access_util.get_player_list():
		mano, monte = (
			monte[:CONST.CardValues.NUM_CARDS_TO_DEAL.value],
			monte[CONST.CardValues.NUM_CARDS_TO_DEAL.value:])
		player.playerHand.mazzo.extend(mano)
	onto_save_manager.salva_ontologia_update_game()

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
	add_points_chiusura(player)
	onto_save_manager.salva_ontologia_update_game()

#crea una nuova scala e la aggiunge al giocatore
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

	for card in cards:
		nuovaScala.hasCards.append(card)
		#aggiorna il punteggio del giocatore
		player.punteggioGiocatore += card.valoreCarta
		card.cartaVisibile = True
		player.playerHand.mazzo.remove(card)

	player.scala.append(nuovaScala)

	#aggiungo i punti per il burraco se c'è
	add_points_burraco(nuovaScala, player)
	add_points_chiusura(player)
	onto_save_manager.salva_ontologia_update_game()
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
	#aggiungo i punti per il burraco se c'è
	add_points_burraco(nuovoTris, player)
	onto_save_manager.salva_ontologia_update_game()
	return nuovoTris

#permette al giocatore di aggiungere carte a un suo tris esistente sul tavolo, aggiornando il Tris.
def aggiunge_carte_tris(player, tris, cards_to_add): 
	for card in cards_to_add:
		tris.hasCards.append(card)
		player.playerHand.mazzo.remove(card)
		#aggiorna il punteggio del giocatore
		player.punteggioGiocatore += card.valoreCarta
		card.cartaVisibile = True
		
	#aggiungo i punti per il burraco se c'è
	add_points_burraco(tris, player)
	onto_save_manager.salva_ontologia_update_game()
	return True


#permette al giocatore di aggiungere carte a una sua scala esistente sul tavolo, aggiornando la scala.
def aggiunge_carte_scala(player, target_scala, cards_to_add):

	for card in cards_to_add:
		# Aggiunge la carta alla scala nell'ontologia
		target_scala.hasCards.append(card)
		#  Rimuove la carta dalla mano del giocatore
		player.playerHand.mazzo.remove(card)
		#aggiorna il punteggio del giocatore
		player.punteggioGiocatore += card.valoreCarta
		# Rende la carta visibile (poichè è ora sul tavolo)
		card.cartaVisibile = True

	# TODO debuggare il pezzo successivo, probabilmente inutile
	all_numeric_cards_in_scala = [
		get_card_number(c) for c in target_scala.hasCards if get_card_number(c) is not None
	]
	all_numeric_cards_in_scala = sorted(list(set(all_numeric_cards_in_scala))) 
	new_min_val = min(all_numeric_cards_in_scala)
	new_max_val = max(all_numeric_cards_in_scala)
	target_scala.minValueScala = new_min_val
	target_scala.maxValueScala = new_max_val

	#aggiungo i punti per il burraco se c'è
	add_points_burraco(target_scala, player)
	add_points_chiusura(player)
	onto_save_manager.salva_ontologia_update_game()
	return True


def add_points_burraco(canasta, player):
	points = 0
	if onto_access_util.isBurracoPulito(canasta):
		points = 200
	elif onto_access_util.isBurraco(canasta):
		points = 100
	player.punteggioGiocatore += points
	return points

def add_points_chiusura(player):
	if len(player.playerHand.mazzo) == 0:
		#aggiungo i punti per la chiusura
		player.punteggioGiocatore += 100