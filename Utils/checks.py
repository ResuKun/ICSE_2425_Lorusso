from owlready2 import *
import Ontologia.onto_access_util as onto_access_util
from Ontologia.onto_save_manager import OntologyManager, OntologyResource
from Utils.CONST import CardValues


def get_tuple_from_cards(lista_carte, include_seme=True):
	lista_tuple = []
	for card in lista_carte:
		if not isinstance(card, (OntologyManager().get_onto().Jolly)):
			if include_seme:
				mia_tupla = (card.numeroCarta, card.idCarta, card.seme.name, card.valoreCarta)
			else:
				mia_tupla = (card.numeroCarta, card.idCarta, card.valoreCarta)
			lista_tuple.append(mia_tupla)
		else:
			if include_seme:
				mia_tupla = (CardValues.JOLLY_VALUE.value, card.idCarta, "Jolly", card.valoreCarta)
			else:
				mia_tupla = (CardValues.JOLLY_VALUE.value, card.idCarta, card.valoreCarta)
			lista_tuple.append(mia_tupla)
		
	return lista_tuple

def get_tuple_from_csp_results(lista_variabili, result):
	if result is None:
		return None
	lista_risultato = []
	for var in lista_variabili:
		var_value = result.arc.to_node[var]
		if var_value is not None:
			lista_risultato.append(var_value)
	return lista_risultato

""" def get_tuple_from_tris(tris):
	lista_tris = []
	contain_jolly = False
	for card in tris.hasCards:
		if not isinstance(card, (onto.Jolly, onto.Pinella)) and (card.numeroCarta, card.name) not in lista_tris:
			mia_tupla = (card.numeroCarta, card.name)
			lista_tris.append(mia_tupla)
		elif isinstance(card, (onto.Jolly, onto.Pinella)):
			mia_tupla = (CardValues.JOLLY_VALUE.value, card.name)
			lista_tris.append(mia_tupla)
			contain_jolly = True
			
	return lista_tris, contain_jolly """

def has_jolly_or_pinella_tuple(lista_carte):
	return any( [x for x in lista_carte if is_jolly_or_pinella(x[0])])

#Rimuove i placeholder (None) dalla lista delle carte
def clean_from_placeholder(lista_carte):
	res_list = [card for card in lista_carte if card[0] != CardValues.PLACEHOLDER_VALUE.value]
	return res_list

#Controlla che la lista di carte contenga almeno 3 carte
def three_or_more_cards(*lista_carte):
	filtered_list = clean_from_placeholder(lista_carte)
	return len(set(filtered_list)) >= 3

#Controlla che la lista di carte contenga 1 sola carta
def only_one_card(*lista_carte):
	filtered_list = clean_from_placeholder(lista_carte)
	return len(set(filtered_list)) == 1

#Controlla che non ci siano duplicati tra le carte
#se le carte sono duplicate ritorna False, altrimenti True
#usato per evitare che si creino scale o tris con carte duplicate
def has_no_duplicate(*lista_carte):
	# pulisco la lista dai placeholder None
	arr_clean = clean_from_placeholder(lista_carte)
	return len(arr_clean) == len(set(arr_clean))

#Controlla che non ci siano duplicati tra le carte
#a differenza del precedente considera solo il primo elemento
def same_number_card(*lista_carte):
	# pulisco la lista dai placeholder None
	arr_clean = clean_from_placeholder(lista_carte)
	numero_carta_list = [card[0] for card in arr_clean]
	return len(numero_carta_list) == len(set(numero_carta_list))


#Da centralizzare eventualmente, copia di playerAction.py
def get_card_number(card):
	if hasattr(card, 'numeroCarta') and card.numeroCarta is not None:
		return card.numeroCarta
	return None


#condizioni per creazione delle scale / aggiunta delle carte a scala
def doppio_jolly_combinazione(carta, contain_jolly):
	#se la scala contiene un Jolly o Pinella e provo ad aggiungerne un altro ritorna Falso
	if contain_jolly[0]:
		return not (is_jolly_or_pinella(carta[0]))
	else:
		return True

	
def doppio_jolly_lista(*lista_carte):
	lista_carte = [x for x in lista_carte if is_jolly_or_pinella(x[0])]
	return len(lista_carte) < 2

#scala normalizzata (has_jolly, seme, min, max)
def stesso_seme_scala(carta, scala):
	return scala[1] == carta[2] if not is_jolly_or_pinella(carta[0]) else True

def stesso_seme_lista(*lista_carte):
	lista_carte = list(lista_carte)
	lista_carte = clean_from_placeholder(lista_carte)
	#rimuovo i Jolly
	if any(is_jolly_or_pinella(num[0]) for num in lista_carte):
		lista_carte = [x for x in lista_carte if not is_jolly_or_pinella(x[0])]

	seme_riferimento = lista_carte[0][2]
	result = all(tupla[2] == seme_riferimento for tupla in lista_carte )
	return result 

