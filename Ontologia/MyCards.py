from owlready2 import *

# Crea una nuova ontologia. L'IRI (Internationalized Resource Identifier) è l'identificatore unico
# dell'ontologia.
onto = get_ontology("http://www.semanticweb.org/les/ontologies/2025/Cards#")
ontology_file = "Cards_Ontology.owl"

with onto:
    # Definizione delle Classi (OWL Classes)

    class Card(Thing):
        pass

    # Sottoclassi di Card.
    class FaceCard(Card):
        pass

    class Numbered(Card):
        pass

    class Special(Card):
        pass

    class Jolly(Special):
        pass

    class Pinella(Special): # La Pinella è il 2 di qualsiasi seme
        pass
    
    class Game(Thing):
        pass

    class Player(Thing):
        pass

    class Seme(Thing):
        pass # Questa classe conterrà gli individui per i semi (Cuori, Fiori, ecc.).

    class Mazzo(Thing):
        pass # Questa classe conterrà i due mazzi (Mazzo_Rosso, Mazzo_Blue).

    class Monte(Mazzo):
        pass # Questa classe conterrà il mazzo da cui pescare.

    class Scarto(Mazzo):
        pass # Questa classe conterrà il mazzo degli scarti.

    class Mano(Mazzo):
        pass # Questa classe conterrà il mazzo della mano del giocatore.

    class Canasta(Thing):
       # pass # Questa classe rappresenta le canaste (Scale e Tris).
        @property
        def isBurraco(self):
            return len(self.hasCards) >= 7

        @property
        def hasJollyOrPinella(self):
            for card in self.hasCards:
                if onto.Jolly in card.is_a or onto.Pinella in card.is_a:
                    return True
            return False

        @property
        def isBurracoPulito(self):
            return self.isBurraco and not self.hasJollyOrPinella

        @property
        def isBurracoSporco(self):
            return self.isBurraco and self.hasJollyOrPinella
   
    class Scala(onto.Canasta):
        pass
    
    class Tris(onto.Canasta):
        pass


    # Definizione delle Proprietà Oggetto
    # Le Proprietà Oggetto definiscono le relazioni tra due individui (istanze di classi).
    # Es. "un giocatore ha una carta" (relazione tra un individuo Player e un individuo Card).

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

    # Proprietà 'turnOf'
    class monte(ObjectProperty, FunctionalProperty):
        domain = [onto.Game] 
        range = [onto.Monte]

    # Proprietà 'canasta'
    class canasta(ObjectProperty):
        domain = [onto.Player]
        range = [onto.Canasta] 

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

    # Proprietà 'hasCards'
    class hasCards(ObjectProperty): 
        domain = [onto.Canasta] 
        range = [onto.Card]

    # Definizione delle Proprietà Dato
    # Le Proprietà Dato definiscono le relazioni tra un individuo e un valore di tipo dato (es. numero, stringa).
    # Es. "una carta ha un numero" (relazione tra un individuo Card e il valore numerico "7").

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

    # Proprietà 'trisValue' per le scale
    class trisValue(DataProperty, FunctionalProperty):
        domain = [onto.Tris]
        range = [int]

    # Proprietà 'nomeGiocatore' per le scale
    class nomeGiocatore(DataProperty, FunctionalProperty):
        domain = [onto.Player]
        range = [str]

    # Proprietà 'nomeGiocatore' per le scale
    class punteggioGiocatore(DataProperty, FunctionalProperty):
        domain = [onto.Player]
        range = [int]

    AllDisjoint([onto.FaceCard, onto.Numbered])

    #utils
    mazzi_arr = ["Rosso", "Blu"]
    card_values_map = { 1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10", 11: "J", 12: "Q", 13: "K" }
    card_valori_punteggio = { 1: 15, 2: 20, 3: 5, 4: 5, 5: 5, 6: 5, 7: 5, 8: 5, 9: 5, 10: 10, 11: 10, 12: 10, 13: 10 }
    semi_names = ["Cuori", "Quadri", "Fiori", "Picche"]
    jolly_names = ["Jolly_N", "Jolly_R"]

    #individui
    onto_semi = {s_name: onto.Seme(s_name) for s_name in semi_names}

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
                singolo_mazzo.mazzo.append(carta)


        #Jolly
        for single_jolly_names in jolly_names:
            new_card_name = f"Jolly_{single_jolly_names}_{singolo_mazzo_name}"
            carta = onto.Special(new_card_name)
            carta.valoreCarta = 30
            carta.is_a.append(onto.Jolly)
            carta.cartaVisibile = False
            singolo_mazzo.mazzo.append(carta)

            

    
onto.save(file = ontology_file, format = "rdfxml")

print(f"Ontologia aggiornata salvata in {ontology_file}")