from owlready2 import *
import random

ontology_file_path = "C:/Users/alexl/Documents/Facolta/ICSE/Progetto/Burraco/ICSE_2425_Lorusso/Ontologia/Cards_Ontology.owl"
ontology_file_save = "C:/Users/alexl/Documents/Facolta/ICSE/Progetto/Burraco/ICSE_2425_Lorusso/Ontologia/Cards_Ontology_Updated.owl"
onto = get_ontology(ontology_file_path).load()

def salva_ontologia():
    onto.save(file = ontology_file_save, format = "rdfxml")
    print(f"\nOntologia aggiornata in {ontology_file_save}")

def get_card_number(card):
    if hasattr(card, 'numeroCarta') and card.numeroCarta is not None:
        return card.numeroCarta
    return None


    
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
    skip = True
    isScala = False

    #TODO aggiungere e delegare i controlli per isScala risolivile tramite CSP
    #quindi sequenzialità e che siano dello stesso seme
    for card in cards:
        #la carta diventa visibile per tutti
        card.cartaVisibile = True
        player.playerHand.mazzo.remove(card)
        #salta i Jolly
        if hasattr(card, 'seme'):
            if skip:
                skip = False
                semeScala = card.seme
            else:
                if semeScala == card.seme:
                    isScala = True
                    break

    if isScala:
        apre_scala(player, cards,semeScala)
    else:
        apre_tris(player, cards)
    salva_ontologia()
                

#crea una nuova scala e la aggiunge al giocatore
def apre_scala(player, cards, seme):
    nScala = len(player.scala)
    nuovaScala = onto.Scala("Scala_" + nScala)

    numbered_cards_for_min_max = [c for c in cards if hasattr(c, 'numeroCarta') and c.numeroCarta is not None]
    min_number = min(c.numeroCarta for c in numbered_cards_for_min_max)
    max_number = max(c.numeroCarta for c in numbered_cards_for_min_max)

    min_number = min(c.numeroCarta for c in cards)
    max_number = max(c.numeroCarta for c in cards)
    nuovaScala.minValueScala = min_number
    nuovaScala.maxValueScala = max_number
    nuovaScala.semeScala = seme

    for card in cards:
        nuovaScala.hasCards.append(card)
    player.scala.append(nuovaScala)

#crea una nuovo Tris e la aggiunge al giocatore
def apre_tris(player, cards):
    nTris = len(player.tris)
    nuovoTris = onto.Tris("Tris_" + nTris)
    trisValue = None
    for card in cards:
        nuovoTris.hasCards.append(card)
        if hasattr(card, 'seme'):
            trisValue = card.numeroCarta
    nuovoTris.trisValue = trisValue
    player.tris.append(nuovoTris)
    

#permette al giocatore di aggiungere carte a un suo tris esistente sul tavolo, aggiornando il Tris.
def aggiunge_carte_tris(player, tris, cards_to_add): 
    print("TODO")
    #TODO aggiungere e delegare i controlli di correttezza all'aggiunta tramite problema CSP
    #quindi sequenzialità e che siano dello stesso seme
    if not cards_to_add:
        print("Nessuna carta fornita per l'aggiunta.")
        return False, "Nessuna carta fornita."
    
    # Verifica che la scala target appartenga al giocatore
    if tris not in player.tris:
        print(f"ERRORE: La scala '{tris.name}' non appartiene al giocatore {player.nomeGiocatore}.")
        return False, "La scala specificata non appartiene al giocatore."
    
    jolly_found = False
    for card in cards_to_add:
        if hasattr(card, 'numeroCarta') and card.numeroCarta is not None:
            numero = card.numeroCarta
            if numero != tris.trisValue:
                print(f"ERRORE: almeno una delle carte da aggiungere non ha lo stesso numero del tris.")
                return False, " almeno una delle carte da aggiungere non ha lo stesso numero del tris."
            tris.hasCards.append(card)
        # se trovo 1 Jolly/Pinella
        elif isinstance(card, (onto.Jolly, onto.Pinella)) and not jolly_found:
            jolly_found = True
            tris.hasCards.append(card)

        # se trovo + di 1 Jolly/Pinella
        elif isinstance(card, (onto.Jolly, onto.Pinella)) and jolly_found:
            print(f"ERRORE: si sta aggiungendo più di un Jolly/Pinella al tris")
            return False, " si sta aggiungendo più di un Jolly/Pinella al tris"
   
    salva_ontologia()
    return True, "Carte aggiunte con successo al tris."




