import Player.player_csp_resolver as csp_resolver
import Player.player_onto_manager as play_onto
import Ontologia.onto_access_util as onto_access_util
from .action_event_static import *
from .action_event_utils import (ActionIndexes,\
                                get_open_tris_action_id,
                                get_open_meld_action_id,
                                get_tris_update_action_id,
                                get_meld_update_action_id)


class BurracoJudge:

    def __init__(self):
        self.action_map = []

    # TODO Possibile implementazione di Monte Carlo Tree Search
    # per la previsione delle mosse a più lungo termine
    def get_legal_actions(self, player):
        legal_actions = []

        # Aggiunge le azioni di base (pescare dal mazzo, prendere dagli scarti, scartare)
        if len(self.action_map) == 0:
            #da regolamento internazionale ART. 16
            if len(onto_access_util.get_monte()) == 2:
                #chiudere la partita
                legal_actions.append(CloseGameJudgeAction(ActionIndexes.CLOSE_GAME_JUDGE_ACTION_ID.value[1]))
            else:
                #continua
                legal_actions.append(PickUpCardAction(ActionIndexes.PICK_UP_ACTION_ID.value[1]))
                legal_actions.append(PickUpDiscardAction(ActionIndexes.PICK_UP_DISCARD_ACTION_ID.value[1]))
        else:
            # Genera le azioni di creazione e update delle combinazioni
            potential_tris = csp_resolver.find_csp_tris(player)
            for tris in potential_tris:
                # Trasforma il tris in action_id
                legal_actions.append(OpenTrisAction(get_open_tris_action_id(tris)))

            potential_melds = csp_resolver.find_csp_scala(player)
            for meld in potential_melds:
                legal_actions.append(OpenMeldAction(get_open_meld_action_id(meld)))


            #[[(False, 10, 1), (-1, 53, 'Jolly', 30)]...]
            #[[(se il tris ha una matta, il rango del tris, tris_id),(carta da aggiungere)]
            potential_tris_upd = csp_resolver.get_possible_tris_to_update(player)
            for tris_up_info in potential_tris_upd:
                #restituisce un array di action_ids perchè divisi per tris
                action_ids = get_tris_update_action_id(tris_up_info)
                count = 0
                for single_tris_up in tris_up_info[0]:
                    #    def __init__(self, tris_id, card_id, action_id):
                    legal_actions.append(UpdateTrisAction(single_tris_up[0][2], single_tris_up[1][1], action_ids[count]))
                    count += 1

            #  ['update_meld_action_id', (0, 'Picche', 7, 30)],
            #(matta, seme, meld_len, card_value)
            potential_melds_upd = csp_resolver.get_possible_meld_to_update(player)
            for meld_up_info in potential_melds_upd:
                action_ids = get_meld_update_action_id(meld_up_info)
                count = 0
                for single_mel_up in meld_up_info[0]:
                    #__init__(self, meld_id, card_id, action_id)
                    legal_actions.append(UpdateMeldAction(single_mel_up[1][5], single_mel_up[0][1], action_ids[count]))
                    count += 1
            
            # TODO PER DEBUG, DA DISATTIVARE
            if len(legal_actions) < 5:
                # Aggiunge l'azione di chiusura del gioco
                card = csp_resolver.can_end_game_csp(player)
                if card != []:
                    legal_actions.append(CloseGameAction(ActionIndexes.CLOSE_GAME_ACTION_ID.value[1] + card[0][0][1]))
                else:
                    for card in play_onto.get_players_card(player):
                        legal_actions.append(DiscardAction(ActionIndexes.DISCARD_ACTION_ID.value[1] + card[1]))


        self.action_map = legal_actions
        return legal_actions

    def decode_action(self, action_id) -> 'ActionEvent':
        ''' Action id -> the action_event in the game.

        Args:
            action_id (int): the id of the action

        Returns:
            action (ActionEvent): the action that will be passed to the game engine.
        '''
        # pickUp
        if action_id == ActionIndexes.PICK_UP_ACTION_ID.value[1]:
            action_event = PickUpCardAction(action_id)
        # pickUpDiscard
        elif action_id == ActionIndexes.PICK_UP_DISCARD_ACTION_ID.value[1]:
            action_event = PickUpDiscardAction(action_id)
        # discard
        elif action_id >= ActionIndexes.DISCARD_ACTION_ID.value[1] and action_id < ActionIndexes.CLOSE_GAME_ACTION_ID.value[1]:
            action_event = DiscardAction(action_id)
        # close game
        elif action_id >= ActionIndexes.CLOSE_GAME_ACTION_ID.value[1] and action_id < ActionIndexes.OPEN_TRIS_ACTION_ID.value[1]:
            action_event = CloseGameAction(action_id)
        
        # open tris
        elif action_id >= ActionIndexes.OPEN_TRIS_ACTION_ID.value[1] and action_id < ActionIndexes.OPEN_MELD_ACTION_ID.value[1]:
            action_event = OpenTrisAction(action_id)
        # open scala
        elif action_id >= ActionIndexes.OPEN_MELD_ACTION_ID.value[1] and action_id < ActionIndexes.UPDATE_TRIS_ACTION_ID.value[1]:
            action_event = OpenMeldAction(action_id)

        # update tris
        # in caso di più azioni possibili con lo stesso id
        # prenderne uno qualsiasi, caso difficile ma non rarissimo
        # in tal caso strategicamente non influisce 
        # sul gioco e/o apprendimento
        elif action_id >= ActionIndexes.UPDATE_TRIS_ACTION_ID.value[1] and action_id < ActionIndexes.UPDATE_MELD_ACTION_ID.value[1]:
            action_event = self.decode_update_action(action_id)
        # update scala
        elif action_id >= ActionIndexes.UPDATE_MELD_ACTION_ID.value[1] and action_id < ActionIndexes.CLOSE_GAME_JUDGE_ACTION_ID.value[1]:
            action_event = self.decode_update_action(action_id)

        # partita chiusa da Judge
        elif action_id == ActionIndexes.CLOSE_GAME_JUDGE_ACTION_ID.value[1]:
            action_event = CloseGameJudgeAction(action_id)

        else:
            raise Exception("decode_action: unknown action_id={}".format(action_id))
        return action_event

    #serve per gestire gli update
    def decode_update_action(self, action_id):
        value = next((obj for obj in self.action_map if obj.action_id == action_id), None)
        return value
    
    def clean_map(self):
        self.action_map = []
