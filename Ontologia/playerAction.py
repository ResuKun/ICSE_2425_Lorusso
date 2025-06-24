from owlready2 import *
import random

ontology_file_path = "C:/Users/alexl/Documents/Facolta/ICSE/Progetto/Burraco/Ontologia/Cards_Ontology.owl"
ontology_file_save = "C:/Users/alexl/Documents/Facolta/ICSE/Progetto/Burraco/Ontologia/Cards_Ontology_Updated.owl"
onto = get_ontology(ontology_file_path).load()

#Gestisce la pesca dal monte:
#la elimina dal mazzo della partita per inserirla nella mano del giocatore
def pesca_carta(player, game):
    monte = game.monte 
    card = monte.mazzo[0]
    monte.mazzo.remove(card)
    player.playerHand.mazzo.append(card)
     # Salva le modifiche all'ontologia
    onto.save(file = ontology_file_save, format = "rdfxml")
    print(f"\nOntologia aggiornata con la mano del giocatore salvata in {ontology_file_save}")

#Il giocatore scarta una carta: 
#elimina dalla mano del giocatore e la aggiunge alla pila degli scarti
def scarta_carta(player, card, game):
    player.playerHand.mazzo.remove(card)
    game.scarto.mazzo.append(card)
    card.cartaVisibile = False
    onto.save(file = ontology_file_save, format = "rdfxml")
    print(f"\nOntologia aggiornata con la mano del giocatore salvata in {ontology_file_save}")


#Permette al giocatore di calare una nuova canasta.
def apre_canasta(player, cards):
    #capire se tris o scala
    #istanziarla
    #associarla al giocatore

    semeScala = None
    numeroCarta = None
    skip = True

    for card in cards:
        card.cartaVisibile = True

        #salta i Jolly
        if hasattr(card, 'seme'):
            if skip:
                skip = False
                semeScala = card.seme
                numeroCarta = card.numeroCarta
            else:
                if semeScala == card.seme:
                    apre_scala(player, cards)
                else:
                    apre_tris(player, cards)
                

def apre_scala(player, cards):
    print("TODO")

def apre_tris(player, cards):
    print("TODO")
