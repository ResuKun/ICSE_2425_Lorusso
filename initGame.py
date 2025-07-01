#initGame
import random
import Ontologia.OntoManager as OntoManager
from Ontologia.OntoManager import OntologyResource

onto = OntoManager.get_ontology_from_manager(OntologyResource.CARD)

def init_game():
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

    start_player = createPlayer("1","Alessio", partita)
    createPlayer("2","Grazia", partita)
    partita.turnOf = start_player
    print(f"\nIl giocatore di turno all'inizio della partita è: {partita.turnOf.nomeGiocatore}")

    # Salva le modifiche all'ontologia
    OntoManager.salva_ontologia_init_game()
    # Creo una copia da aggiornare e una con lo start della partita
    OntoManager.salva_ontologia_update_game()


def createPlayer(number,name, partita):
    #creo i giocatori
    player1 = onto.Player("Giocatore" + number)
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