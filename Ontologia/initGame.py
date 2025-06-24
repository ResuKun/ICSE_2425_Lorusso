#initGame
from owlready2 import *
import random

ontology_file_path = "C:/Users/alexl/Documents/Facolta/ICSE/Progetto/Burraco/ICSE_2425_Lorusso/Ontologia/Cards_Ontology.owl"
ontology_file_save = "C:/Users/alexl/Documents/Facolta/ICSE/Progetto/Burraco/ICSE_2425_Lorusso/Ontologia/Cards_Ontology_Updated.owl"
onto = get_ontology(ontology_file_path).load()


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
        print("Card:", card)
        monte_gioco.mazzo.append(card) # Cambiato da partita.monte.mazzo.append(card)

    primo_scarto = monte_gioco.mazzo[0]
    scarto_gioco.mazzo.append(primo_scarto)
    partita.monte.mazzo.remove(primo_scarto)

    start_player = createPlayer("1","Alessio", partita)
    createPlayer("2","Grazia", partita)
    partita.turnOf = start_player
    print(f"\nIl giocatore di turno all'inizio della partita è: {partita.turnOf.nomeGiocatore}")

    # Salva le modifiche all'ontologia
    onto.save(file = ontology_file_save, format = "rdfxml")
    print(f"\nOntologia aggiornata con la mano del giocatore salvata in {ontology_file_save}")





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
    
    for card in mano:
        player1.playerHand.mazzo.append(card)
        partita.monte.mazzo.remove(card)
    
    for card in player1.playerHand.mazzo:
        seme_str = card.seme.name if card.seme else "N/A"
        numero_str = card.numeroCarta if hasattr(card, 'numeroCarta') else "Special"
        valore_str = card.valoreCarta
        print(f"- {card.name} (Seme: {seme_str}, Numero/Tipo: {numero_str}, Valore: {valore_str})")
    
    return player1

init_game()