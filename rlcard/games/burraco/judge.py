import Player.player_csp_resolver as csp_resolver
import Player.player_onto_manager as play_onto
import Ontologia.onto_access_util as onto_access_util
from .action_event_dyn import *

class BurracoJudge:

    def __init__(self):
        self.action_map = []

    # TODO Possibile implementazione di Monte Carlo Tree Search
    # per la previsione delle mosse a più lungo termine
    def get_legal_actions(self, player):
        legal_actions = []

        #TODO FIXME: gestire le legal_actions in base allo stato del gioco
        # es. se il giocatore NON ha già pescato, DEVE pescare (mazzo o scarti)
        # es. se il giocatore ha già pescato, non può pescare di nuovo
        
        #pulisce lo storico da AddDiscardToPickupAction
        if len(self.action_map) == 1 and isinstance(self.action_map[0], AddDiscardToPickupAction):
            self.action_map = []

        # Aggiunge le azioni di base (pescare dal mazzo, prendere dagli scarti, scartare)
        if len(self.action_map) == 0:
            #da regolamento internazionale ART. 16
            if len(onto_access_util.get_monte()) == 2:
                #print("not monte_gt_0 and not scarti_gt_1")
                #chiudere la partita
                legal_actions.append(CloseGameJudgeAction(len(legal_actions)))
            else:
                #continua
                legal_actions.append(PickUpCardAction(len(legal_actions)))
                legal_actions.append(PickUpDiscardAction(len(legal_actions)))
        else:
            # Genera le azioni di creazione e update delle combinazioni
            potential_tris = csp_resolver.find_csp_tris(player)
            for tris in potential_tris:
                legal_actions.append(OpenTrisAction(tris,len(legal_actions)))

            potential_melds = csp_resolver.find_csp_scala(player)
            for meld in potential_melds:
                legal_actions.append(OpenMeldAction(meld,len(legal_actions)))

            potential_tris_upd = csp_resolver.get_possible_tris_to_update(player)
            for tris in potential_tris_upd:
                legal_actions.append(UpdateTrisAction(tris[0][2], tris[1][1], len(legal_actions)))

            potential_melds_upd = csp_resolver.get_possible_meld_to_update(player)
            for meld in potential_melds_upd:
                legal_actions.append(UpdateMeldAction(meld[1][5],meld[0][1],len(legal_actions)))
            
            # Aggiunge l'azione di chiusura del gioco
            #if(len(legal_actions) == 0):
            card = csp_resolver.can_end_game_csp(player)
            if card != []:
                legal_actions.append(CloseGameAction(card[0][0][1],len(legal_actions)))
            else:
                for card in play_onto.get_players_card(player):
                    legal_actions.append(DiscardAction(card[1],len(legal_actions)))


        self.action_map = legal_actions
        return legal_actions
    

    def decode_action(self, action_id):
        return self.action_map[action_id]

    def clean_map(self):
        self.action_map = []
