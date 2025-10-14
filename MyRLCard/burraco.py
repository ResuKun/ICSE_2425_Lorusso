#env/
import numpy as np
from collections import OrderedDict
from rlcard.envs import Env
from .game import BurracoGame as Game
import utils as utils
import Utils.CONST as CONST

class BurracoEnv(Env):
    ''' Burraco Environment
    '''
    def __init__(self, config):

        self._utils = utils

        self.name = 'burraco'
        self.game = Game()
        super().__init__(config=config)
        self.state_shape = [[5, CONST.CardValues.TOTAL_CARDS.value] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]


    #costruisce i tensori numerici
    def _extract_state(self, state):
        ''' Encode state

        Args:
            state (dict): dict of original state

        Returns:
            basato su 1 hot encoding (_utils.encode_cards)
            numpy array: 5 * 108 array
                         5 : hand (carte nella mano del giocatore)
                             top_discard (scarti)
                             dead_cards (monte)
                             opponent_known_cards (carte già viste dell'avversario (avversario raccoglie gli scarti))
                             opponent_unknown_cards (carte non viste dell'avversario)
        '''
        if self.game.is_over():
            obs = np.array([self._utils.encode_cards([]) for _ in range(5)])
            extracted_state = {'obs': obs, 'legal_actions': self._get_legal_actions()}
            extracted_state['raw_legal_actions'] = list(self._get_legal_actions().keys())
            extracted_state['raw_obs'] = obs
        else:

            player_hand = state['hand']
            top_discard = state['top_discard']
            dead_cards = state['dead_cards']
            known_cards = state['opponent_known_cards']
            unknown_cards = state['opponent_unknown_cards']

            hand_rep = self._utils.encode_cards(player_hand)
            top_discard_rep = self._utils.encode_cards(top_discard)
            dead_cards_rep = self._utils.encode_cards(dead_cards)
            known_cards_rep = self._utils.encode_cards(known_cards)
            unknown_cards_rep = self._utils.encode_cards(unknown_cards)
            rep = [hand_rep, top_discard_rep, dead_cards_rep, known_cards_rep, unknown_cards_rep]
            obs = np.array(rep)
           
           # come nell' Uno, costruisce e restituisce un extracted_state
            extracted_state = {'obs': obs, 'legal_actions': self._get_legal_actions(), 'raw_legal_actions': list(self._get_legal_actions().keys())}
            extracted_state['raw_obs'] = obs
        return extracted_state

    def get_payoffs(self):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            payoffs (list): a list of payoffs for each player
        '''
        payoffs = [self.game.round.players[0].get_player_score(), self.game.round.players[1].get_player_score()]
        return np.array(payoffs)

    def _decode_action(self, action_id):
        ''' Action id -> the action in the game. Must be implemented in the child class.

        Args:
            action_id (int): the id of the action

        Returns:
            action (ActionEvent): the action that will be passed to the game engine.
        '''
        return self.game.decode_action(action_id=action_id)

    def _get_legal_actions(self):
        ''' Get all legal actions for current state

        Returns:
            legal_actions (list): a list of legal actions' id
        '''
        legal_actions = self.game.judge.get_legal_actions()
        legal_actions_ids = {action_event.action_id: None for action_event in legal_actions}
        return OrderedDict(legal_actions_ids)
