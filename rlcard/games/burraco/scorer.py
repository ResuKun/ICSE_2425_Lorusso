from game import BurracoGame
from player import BurracoPlayer
import Player.player_onto_manager as pom

class BurracoScorer:

    def __init__(self):
        pass

    def get_payoffs(self, game: BurracoGame ):
        payoffs = [0, 0]
        for i in range(2):
            player = game.round.players[i]
            payoff = self.get_payoff(player=player, game=game)
            payoffs[i] = payoff
        return payoffs

# restituisce il punteggio - il valore le carte in mano
# se il giocatore ha chiuso il punteggio non verrà quindi scalato
def get_payoff(player: BurracoPlayer, game: BurracoGame ) -> int:
    return pom.get_player_score(player.player1) - sum(card.valoreCarta for card in pom.get_player_cards(player.player1))

