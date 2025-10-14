import Utils.CONST as CONST

class ActionEvent(object):

    def __init__(self, judge):
        self.judge = judge
        self.action_map = []

    def __eq__(self, other):
        return isinstance(other, ActionEvent)
    
    # serve per dichiarare il volume del
    # massimo spazio di ricerca
    @staticmethod
    def get_num_actions():
        ''' Restituisce la dimensione totale dello spazio delle azioni. '''
        # Azioni di base (pesca, scarto, punteggio, ecc.)
        num_base_actions = 7 
        
        # Azioni di scarto (una per ogni carta)
        num_discard_actions = CONST.CardValues.TOTAL_CARDS.value
        
        # stima delle possibili combinazioni senza ripetizione: 
        # con 15(n) carte e set da 3(k) carte
        # C(n,k) = n! / k!(n-k)!
        # possibile Tuning 
        num_open_actions = 455
        
        # Assumiamo un massimo di 15 carte in mano 
        # e 10 scale/tris sul tavolo.
        # 15 * 10 = 150.
        num_update_actions = 150
        
        # Somma tutte le categorie per ottenere la dimensione totale
        return num_base_actions + num_discard_actions + num_open_actions + num_update_actions

class PickUpCardAction(ActionEvent):

    def __init__(self, action_id):
        self.action_id = action_id

    def __str__(self):
        return "pick_up_card"


class PickUpDiscardAction(ActionEvent):

    def __init__(self, action_id):
        self.action_id = action_id

    def __str__(self):
        return "pick_up_discard"

class OpenMeldAction(ActionEvent):

    def __init__(self, cards,action_id):
        self.action_id = action_id
        self.cards = cards

    def __str__(self):
        return "open_meld_action_id"

class OpenTrisAction(ActionEvent):

    def __init__(self, cards, action_id):
        self.action_id = action_id
        self.cards = cards

    def __str__(self):
        return "open_tris_action_id"

class UpdateMeldAction(ActionEvent):

    def __init__(self,meld,card, action_id):
        self.meld = meld
        self.card = card
        self.action_id = action_id

    def __str__(self):
        return "update_meld_action_id"

class UpdateTrisAction(ActionEvent):

    def __init__(self, tris, card, action_id):
        self.tris = tris
        self.card = card
        self.action_id = action_id

    def __str__(self):
        return "update_tris_action_id"


class DiscardAction(ActionEvent):

    def __init__(self, card_id, action_id):
        self.card_id = card_id
        self.action_id = action_id

    def __str__(self):
        return "discard {}".format(str(self.card_id))


class CloseGameAction(ActionEvent):
    def __init__(self, card_id, action_id):
        self.card_id = card_id
        self.action_id = action_id

    def __str__(self):
        return "CloseGame "