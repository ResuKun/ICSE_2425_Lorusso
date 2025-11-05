#initGame
import random
from Ontologia.onto_save_manager import OntologyManager, OntologyResource
import Utils.CONST as CONST
from Utils.logger import SingletonLogger 
from datetime import datetime

def init_game_files(debug_mode):
    if debug_mode:
        #debug mode per tester.py
        manager = OntologyManager()
        manager.create_init_file_test()
        manager.create_update_file_test()
    else:
        manager = OntologyManager()
        # Salva le modifiche all'ontologia
        manager.create_init_file()
        # Creo una copia da aggiornare e una con lo start della partita
        manager.create_update_file()

def get_onto(debug_mode = False):
    if not hasattr(get_onto, "_onto"):
        manager = OntologyManager()
        get_onto._manager= manager
        if debug_mode:
            get_onto._onto = manager.get_ontology_from_manager(OntologyResource.UPDATED_GAME_TEST)
        else:
            get_onto._onto = manager.get_ontology_from_manager()
    return get_onto._onto, get_onto._manager

def init_game(players_names = ["Alessio", "MariaGrazia"],  debug_mode = False):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    gamename = "Partita_" + timestamp
    SingletonLogger.init(name="gioco", partita = gamename)
    init_game_files(debug_mode)

    if len(players_names) > CONST.CardValues.MAX_PLAYER.value:
        raise TypeError("Numero massimo di giocatori consentito : " + CONST.CardValues.MAX_PLAYER.value)
    onto, manager = get_onto(debug_mode)
    partita = onto.Game(gamename)
    partita.monte = onto.Monte("Monte_della_partita")
    partita.scarto = onto.Scarto("Scarto_della_partita")

    if len(players_names) == 0:
        raise TypeError("Deve esserci almeno un giocatore per iniziare la partita.")
    if len(players_names) % 2 != 0:
        raise TypeError("Il numero di giocatori deve essere pari.")
    
    partita.turnOf = createPlayer(0,players_names[0], partita)
    for i in range(1, len(players_names)):
        createPlayer(i, players_names[i], partita)

    print(f"\nIl giocatore di turno all'inizio della partita è: {partita.turnOf.nomeGiocatore}")

    # Salva le modifiche all'ontologia
    manager.salva_ontologia_init_game(OntologyResource.INIT_GAME_TEST)
    manager.salva_ontologia_update_game(OntologyResource.UPDATED_GAME_TEST)
    return partita


def createPlayer(number,name, partita):
    #creo i giocatori
    onto,_ = get_onto()
    player1 = onto.Player("Giocatore" + str(number))
    player1.idGiocatore = number
    player1.nomeGiocatore = name
    player1.punteggioGiocatore = 0
    player1.playerHand = onto.Mano(f"Mano_di_{player1.name}")
    player1.playerHand.mazzo = []
    #aggiungo i giocatori alla partita
    partita.players.append(player1)
    return player1

if __name__ == "__main__":
    init_game()