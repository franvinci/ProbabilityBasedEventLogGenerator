from scipy.stats import gaussian_kde

def get_arrival_times(log):
    
    arrival_times = []
    for i in range(1, len(log)):
        time_prec = log[i-1][0]['time:timestamp']
        time_curr = log[i][0]['time:timestamp']
        arrival_times.append((time_curr - time_prec).total_seconds())

    return arrival_times


def get_ex_times(log):

    ex_times = dict()
    for trace in log:
        for i in range(1, len(trace)):
            prec_t = trace[i-1]['time:timestamp']
            cur_t = trace[i]['time:timestamp']
            prec_a = trace[i-1]['concept:name']
            cur_a = trace[i]['concept:name']
            if (prec_a, cur_a) in ex_times.keys():
                ex_times[(prec_a, cur_a)].append((cur_t - prec_t).total_seconds())
            else:
                ex_times[(prec_a, cur_a)] = [(cur_t - prec_t).total_seconds()]

    return ex_times


def get_kde_arrival_time(log):
    
    arrival_times = get_arrival_times(log)
    kde = gaussian_kde(arrival_times)

    return kde


def get_kde_ex_times(log):

    ex_times = get_ex_times(log)
    ex_times_kde = dict()

    acts_couples = list(ex_times.keys())
    for acts in acts_couples:
        if len(set(ex_times[acts])) > 1:
            ex_times_kde[acts] = gaussian_kde(ex_times[acts])
        else:
            ex_times_kde[acts] = {'fixed': ex_times[acts][0]}

    return ex_times_kde


def sample_arrival_times(kde, N):

    arrival_times_sim = list(kde.resample(N)[0])
    arrival_times_sim = [max(0, x) for x in arrival_times_sim]

    return arrival_times_sim


def sample_ex_times_acts(kde, acts, sim_traces):

    prev = acts[0]
    cur = acts[1]

    N = 0
    for trace in sim_traces:
        for i in range(1, len(trace)):
            if (trace[i-1] == prev) and (trace[i] == cur):
                N += 1

    if type(kde) == dict:
        ex_times_acts = [kde['fixed']]*N
    else:
        ex_times_acts = list(kde.resample(N)[0])
        ex_times_acts = [max(0, x) for x in ex_times_acts]

    return ex_times_acts


def sample_ex_times(ex_times_kde, sim_traces):

    ex_times_sim = dict()

    acts_couples = list(ex_times_kde.keys())
    for acts in acts_couples:
        ex_times_sim[acts] = sample_ex_times_acts(ex_times_kde[acts], acts, sim_traces)

    return ex_times_sim


