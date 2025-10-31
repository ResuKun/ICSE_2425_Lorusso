from owlready2 import *
from Ontologia.onto_save_manager import OntologyResource

# Crea una nuova ontologia. L'IRI (Internationalized Resource Identifier) è l'identificatore unico
# dell'ontologia.
onto = get_ontology("http://www.semanticweb.org/les/ontologies/2025/Cards#")
ontology_file = OntologyResource.CARD.value

with onto:
    # Definizione delle Classi (OWL Classes)

    class Card(Thing):
        pass# Questa classe conterrà le carte generiche

    # Sottoclassi di Card.
    class FaceCard(Card):
        pass# Questa classe conterrà la classe carte con figura

    class Numbered(Card):
        pass# Questa classe conterrà le carte numerate

    class Special(Card):
        pass# Questa classe conterrà speciali (Jolly/Pinelle)

    class Jolly(Special):
        pass# Questa classe conterrà i Jolly

    class Pinella(Special): # La Pinella è il 2 di qualsiasi seme
        pass
    
    class Game(Thing):
        pass# Questa classe conterrà una rappresentazione della partita

    class Player(Thing):
        pass# Questa classe conterrà una rappresentazione del giocatore

    class Seme(Thing):
        pass # Questa classe conterrà gli individui per i semi (Cuori, Fiori, ecc.).

    class Mazzo(Thing):
        #pass # Questa classe conterrà i due mazzi (Mazzo_Rosso, Mazzo_Blue).
        @property
        def numeroCarte(self):
            return len(self.mazzo)

    class Monte(Mazzo):
        pass # Questa classe conterrà il mazzo da cui pescare.

    class Scarto(Mazzo):
        pass # Questa classe conterrà il mazzo degli scarti.

    class Mano(Mazzo):
        pass # Questa classe conterrà il mazzo della mano del giocatore.

    class Canasta(Thing):
       # Questa classe rappresenta le canaste (Scale e Tris).
        pass
   
    class Scala(onto.Canasta):
        pass #Questa classe rappresenta le Scale.

    class Tris(onto.Canasta):
        pass #Questa classe rappresenta i Tris.


    # Definizione delle Proprietà Oggetto
    # Le Proprietà Oggetto definiscono le relazioni tra due individui (istanze di classi).
    # Es. "un giocatore ha una carta" (relazione tra un individuo Player e un individuo Card).

    # Proprietà 'hasCards'
    class hasCards(ObjectProperty): 
        domain = [onto.Canasta] 
        range = [onto.Card]
        
    # Proprietà 'players'
    class players(ObjectProperty):
        domain = [onto.Game]
        range = [onto.Player]

    # Proprietà 'turnOf'
    class turnOf(ObjectProperty, FunctionalProperty):
        domain = [onto.Game] 
        range = [onto.Player]

    # Proprietà 'scarto'
    class scarto(ObjectProperty, FunctionalProperty):
        domain = [onto.Game] 
        range = [onto.Scarto]

    # Proprietà 'monte'
    class monte(ObjectProperty, FunctionalProperty):
        domain = [onto.Game] 
        range = [onto.Monte]

    # Proprietà 'scala'
    class scala(ObjectProperty):
        domain = [onto.Player]
        range = [onto.Scala] 

    # Proprietà 'tris'
    class tris(ObjectProperty):
        domain = [onto.Player]
        range = [onto.Tris] 

    # Proprietà 'playerHand'
    class playerHand(ObjectProperty, FunctionalProperty):
        domain = [onto.Player] 
        range = [onto.Mano]

    # Proprietà 'seme' per le carte
    class seme(ObjectProperty, FunctionalProperty):
        domain = [onto.Card]
        range = [onto.Seme]

    # Proprietà 'seme' per le scale
    class semeScala(ObjectProperty, FunctionalProperty):
        domain = [onto.Scala]
        range = [onto.Seme]

    # Proprietà 'mazzo'
    class mazzo(ObjectProperty):
        domain = [onto.Mazzo]
        range = [onto.Card]



    # Definizione delle Proprietà Dato
    # Le Proprietà Dato definiscono le relazioni tra un individuo e un valore di tipo dato (es. numero, stringa).
    # Es. "una carta ha un numero" (relazione tra un individuo Card e il valore numerico "7").

    # Proprietà 'id'
    # un numerico progressivo per identificare le carte
    class idCarta(DataProperty, FunctionalProperty):
        domain = [onto.Card]
        range = [int]
    
    # Proprietà 'numeroCarta'
    class numeroCarta(DataProperty, FunctionalProperty):
        domain = [onto.Card]
        range = [int]

    # Proprietà 'valoreCarta'
    class valoreCarta(DataProperty, FunctionalProperty):
        domain = [onto.Card]
        range = [int]

    # Proprietà 'cartaVisibile'
    class cartaVisibile(DataProperty, FunctionalProperty):
        domain = [onto.Card]
        range = [bool]

    # Proprietà 'cartaNota'
    # si distingue da cartaVisibile in quanto
    # una volta scartata (o inserita in una scala/tris)
    # ormai è noto che la carta è "uscita"
    class cartaNota(DataProperty, FunctionalProperty):
        domain = [onto.Card]
        range = [bool]

    # Proprietà 'isClosed'
    class isClosed(DataProperty):
        domain = [onto.Canasta]
        range = [bool]

    # Proprietà 'minValueScala' per le scale
    class minValueScala(DataProperty, FunctionalProperty):
        domain = [onto.Scala]
        range = [int]

    # Proprietà 'maxValueScala' per le scale
    class maxValueScala(DataProperty, FunctionalProperty):
        domain = [onto.Scala]
        range = [int]

    # Proprietà 'scalaId' per le scale
    class scalaId(DataProperty, FunctionalProperty):
        domain = [onto.Scala]
        range = [int]

    # Proprietà 'trisValue' per le scale
    class trisValue(DataProperty, FunctionalProperty):
        domain = [onto.Tris]
        range = [int]

    # Proprietà 'trisId' per le scale
    class trisId(DataProperty, FunctionalProperty):
        domain = [onto.Tris]
        range = [int]

    # Proprietà 'id'
    # un numerico progressivo per identificare il giocatore
    class idGiocatore(DataProperty, FunctionalProperty):
        domain = [onto.Player]
        range = [int]

    # Proprietà 'nomeGiocatore' per le scale
    class nomeGiocatore(DataProperty, FunctionalProperty):
        domain = [onto.Player]
        range = [str]

    # Proprietà 'punteggioGiocatore' per le scale
    class punteggioGiocatore(DataProperty, FunctionalProperty):
        domain = [onto.Player]
        range = [int]

    # Proprietà 'punteggioGiocatore' per le scale
    class isBurracoClosed(DataProperty, FunctionalProperty):
        domain = [onto.Scala]
        range = [bool]

    # Proprietà 'punteggioGiocatore' per le scale
    class isTrisClosed(DataProperty, FunctionalProperty):
        domain = [onto.Tris]
        range = [bool]

    AllDisjoint([onto.FaceCard, onto.Numbered])


