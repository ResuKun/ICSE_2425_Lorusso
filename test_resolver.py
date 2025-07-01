import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "aipython"))

from owlready2 import *
from aipython.cspProblem import Variable, Constraint, CSP
from operator import lt,ne,eq,gt,ge
from aipython.searchGeneric import Searcher
from aipython.cspDFS import dfs_solve_all
from aipython.cspSearch import Search_from_CSP
from playerAction import apre_canasta_test
import Ontologia.OntoManager as OntoManager

onto = OntoManager.get_ontology_from_manager()


def get_tuple_from_card(lista_carte, include_seme=True):
    lista_tuple = []
    for card in lista_carte:
        if not isinstance(card, (onto.Jolly, onto.Pinella)):
            if include_seme:
                mia_tupla = (card.numeroCarta, card.name, card.seme.name)
            else:
                mia_tupla = (card.numeroCarta, card.name)
            lista_tuple.append(mia_tupla)
        else:
            if include_seme:
                mia_tupla = (-1, card.name, "Jolly")
            else:
                mia_tupla = (-1, card.name)
            lista_tuple.append(mia_tupla)
        
    return lista_tuple

def get_tuple_from_tris(tris):
    lista_tris = []
    contain_jolly = False
    for card in tris.hasCards:
        if not isinstance(card, (onto.Jolly, onto.Pinella)) and (card.numeroCarta, card.name) not in lista_tris:
            mia_tupla = (card.numeroCarta, card.name)
            lista_tris.append(mia_tupla)
        elif isinstance(card, (onto.Jolly, onto.Pinella)):
            mia_tupla = (-1, card.name)
            lista_tris.append(mia_tupla)
            contain_jolly = True
            
    return lista_tris, contain_jolly

#Controlla che non ci siano duplicati tra le carte
#se le carte sono duplicate ritorna False, altrimenti True
#usato per evitare che si creino scale o tris con carte duplicate
def has_no_duplicate(*lista_carte):
    return len(lista_carte) == len(set(lista_carte))


#Da centralizzare eventualmente, copia di playerAction.py
def get_card_number(card):
    if hasattr(card, 'numeroCarta') and card.numeroCarta is not None:
        return card.numeroCarta
    return None

#Da centralizzare
def remove_jolly_pinella(lista_carte):
    return [card for card in lista_carte if not isinstance(card, (onto.Jolly, onto.Pinella))]

#condizioni per creazione delle scale / aggiunta delle carte a scala
def doppio_jolly_combinazione(carta, contain_jolly):
    #se la scala contiene un Jolly o Pinella e provo ad aggiungerne un altro ritorna Falso
    if carta[0] == -1 and contain_jolly[0]:
        return False
    return True


def doppio_jolly_lista(*lista_carte):
    if lista_carte[0][1] == "6_Quadri_Blu" and lista_carte[1][1] == "2_Picche_Rosso" and lista_carte[2][1] == "2_Cuori_Rosso":
        print("debug")

    lista_carte = [x for x in lista_carte if x[0] == -1]
    return len(lista_carte) < 2


def stesso_seme_scala(lista_carte, scala):
    seme_scala = scala.semeScala
    lista_carte = remove_jolly_pinella(lista_carte)
    for card in lista_carte:
        if seme_scala != card.seme:
            return False
    return True

def stesso_seme_lista(*lista_carte):
    lista_carte = list(lista_carte)
    #rimuovo i Jolly
    if any(num[0] == -1 for num in lista_carte):
        lista_carte[:] = [x for x in lista_carte if x[0] != -1]

    seme_riferimento = lista_carte[0][2]
    return all(tupla[2] == seme_riferimento for tupla in lista_carte )


def stesso_numero_tris(card, tris):
    return card[0] == tris[1]

#controlla che le carte abbiano lo stesso numero
#e che non siano la stessa carta (es. 10_Cuori_Blu,
def stesso_numero_lista(*lista_carte):
    lista_carte = list(lista_carte)

    #controllo che non ci siano doppioni
    if len(lista_carte) != len(set(lista_carte)):
        return False
        
    if all(num[0] == -1 for num in lista_carte):
        print(f"Errore: tutti i numeri sono Jolly : {[num[1] for num in lista_carte]}")
        return False
    
    #rimuovo i Jolly
    if any(num[0] == -1 for num in lista_carte):
        lista_carte[:] = [x for x in lista_carte if x[0] != -1]

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


def in_scala(lista_carte, scala):
    #da raffinare con i controlli di esistenza di un jolly nella scala e della sua eventuale possibilità di muoversi
    special_card = any(isinstance(card, (onto.Jolly, onto.Pinella)) for card in lista_carte)
    
    min_scala = scala.minValueScala
    max_scala = scala.maxValueScala
    min_number = min(c.numeroCarta for c in lista_carte)
    max_number = max(c.numeroCarta for c in lista_carte)

    lista_in_scala = (min_number == max_scala + 1) or (min_number == max_scala + 2 and special_card) or (max_number == min_scala - 1) or (max_number == min_scala - 2 and special_card)

    return lista_in_scala

