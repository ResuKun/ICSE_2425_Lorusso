'''
    File name: gin_rummy/action_event.py
    Author: William Hale
    Date created: 2/12/2020
'''

from rlcard.games.base import Card
from map_actions_ids import create_mapping
from . import utils as utils


pick_up_action_id = 0
pick_up_discard_action_id = 1
discard_action_id = 2 
# 110 - 205
close_game_action_id = 110
# open_tris_action_id = 206 - 4909
# open_meld_action_id = 4910 - 11597
# update_tris_action_id = 11598 - 12893
#12894 - 13217
# update_meld_action_id = 12894 - 13217

# Vedere Excel per mappatura dettagliata

class ActionEvent(object):

    def __init__(self, action_id: int):
        self.mapping = create_mapping()
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

    @staticmethod
    def decode_action(action_id) -> 'ActionEvent':
        ''' Action id -> the action_event in the game.

        Args:
            action_id (int): the id of the action

        Returns:
            action (ActionEvent): the action that will be passed to the game engine.
        '''
        # pickUp
        if action_id == pick_up_action_id:
            action_event = PickUpCardAction()
        # pickUpDiscard
        elif action_id == pick_up_discard_action_id:
            action_event = PickUpDiscardAction()
        # discard
        elif action_id >= discard_action_id and action_id < close_game_action_id:
            action_event = DiscardAction(action_id)
        #close game TODO
        elif action_id >= discard_action_id and action_id < close_game_action_id:
            action_event = DiscardAction(action_id)

        elif action_id in range(knock_action_id, knock_action_id + 52):
            card_id = action_id - knock_action_id
            card = utils.get_card(card_id=card_id)
            action_event = KnockAction(card=card)
        else:
            raise Exception("decode_action: unknown action_id={}".format(action_id))
        return action_event


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
        self.card_id = action_id - discard_action_id

    def __str__(self):
        return "discard {}".format(str(self.card_id))

class CloseGameAction(ActionEvent):
    def __init__(self, action_id):
        super().__init__(action_id)
        self.card_id = self.mapping[action_id][1]
        self.action_id = action_id

    def __str__(self):
        return "CloseGame"

class OpenMeldAction(ActionEvent):
    def __init__(self, cards, action_id):
        super().__init__(action_id)
        self.action_id = action_id
        self.cards_ids = self.mapping[action_id][1]

    def __str__(self):
        return "open_meld_action_id"

class OpenTrisAction(ActionEvent):
    def __init__(self, cards, action_id):
        super().__init__(action_id)
        self.action_id = action_id
        self.cards_ids = self.mapping[action_id][1]

    def __str__(self):
        return "open_tris_action_id"

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