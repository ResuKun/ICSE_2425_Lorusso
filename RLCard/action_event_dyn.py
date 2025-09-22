import Utils.CONST as CONST
import Ontologia.onto_save_manager as onto_save_manager
import Player.player_csp_resolver as csp_resolver
import math

onto = onto_save_manager.get_ontology_from_manager()

score_player_0_action_id = 0
score_player_1_action_id = 1
draw_card_action_id = 2
pick_up_discard_action_id = 3
open_meld_action_id = 4
open_tris_action_id = 5
update_meld_action_id = 6
update_tris_action_id = 7
discard_action_id = 8 #( 8 / 8 + 108 )
close_game_action_id = 117


class ActionEvent(object):

    def __init__(self, action_id: int):
        self.action_id = action_id

    def __eq__(self, other):
        result = False
        if isinstance(other, ActionEvent):
            result = self.action_id == other.action_id
        return result
    
    # serve per dichiarare il volume del
    # massimo spazio di ricerca
    @staticmethod
    def get_num_actions():
        ''' Restituisce la dimensione totale dello spazio delle azioni. '''
        # Azioni di base (pesca, scarto, punteggio, ecc.)
        num_base_actions = 7 
        
        # Azioni di scarto (una per ogni carta)
        num_discard_actions = discard_action_id + CONST.CardValues.TOTAL_CARDS.value
        
        # stima delle possibili combinazioni senza ripetizione: 
        # C(n,k) = n! / k!(n-k)!
        # con 15(n) carte e set da 3(k) carte
        # possibile Tuning 
        num_open_actions = 455
        
        # Assumiamo un massimo di 15 carte in mano 
        # e 10 scale/tris sul tavolo.
        # 15 * 10 = 150.
        num_update_actions = 150
        
        # Somma tutte le categorie per ottenere la dimensione totale
        return num_base_actions + num_discard_actions + num_open_actions + num_update_actions
        
    #gestione dinamica dello spazio di ricerca delle azioni
    def get_legal_actions(state, player):
        """
        Genera la lista delle azioni valide per il giocatore e lo stato attuali.

        Args:
            state: L'oggetto che rappresenta lo stato del gioco.
            player: Il giocatore corrente.

        Returns:
            Una lista di oggetti ActionEvent validi.
        """
        legal_actions = []

        #TODO FIXME: gestire le legal_actions in base allo stato del gioco
        # es. se il giocatore NON ha già pescato, DEVE pescare (mazzo o scarti)
        # es. se il giocatore ha già pescato, non può pescare di nuovo

        # Aggiunge le azioni di base (pescare dal mazzo, prendere dagli scarti, scartare)
        legal_actions.append(PickUpCardAction())
        legal_actions.append(PickUpDiscardAction())

        # Genera le azioni di creazione e update delle combinazioni
        potential_tris = csp_resolver.find_csp_tris(player)
        for tris in potential_tris:
            legal_actions.append(OpenTrisAction(tris))

        potential_melds = csp_resolver.find_csp_scala(player)
        for meld in potential_melds:
            legal_actions.append(OpenMeldAction(meld))

        potential_tris = csp_resolver.get_possible_tris_to_update(player)
        for tris in potential_tris:
            legal_actions.append(UpdateTrisAction(tris))

        potential_melds = csp_resolver.get_possible_meld_to_update(player)
        for meld in potential_melds:
            legal_actions.append(UpdateMeldAction(meld))
        
        # Aggiunge le azioni di scarto per ogni carta scartabile
        for card in csp_resolver.can_discard_card(player):
            legal_actions.append(DiscardAction(card.card_id))

        # Aggiunge l'azione di chiusura del gioco
        if csp_resolver.can_end_game_csp(player):
            legal_actions.append(CloseGameAction())

        return legal_actions

class ScoreFirstPlayerAction(ActionEvent):

    def __init__(self):
        super().__init__(action_id=score_player_0_action_id)

    def __str__(self):
        return "score N"

class ScoreSecondPlayerAction(ActionEvent):

    def __init__(self):
        super().__init__(action_id=score_player_1_action_id)

    def __str__(self):
        return "score S"


class PickUpCardAction(ActionEvent):

    def __init__(self, player):
        super().__init__(action_id=draw_card_action_id)
        self.player = player

    def __str__(self):
        return "pick_up_card"


class PickUpDiscardAction(ActionEvent):

    def __init__(self, player):
        super().__init__(action_id=pick_up_discard_action_id)
        self.player = player

    def __str__(self):
        return "pick_up_discard"

class OpenMeldAction(ActionEvent):

    def __init__(self, cards):
        super().__init__(action_id=open_meld_action_id)
        self.cards = cards

    def __str__(self):
        return "open_meld_action_id"

class OpenTrisAction(ActionEvent):

    def __init__(self, cards):
        super().__init__(action_id=open_tris_action_id)
        self.cards = cards

    def __str__(self):
        return "open_tris_action_id"

class UpdateMeldAction(ActionEvent):

    def __init__(self, update):
        super().__init__(action_id=update_meld_action_id)
        self.update = update

    def __str__(self):
        return "update_meld_action_id"

class UpdateTrisAction(ActionEvent):

    def __init__(self, update):
        super().__init__(action_id=update_tris_action_id)
        self.update = update

    def __str__(self):
        return "update_tris_action_id"


class DiscardAction(ActionEvent):

    def __init__(self, card_id):
        super().__init__(action_id=discard_action_id + card_id)
        self.card_id = card_id

    def __str__(self):
        return "discard {}".format(str(self.card_id))


class CloseGameAction(ActionEvent):
    def __init__(self, card):
        super().__init__(action_id=close_game_action_id)
        self.card = card

    def __str__(self):
        return "CloseGame "
    
""" 
--POSSIBILE ESPANSIONE INSERENDO LA RICERCA 
DELLE POSSIBILI CONMBINAZIONI 
COME AZIONE ATTIVA IN MODO DA 
POTERLE VALUTARE, E NON SOLO COME 
MEZZO PER UNA EVENTUALE GIOCATA

--cosi come la valutazione delle combinazioni 
avversarie sul tavolo

class FindMeldAction(ActionEvent):

    def __init__(self, cards):
        super().__init__(action_id=find_meld_action_id)
        self.cards = cards

    def __str__(self):
        return "find_meld_action_id"
    
class FindTrisAction(ActionEvent):

    def __init__(self, cards):
        super().__init__(action_id=find_tris_action_id)
        self.cards = cards

    def __str__(self):
        return "find_tris_action_id"

 """