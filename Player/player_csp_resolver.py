import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "aipython"))

from owlready2 import *
from aipython.cspProblem import Variable, Constraint, CSP
#from operator import lt,ne,eq,gt,ge
from aipython.searchGeneric import Searcher
from aipython.cspSearch import Search_from_CSP
#from aipython.cspDFS import *
#from Player.player_onto_modifier import apre_canasta_test
import Ontologia.onto_access_util as onto_access_util
import Utils.checks as checks
from Ontologia.onto_save_manager import OntologyManager, OntologyResource
from Utils.CONST import CardValues

#carica l'ontologia (singleton)
def get_manager():
    return OntologyManager()

def get_onto():
    return onto_access_util.get_onto()
#da rendere adattivo , magari in base al numero di carte 
#dato che con poche carte si abbasano le probabilità di trovare combinazioni
#fino a 5 è gestibile
MELD_DEFAULT_DEPTH = 3

## -------------- START PROBLEMI CSP -------------- ##


def solve_csp(csp, vars, is_update = False):
    searcher = Searcher(Search_from_CSP(csp))
    unique_combinations = set()
    while searcher.frontier:
        result = searcher.search()
        tuple_res = checks.get_tuple_from_csp_results(vars, result)
        if tuple_res is not None:
            tuple_res_no_dupes = list(dict.fromkeys(tuple_res))
            #combination = frozenset(tuple_res)
            combination = frozenset(tuple_res_no_dupes)
            unique_combinations.add(combination)

    # Converto l'insieme di combinazioni
    # in una lista di set cosi da evitare duplicati
    solutions_list = []
    for elem in unique_combinations:
        partial_solution = list(elem)
        if not is_update:
            partial_solution.sort(key=lambda x: x[0])
        else:
            partial_solution.sort(key=lambda x: len(x))
        solutions_list.append(partial_solution)

    # Rimuovo i placeholder dalle soluzioni
    for i in range(len(solutions_list)):
        solutions_list[i] = checks.clean_from_placeholder(solutions_list[i])

    return solutions_list


## SCALE  ##
#Creazione di una scala

#controlla se esiste una Scala fattibile con le carte a disposizione
#la scala deve essere composta da 3 carte dello stesso seme, oppure da 2 carte dello stesso seme e un Jolly o Pinella
def find_csp_scala(player):
    lista_carte = player.playerHand.mazzo
    #print(f"Start find_csp_scala --> lista_carte: {lista_carte}" )
    
    lista_tuple = checks.get_tuple_from_cards(lista_carte)
    lista_tuple.append(CardValues.PLACEHOLDER_OBJECT.value)
    # Costruisce le variabili da selezionare (tris di 3 carte)
    vars_tris = []

    # +2 per il range
    for i in range(1, MELD_DEFAULT_DEPTH + 1):
        var = Variable(f"c{i}", lista_tuple)
        vars_tris.append(var)

    #versione closure delle regole di gioco
    regole_di_gioco = checks.closure_player_regole_di_gioco(player)
    csp = CSP("find_csp_scala",
              vars_tris,
              [
                Constraint(vars_tris, checks.has_no_duplicate, "has_no_duplicate"),
                Constraint(vars_tris, checks.same_number_card, "same_number_card"),
                Constraint(vars_tris, checks.three_or_more_cards, "minimo 3 carte"),
                Constraint(vars_tris, regole_di_gioco,"regole_di_gioco"),
                Constraint(vars_tris, checks.doppio_jolly_lista,"doppio_jolly_lista"),
                Constraint(vars_tris, checks.stesso_seme_lista,"stesso_seme_lista"),
                Constraint(vars_tris, checks.lista_contigua,"lista_contigua"),
              ])

    solutions_list = solve_csp(csp, vars_tris)
   # print(f"\n\n\n [ find_csp_scala ] SOLUZIONI TROVATE-->")
   # print(f"------------------------------------------------------------------------\n\n\n")
   # print(*solutions_list, sep="\n")
   # print(f"------------------------------------------------------------------------\n\n\n")
    return sort_combination_by_value(solutions_list)

#Update di una scala
# restituisce una lista di coppie (Scala - Carta) in formato tupla
def can_update_csp_scala(player, lista_carte, scala):

    lista_tuple = checks.get_tuple_from_cards(lista_carte)
    lista_scala = [ checks.get_scala_normalized(scala)]

    carte_scala = [checks.get_tuple_from_cards(scala.hasCards)]

    #versione closure delle regole di gioco
    regole_di_gioco = checks.closure_player_regole_di_gioco(player)

    var = Variable("c1", lista_tuple)
    var2 = Variable("c2", lista_scala)
    var3 = Variable("c3", carte_scala)
    update_scala_CSP = CSP("update_scala_CSP",
         [var, var2, var3],
        [
            Constraint(  [var], regole_di_gioco,"regole_di_gioco"),
            Constraint( [var, var2], checks.doppio_jolly_combinazione,"doppio_jolly_combinazione"),
            Constraint( [var, var2], checks.stesso_seme_scala,"stesso_seme_scala"),
            #Constraint( [var, var2], checks.in_scala,"in_scala")
            Constraint( [var3, var] , checks.lista_contigua_with_card,"lista_contigua"),
        ])
    
    solutions_list = solve_csp(update_scala_CSP,  [var, var2], True)

    #print(f"\n\n\n[ can_update_csp_scala ] SOLUZIONI TROVATE-->")
    #print(f"{[sol for sol in solutions_list]}")
    #print(f"------------------------------------------------------------------------\n\n\n")
    return solutions_list

