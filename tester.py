import sys
import Player.player_onto_manager as OntoModifier
import Player.player_csp_resolver as CSPResolver
import Utils.checks as checks
import Ontologia.initGame as initGame
from Ontologia.onto_save_manager import OntologyManager, OntologyResource

def get_manager():
    if not hasattr(get_manager, "_manager"):
        get_manager._manager = OntologyManager()
    return get_manager._manager

def get_onto():
    if not hasattr(get_onto, "_onto"):
        get_onto._onto = get_manager().get_ontology_from_manager(OntologyResource.UPDATED_GAME_TEST)
    return get_onto._onto

import sys
def test_resolver():
    print("--------------------------------------------------")
    print("PYTHONPATH:", sys.path)
    print("--------------------------------------------------")
   # initGame.init_game(players_names = ["Alessio", "MariaGrazia"],  debug_mode = True)
    
    all_players = list(get_onto().Player.instances())
    player1 = all_players[0]
    
    # (True,False) True per creare un tris, False per testare l'update di un tris esistente
    create_tris = False 
   # player1.playerHand.mazzo.clear()

    #if create_tris:
    #create_tris_test(player1)
    #create_scala_test(player1)
   # else:
        #print(f"Mazzo Giocatore: {[card.name for card in player1.playerHand.mazzo]}")

        #CSPResolver.find_csp_tris(player1.playerHand.mazzo)

        #CSPResolver.can_update_csp_tris(player1.playerHand.mazzo,tris_0)
        #CSPResolver.find_csp_scala(player1, player1.playerHand.mazzo)
        #find_csp_tris(player1.playerHand.mazzo)
        #create_scala_test(player1)

    add_card(player1)
    scala = get_onto()["Tris_6_Giocatore0"]
    result = CSPResolver.can_update_csp_tris(player1, player1.playerHand.mazzo, scala, True)

        #player1 = all_players[1]
        #print(f"Mazzo Giocatore: {[card.name for card in player1.playerHand.mazzo]}")
        #tris_0 = get_onto()["Tris_0_Giocatore1"]
        #result_2 = CSPResolver.can_update_csp_tris(player1, player1.playerHand.mazzo,tris_0)


    print(f"results: {result}")
        #print(f"results_2: {result_2}")
    #find_csp_scala(player1.playerHand.mazzo)
    #result1 = find_csp_tris(player1.playerHand.mazzo)
    print(f"END")

def create_tris_test(player1):
    prima_carta = get_onto()["10_Cuori_Blu"]
    seconda_carta = get_onto()["10_Cuori_Rosso"]
    terza_carta = get_onto()["10_Picche_Rosso"]
    lista_carte = [prima_carta, seconda_carta, terza_carta]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    OntoModifier.apre_tris(player1,checks.get_tuple_from_cards(lista_carte))

def create_scala_test(player1):
    prima_carta = get_onto()["8_Cuori_Rosso"]
    seconda_carta = get_onto()["7_Cuori_Blu"]
    terza_carta = get_onto()["2_Picche_Blu"]
    lista_carte = [prima_carta, seconda_carta, terza_carta]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    OntoModifier.apre_scala(player1,checks.get_tuple_from_cards(lista_carte, True, True), True)

def add_card_tris(player1):
    prima_carta = get_onto()["10_Cuori_Blu"]
    seconda_carta = get_onto()["10_Cuori_Rosso"]
    terza_carta = get_onto()["10_Picche_Rosso"]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    terza_carta = get_onto()["Jolly_Jolly_R_Rosso"]
    player1.playerHand.mazzo.append(terza_carta)

def add_card_scala(player1):
    seconda_carta = get_onto()["7_Picche_Blu"]
    prima_carta = get_onto()["8_Picche_Rosso"]
    terza_carta = get_onto()["9_Picche_Blu"]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    terza_carta = get_onto()["Jolly_Jolly_R_Rosso"]
    player1.playerHand.mazzo.append(terza_carta)
    terza_carta = get_onto()["10_Picche_Rosso"]
    player1.playerHand.mazzo.append(terza_carta)
    terza_carta = get_onto()["10_Cuori_Blu"]
    player1.playerHand.mazzo.append(terza_carta)
    seconda_carta = get_onto()["10_Cuori_Rosso"]
    player1.playerHand.mazzo.append(seconda_carta)



def add_card(player1):
    player1.playerHand.mazzo.append(get_onto()["8_Picche_Rosso"])

#test_resolver_all()
test_resolver()