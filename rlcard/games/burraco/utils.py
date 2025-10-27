from Ontologia.MyCards import Card

from typing import List
import numpy as np
import Utils.CONST as CONST


# 1 hot encoding
# riceve una lista di id di carta
def encode_cards(cards: List) -> np.ndarray:
    #inizializza a zero e poi aggiorna il corretto valore
    plane = np.zeros(CONST.CardValues.TOTAL_CARDS.value, dtype=int)
    for card in cards:
        plane[card] = 1
    return plane
