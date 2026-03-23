from .map_actions_ids import ActionIndexes, get_map_actions, create_mapping

def get_mapping():
    return create_mapping()

#mappatura
#['update_tris_action_id', (0, 6, 5, 30)],
#(matta, tris_len, tris_value, card_value)
#CSP
# ( [[res_csp], [res_csp]], len_tris)
#res_csp = [(False, 10, 1), (-1, 53, 'Jolly', 30)]
#[[(se il tris ha una matta, il rango del tris, tris_id),(carta da aggiungere)]
def get_tris_update_action_id(csp_len_updates):
    #da migliorare A/K:
    values = [15, 20, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10]
    tris_len = csp_len_updates[1][3] if csp_len_updates[1][3] < 7 else 7
    tris_rank = csp_len_updates[1][1] - 1

    #trovare in mappa
    action = (int(csp_len_updates[1][0]),   # matta 
            tris_len,                       # tris_len
            values[tris_rank],              # tris_value
            csp_len_updates[0][3]           # card_value
            )
    
    # Ricerca O(1) nella mappa
    action_map = get_map_actions()
    search_key = tuple((ActionIndexes.UPDATE_TRIS_ACTION_ID.value[0], action))
    indice = action_map.get(search_key)
    if indice is None:
        raise Exception(f"get_tris_update_action_id: action {action} not found in mapping")
        
    return indice

#mappatura
#  ['update_meld_action_id', (0, 'Picche', 7, 30)],
#(matta, seme, meld_len, card_value)

#CSP
# res_csp = [(6, 72, 'Quadri', 5), (True, 'Quadri', 8, 10, (7,8,9), 3)]
#[[(carta da aggiungere), (se il tris ha una matta, seme della scala, min, max, (ranks), scalaId)]
def get_meld_update_action_id(csp_len_updates):
    # Recupera il dizionario pre-calcolato tramite get_map_actions()

    #meld_len = csp_len_updates[1] if csp_len_updates[1] < 7 else 7
    meld_len = len(csp_len_updates[1][1]) if len(csp_len_updates[1][1]) < 7 else 7
    # Il seme è costante per questo gruppo di update
    meld_seme = csp_len_updates[1][0][1]

    # Costruzione della chiave di ricerca (matta, seme, meld_len, card_value)
    action = (int(csp_len_updates[1][0][0]),    # matta (0 o 1)
                meld_seme,                      # seme
                meld_len,                       # meld_len
                csp_len_updates[0][3]           # card_value
                )

    # Ricerca O(1) nella mappa
    action_map = get_map_actions()
    search_key = tuple((ActionIndexes.UPDATE_MELD_ACTION_ID.value[0], action))
    indice = action_map.get(search_key)
    if indice is None:
        raise Exception(f"get_meld_update_action_id: action {action} not found in mapping")

    return indice

# Formato di un singolo tris dal CSP:
# [(-1, 53, 'Jolly', 30), (10, 35, 'Fiori', 10), (10, 9, 'Cuori', 10)]
def get_open_tris_action_id(tris_meld):
    # Recupera il dizionario pre-calcolato tramite get_map_actions()
    action_map = get_map_actions()

    normali = [c[1] for c in tris_meld if c[0] not in (2, -1)]
    matte = [c[1] for c in tris_meld if c[0] in (2, -1)]

    unordered_ids = sorted(normali) + matte
    sorted_ids_tuple = tuple(unordered_ids)

    # Ricerca diretta nel dizionario (O(1))
    search_key = tuple((ActionIndexes.OPEN_TRIS_ACTION_ID.value[0], sorted_ids_tuple))
    indice = action_map.get(search_key)

    if indice is not None:
        return indice
    else:
        raise Exception(f"get_open_tris_action_id: {search_key} not found in mapping")

# Formato di un singolo tris dal CSP:
# [(-1, 53, 'Jolly', 30), (10, 35, 'Fiori', 10), (10, 9, 'Cuori', 10)]
def get_open_meld_action_id(meld):
    # Recupera il dizionario pre-calcolato tramite get_map_actions()
    action_map = get_map_actions()
    meld = sorted(meld, key=lambda x: x[0])

    values = [c[0] for c in meld if c[0] not in (2, -1)]
    normali = [c[1] for c in meld if c[0] not in (2, -1)]
    matte = [c[1] for c in meld if c[0] in (2, -1)]

    sorted_ids_tuple = []
    if len(values) < 3:
        if(values[1] - values[0]) > 1:
            sorted_ids_tuple = tuple([normali[0], matte[0], normali[1]])
        else:
            sorted_ids_tuple = tuple([normali[0], normali[1], matte[0]])
    else:
        sorted_ids_tuple = tuple(normali)

    # Ricerca diretta nel dizionario (O(1))
    # La chiave nella mappa sarà (tipo_azione, (id1, id2, id3...))
    search_key = tuple((ActionIndexes.OPEN_MELD_ACTION_ID.value[0], sorted_ids_tuple))
    indice = action_map.get(search_key)

    if indice is not None:
        return indice
    else:
        raise Exception(f"get_open_meld_action_id: {search_key} not found in mapping")