
import Ontologia.onto_access_util as onto_access_util

#classe di integrazione per RLCard
class BurracoPlayer:

	def __init__(self, player_name):
		''' Initialize a Burraco player class

		Args:
			player_id (int): id for the player
		'''
		self.player1 = onto_access_util.get_player_by_name(player_name)
		self.player_id = self.player1.idGiocatore

	def get_player_id(self):
		''' Get the id of the player

		Returns:
			int: the id of the player
		'''
		return self.player_id
	
	def get_player_name(self):
		''' Get the name of the player

		Returns:
			str: the name of the player
		'''
		return self.player1.nomeGiocatore
	
	def get_player_score(self):
		''' Get the score of the player

		Returns:
			int: the score of the player
		'''
		return self.player1.punteggioGiocatore
	
	def get_player_hand(self):
		''' Get the hand of the player

		Returns:
			list: the hand of the player
		'''
		return self.player1.playerHand.mazzo if self.player1.playerHand else []
	
	def get_player_melds(self):
		''' Get the player's melds

		Returns:
			list: player's meld
		'''
		return self.player1.scala
	
	def get_player_tris(self):
		''' Get the player's tris

		Returns:
			list: player's tris
		'''
		return self.player1.tris