def stesso_numero_tris(card, tris):
	return card[0] == tris[1] if not is_jolly_or_pinella(card[0]) else True

#controlla che le carte abbiano lo stesso numero
#e che non siano la stessa carta (es. 10_Cuori_Blu,
def stesso_numero_lista(*lista_carte):
	lista_carte = list(lista_carte)
	lista_carte = clean_from_placeholder(lista_carte)

	#controllo che non ci siano doppioni
	if len(lista_carte) != len(set(lista_carte)):
		return False
		
	if all( is_jolly_or_pinella(num[0]) for num in lista_carte):
		print(f"Errore: tutti i numeri sono Jolly : {[num[1] for num in lista_carte]}")
		return False
	
	#rimuovo i Jolly
	if any(is_jolly_or_pinella(num[0]) for num in lista_carte):
		lista_carte[:] = [x for x in lista_carte if not is_jolly_or_pinella(x[0])]

	valore_riferimento = lista_carte[0][0]
	#controllo che abbiano tutti lo stesso numero (Jolly gia esclusi)
	if all(tupla[0] == valore_riferimento for tupla in lista_carte[1:]):
		# controllo che non siano la stessa carta
		valori_elementi = [tupla[1] for tupla in lista_carte]
		if len(valori_elementi) != len(set(valori_elementi)):
			# se sono carte diverse ( non ci sono doppioni) e hanno tutte lo stesso numero, allora va bene
			return False
	else: 
		return False
	
	return True


#scala normalizzata (has_jolly, seme, min, max, lista_numeri)
def in_scala(carta, scala):
	if is_jolly_or_pinella(carta[0]) and not scala[0]:
		return True
	#se la carta e' gia' presente nella scala non va bene
	if carta[0] in scala[4]:
		return False
	return (carta[0] == scala[2] -1 
		 	or carta[0] == scala[3] +1 
			or (scala[3] > carta[0] > scala[2]))

def lista_contigua_with_card(lista_carte, card = None):
	lista_carte.append(card)
	test = tuple(lista_carte)
	return lista_contigua((test))

#lista_carte
def lista_contigua(*lista_carte):
	if len(lista_carte) == 1:
		lista_carte = lista_carte[0]
	lista_carte = clean_from_placeholder(lista_carte)
	old_num = None
	found_jolly = False
	if any(is_jolly_or_pinella(num[0]) for num in lista_carte):
		found_jolly = True
		lista_carte[:] = [x for x in lista_carte if not is_jolly_or_pinella(x[0])]

	#ordino le carte per numeroCarta e controllo che siano contigue
	#se presente un jolly concedo un "buco" nella lista
	old_num = lista_carte[0][0]
	jolly_used = False
	for num, *_ in lista_carte[1:]:
		gap = num - old_num
		if gap == 1:
			old_num = num
		elif gap == 2 and found_jolly and not jolly_used:
			jolly_used = True
			old_num = num
		else:
			return False

	return True

#ritorna una tupla normalizzata della scala
def get_scala_normalized(scala):
	lista_numeri = tuple([carta.numeroCarta for carta in scala.hasCards])
	has_jolly = onto_access_util.has_jolly_or_pinella_clean(scala)
	return (has_jolly, scala.semeScala.name, scala.minValueScala, scala.maxValueScala, lista_numeri, scala.scalaId)

def get_player_normalized(player):
	return tuple(player)
	
#controlla delle regole di gioco anticipando anche 
# la condizione di chiusura partita scendendo una o più carte:
#   se ho solo una carta 
#   (e la mia squadra ha già raccolto il pozzo (DA IMPLEMENTARE))
#	   la mia squadra deve avere almeno una canasta (pura/impura)
#	   e l'ultima carta che scarto non deve essere una pinella/jolly

def regole_di_gioco(player, is_closing_game, *cards_to_play):
	cards_to_play = clean_from_placeholder(cards_to_play)
	mano_player = get_tuple_from_cards(player.playerHand.mazzo)
	result = False
	#filtro le carte che voglio giocare
	if not is_closing_game:
		mano_player = list( set(mano_player) - set(cards_to_play))
	if len(mano_player) > 1:
		result = not is_closing_game
	if( len(mano_player) == 1 
		and (any(onto_access_util.isBurraco(scala) for scala in player.scala)
			or any(onto_access_util.isBurraco(tris) for tris in player.tris))
		and not has_jolly_or_pinella_tuple(mano_player)
		):
		result = True
	return result

def closure_player_regole_di_gioco(player):
	def constraint(*carte):
		return regole_di_gioco(player, False, *carte)
	return constraint

def closure_player_close_game(player):
	def constraint(*carte):
		return regole_di_gioco(player, True, *carte)
	return constraint

def is_jolly_or_pinella(num):
	return num == CardValues.JOLLY_VALUE.value or num == CardValues.PINELLA_VALUE.value