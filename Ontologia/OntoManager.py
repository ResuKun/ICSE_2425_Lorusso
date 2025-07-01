from owlready2 import *
from enum import Enum

# Path to the ontology files
# Constants for ontology types
class OntologyResource(Enum):
    CARD = "C:/Users/alexl/Documents/Facolta/ICSE/Progetto/Burraco/ICSE_2425_Lorusso/Ontologia/Cards_Ontology.owl"
    INIT_GAME= "C:/Users/alexl/Documents/Facolta/ICSE/Progetto/Burraco/ICSE_2425_Lorusso/Ontologia/Init_Game_Ontology.owl"
    UPDATED_GAME = "C:/Users/alexl/Documents/Facolta/ICSE/Progetto/Burraco/ICSE_2425_Lorusso/Ontologia/Updated_Game_Ontology.owl"

onto = None
onto_type = None

def get_ontology_from_manager(ontology_type = OntologyResource.UPDATED_GAME):
    global onto, onto_type
    onto_type = ontology_type
    if isinstance(ontology_type, OntologyResource):
        if onto is None:
            onto_pre_load = None
            if ontology_type == OntologyResource.CARD:
                 onto_pre_load = get_ontology(OntologyResource.CARD.value)
            elif ontology_type == OntologyResource.INIT_GAME:
                 onto_pre_load = get_ontology(OntologyResource.INIT_GAME.value)
            elif ontology_type == OntologyResource.UPDATED_GAME:
                 onto_pre_load = get_ontology(OntologyResource.UPDATED_GAME.value)
            else:
                raise ValueError("Caso Invalido e non gestito")
            if onto_pre_load is None:
                raise ValueError(f"Il File Ontologia {onto_type.name} non è stato trovato")
            onto = onto_pre_load.load()
        else:
            print(f"ONTO - INFO::  Ontologia già caricata {onto_type.name}, non la ricarico")
    else:
        raise ValueError("Errore: Tipo di ontologia non valido. Usa l'enum OntologyResource.")
    return onto

def salva_ontologia():
    onto.save(file = OntologyResource.CARD.value, format = "rdfxml")
    print(f"ONTO - UPDATE::  Ontologia aggiornata in CARD_INIT_GAME_FILE")

def salva_ontologia_init_game():
    onto.save(file = OntologyResource.INIT_GAME.value, format = "rdfxml")
    print(f"UPDATE - UPDATE::  Ontologia aggiornata in CARD_INIT_GAME_FILE")

def salva_ontologia_update_game():
    onto.save(file = OntologyResource.UPDATED_GAME.value, format = "rdfxml")
    print(f"TEST - UPDATE::  Ontologia aggiornata in CARD_UPDATED_GAME_FILE")

