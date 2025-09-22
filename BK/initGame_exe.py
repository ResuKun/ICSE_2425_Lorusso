#initGame
import random
import Ontologia.onto_save_manager as onto_save_manager
from Ontologia.onto_save_manager import OntologyResource
import Utils.CONST as CONST

onto = onto_save_manager.get_ontology_from_manager(OntologyResource.CARD)

        
def init_game(players_names = ["Alessio", "MariaGrazia"]):

    if len(players_names) > CONST.CardValues.MAX_PLAYER.value:
        raise TypeError("Numero massimo di giocatori consentito : " + CONST.CardValues.MAX_PLAYER.value)

    partita = onto.Game("Partita")
    monte_gioco = onto.Monte("Monte_della_partita") 
    partita.monte = monte_gioco 
    scarto_gioco = onto.Scarto("Scarto_della_partita")
    partita.scarto = scarto_gioco 

    #mischio le carte
    all_cards_in_ontology = list(onto.Card.instances())
    random.shuffle(all_cards_in_ontology)
    
    for card in all_cards_in_ontology:
        monte_gioco.mazzo.append(card) # Cambiato da partita.monte.mazzo.append(card)

    primo_scarto = monte_gioco.mazzo[0]
    scarto_gioco.mazzo.append(primo_scarto)
    partita.monte.mazzo.remove(primo_scarto)

    if len(players_names) == 0:
        raise TypeError("Deve esserci almeno un giocatore per iniziare la partita.")
    if len(players_names) % 2 != 0:
        raise TypeError("Il numero di giocatori deve essere pari.")
    
    partita.turnOf = createPlayer("1",players_names[0], partita)
    for i in range(1, len(players_names)):
        createPlayer(str(i+1), players_names[i], partita)

    print(f"\nIl giocatore di turno all'inizio della partita è: {partita.turnOf.nomeGiocatore}")

    # Salva le modifiche all'ontologia
    onto_save_manager.salva_ontologia_init_game()
    # Creo una copia da aggiornare e una con lo start della partita
    onto_save_manager.salva_ontologia_update_game()
    return partita


def createPlayer(number,name, partita):
    #creo i giocatori
    player1 = onto.Player("Giocatore" + number)
    player1.idGiocatore = number
    player1.nomeGiocatore = name
    player1.punteggioGiocatore = 0
    #aggiungo i giocatori alla partita
    partita.players.append(player1)
    #mano del giocatore
    num_cards_to_deal = 11
    player1.playerHand = onto.Mano(f"Mano_di_{player1.name}")
    mano = partita.monte.mazzo[:num_cards_to_deal]
    
    print(f"carte di {player1.nomeGiocatore} : ")
    for card in mano:
        print(f"{card.name}")
        player1.playerHand.mazzo.append(card)
        partita.monte.mazzo.remove(card)

    return player1

init_game()