#lista_carte
def lista_contigua(*lista_carte):
    lista_carte = list(lista_carte)

    if lista_carte[0][1] == "Q_Cuori_Blu" and lista_carte[1][1] == "J_Cuori_Rosso" and lista_carte[2][1] == "10_Cuori_Rosso":
        print("debug")

    old_num = None
    found_jolly = False
    if any(num[0] == -1 for num in lista_carte):
        found_jolly = True
        lista_carte[:] = [x for x in lista_carte if x[0] != -1]

    #ordino le carte per numeroCarta e controllo che siano contigue
    #se presente un jolly concedo un "buco" nella lista
    lista_carte = sorted(lista_carte, key=lambda x: x[0])
    for num,_,_ in lista_carte:
        if old_num is None:
            old_num = num
        elif old_num is not None:
            if (old_num + 1) < num and found_jolly is False:
                return False
            elif (old_num + 2) < num and found_jolly:
                return False
            else: 
                old_num = num
                print("corretto")
            #    print(f"caso strano old: {old_num} - new: {num}")
    return True
    
#check di fine partita, per ora controlliamo solo che le carte in mano siano terminate
def check_end_game_condition(player_hand):
    return len(player_hand.mazzo) == 0


## -------------- START PROBLEMI CSP -------------- ##

## SCALE  ##
#Creazione di una scala

#controlla se esiste una Scala fattibile con le carte a disposizione
#la scala può essere composta da 3 carte dello stesso seme, oppure da 2 carte dello stesso seme e un Jolly o Pinella
def find_csp_scala(lista_carte):
    print(f"Start find_csp_scala --> lista_carte: {lista_carte}" )
    
    lista_tuple = get_tuple_from_card(lista_carte)
   
    # Costruisce le variabili da selezionare (tris di 3 carte)
    var1 = Variable("c1", lista_tuple)
    var2 = Variable("c2", lista_tuple)
    var3 = Variable("c3", lista_tuple)

    vars_tris = [var1, var2, var3]
    csp = CSP("find_csp_scala",
              vars_tris,
              [
                Constraint(vars_tris, lambda *args: len(set(args)) <= 3, "minimo 3 carte"),
                Constraint(vars_tris, has_no_duplicate, "has_no_duplicate"),
                Constraint(vars_tris, doppio_jolly_lista,"doppio_jolly_lista"),
                Constraint(vars_tris, stesso_seme_lista,"stesso_seme_lista"),
                Constraint(vars_tris, lista_contigua,"lista_contigua"),
              ])
    

    #list_solution = dfs_solve_all(csp)
    searcher = Searcher(Search_from_CSP(csp))
    list_solution = []
    while searcher.frontier:
        result = searcher.search()
        list_solution.append(result)

    print(f"\n\n\n [ find_csp_scala ] SOLUZIONI TROVATE-->")
    print(f"{[sol for sol in list_solution]}")
    print(f"------------------------------------------------------------------------\n\n\n")
    return list_solution

#Update di una scala
def can_update_csp_scala(lista_carte, scala):
    # def __init__(self, title, variables, constraints):
    update_scala_CSP = CSP("update_scala_CSP",
        [lista_carte, scala],
        [
        Constraint([lista_carte,scala], doppio_jolly_combinazione,"doppio_jolly_combinazione"),
        Constraint(lista_carte, doppio_jolly_lista,"doppio_jolly_lista"),
        Constraint([lista_carte,scala], stesso_seme_scala,"stesso_seme_scala"),
        Constraint(lista_carte, stesso_seme_lista,"stesso_seme_lista"),
        Constraint([lista_carte,scala], in_scala,"in_scala"),
        Constraint(lista_carte, lista_contigua,"lista_contigua"),
        ])
    
    searcher = Searcher(Search_from_CSP(update_scala_CSP))
    result = None
    list_solution = []
    while searcher.frontier:
        result = searcher.search()
        if result is not None:
            list_solution.append(result)

    print(f"\n\n\n[ can_update_csp_scala ] SOLUZIONI TROVATE-->")
    print(f"{[sol for sol in list_solution]}")
    print(f"------------------------------------------------------------------------\n\n\n")
    return list_solution

