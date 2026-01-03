from . import utils as utils
from .action_event_utils import get_mapping

class ActionEvent(object):

    def __init__(self, action_id: int):
        self.mapping = get_mapping()
        self.action_id = action_id

    def __eq__(self, other):
        result = False
        if isinstance(other, ActionEvent):
            result = self.action_id == other.action_id
        return result

    @staticmethod
    def get_num_actions():
        ''' Return the number of possible actions in the game
        '''
        return 13217 + 1

class PickUpCardAction(ActionEvent):
    def __init__(self, action_id):
        super().__init__(action_id)
        self.action_id = action_id

    def __str__(self):
        return "pick_up_card"

class PickUpDiscardAction(ActionEvent):
    def __init__(self, action_id):
        super().__init__(action_id)
        self.action_id = action_id

    def __str__(self):
        return "pick_up_discard"

class DiscardAction(ActionEvent):
    def __init__(self, action_id):
        super().__init__(action_id)
        self.action_id = action_id
        self.card_id = self.mapping[action_id][1]

    def __str__(self):
        return "discard {}".format(str(self.card_id))

class CloseGameAction(ActionEvent):
    def __init__(self, action_id):
        super().__init__(action_id)
        self.card_id = self.mapping[action_id][1]
        self.action_id = action_id

    def __str__(self):
        return "CloseGame"
    
class OpenTrisAction(ActionEvent):
    def __init__(self, action_id):
        super().__init__(action_id)
        self.action_id = action_id
        self.cards_ids = self.mapping[action_id][1]

    def __str__(self):
        return "open_tris_action_id"
    
class OpenMeldAction(ActionEvent):
    def __init__(self, action_id):
        super().__init__(action_id)
        self.action_id = action_id
        self.cards_ids = self.mapping[action_id][1]

    def __str__(self):
        return "open_meld_action_id"

class UpdateMeldAction(ActionEvent):
    def __init__(self, meld_id, card_id, action_id):
        super().__init__(action_id)
        self.meld_id = meld_id
        self.card_id = card_id
        self.action_id = action_id

    def __str__(self):
        return "update_meld_action_id"

class UpdateTrisAction(ActionEvent):
    def __init__(self, tris_id, card_id, action_id):
        super().__init__(action_id)
        self.tris_id = tris_id
        self.card_id = card_id
        self.action_id = action_id

    def __str__(self):
        return "update_tris_action_id"

class CloseGameJudgeAction(ActionEvent):
    def __init__(self, action_id):
        super().__init__(action_id)
        self.action_id = action_id

    def __str__(self):
        return "CloseGameJudge"
    
    
# TODO ???
class AddDiscardToPickupAction(ActionEvent):
    def __init__(self, action_id):
        super().__init__(action_id)
        self.action_id = action_id

    def __str__(self):
        return "add_discard_to_pickup_action"