#permette al giocatore di aggiungere carte a una sua scala esistente sul tavolo, aggiornando la scala.
def aggiunge_carte_scala(player, target_scala, cards_to_add):
    if not cards_to_add:
        print("Nessuna carta fornita per l'aggiunta.")
        return False, "Nessuna carta fornita."

    #  Verifica che le carte da aggiungere siano effettivamente nella mano del giocatore
    for card in cards_to_add:
        if card not in player.playerHand.mazzo:
            print(f"ERRORE: La carta {card.name} non è presente nella mano del giocatore {player.nomeGiocatore}.")
            return False, f"La carta {card.name} non è nella mano del giocatore."

    # Verifica che la scala target appartenga al giocatore
    if target_scala not in player.scala:
        print(f"ERRORE: La scala '{target_scala.name}' non appartiene al giocatore {player.nomeGiocatore}.")
        return False, "La scala specificata non appartiene al giocatore."


## ---------------------------- START ---------------------------- ##

    #TODO INIZIO SEMPLIFICAZIONE AL POSTO DEL CSP

# (Questa logica è la bozza più semplice in attesa del CSP)
    scala_seme = target_scala.semeScala
    
    # Raccogli le carte numerate e speciali da aggiungere
    numbered_new_cards = []
    special_new_cards = []
    for card in cards_to_add:
        if isinstance(card, (onto.Numbered, onto.FaceCard)):
            if card.seme != scala_seme:
                print(f"  Fallimento: Seme della carta {card.name} non corrisponde al seme della scala {scala_seme.name}.")
                return False, f"Seme della carta {card.name} non corrisponde al seme della scala."
            numbered_new_cards.append(card)
        elif isinstance(card, (onto.Jolly, onto.Pinella)):
            special_new_cards.append(card)
        else:
            print(f"  Fallimento: Tipo di carta non gestito: {card.name}.")
            return False, f"Tipo di carta non gestito: {card.name}"

    #  Massimo 1 Jolly/Pinelle totali in una scala.
    current_special_cards_count = sum(1 for c in target_scala.hasCards if isinstance(c, (onto.Jolly, onto.Pinella)))
    if current_special_cards_count + len(special_new_cards) > 1:
        print(f"  Fallimento: Troppi Jolly/Pinelle nella scala dopo l'aggiunta. Attuali: {current_special_cards_count}, Nuovi: {len(special_new_cards)}.")
        return False, "Numero massimo di Jolly/Pinelle superato."

    # Ottieni i numeri delle carte esistenti e delle nuove carte numerate
    existing_card_numbers = sorted([c.numeroCarta for c in target_scala.hasCards if c.hasattr(c, 'numeroCarta') ])
    new_card_numbers = sorted([ c.numeroCarta for c in numbered_new_cards if c.hasattr(c, 'numeroCarta')])

    if not existing_card_numbers:
        return False, "Nessuna carta numerica coinvolta."

    # Controllo contiguità delle nuove carte tra loro
    if len(new_card_numbers) > 1:
        for i in range(len(new_card_numbers) - 1):
            if new_card_numbers[i+1] - new_card_numbers[i] != 1:
                print(f"  Fallimento: Le nuove carte numerate non sono contigue tra loro: {new_card_numbers}.")
                return False, "Le nuove carte non sono contigue."

    min_existing = target_scala.minValueScala
    max_existing = target_scala.maxValueScala
    
    # Scenario 1: Estensione alla fine della scala
    if new_card_numbers and new_card_numbers[0] > max_existing:
        gap_needed = new_card_numbers[0] - max_existing - 1
        if gap_needed == 0 and len(special_new_cards) == 0: # Estensione diretta senza jolly
            print("  Verifica OK: Estensione diretta alla fine.")
        elif gap_needed == 1 and len(special_new_cards) >= 1: # Estensione con un jolly
            print("  Verifica OK: Estensione alla fine con un Jolly/Pinella.")
        else:
            print(f"  Fallimento: Gap alla fine ({gap_needed}) non coperto correttamente da {len(special_new_cards)} Jolly/Pinelle.")
            return False, "Estensione alla fine non valida."
    # Scenario 2: Estensione all'inizio della scala
    elif new_card_numbers and new_card_numbers[-1] < min_existing:
        gap_needed = min_existing - new_card_numbers[-1] - 1
        if gap_needed == 0 and len(special_new_cards) == 0: # Estensione diretta senza jolly
            print("  Verifica OK: Estensione diretta all'inizio.")
        elif gap_needed == 1 and len(special_new_cards) >= 1: # Estensione con un jolly
            print("  Verifica OK: Estensione all'inizio con un Jolly/Pinella.")
        else:
            print(f"  Fallimento: Gap all'inizio ({gap_needed}) non coperto correttamente da {len(special_new_cards)} Jolly/Pinelle.")
            return False, "Estensione all'inizio non valida."
    elif not new_card_numbers and special_new_cards: # Caso di aggiunta di solo jolly/pinelle senza carte numerate
        # TODO> Questo caso è problematico per la logica semplificata.
        # Un jolly può essere aggiunto a una scala se è l'unico jolly o il secondo,
        # e se può occupare una posizione valida. Senza CSP, è difficile validarlo.
        # Per ora, lo neghiamo se non ci sono carte numerate da aggiungere che diano contesto.
        print("  Fallimento: Aggiunta di sole carte speciali a una scala esistente. Richiede logica CSP.")
        return False, "Solo Jolly/Pinella non validabile in modo semplificato."
    else:
        print("  Fallimento: Le carte non si incastrano correttamente all'inizio o alla fine della scala.")
        return False, "Carte non compatibili per l'estensione."

    # Se arriviamo qui, la validazione semplificata è passata
    print(f"Validazione semplificata superata. Aggiungendo carte alla scala: {target_scala.name}")

    #TODO FINE SEMPLIFICAZIONE AL POSTO DEL CSP
