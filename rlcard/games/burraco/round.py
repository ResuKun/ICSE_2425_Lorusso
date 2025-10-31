from typing import List
import Utils.CONST as CONST
import Ontologia.onto_access_util as onto_access_util
import Player.player_onto_manager as player_onto_util
from .move import *
from Utils.logger import SingletonLogger 

from .player import BurracoPlayer


# Per RLCard, un round nel Burraco è una mano intera, 
# ovvero dalla distribuzione delle carte alla chiusura

#questo vuol dire dover gestire:
#   - shuffle delle carte
#   - porre la prima carta del monte degli scarti
#   - creazione del pozzo (TOBE)
#   - distribuzione delle carte
#   - inizia il turno del primo giocatore

class BurracoRound:

    def __init__(self, players, round_number, judge):
        self.init_round_cards()
        #self.players = [BurracoPlayer(player_id=0, np_random=self.np_random), BurracoPlayer(player_id=1, np_random=self.np_random)]
        self.players = [BurracoPlayer(players[0].nomeGiocatore), BurracoPlayer(players[1].nomeGiocatore)]
        
        #TODO verificare se RL ha bisogno di partire da 0 o da 1
        self.current_player_id = (int(round_number)) % CONST.CardValues.MAX_PLAYER.value
        
        self.is_over = False
        self.going_out_action = None  # going_out_action: int or None
        self.going_out_player_id = None  # going_out_player_id: int or None
        self.move_sheet = []  # type: List[BurracoMove]
        self.game_judge = judge
        self.log = SingletonLogger().get_logger()
        
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
        player_onto_util.pesca_carta(current_player.player1)
        #registro l'evento
        self.move_sheet.append(PickUpCardMove(current_player, action=action, card=current_player.player1.playerHand.mazzo[-1]))
        self.log.info(f"{current_player.player1.nomeGiocatore} ----> {current_player.player1.playerHand.mazzo[-1].name}")

    def pick_up_discard(self, action: PickUpDiscardAction):
        #raccoglie la carta dagli scarti
        current_player = self.players[self.current_player_id]
        len_cards = player_onto_util.pesca_scarti(current_player.player1)
        self.move_sheet.append(PickupDiscardMove(current_player, action, cards=current_player.player1.playerHand.mazzo[-len_cards]))
        self.log.info(f"{current_player.player1.nomeGiocatore} ----> {current_player.player1.playerHand.mazzo[-len_cards].name}")

    def open_meld(self, action: OpenMeldAction):
        current_player = self.players[self.current_player_id]
        cards = action.cards
        accumulatedScore = player_onto_util.apre_scala(current_player.player1, cards)
        self.move_sheet.append(OpenMeldMove(current_player, action, cards, accumulatedScore))
        self.log.info(f"{current_player.player1.nomeGiocatore} ----> {cards}")
    
    def open_tris(self, action: OpenTrisAction):
        current_player = self.players[self.current_player_id]
        cards = action.cards
        accumulatedScore = player_onto_util.apre_tris(current_player.player1, cards)
        self.move_sheet.append(OpenTrisMove(current_player, action, cards, accumulatedScore))
        self.log.info(f"{current_player.player1.nomeGiocatore} ----> {cards}")

    def update_meld(self, action: UpdateMeldAction):
        current_player = self.players[self.current_player_id]
        card_id = action.card_id
        meld_id = action.meld_id
        accumulatedScore = player_onto_util.aggiunge_carta_scala(current_player.player1, meld_id, card_id)
        self.move_sheet.append(UpdateMeldMove(current_player, action, meld_id, card_id, accumulatedScore))
        self.log.info(f"{current_player.player1.nomeGiocatore} ----> {onto_access_util.get_meld_from_id(meld_id).semeScala} --> {onto_access_util.get_card_from_id(action.card_id).name}")
    
    def update_tris(self, action: UpdateTrisAction):
        current_player = self.players[self.current_player_id]
        card_id = action.card_id
        tris_id = action.tris_id
        accumulatedScore = player_onto_util.aggiunge_carta_tris(current_player.player1, tris_id, card_id)
        self.move_sheet.append(UpdateTrisMove(current_player, action, tris_id, card_id, accumulatedScore))
        self.log.info(f"{current_player.player1.nomeGiocatore} ----> {onto_access_util.get_tris_from_id(tris_id).trisValue} -->{onto_access_util.get_card_from_id(action.card_id).name}")
    
    def discard(self, action: DiscardAction):
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(DiscardMove(current_player, action))
        player_onto_util.scarta_carta(current_player.player1,action.card_id)
        #turno al giocatore successivo
        self.current_player_id = (self.current_player_id + 1) % 2
        onto_access_util.set_turnOf_by_id_player(self.current_player_id)
        self.game_judge.clean_map()
        self.log.info(f"{current_player.player1.nomeGiocatore} ----> {onto_access_util.get_card_from_id(action.card_id).name}")

    def close_game(self,action: CloseGameAction):
        current_player = self.players[self.current_player_id]
        player_onto_util.chiudi_gioco(current_player.player1,action.card_id)
        self.is_over = True
        self.log.info(f"{current_player.player1.nomeGiocatore} ----> {onto_access_util.get_card_from_id(action.card_id).name}")

