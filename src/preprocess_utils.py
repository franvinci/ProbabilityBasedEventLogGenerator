def add_lc_to_act(log):
    
    for i in range(len(log)):
        for j in range(len(log[i])):
            log[i][j]['concept:name'] = log[i][j]['concept:name'] + '_lc:' + log[i][j]['lifecycle:transition']

    return log