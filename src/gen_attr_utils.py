import pm4py


def get_prefix_attr_freq(log, data_attr_labels):

    prefixes_freq_next_attr = dict()
    for trace in log:
        prefix = tuple()
        for event in trace:
            act = event['concept:name']
            attr = []
            for l in data_attr_labels:
                attr.append(event[l])
            attr = tuple(attr)
            pref_act = (prefix, act)
            if pref_act in prefixes_freq_next_attr.keys():
                if attr in prefixes_freq_next_attr[pref_act].keys():
                    prefixes_freq_next_attr[pref_act][attr] += 1
                else:
                    prefixes_freq_next_attr[pref_act][attr] = 1
            else:
                prefixes_freq_next_attr[pref_act] = {attr: 1}
            prefix = prefix + ((act, attr),)

    return prefixes_freq_next_attr


def get_prefix_attr_proba(log, data_attr_labels):
    """
    
    Returns a dictionary: {'prefix': {'attr': probability to execute 'attr' after 'prefix'}}
    'prefix' is a list of (act, attr)

    """

    prefixes_freq_next_attr = get_prefix_attr_freq(log, data_attr_labels)
    prefixes_act = prefixes_freq_next_attr.keys()
    prefixes_proba_next_attr = prefixes_freq_next_attr.copy()
    for prefix_act in prefixes_act:
        N_freq = sum(prefixes_freq_next_attr[prefix_act].values())
        for attr in prefixes_proba_next_attr[prefix_act].keys():
            prefixes_proba_next_attr[prefix_act][attr] /= N_freq

    return prefixes_proba_next_attr


def get_possible_prefixes_attr_act(prefixes_proba_next_attr):

    possible_prefixes_act = list(prefixes_proba_next_attr.keys())
    possible_prefixes = dict()
    for p in possible_prefixes_act:
        cur_act = p[1]
        pref = p[0]
        if cur_act in possible_prefixes.keys():
            possible_prefixes[cur_act].append(pref)
        else:
            possible_prefixes[cur_act] = [pref]

    return possible_prefixes