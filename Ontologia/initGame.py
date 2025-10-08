#initGame
import random
import Ontologia.onto_save_manager as onto_save_manager
from Ontologia.onto_save_manager import OntologyResource
import Utils.CONST as CONST

#onto = onto_save_manager.get_ontology_from_manager(OntologyResource.CARD)


def get_onto():
    if not hasattr(get_onto, "_onto"):
        get_onto._onto = onto_save_manager.get_ontology_from_manager()
    return get_onto._onto

def init_game(players_names = ["Alessio", "MariaGrazia"]):

    if len(players_names) > CONST.CardValues.MAX_PLAYER.value:
        raise TypeError("Numero massimo di giocatori consentito : " + CONST.CardValues.MAX_PLAYER.value)

    partita = get_onto().Game("Partita")
    partita.monte = get_onto().Monte("Monte_della_partita")
    partita.scarto = get_onto().Scarto("Scarto_della_partita")

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
    player1 = get_onto().Player("Giocatore" + number)
    player1.idGiocatore = number
    player1.nomeGiocatore = name
    player1.punteggioGiocatore = 0
    #aggiungo i giocatori alla partita
    partita.players.append(player1)
    return player1

#init_game()