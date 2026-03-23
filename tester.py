import sys
import Player.player_onto_manager as OntoModifier
import Player.player_csp_resolver as CSPResolver
import Utils.checks as checks
import Ontologia.initGame as initGame
from Ontologia.onto_save_manager import OntologyManager, OntologyResource
from rlcard.games.burraco.action_event_static import *
from rlcard.games.burraco.action_event_utils import (
                                get_open_tris_action_id,
                                get_open_meld_action_id,
                                get_tris_update_action_id,
                                get_meld_update_action_id)


import sys
def test_resolver():
    print("--------------------------------------------------")
    print("PYTHONPATH:", sys.path)
    print("--------------------------------------------------")
    partita = initGame.init_game(players_names = ["Alessio", "MariaGrazia"],  debug_mode = True)
    res = OntologyResource.UPDATED_GAME_TEST.value
    manager = OntologyManager()
    manager.reload_file_name()
    onto = manager.get_ontology_from_manager(res)

    all_players = list(onto.Player.instances())
    player1 = all_players[0]
    
    # (True,False) True per creare un tris, False per testare l'update di un tris esistente
    #player1.playerHand.mazzo.clear()

    #if create_tris:
    #def add_card_tris(player1, onto, value, value2 = "5", jolly = True):

    create_tris_test(player1, onto, "10")
    create_tris_test(player1, onto, "8")
    add_card_tris(player1, onto, "10")
    add_card_tris(player1, onto, "8", "7", False)
   # create_scala_test(player1, onto, "Cuori", "Blu")
   # create_scala_test(player1, onto, "Fiori")
   # else:
        #print(f"Mazzo Giocatore: {[card.name for card in player1.playerHand.mazzo]}")

    legal_actions = []
    potential_tris_upd = CSPResolver.get_possible_tris_to_update(player1)
    for tris_up_info in potential_tris_upd:
        #restituisce un array di action_ids perchè divisi per tris
        action_ids = get_tris_update_action_id(tris_up_info)
        #def __init__(self, tris_id, card_id, action_id)
        legal_actions.append(UpdateTrisAction(tris_up_info[1][2], tris_up_info[0][1], action_ids))
    
    #result_2 = CSPResolver.find_csp_scala(player1)
    #find_csp_tris(player1.playerHand.mazzo)
    #create_scala_test(player1)
    add_card(player1, onto)
    #result = CSPResolver.can_update_csp_scala(player1, player1.playerHand.mazzo, scala, True)

        #player1 = all_players[1]
        #print(f"Mazzo Giocatore: {[card.name for card in player1.playerHand.mazzo]}")
        #tris_0 = onto["Tris_0_Giocatore1"]
        #result_2 = CSPResolver.can_update_csp_tris(player1, player1.playerHand.mazzo,tris_0)


        #print(f"results_2: {result_2}")
    #find_csp_scala(player1.playerHand.mazzo)
    #result1 = find_csp_tris(player1.playerHand.mazzo)
    print(f"END")

def create_tris_test(player1, onto, value):
    prima_carta = onto[f"{value}_Cuori_Blu"]
    seconda_carta = onto[f"{value}_Cuori_Rosso"]
    terza_carta = onto[f"{value}_Picche_Rosso"]
    lista_carte = [prima_carta, seconda_carta, terza_carta]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    OntoModifier.apre_tris(player1,lista_carte, True)

def create_scala_test(player1, onto, seme, colore = "Rosso"):
    prima_carta = onto[f"10_{seme}_{colore}"]
    seconda_carta = onto[f"J_{seme}_{colore}"]
    terza_carta = onto[f"Q_{seme}_{colore}"]
    lista_carte = [prima_carta, seconda_carta, terza_carta]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    OntoModifier.apre_scala(player1,lista_carte, True)

def add_card_tris(player1, onto, value, value2 = "5", jolly = True):
    prima_carta = onto[f"{value}_Cuori_Rosso"]
    seconda_carta = onto[f"{value2}_Cuori_Rosso"]
    terza_carta = onto[f"{value}_Picche_Blu"]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(terza_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    if jolly:
        terza_carta = onto[f"Jolly_Jolly_R_Rosso"]
        player1.playerHand.mazzo.append(terza_carta)

def add_card_scala(player1, onto, seme, flag = True, colore = "Rosso"):
    seconda_carta = onto[f"9_{seme}_{colore}"]
    player1.playerHand.mazzo.append(seconda_carta)
    terza_carta = onto[f"K_{seme}_{colore}"]
    player1.playerHand.mazzo.append(terza_carta)
    if flag:
        terza_carta = onto[f"Jolly_Jolly_R_{colore}"]
        player1.playerHand.mazzo.append(terza_carta)




def add_card(player1, onto):
    player1.playerHand.mazzo.append(onto["8_Picche_Rosso"])

#test_resolver_all()
test_resolver()