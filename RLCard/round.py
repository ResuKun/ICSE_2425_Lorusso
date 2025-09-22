from typing import List
from rlcard.games.gin_rummy.dealer import GinRummyDealer
import Utils.CONST as CONST
import Ontologia.onto_access_util as onto_access_util
import Player.player_onto_modifier as player_onto_util
from move import *

from .player import BurracoPlayer
from . import judge

from rlcard.games.gin_rummy.utils import melding
from rlcard.games.gin_rummy.utils import utils


# Per RLCard, un round nel Burraco è una mano intera, 
# ovvero dalla distribuzione delle carte alla chiusura

#questo vuol dire dover gestire:
#   - shuffle delle carte
#   - porre la prima carta del monte degli scarti
#   - creazione del pozzo (TOBE)
#   - distribuzione delle carte
#   - inizia il turno del primo giocatore

class BurracoRound:

    

    def __init__(self, players, round_number):
        #TODO verificare se self.{nome metodo} funziona
        self.init_round_cards(self)
        #self.players = [BurracoPlayer(player_id=0, np_random=self.np_random), BurracoPlayer(player_id=1, np_random=self.np_random)]
        self.players = [BurracoPlayer(players[0].nomeGiocatore), BurracoPlayer(players[1].nomeGiocatore)]
        
        #TODO verificare se RL ha bisogno di partire da 0 o da 1
        self.current_player_id = (round_number + 1) % CONST.CardValues.MAX_PLAYER.value
        
        self.is_over = False
        self.going_out_action = None  # going_out_action: int or None
        self.going_out_player_id = None  # going_out_player_id: int or None
        self.move_sheet = []  # type: List[BurracoMove]
        
       #nel GinRummy qui inizializza la Move
       #player_dealing = BurracoPlayer(player_id=dealer_id, np_random=self.np_random)
       #shuffled_deck = self.dealer.shuffled_deck
       #self.move_sheet.append(DealHandMove(player_dealing=player_dealing, shuffled_deck=shuffled_deck))

    def init_round_cards(self):
        #faccio il reset del mazzo e degli scarti
        onto_access_util.reset_deck()
        #faccio il reset delle mani dei giocatori
        player_onto_util.reset_players_hands()

    def get_current_player(self) -> BurracoPlayer or None:
        current_player_id = self.current_player_id
        return None if current_player_id is None else self.players[current_player_id]

    def pick_up_card(self, action: PickUpCardAction):
        #raccoglie la carta dal mazzo
        current_player = self.players[self.current_player_id]
        player_onto_util.pesca_carta(current_player)
        #registro l'evento
        self.move_sheet.append(PickUpCardMove(current_player, action=action, card=current_player.player1.playerHand.mazzo[-1]))

    def pick_up_discard(self, action: PickUpDiscardAction):
        #raccoglie la carta dagli scarti
        current_player = self.players[self.current_player_id]
        len_cards = player_onto_util.pesca_scarti(current_player)
        self.move_sheet.append(PickupDiscardMove(current_player, action, cards=current_player.player1.playerHand.mazzo[-len_cards]))

    def open_meld(self, action: OpenMeldAction):
        current_player = self.players[self.current_player_id]
        len_cards = player_onto_util.pesca_carta(current_player)
        self.move_sheet.append(OpenMeldAction(current_player, action, cards=current_player.player1.playerHand.mazzo[-len_cards]))


#TODO riprendi da qui

    def declare_dead_hand(self, action: DeclareDeadHandAction):
        # when current_player takes DeclareDeadHandAction step, the move is recorded and executed
        # north becomes current_player to score his hand
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(DeclareDeadHandMove(current_player, action))
        self.going_out_action = action
        self.going_out_player_id = self.current_player_id
        if not len(current_player.hand) == 10:
            raise BurracoProgramError("len(current_player.hand) is {}: should be 10.".format(len(current_player.hand)))
        self.current_player_id = 0

    def discard(self, action: DiscardAction):
        # when current_player takes DiscardAction step, the move is recorded and executed
        # opponent knows that the card is no longer in current_player hand
        # current_player loses his turn and the opponent becomes the current player
        current_player = self.players[self.current_player_id]
        if not len(current_player.hand) == 11:
            raise BurracoProgramError("len(current_player.hand) is {}: should be 11.".format(len(current_player.hand)))
        self.move_sheet.append(DiscardMove(current_player, action))
        card = action.card
        current_player.remove_card_from_hand(card=card)
        if card in current_player.known_cards:
            current_player.known_cards.remove(card)
        self.dealer.discard_pile.append(card)
        self.current_player_id = (self.current_player_id + 1) % 2

    def knock(self, action: KnockAction):
        # when current_player takes KnockAction step, the move is recorded and executed
        # opponent knows that the card is no longer in current_player hand
        # north becomes current_player to score his hand
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(KnockMove(current_player, action))
        self.going_out_action = action
        self.going_out_player_id = self.current_player_id
        if not len(current_player.hand) == 11:
            raise BurracoProgramError("len(current_player.hand) is {}: should be 11.".format(len(current_player.hand)))
        card = action.card
        current_player.remove_card_from_hand(card=card)
        if card in current_player.known_cards:
            current_player.known_cards.remove(card)
        self.current_player_id = 0

    def gin(self, action: GinAction, going_out_deadwood_count: int):
        # when current_player takes GinAction step, the move is recorded and executed
        # opponent knows that the card is no longer in current_player hand
        # north becomes current_player to score his hand
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(GinMove(current_player, action))
        self.going_out_action = action
        self.going_out_player_id = self.current_player_id
        if not len(current_player.hand) == 11:
            raise BurracoProgramError("len(current_player.hand) is {}: should be 11.".format(len(current_player.hand)))
        _, gin_cards = judge.get_going_out_cards(current_player.hand, going_out_deadwood_count)
        card = gin_cards[0]
        current_player.remove_card_from_hand(card=card)
        if card in current_player.known_cards:
            current_player.known_cards.remove(card)
        self.current_player_id = 0

    def score_player_0(self, action: ScoreNorthPlayerAction):
        # when current_player takes ScoreNorthPlayerAction step, the move is recorded and executed
        # south becomes current player
        if not self.current_player_id == 0:
            raise BurracoProgramError("current_player_id is {}: should be 0.".format(self.current_player_id))
        current_player = self.get_current_player()
        best_meld_clusters = melding.get_best_meld_clusters(hand=current_player.hand)
        best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
        deadwood_count = utils.get_deadwood_count(hand=current_player.hand, meld_cluster=best_meld_cluster)
        self.move_sheet.append(ScoreNorthMove(player=current_player,
                                              action=action,
                                              best_meld_cluster=best_meld_cluster,
                                              deadwood_count=deadwood_count))
        self.current_player_id = 1

    def score_player_1(self, action: ScoreSouthPlayerAction):
        # when current_player takes ScoreSouthPlayerAction step, the move is recorded and executed
        # south remains current player
        # the round is over
        if not self.current_player_id == 1:
            raise BurracoProgramError("current_player_id is {}: should be 1.".format(self.current_player_id))
        current_player = self.get_current_player()
        best_meld_clusters = melding.get_best_meld_clusters(hand=current_player.hand)
        best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
        deadwood_count = utils.get_deadwood_count(hand=current_player.hand, meld_cluster=best_meld_cluster)
        self.move_sheet.append(ScoreSouthMove(player=current_player,
                                              action=action,
                                              best_meld_cluster=best_meld_cluster,
                                              deadwood_count=deadwood_count))
        self.is_over = True