## TRIS  ##
#Creazione di un TRIS
#controlla se esiste un Tris fattibile tra le carte
def find_csp_tris(lista_carte):
    print(f"Start find_csp_tris --> lista_carte: {lista_carte}" )
    
    lista_numeri = get_tuple_from_card(lista_carte, False)
    # Costruisce le variabili da selezionare (tris di 3 carte)
    var1 = Variable("c1", lista_numeri)
    var2 = Variable("c2", lista_numeri)
    var3 = Variable("c3", lista_numeri)

    vars_tris = [var1, var2, var3]
    csp = CSP("find_csp_tris",
              vars_tris,
              [
                  Constraint(vars_tris, lambda *args: len(set(args)) <= 3, "minimo 3 carte"),
                  Constraint(vars_tris, has_no_duplicate, "has_no_duplicate"),
                  Constraint(vars_tris, doppio_jolly_lista, "doppio_jolly_lista"),
                  Constraint(vars_tris, stesso_numero_lista, "stesso_numero_lista")
              ])
    
    searcher = Searcher(Search_from_CSP(csp))
    result = None
    list_solution = []
    while searcher.frontier:
        result = searcher.search()
        if result is not None:
            list_solution.append(result)

    print(f"\n\n\n [ find_csp_tris ] SOLUZIONI TROVATE-->")
    print(f"{[sol for sol in list_solution]}")
    print(f"------------------------------------------------------------------------\n\n\n")
    return list_solution


#Update di un TRIS
def can_update_csp_tris(lista_carte, tris):
    # def __init__(self, title, variables, constraints):
    lista_numeri = get_tuple_from_card(lista_carte)
    lista_tris = []
    contain_jolly = False
    for card in tris.hasCards:
        if not isinstance(card, (onto.Jolly, onto.Pinella)) and (card.numeroCarta, card.name) not in lista_tris:
            mia_tupla = (card.numeroCarta, card.name)
            lista_tris.append(mia_tupla)
        elif isinstance(card, (onto.Jolly, onto.Pinella)):
            mia_tupla = (-1, card.name)
            lista_tris.append(mia_tupla)
            contain_jolly = True

    trisValue_list = []
    tupla = (contain_jolly, tris.trisValue)
    trisValue_list.append(tupla)

    var1 = Variable("c1", lista_numeri)
    var2 = Variable("c2", trisValue_list)
    vars_jolly_single = [var1, var2]

    update_scala_CSP = CSP("update_scala_CSP",
        vars_jolly_single,
        [
            Constraint(vars_jolly_single, doppio_jolly_combinazione,"doppio_jolly_combinazione"),
            Constraint(vars_jolly_single, stesso_numero_tris,"stesso_numero_tris"),
        ])
    
    searcher = Searcher(Search_from_CSP(update_scala_CSP))
    result = None
    list_solution = []
    while searcher.frontier:
        result = searcher.search()
        if result is not None:
            list_solution.append(result)

    print(f"\n\n\n [ can_update_csp_tris ] SOLUZIONI TROVATE-->")
    print(f"{[sol for sol in list_solution]}")
    print(f"------------------------------------------------------------------------\n\n\n")
    return list_solution
    

#fine partita
def can_end_game_csp(player):
    player_hand = player.playerHand
    # def __init__(self, title, variables, constraints):
    end_game_csp = CSP("end_game_CSP",
        [player_hand], # La variabile è la mano del giocatore
        [
        Constraint([player_hand], check_end_game_condition, "player_hand_is_empty")
        ]
    )
    
    searcher = Searcher(Search_from_CSP(end_game_csp))
    result = searcher.search()
    print(f"can_end_game_csp --> player: {player.nomeGiocatore} --> player_hand: {player_hand}")
    return result


import sys
def test_resolver():
    print("--------------------------------------------------")
    print("PYTHONPATH:", sys.path)
    print("--------------------------------------------------")
    
    all_players = list(onto.Player.instances())
    player1 = all_players[0]
    
    # (True,False) True per creare un tris, False per testare l'update di un tris esistente
    create_tris = False 
    
    if create_tris:
        create_tris_test(player1)
    else:

        print(f"Mazzo Giocatore: {[card.name for card in player1.playerHand.mazzo]}")
        tris_0 = onto["Tris_0_Giocatore1"]
        #can_update_csp_tris(player1.playerHand.mazzo,tris_0)
        find_csp_scala(player1.playerHand.mazzo)
        #find_csp_tris(player1.playerHand.mazzo)
       # can_update_csp_tris(player1.playerHand.mazzo,tris_0)

        player1 = all_players[1]
        print(f"Mazzo Giocatore: {[card.name for card in player1.playerHand.mazzo]}")
        #can_update_csp_tris(player1.playerHand.mazzo,tris_0)
    
    #find_csp_scala(player1.playerHand.mazzo)
    #result1 = find_csp_tris(player1.playerHand.mazzo)
    print(f"END")

def create_tris_test(player1):
    prima_carta = onto["10_Cuori_Blu"]
    seconda_carta = onto["10_Cuori_Rosso"]
    terza_carta = onto["10_Picche_Rosso"]
    lista_carte = [prima_carta, seconda_carta, terza_carta]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    apre_canasta_test(player1,lista_carte)

def create_scala_test(player1):
    prima_carta = onto["8_Picche_Rosso"]
    seconda_carta = onto["7_Picche_Blu"]
    terza_carta = onto["9_Picche_Blu"]
    lista_carte = [prima_carta, seconda_carta, terza_carta]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    apre_canasta_test(player1,lista_carte)

test_resolver()