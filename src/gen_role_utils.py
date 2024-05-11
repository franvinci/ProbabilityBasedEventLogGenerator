import pm4py


def find_roles(log):

    roles = pm4py.discover_organizational_roles(log)
    roles_acts = {f'Role {i+1}': roles[i].activities for i in range(len(roles))}
    activities = pm4py.get_event_attribute_values(log, "concept:name").keys()
    act_role = dict()
    for a in activities:
        for i in range(len(roles)):
            if a in roles_acts[f'Role {i+1}']:
                act_role[a] = f'Role {i+1}'
                break

    return act_role


def add_roles_to_log(log):

    act_role = find_roles(log)
    for i in range(len(log)):
        for j in range(len(log[i])):
            log[i][j]['org:role'] = act_role[log[i][j]['concept:name']]

    return log


def get_prefix_role_freq(log):

    prefixes_freq_next_role = dict()
    roles = pm4py.get_event_attribute_values(log, "org:role").keys()
    for trace in log:
        prefix = tuple()
        for event in trace:
            act = event['concept:name']
            role = event['org:role']
            pref_act = (prefix, act)
            if pref_act in prefixes_freq_next_role.keys():
                prefixes_freq_next_role[pref_act][role] += 1
            else:
                prefixes_freq_next_role[pref_act] = {r: 0 for r in roles}
                prefixes_freq_next_role[pref_act][role] += 1
            prefix = prefix + ((act, role),)

    return prefixes_freq_next_role


def get_prefix_role_proba(log):

    prefixes_freq_next_role = get_prefix_role_freq(log)
    prefixes_act = prefixes_freq_next_role.keys()
    prefixes_proba_next_role = prefixes_freq_next_role.copy()
    for prefix_act in prefixes_act:
        N_freq = sum(prefixes_freq_next_role[prefix_act].values())
        for role in prefixes_proba_next_role[prefix_act].keys():
            prefixes_proba_next_role[prefix_act][role] /= N_freq

    return prefixes_proba_next_role


def get_possible_prefixes_act(prefixes_proba_next_role):

    possible_prefixes_act = list(prefixes_proba_next_role.keys())
    possible_prefixes = dict()
    for p in possible_prefixes_act:
        cur_act = p[1]
        pref = p[0]
        if cur_act in possible_prefixes.keys():
            possible_prefixes[cur_act].append(pref)
        else:
            possible_prefixes[cur_act] = [pref]

    return possible_prefixes