from typing import List
from .player import BurracoPlayer
from .action_event_dyn import *
from Ontologia.MyCards import Card, Scala, Tris
from RLCard.burraco_error import BurracoProgramError

#
#   These classes are used to keep a move_sheet history of the moves in a round.
#

class BurracoMove(object):
    pass


class PlayerMove(BurracoMove):

    def __init__(self, player: BurracoPlayer, action: ActionEvent):
        super().__init__()
        self.player = player
        self.action = action

class PickUpCardMove(PlayerMove):
    def __init__(self, player: BurracoPlayer, action: PickUpCardAction, card: Card):
        super().__init__(player, action)
        if not isinstance(action, PickUpCardAction):
            raise BurracoProgramError("action must be PickUpCardAction.")
        self.card = card

    def __str__(self):
        return "{} {} {}".format(self.player, self.action, str(self.card))


class PickupDiscardMove(PlayerMove):
    def __init__(self, player: BurracoPlayer, action: PickUpDiscardAction, cards: List[Card]):
        super().__init__(player, action)
        if not isinstance(action, PickUpDiscardAction):
            raise BurracoProgramError("action must be PickUpDiscardAction.")
        self.cards = cards

    def __str__(self):
        return "{} {} {}".format(self.player, self.action, str(self.cards))


class OpenMeldMove(PlayerMove):
    def __init__(self, player: BurracoPlayer, action: OpenMeldAction, cards: List[Card], accumulatedScore: int):
        super().__init__(player, action)
        if not isinstance(action, OpenMeldAction):
            raise BurracoProgramError("action must be OpenMeldAction.")
        self.cards = cards
        self.accumulatedScore = accumulatedScore

    def __str__(self):
        return "{} {} {} {}".format(self.player, self.action, str(self.cards), self.accumulatedScore)


class OpenTrisMove(PlayerMove):
    def __init__(self, player: BurracoPlayer, action: OpenTrisAction, cards: List[Card], accumulatedScore: int):
        super().__init__(player, action)
        if not isinstance(action, OpenTrisAction):
            raise BurracoProgramError("action must be OpenTrisAction.")
        self.cards = cards
        self.accumulatedScore = accumulatedScore

    def __str__(self):
        return "{} {} {} {}".format(self.player, self.action, str(self.cards), self.accumulatedScore)


class UpdateMeldMove(PlayerMove):
    def __init__(self, player: BurracoPlayer, action: UpdateMeldAction, meld: Scala, card: Card, accumulatedScore: int):
        super().__init__(player, action)
        if not isinstance(action, UpdateMeldAction):
            raise BurracoProgramError("action must be UpdateMeldAction.")
        self.card = card
        self.meld = meld
        self.accumulatedScore = accumulatedScore

    def __str__(self):
        return "{} {} {} {} {}".format(self.player, self.action, self.meld, self.card, self.accumulatedScore)


class UpdateTrisMove(PlayerMove):
    def __init__(self, player: BurracoPlayer, action: UpdateTrisAction, tris: Tris, card: Card, accumulatedScore: int):
        super().__init__(player, action)
        if not isinstance(action, UpdateTrisAction):
            raise BurracoProgramError("action must be UpdateTrisAction.")
        self.tris = tris
        self.card = card
        self.accumulatedScore = accumulatedScore

    def __str__(self):
        return "{} {} {} {} {}".format(self.player, self.action, self.tris, self.card, self.accumulatedScore)

class DiscardMove(PlayerMove):
    def __init__(self, player: BurracoPlayer, action: DiscardAction, card: Card):
        super().__init__(player, action)
        if not isinstance(action, DiscardAction):
            raise BurracoProgramError("action must be DiscardAction.")
        self.card = card

    def __str__(self):
        return "{} {} {}".format(self.player, self.action, str(self.card))