## ---------------------------- END ---------------------------- ##


    for card in cards_to_add:
        # 1. Aggiungi la carta alla scala nell'ontologia
        target_scala.hasCards.append(card)
        print(f"  - Aggiunta carta {card.name} alla scala '{target_scala.name}'.")

        # 2. Rimuovi la carta dalla mano del giocatore
        if card in player.playerHand.mazzo:
            player.playerHand.mazzo.remove(card)
            print(f"  - Carta {card.name} rimossa dalla mano di {player.nomeGiocatore}.")
        else:
            print(f"  ATTENZIONE: La carta {card.name} non è stata trovata nella mano del giocatore. Possibile errore di stato.")

        # 3. Rendi la carta visibile (poiché è ora sul tavolo)
        card.cartaVisibile = True
        print(f"  - Carta {card.name} resa visibile.")

    # In questa logica semplificata, contiamo solo le carte numerate "pure" per min/max,
    # TODO ma un CSP sarebbe necessario per assegnare correttamente il valore ai Jolly/Pinelle.
    all_numeric_cards_in_scala = [
        get_card_number(c) for c in target_scala.hasCards 
        if get_card_number(c) is not None and not isinstance(c, onto.Jolly) # Pinella (2) ha un numeroCarta, Jolly no.
    ]
    all_numeric_cards_in_scala = sorted(list(set(all_numeric_cards_in_scala))) # Rimuovi duplicati e ordina

    # TODO Se ci sono Jolly/Pinelle, la logica diventa più complessa e richiederebbe un CSP.
    # Ad esempio, un Jolly potrebbe estendere una scala "saltando" un numero.
    # Per questa versione semplificata, assumiamo che le nuove carte numerate siano contigue
    # o che un singolo jolly/pinella copra un singolo buco.
    
    # Se dopo l'aggiunta ci sono ancora carte numeriche nella scala
    if all_numeric_cards_in_scala:
        new_min_val = min(all_numeric_cards_in_scala)
        new_max_val = max(all_numeric_cards_in_scala)

        # Considera i casi in cui Asso (1) può essere 14
        #has_ace = any(c.numeroCarta == 1 for c in target_scala.hasCards if hasattr(c, 'numeroCarta'))
        
        # Se l'Asso è presente e la scala è lunga abbastanza da "girare"
        # (es. Q-K-A o K-A-2), è una logica avanzata per il CSP.
        
        target_scala.minValueScala = new_min_val
        target_scala.maxValueScala = new_max_val
        print(f"  - Valori min/max della scala '{target_scala.name}' aggiornati: Min={target_scala.minValueScala}, Max={target_scala.maxValueScala}")
    else:
        print(f"  AVVISO: Impossibile aggiornare min/max per scala '{target_scala.name}'. Nessuna carta numerica pura o assegnabile trovata dopo l'aggiunta.")


    salva_ontologia()

    for card in player.playerHand.mazzo:
        print(f"  - {card.name}")

    print(f"--- Fine aggiunta carte a scala ---\n")
    return True, "Carte aggiunte con successo alla scala esistente."