if __name__ == '__main__':
    #utils
    mazzi_arr = ["Rosso", "Blu"]
    card_values_map = { 1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10", 11: "J", 12: "Q", 13: "K" }
    card_valori_punteggio = { 1: 15, 2: 20, 3: 5, 4: 5, 5: 5, 6: 5, 7: 5, 8: 10, 9: 10, 10: 10, 11: 10, 12: 10, 13: 10 }
    semi_names = ["Cuori", "Quadri", "Fiori", "Picche"]
    jolly_names = ["Jolly_N", "Jolly_R"]

    #individui
    onto_semi = {s_name: onto.Seme(s_name) for s_name in semi_names}


    #CREAZIONE DEL MAZZO
    
    #rimpiazzato con 0 per per il metodo (encode_cards) della classe utils.py
    #id_carta = 1
    id_carta = 0
    #per ogni mazzo
    for singolo_mazzo_name in mazzi_arr:
        singolo_mazzo = onto.Mazzo(singolo_mazzo_name)
        #per ogni seme
        for single_semi_name in semi_names:
            single_semi = onto_semi[single_semi_name]

            new_card_name = f"A_{single_semi_name}_{singolo_mazzo_name}"
            asso = onto.Numbered(new_card_name)
            asso.numeroCarta = 1
            asso.valoreCarta = 15
            asso.seme = single_semi
            asso.cartaVisibile = False
            asso.cartaNota = False
            asso.idCarta = id_carta
            id_carta += 1
            singolo_mazzo.mazzo.append(asso)

            for number in range(2,11):
                card_index = number
                card_name = card_values_map[number]
                new_card_name = f"{card_name}_{single_semi_name}_{singolo_mazzo_name}"
                carta = onto.Numbered(new_card_name)
                carta.numeroCarta = card_index
                carta.valoreCarta = card_valori_punteggio[card_index]
                carta.seme = single_semi
                carta.cartaVisibile = False
                carta.cartaNota = False
                carta.idCarta = id_carta
                id_carta += 1
                singolo_mazzo.mazzo.append(carta)
                if card_index == 2:
                    carta.is_a.append(onto.Special)
                    carta.is_a.append(onto.Pinella)

            #J,Q,K
            for number in range(11,14):
                card_index = number
                card_name = card_values_map[number]
                new_card_name = f"{card_name}_{single_semi_name}_{singolo_mazzo_name}"
                carta = onto.FaceCard(new_card_name)
                carta.numeroCarta = card_index
                carta.valoreCarta = card_valori_punteggio[card_index]
                carta.seme = single_semi
                carta.cartaVisibile = False
                carta.cartaNota = False
                carta.idCarta = id_carta
                id_carta += 1
                singolo_mazzo.mazzo.append(carta)


        #Jolly
        for single_jolly_names in jolly_names:
            new_card_name = f"Jolly_{single_jolly_names}_{singolo_mazzo_name}"
            carta = onto.Special(new_card_name)
            carta.valoreCarta = 30
            carta.is_a.append(onto.Special)
            carta.is_a.append(onto.Jolly)
            carta.cartaVisibile = False
            carta.cartaNota = False
            carta.idCarta = id_carta
            id_carta += 1
            singolo_mazzo.mazzo.append(carta)

    print(f"ontology_file {ontology_file}")
    onto.save(file = ontology_file, format = "rdfxml")
    print(f"Ontologia aggiornata salvata in {ontology_file}")