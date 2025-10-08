from Ontologia.MyCards import Card

from typing import List
import numpy as np
import Utils.CONST as CONST


# 1 hot encoding
def encode_cards(cards: List[Card]) -> np.ndarray:
    #inizializza a zero e poi aggiorna il corretto valore
    plane = np.zeros(CONST.CardValues.TOTAL_CARDS.value, dtype=int)
    for card in cards:
        card_id = card.idCarta
        plane[card_id] = 1
    return plane