def get_possible_meld_to_update(player):
    list_meld = []
    #TODO da debuggare
    for meld in player.scala:
        list_meld += can_update_csp_scala(player, player.playerHand.mazzo, meld)
    return list_meld
    
## TRIS  ##
#Creazione di un TRIS
#controlla se esiste un Tris fattibile tra le carte
def find_csp_tris(player):
    lista_carte = player.playerHand.mazzo
    #print(f"Start find_csp_tris --> lista_carte: {lista_carte}" )
    
    lista_tuple = checks.get_tuple_from_cards(lista_carte)
    lista_tuple.append(CardValues.PLACEHOLDER_OBJECT.value)
    # Costruisce le variabili da selezionare (tris di 3 carte)
    vars_tris = []
    # +1 per il range
    for i in range(1, MELD_DEFAULT_DEPTH + 1):
        var = Variable(f"c{i}", lista_tuple)
        vars_tris.append(var)

    #versione closure delle regole di gioco
    regole_di_gioco = checks.closure_player_regole_di_gioco(player)

    csp = CSP("find_csp_tris",
              vars_tris,
              [
                Constraint(vars_tris, checks.three_or_more_cards, "minimo 3 carte"),
                Constraint(vars_tris, checks.has_no_duplicate, "has_no_duplicate"),
                Constraint(vars_tris, regole_di_gioco,"regole_di_gioco"),
                Constraint(vars_tris, checks.doppio_jolly_lista, "doppio_jolly_lista"),
                Constraint(vars_tris, checks.stesso_numero_lista, "stesso_numero_lista"),
              ])
    
    solutions_list = solve_csp(csp, vars_tris)

   #print(f"\n\n\n [ find_csp_tris ] SOLUZIONI TROVATE-->")
   #print(f"{[sol for sol in solutions_list]}")
   #print(f"------------------------------------------------------------------------\n\n\n")
    return sort_combination_by_value(solutions_list)


#Update di un TRIS
def can_update_csp_tris(player, lista_carte, tris):
    # def __init__(self, title, variables, constraints):
    lista_numeri = checks.get_tuple_from_cards(lista_carte, True)

    trisValue_list = []
    contain_jolly = any(isinstance(card, (get_onto().Jolly, get_onto().Pinella)) for card in tris.hasCards)
    tupla = (contain_jolly, tris.trisValue, tris.trisId)
    trisValue_list.append(tupla)

    #versione closure delle regole di gioco
    regole_di_gioco = checks.closure_player_regole_di_gioco(player)

    var1 = Variable("c1", lista_numeri)
    var2 = Variable("c2", trisValue_list)
    vars_jolly_single = [var1, var2]

    update_scala_CSP = CSP("update_scala_CSP",
        vars_jolly_single, #mettere le variabili
        [
            Constraint(vars_jolly_single, regole_di_gioco,"regole_di_gioco"),
            Constraint(vars_jolly_single, checks.doppio_jolly_combinazione,"doppio_jolly_combinazione"),
            Constraint(vars_jolly_single, checks.stesso_numero_tris,"stesso_numero_tris"),
        ])
    
    solutions_list = solve_csp(update_scala_CSP, vars_jolly_single, True)

    #print(f"\n\n\n [ can_update_csp_tris ] SOLUZIONI TROVATE-->")
    #print(f"{[sol for sol in solutions_list]}")
    #print(f"------------------------------------------------------------------------\n\n\n")
    return solutions_list

def get_possible_tris_to_update(player):
    list_meld = []
    for meld in player.tris:
        list_meld.extend(can_update_csp_tris(player, player.playerHand.mazzo, meld))
    return list_meld

# effettua i check per verificare se il giocatore può chiudere la partita
# restituisce l'unica carta da scartare nel caso di chiusura
def can_end_game_csp(player):
    player_hand = checks.get_tuple_from_cards(player.playerHand.mazzo)
    regole_di_gioco = checks.closure_player_close_game(player)
    var1 = Variable("c1", player_hand)
    end_game_csp = CSP("end_game_CSP",
        [var1], 
        [
            Constraint([var1], checks.only_one_card, "solo una carta"),
            Constraint([var1], regole_di_gioco,"regole_di_gioco")]
    )
    
    #searcher = Searcher(Search_from_CSP(end_game_csp))
    #result = searcher.search()
    result = solve_csp(end_game_csp, [var1], True)
    return result

def can_pick_up():
    pass

#ordina la lista di combinazioni in base al loro valore (somma dei valori delle singole carte)
def sort_combination_by_value(solutions_list):
    if solutions_list is not None and len(solutions_list) > 0:
        len_tuple = len(solutions_list[0][0]) -1
    return sorted(solutions_list, key=lambda sublist: sum(item[len_tuple] for item in sublist), reverse=True)
