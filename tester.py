import sys
import Player.player_onto_manager as OntoModifier
import Player.player_csp_resolver as CSPResolver
import Utils.checks as checks
import Ontologia.initGame as initGame
from Ontologia.onto_save_manager import OntologyManager, OntologyResource



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
    create_tris = False 
    #player1.playerHand.mazzo.clear()

    #if create_tris:
    create_tris_test(player1, onto)
    create_scala_test(player1, onto)
   # else:
        #print(f"Mazzo Giocatore: {[card.name for card in player1.playerHand.mazzo]}")

    add_card_scala(player1, onto)
    scala_0 = onto["Scala_0_Giocatore0"]
    #result_2 = CSPResolver.can_update_csp_scala(player1, player1.playerHand.mazzo,scala_0)

    add_card_tris(player1, onto)
    tris_0 = onto["Tris_0_Giocatore0"]
    #result_1 = CSPResolver.find_csp_tris(player1)
    result_2 = CSPResolver.can_update_csp_tris(player1, player1.playerHand.mazzo,tris_0)

    result = CSPResolver.get_possible_meld_to_update(player1)
    #result_2 = CSPResolver.find_csp_scala(player1)
        #find_csp_tris(player1.playerHand.mazzo)
        #create_scala_test(player1)
    print(result)
    add_card(player1, onto)
    scala = onto["Tris_0_Giocatore0"]
    #result = CSPResolver.can_update_csp_scala(player1, player1.playerHand.mazzo, scala, True)

        #player1 = all_players[1]
        #print(f"Mazzo Giocatore: {[card.name for card in player1.playerHand.mazzo]}")
        #tris_0 = onto["Tris_0_Giocatore1"]
        #result_2 = CSPResolver.can_update_csp_tris(player1, player1.playerHand.mazzo,tris_0)


    print(f"results: {result}")
        #print(f"results_2: {result_2}")
    #find_csp_scala(player1.playerHand.mazzo)
    #result1 = find_csp_tris(player1.playerHand.mazzo)
    print(f"END")

def create_tris_test(player1, onto):
    prima_carta = onto["10_Cuori_Blu"]
    seconda_carta = onto["10_Cuori_Rosso"]
    terza_carta = onto["10_Picche_Rosso"]
    lista_carte = [prima_carta, seconda_carta, terza_carta]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    OntoModifier.apre_tris(player1,lista_carte, True)

def create_scala_test(player1, onto):
    prima_carta = onto["K_Cuori_Rosso"]
    seconda_carta = onto["J_Cuori_Blu"]
    terza_carta = onto["Q_Cuori_Blu"]
    lista_carte = [prima_carta, seconda_carta, terza_carta]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    OntoModifier.apre_scala(player1,lista_carte, True)

def add_card_tris(player1, onto):
    prima_carta = onto["10_Cuori_Rosso"]
    seconda_carta = onto["5_Cuori_Rosso"]
    terza_carta = onto["10_Picche_Blu"]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(terza_carta)
    player1.playerHand.mazzo.append(seconda_carta)

def add_card_scala(player1, onto):
    seconda_carta = onto["6_Cuori_Blu"]
    player1.playerHand.mazzo.append(seconda_carta)
    terza_carta = onto["J_Picche_Blu"]
    player1.playerHand.mazzo.append(terza_carta)
    terza_carta = onto["Jolly_Jolly_R_Rosso"]
    player1.playerHand.mazzo.append(terza_carta)




def add_card(player1, onto):
    player1.playerHand.mazzo.append(onto["8_Picche_Rosso"])

#test_resolver_all()
test_resolver()