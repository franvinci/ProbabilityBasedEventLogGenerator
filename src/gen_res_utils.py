import pm4py


def get_prefix_res_freq(log):

    prefixes_freq_next_res = dict()
    resources = pm4py.get_event_attribute_values(log, "org:resource").keys()
    for trace in log:
        prefix = tuple()
        for event in trace:
            act = event['concept:name']
            res = event['org:resource']
            pref_act = (prefix, act)
            if pref_act in prefixes_freq_next_res.keys():
                prefixes_freq_next_res[pref_act][res] += 1
            else:
                prefixes_freq_next_res[pref_act] = {r: 0 for r in resources}
                prefixes_freq_next_res[pref_act][res] += 1
            prefix = prefix + ((act, res),)

    return prefixes_freq_next_res


def get_prefix_res_proba(log):

    prefixes_freq_next_res = get_prefix_res_freq(log)
    prefixes_act = prefixes_freq_next_res.keys()
    prefixes_proba_next_res = prefixes_freq_next_res.copy()
    for prefix_act in prefixes_act:
        N_freq = sum(prefixes_freq_next_res[prefix_act].values())
        for res in prefixes_proba_next_res[prefix_act].keys():
            prefixes_proba_next_res[prefix_act][res] /= N_freq

    return prefixes_proba_next_res


def get_possible_prefixes_act(prefixes_proba_next_res):

    possible_prefixes_act = list(prefixes_proba_next_res.keys())
    possible_prefixes = dict()
    for p in possible_prefixes_act:
        cur_act = p[1]
        pref = p[0]
        if cur_act in possible_prefixes.keys():
            possible_prefixes[cur_act].append(pref)
        else:
            possible_prefixes[cur_act] = [pref]

    return possible_prefixes