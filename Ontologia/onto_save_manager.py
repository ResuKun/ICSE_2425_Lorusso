from owlready2 import *
from enum import Enum
from threading import Lock
from datetime import datetime


class OntologyResource(Enum):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    date = datetime.now().strftime("%Y_%m_%d")
    ONTO_FOLDER = "C:/Users/alexl/Documents/Facolta/ICSE/Progetto/Burraco/ICSE_2425_Lorusso/Ontologia"
    DATE_BK_DIR = ONTO_FOLDER + f"/BK/{date}"
    CARD = ONTO_FOLDER + "/Cards_Ontology.owl"
    INIT_GAME = DATE_BK_DIR + f"/Init_Game_Ontology{timestamp}.owl"
    UPDATED_GAME = DATE_BK_DIR + f"/Updated_Game_Ontology{timestamp}.owl"


class OntologyManager:
    """Singleton che gestisce il caricamento e salvataggio delle ontologie Owlready2."""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(OntologyManager, cls).__new__(cls)
                cls._instance.onto = None
                cls._instance.onto_type = None
        return cls._instance

    def get_ontology_from_manager(self, ontology_type=OntologyResource.UPDATED_GAME):
        """Carica un'ontologia dal tipo specificato, come nella versione originale."""
        self.onto_type = ontology_type
        if isinstance(ontology_type, OntologyResource):
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
                raise ValueError(f"Il File Ontologia {ontology_type.name} non è stato trovato")

            self.onto = onto_pre_load.load()
        else:
            raise ValueError("Errore: Tipo di ontologia non valido. Usa l'enum OntologyResource.")

        return self.onto

    def salva_ontologia(self):
        """Salva l'ontologia nel file CARD.owl"""
        if self.onto is None:
            raise ValueError("Nessuna ontologia caricata.")
        self.onto.save(file=OntologyResource.CARD.value, format="rdfxml")
        print("UPDATE::  Ontologia aggiornata in CARD_CARD_GAME_FILE")

    def salva_ontologia_init_game(self):
        """Salva l'ontologia nel file INIT_GAME.owl"""
        if self.onto is None:
            raise ValueError("Nessuna ontologia caricata.")
        self.onto.save(file=OntologyResource.INIT_GAME.value, format="rdfxml")
        print("UPDATE::  Ontologia aggiornata in CARD_INIT_GAME_FILE")

    def salva_ontologia_update_game(self):
        """Salva l'ontologia nel file UPDATED_GAME.owl"""
        if self.onto is None:
            raise ValueError("Nessuna ontologia caricata.")
        self.onto.save(file=OntologyResource.UPDATED_GAME.value, format="rdfxml")
        print("UPDATE::  Ontologia aggiornata in CARD_UPDATED_GAME_FILE")

    def scarica_ontologia(self):
        """Rimuove l'ontologia corrente dalla memoria (unload)."""
        if self.onto is not None:
            try:
                default_world.ontologies.remove(self.onto)
                print(f"ONTO - INFO:: Ontologia {self.onto_type.name} scaricata dalla memoria")
            except ValueError:
                print("ONTO - WARNING:: L'ontologia non era registrata nel world")
            del self.onto
            self.onto = None
            self.onto_type = None
            import gc; gc.collect()
        else:
            print("ONTO - INFO:: Nessuna ontologia da scaricare")


    def create_update_file(self):
        if not os.path.exists(OntologyResource.DATE_BK_DIR.value):
            os.makedirs(OntologyResource.DATE_BK_DIR.value)
        """Crea un nuovo file UPDATED_GAME aggiornando l’IRI."""
        file = open(OntologyResource.CARD.value, "r")
        content = file.read()
        file.close()
        content = content.replace(
            "http://www.semanticweb.org/les/ontologies/2025/Cards",
            "http://www.semanticweb.org/les/ontologies/2025/Updated_Game_Ontology"
        )
        f = open(OntologyResource.UPDATED_GAME.value, "w")
        f.write(content)
        f.close()
        print("ONTO - INFO:: Creato file UPDATED_GAME aggiornato")

    def create_init_file(self):
        if not os.path.exists(OntologyResource.DATE_BK_DIR.value):
            os.makedirs(OntologyResource.DATE_BK_DIR.value)
        """Crea un nuovo file UPDATED_GAME aggiornando l’IRI."""
        file = open(OntologyResource.CARD.value, "r")
        content = file.read()
        file.close()
        content = content.replace(
            "http://www.semanticweb.org/les/ontologies/2025/Cards",
            "http://www.semanticweb.org/les/ontologies/2025/Init_Game_Ontology"
        )
        f = open(OntologyResource.INIT_GAME.value, "w")
        f.write(content)
        f.close()
        print("ONTO - INFO:: Creato file UPDATED_GAME aggiornato")