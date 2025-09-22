from enum import Enum

class CardValues(Enum):
    MAX_PLAYER = 2
    TOTAL_CARDS = 108
    JOLLY_VALUE = -1
    PINELLA_VALUE = 2
    PLACEHOLDER_VALUE = -2
    PLACEHOLDER_OBJECT = (-2, "Empty")
    MAX_HAND_CARD  = 20
    NUM_CARDS_TO_DEAL  = 11
