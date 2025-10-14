import Player.player_csp_resolver as csp_resolver
import Player.player_onto_manager as play_onto
from .action_event_dyn import (PickUpCardAction,PickUpDiscardAction,
                              OpenTrisAction,OpenMeldAction,UpdateTrisAction,
                              UpdateMeldAction,DiscardAction,CloseGameAction)

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

        # Aggiunge le azioni di base (pescare dal mazzo, prendere dagli scarti, scartare)
        legal_actions.append(PickUpCardAction(len(legal_actions)))
        legal_actions.append(PickUpDiscardAction(len(legal_actions)))

        # Genera le azioni di creazione e update delle combinazioni
        potential_tris = csp_resolver.find_csp_tris(player)
        for tris in potential_tris:
            legal_actions.append(OpenTrisAction(tris,len(legal_actions)))

        potential_melds = csp_resolver.find_csp_scala(player)
        for meld in potential_melds:
            legal_actions.append(OpenMeldAction(meld,len(legal_actions)))

        potential_tris = csp_resolver.get_possible_tris_to_update(player)
        for tris in potential_tris:
            legal_actions.append(UpdateTrisAction(tris,len(legal_actions)))

        potential_melds = csp_resolver.get_possible_meld_to_update(player)
        for meld in potential_melds:
            legal_actions.append(UpdateMeldAction(meld,len(legal_actions)))
        
        # Aggiunge le azioni di scarto per ogni carta scartabile
        for card in play_onto.get_players_card(player):
            legal_actions.append(DiscardAction(card[1],len(legal_actions)))

        # Aggiunge l'azione di chiusura del gioco
        card = csp_resolver.can_end_game_csp(player)
        if card != None:
            legal_actions.append(CloseGameAction(card[1],len(legal_actions)))
        
        self.action_map = legal_actions
        return legal_actions
    
    def decode_action(self, action_id):
        return self.action_map[action_id]