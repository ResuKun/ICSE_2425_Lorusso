import Utils.CONST as CONST
import Ontologia.onto_save_manager as onto_save_manager
onto = onto_save_manager.get_ontology_from_manager()


score_player_0_action_id = 0
score_player_1_action_id = 1
draw_card_action_id = 2
pick_up_discard_action_id = 3
find_meld_action_id = 4
find_tris_action_id = 5
open_meld_action_id = 6
open_tris_action_id = 7
find_meld_update_action_id = 8
find_tris_update_action_id = 9
update_meld_action_id = 10
update_tris_action_id = 11
discard_action_id = 12
close_game_action_id = 121


class ActionEvent(object):

    def __init__(self, action_id: int):
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
        return discard_action_id + CONST.CardValues.TOTAL_CARDS  # FIXME: 120 dato il totale, ma da ricontrollare

    @staticmethod
    def decode_action(action_id) -> 'ActionEvent':
        ''' Action id -> the action_event in the game.

        Args:
            action_id (int): the id of the action

        Returns:
            action (ActionEvent): the action that will be passed to the game engine.
        '''
        if action_id == score_player_0_action_id:
            action_event = ScoreFirstPlayerAction()
        elif action_id == score_player_1_action_id:
            action_event = ScoreSecondPlayerAction()
       
        elif action_id == draw_card_action_id:
            action_event = DrawCardAction()
        elif action_id == pick_up_discard_action_id:
            action_event = PickUpDiscardAction()
            
        elif action_id == find_meld_action_id:
            action_event = FindMeldAction()
        elif action_id == find_tris_action_id:
            action_event = FindTrisAction()
        elif action_id == open_meld_action_id:
            action_event = OpenMeldAction()
        elif action_id == open_tris_action_id:
            action_event = OpenTrisAction()

        elif action_id == find_meld_update_action_id:
            action_event = FindMeldUpdateAction()
        elif action_id == find_tris_update_action_id:
            action_event = FindTrisUpdateAction()
        elif action_id == update_meld_action_id:
            action_event = UpdateMeldAction()
        elif action_id == update_tris_action_id:
            action_event = UpdateTrisAction()


        elif action_id in range(discard_action_id, ActionEvent.get_num_actions()):
            card_id = action_id - discard_action_id
            action_event = DiscardAction(card_id)
        
        elif action_id == close_game_action_id:
            action_event = CloseGameAction()

        else:
            raise Exception("decode_action: unknown action_id={}".format(action_id))
        return action_event


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


class DrawCardAction(ActionEvent):

    def __init__(self):
        super().__init__(action_id=draw_card_action_id)

    def __str__(self):
        return "draw_card"


class PickUpDiscardAction(ActionEvent):

    def __init__(self):
        super().__init__(action_id=pick_up_discard_action_id)

    def __str__(self):
        return "pick_up_discard"


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


class OpenMeldAction(ActionEvent):

    def __init__(self, meld):
        super().__init__(action_id=open_meld_action_id)
        self.meld = meld

    def __str__(self):
        return "open_meld_action_id"

class OpenTrisAction(ActionEvent):

    def __init__(self, tris):
        super().__init__(action_id=open_tris_action_id)
        self.tris = tris

    def __str__(self):
        return "open_tris_action_id"

class FindMeldUpdateAction(ActionEvent):

    def __init__(self, cards, meld):
        super().__init__(action_id=find_meld_update_action_id)
        self.cards = cards
        self.meld = meld

    def __str__(self):
        return "find_meld_update_action_id"

class FindTrisUpdateAction(ActionEvent):

    def __init__(self, cards, tris):
        super().__init__(action_id=find_tris_update_action_id)
        self.cards = cards
        self.tris = tris

    def __str__(self):
        return "find_meld_update_action_id"

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