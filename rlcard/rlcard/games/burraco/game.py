import numpy as np

from .player import BurracoPlayer
from .round import BurracoRound
from .judge import BurracoJudge
from .action_event import *
from Player.player_onto_manager import get_player_known_cards, get_player_unknown_cards, get_player_melds, get_player_tris,get_player_cards
from Ontologia.onto_access_util import get_monte, get_scarti


import Ontologia.initGame as initGame

class BurracoGame:
	''' Game class. This class will interact with outer environment.
	'''

	def __init__(self, allow_step_back=False):
		'''Initialize the class BurracoGame
		'''
		self.allow_step_back = allow_step_back
		self.np_random = np.random.RandomState()
		self.actions = None  # type: List[ActionEvent] or None # must reset in init_game
		self.round = None  # round: BurracoRound or None, must reset in init_game
		self.num_players = 2
		self.judge = BurracoJudge()


	def init_game(self):
		self.game=initGame.init_game()
		self.round = BurracoRound(self.game.players, self.game.turnOf.idGiocatore)
		self.actions = []
		self.round = None
		current_player_id = self.round.current_player_id
		state = self.get_state(player_id=current_player_id)
		return state, current_player_id


	def step(self, action: ActionEvent):
		''' Perform game action and return next player number, and the state for next player
		'''
		if isinstance(action, PickUpCardAction):
			self.round.pick_up_card(action)
		elif isinstance(action, PickUpDiscardAction):
			self.round.pick_up_discard(action)

		elif isinstance(action, OpenMeldAction):
			self.round.open_meld(action)
		elif isinstance(action, OpenTrisAction):
			self.round.open_tris(action)
		elif isinstance(action, UpdateMeldAction):
			self.round.update_meld(action)
		elif isinstance(action, UpdateTrisAction):
			self.round.update_tris(action)

		elif isinstance(action, DiscardAction):
			self.round.discard(action)

		elif isinstance(action, CloseGameAction):
			self.round.close_game(action)

		else:
			raise Exception('Unknown step action={}'.format(action))
		
		self.actions.append(action)
		next_player_id = self.round.current_player_id
		next_state = self.get_state(player_id=next_player_id)
		return next_state, next_player_id

	def step_back(self):
		''' Takes one step backward and restore to the last state
		'''
		raise NotImplementedError

	def get_num_players(self):
		''' Return the number of players in the game
		'''
		return len(self.game.players)

	def get_num_actions(self):
		''' Return the number of possible actions in the game
		'''
		return ActionEvent.get_num_actions()

	def get_player_id(self):
		''' Return the current player that will take actions soon
		'''
		return self.round.current_player_id

	def is_over(self):
		''' Return whether the current game is over
		'''
		return self.round.is_over

	def get_current_player(self) -> BurracoPlayer or None:
		return self.round.get_current_player()

	def get_last_action(self) -> ActionEvent or None:
		return self.actions[-1] if self.actions and len(self.actions) > 0 else None

	def get_state(self, player_id: int):
		''' Get player's state

		Return:
			state (dict): The information of the state
		'''
		state = {}
		if not self.is_over():
			last_action = self.get_last_action()
			opponent_id = (player_id + 1) % 2
			opponent = self.round.players[opponent_id]
			opponent_known_cards = None
			opponent_unknown_cards = None

			#se il gioco è chiuso le carte dell'avversario diventano visibili
			if isinstance(last_action, CloseGameAction):
				opponent_known_cards = get_player_cards(opponent.player1) + get_player_melds(opponent.player1) + get_player_tris(opponent.player1)
				opponent_unknown_cards = []
			else:
				opponent_known_cards = get_player_known_cards(opponent.player1) + get_player_melds(opponent.player1) + get_player_tris(opponent.player1)
				opponent_unknown_cards = get_player_unknown_cards()

			opponent_known_cards.extend( get_player_melds(opponent.player1) + get_player_tris(opponent.player1))

			state['player_id'] = player_id
			state['hand'] = [card.idCarta for card in get_player_cards(self.round.players[player_id].player1)]
			state['top_discard'] =[card.idCarta for card in get_scarti()]
			state['dead_cards'] = [card.idCarta for card in get_monte() ]
			state['opponent_known_cards'] = [x.get_index() for x in opponent_known_cards]
			state['opponent_unknown_cards'] = [x.get_index() for x in opponent_unknown_cards]
		return state


# non più statico in quanto serve 
# la mappa dinamica della action
#	@staticmethod
	def decode_action(self, action_id) -> ActionEvent:
		return self.judge.decode_action(action_id)