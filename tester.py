import sys
import Ontologia.onto_save_manager as onto_save_manager
import Player.player_onto_modifier as OntoModifier
import Player.player_csp_resolver as CSPResolver

onto = onto_save_manager.get_ontology_from_manager()

def test_resolver_all():
    print("--------------------------------------------------")
    print("PYTHONPATH:", sys.path)
    print("--------------------------------------------------")
    
    all_players = list(onto.Player.instances())
    player1 = all_players[0]

    # pulisco la mano del giocatore
    player1.playerHand.mazzo.clear()

    carte = [
        "7_Picche_Blu",
        "8_Picche_Rosso",
        "9_Picche_Blu",
        "10_Picche_Rosso",
        "4_Cuori_Rosso",
        "6_Cuori_Rosso",
        "Jolly_Jolly_N_Rosso"]
    
    lista_carte = []
    for card in carte:
        lista_carte.append(onto[card])

    player1.playerHand.mazzo.extend(lista_carte)

    CSPResolver.find_csp_scala(player1, player1.playerHand.mazzo)

    print(f"END")




import sys
def test_resolver():
    print("--------------------------------------------------")
    print("PYTHONPATH:", sys.path)
    print("--------------------------------------------------")
    
    all_players = list(onto.Player.instances())
    player1 = all_players[0]
    
    # (True,False) True per creare un tris, False per testare l'update di un tris esistente
    create_tris = False 
    player1.playerHand.mazzo.clear()

    if create_tris:
        create_tris_test(player1)
        create_scala_test(player1)
    else:
        add_card_scala(player1)
        #print(f"Mazzo Giocatore: {[card.name for card in player1.playerHand.mazzo]}")

       # tris_0 = onto["Tris_0_Giocatore1"]
        #CSPResolver.find_csp_tris(player1.playerHand.mazzo)

        #CSPResolver.can_update_csp_tris(player1.playerHand.mazzo,tris_0)
        CSPResolver.find_csp_scala(player1, player1.playerHand.mazzo)
        #find_csp_tris(player1.playerHand.mazzo)
        #create_scala_test(player1)

        CSPResolver.can_discard_card(player1)

        #scala = onto["Scala_0_Giocatore1"]
        #CSPResolver.can_update_csp_scala(player1, player1.playerHand.mazzo, scala)

        #player1 = all_players[1]
        #print(f"Mazzo Giocatore: {[card.name for card in player1.playerHand.mazzo]}")
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
    OntoModifier.apre_tris(player1,lista_carte)

def create_scala_test(player1):
    prima_carta = onto["8_Cuori_Rosso"]
    seconda_carta = onto["7_Cuori_Blu"]
    terza_carta = onto["9_Cuori_Blu"]
    lista_carte = [prima_carta, seconda_carta, terza_carta]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    OntoModifier.apre_scala(player1,lista_carte)

def add_card_tris(player1):
    prima_carta = onto["10_Cuori_Blu"]
    seconda_carta = onto["10_Cuori_Rosso"]
    terza_carta = onto["10_Picche_Rosso"]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    terza_carta = onto["Jolly_Jolly_R_Rosso"]
    player1.playerHand.mazzo.append(terza_carta)

def add_card_scala(player1):
    seconda_carta = onto["7_Picche_Blu"]
    prima_carta = onto["8_Picche_Rosso"]
    terza_carta = onto["9_Picche_Blu"]
    player1.playerHand.mazzo.append(prima_carta)
    player1.playerHand.mazzo.append(seconda_carta)
    player1.playerHand.mazzo.append(terza_carta)
    terza_carta = onto["Jolly_Jolly_R_Rosso"]
    player1.playerHand.mazzo.append(terza_carta)
    terza_carta = onto["10_Picche_Rosso"]
    player1.playerHand.mazzo.append(terza_carta)
    terza_carta = onto["10_Cuori_Blu"]
    player1.playerHand.mazzo.append(terza_carta)
    seconda_carta = onto["10_Cuori_Rosso"]
    player1.playerHand.mazzo.append(seconda_carta)



def add_card(player1):
    terza_carta = onto["Jolly_Jolly_R_Rosso"]
    player1.playerHand.mazzo.append(terza_carta)
    terza_carta = onto["3_Cuori_Blu"]
    player1.playerHand.mazzo.append(terza_carta)
    #seconda_carta = onto["Jolly_Jolly_R_Rosso"]
    #player1.playerHand.mazzo.append(seconda_carta)

#test_resolver_all()
test_resolver()