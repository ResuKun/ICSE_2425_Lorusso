from owlready2 import *
from enum import Enum
from threading import Lock
from datetime import datetime
from pathlib import Path

#TODO rendere i path relativi
class OntologyResource(Enum):
    ONTO_FOLDER = str(Path("Ontologia").absolute())
    CARD = ONTO_FOLDER + "/Cards_Ontology.owl"
    INIT_GAME =  "/Init_Game_Ontology"
    UPDATED_GAME = "/Updated_Game_Ontology"
    UPDATED_GAME_TEST = "/Updated_Game_Ontology"
    FILE_EXTENSION = ".owl"


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
                cls._instance.bk_dir = None
                cls._instance.card = None
                cls._instance.init_game = None
                cls._instance.updated_game = None
                cls._instance.init_game_test = None
                cls._instance.updated_game_test = None
        return cls._instance

    def get_ontology_from_manager(self, ontology_type=OntologyResource.UPDATED_GAME):
        """Carica un'ontologia dal tipo specificato, come nella versione originale."""
        self.onto_type = ontology_type
        if isinstance(ontology_type, OntologyResource):
            onto_pre_load = None
            if ontology_type == OntologyResource.CARD:
                onto_pre_load = get_ontology(self.card )
            elif ontology_type == OntologyResource.INIT_GAME:
                onto_pre_load = get_ontology(self.init_game)
            elif ontology_type == OntologyResource.UPDATED_GAME:
                onto_pre_load = get_ontology(self.updated_game )
            elif ontology_type == OntologyResource.UPDATED_GAME_TEST:
                onto_pre_load = get_ontology(self.updated_game_test)
            else:
                raise ValueError("Caso Invalido e non gestito")

            if onto_pre_load is None:
                raise ValueError(f"Il File Ontologia {ontology_type.name} non è stato trovato")

            self.onto = onto_pre_load.load()
        else:
            raise ValueError("Errore: Tipo di ontologia non valido. Usa l'enum OntologyResource.")

        return self.onto
    
    def get_onto(self):
        if self.onto is None:
            raise ValueError("Nessuna ontologia caricata.")
        return self.onto

    def salva_ontologia(self):
        """Salva l'ontologia nel file CARD.owl"""
        if self.onto is None:
            raise ValueError("Nessuna ontologia caricata.")
        self.onto.save(file=self.card , format="rdfxml")
        #print(f"UPDATE::  Ontologia aggiornata in {self.card}")

    def salva_ontologia_init_game(self ):
        #"""Salva l'ontologia nel file INIT_GAME.owl"""
        #if self.onto is None:
        #    raise ValueError("Nessuna ontologia caricata.")
        #self.onto.save(file=self.init_game, format="rdfxml")
        #print(f"UPDATE::  Ontologia aggiornata in {self.init_game}")
        pass

    def salva_ontologia_update_game(self, debuge_mode = False):
        """Salva l'ontologia nel file UPDATED_GAME.owl"""
        if self.onto is None:
            raise ValueError("Nessuna ontologia caricata.")
        file_name = self.updated_game
        if debuge_mode:
            file_name = self.updated_game_test
        self.onto.save(file = file_name, format="rdfxml")
        #print(f"UPDATE::  Ontologia aggiornata in {file_name}")


 #  def scarica_ontologia(self):
 #      """Rimuove l'ontologia corrente dalla memoria (unload)."""
 #      if self.onto is not None:
 #          try:
 #              default_world.ontologies.remove(self.onto)
 #              print(f"ONTO - INFO:: Ontologia {self.onto_type.name} scaricata dalla memoria")
 #          except ValueError:
 #              print("ONTO - WARNING:: L'ontologia non era registrata nel world")
 #          del self.onto
 #          self.onto = None
 #          self.onto_type = None
 #          import gc; gc.collect()
 #      else:
 #          print("ONTO - INFO:: Nessuna ontologia da scaricare")

    def scarica_ontologia(self):
        """Rimuove l'ontologia corrente dalla memoria (unload)."""
        if self.onto is not None:
            try:
                # Recupera l'IRI di base dell'ontologia (identificatore univoco)
                iri_to_remove = getattr(self.onto, "base_iri", None)

                # Rimuove l'ontologia dal dizionario globale se presente
                if iri_to_remove and iri_to_remove in default_world.ontologies:
                    del default_world.ontologies[iri_to_remove]
                    #print(f"ONTO - INFO:: Ontologia {self.onto_type.name} scaricata dalla memoria")
                else:
                    print("ONTO - WARNING:: L'ontologia non era registrata nel world")

            except Exception as e:
                print(f"ONTO - ERROR:: Errore durante la rimozione dell'ontologia: {e}")

            finally:
                # Pulizia della memoria
                del self.onto
                self.onto = None
                self.onto_type = None
                import gc
                gc.collect()

        else:
            print("ONTO - INFO:: Nessuna ontologia da scaricare")


    def reload_file_name(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        date = datetime.now().strftime("%Y_%m_%d")
        self.card = OntologyResource.CARD.value
        self.bk_dir = OntologyResource.ONTO_FOLDER.value + f"/BK/{date}"
        self.init_game = self.bk_dir + OntologyResource.INIT_GAME.value + str(self.timestamp) + OntologyResource.FILE_EXTENSION.value
        self.init_game_test = OntologyResource.ONTO_FOLDER.value + OntologyResource.INIT_GAME.value + OntologyResource.FILE_EXTENSION.value
        self.updated_game = self.bk_dir + OntologyResource.UPDATED_GAME.value + str(self.timestamp) + OntologyResource.FILE_EXTENSION.value
        self.updated_game_test = OntologyResource.ONTO_FOLDER.value + OntologyResource.UPDATED_GAME.value + OntologyResource.FILE_EXTENSION.value
        #print(f"reload_file_name --> {self.updated_game}")

    def create_update_file(self, reload = False):
        """Crea un nuovo file UPDATED_GAME aggiornando l’IRI."""
        if reload:
            self.reload_file_name()
        if not os.path.exists(self.bk_dir):
            os.makedirs(self.bk_dir)
        file = open(self.card , "r")
        content = file.read()
        file.close()
        content = content.replace(
            "http://www.semanticweb.org/les/ontologies/2025/Cards",
            f"http://www.semanticweb.org/les/ontologies/2025/Updated_Game_Ontology{self.timestamp}"
        )
        f = open(self.updated_game , "w")
        f.write(content)
        f.close()
        print(f"ONTO - INFO:: Creato file {self.updated_game} ")

    def create_init_file(self, reload = False):
        """Crea un nuovo file UPDATED_GAME aggiornando l’IRI."""
        if reload:
            self.reload_file_name()
        if not os.path.exists(self.bk_dir):
            os.makedirs(self.bk_dir)
       # file = open(self.card , "r")
       # content = file.read()
       # file.close()
       # content = content.replace(
       #     "http://www.semanticweb.org/les/ontologies/2025/Cards",
       #     f"http://www.semanticweb.org/les/ontologies/2025/Init_Game_Ontology{self.timestamp}"
       # )
       # f = open(self.init_game, "w")
       # f.write(content)
       # f.close()
       # print(f"ONTO - INFO:: Creato file {self.init_game} ")

    def create_update_file_test(self):
        """Crea un nuovo file UPDATED_GAME aggiornando l’IRI."""
        file = open(self.card , "r")
        content = file.read()
        file.close()
        content = content.replace(
            "http://www.semanticweb.org/les/ontologies/2025/Cards",
            "http://www.semanticweb.org/les/ontologies/2025/Updated_Game_Ontology"
        )
        f = open(self.updated_game_test, "w")
        f.write(content)
        f.close()
        #print("ONTO - INFO:: Creato file UPDATED_GAME aggiornato")

    def create_init_file_test(self):
        pass
        #"""Crea un nuovo file UPDATED_GAME aggiornando l’IRI."""
        #file = open(self.card , "r")
        #content = file.read()
        #file.close()
        #content = content.replace(
        #    "http://www.semanticweb.org/les/ontologies/2025/Cards",
        #    "http://www.semanticweb.org/les/ontologies/2025/Init_Game_Ontology"
        #)
        #f = open(self.init_game_test, "w")
        #f.write(content)
        #f.close()
        #print("ONTO - INFO:: Creato file UPDATED_GAME aggiornato")