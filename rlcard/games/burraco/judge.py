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
            #gestire il caso in cui finiscono le carte
            monte_gt_0, scarti_gt_1 = len(onto_access_util.get_monte()) > 0, len(onto_access_util.get_scarti()) > 0
            mask = (scarti_gt_1 << 1) | monte_gt_0
            match mask:
                case 0b00:
                    #print("not monte_gt_0 and not scarti_gt_1")
                    #chiudere la partita
                    legal_actions.append(CloseGameJudgeAction(len(legal_actions)))
                case 0b01:
                    #print("monte_gt_0 and not scarti_gt_1")
                    #continua (caso impossibile a meno di bug)
                    legal_actions.append(PickUpCardAction(len(legal_actions)))
                    legal_actions.append(PickUpDiscardAction(len(legal_actions)))
                case 0b10:
                    #print("not monte_gt_0 and scarti_gt_1")
                    #ripristinare mazzo
                    legal_actions.append(AddDiscardToPickupAction(len(legal_actions)))
                case 0b11:
                    #print("monte_gt_0 and scarti_gt_1")
                    #continua
                    legal_actions.append(PickUpCardAction(len(legal_actions)))
                    legal_actions.append(PickUpDiscardAction(len(legal_actions)))
                case _:
                    print("Altra combinazione")
                    #caso impossibile, lanciare errore
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
            card = csp_resolver.can_end_game_csp(player)
            if card != []:
                legal_actions.append(CloseGameAction(card[0][0][1],len(legal_actions)))
            # Aggiunge le azioni di scarto per ogni carta scartabile
            elif(len(potential_tris) == 0 and len(potential_melds) == 0 and len(potential_tris_upd) == 0 and len(potential_melds_upd) == 0 ):
                for card in play_onto.get_players_card(player):
                    legal_actions.append(DiscardAction(card[1],len(legal_actions)))


        self.action_map = legal_actions
        return legal_actions
    

    def decode_action(self, action_id):
        return self.action_map[action_id]

    def clean_map(self):
        self.action_map = []
