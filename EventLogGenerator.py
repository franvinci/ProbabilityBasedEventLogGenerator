from src.gen_seq_utils import get_prefix_proba
from src.gen_res_utils import get_prefix_res_proba, get_possible_prefixes_act
from src.gen_time_utils import get_kde_arrival_time, get_kde_ex_times, sample_arrival_times, sample_ex_times
from src.prefix_utils import get_more_similar_prefix
from src.preprocess_utils import add_lc_to_act
import random
import pandas as pd
from datetime import timedelta, datetime
from tqdm import tqdm

class EventLogGenerator:
    def __init__(self, log):
        self.log = log

        self.log = add_lc_to_act(log)

        # compute conditional probabilities: probability to execute an activity given a prefix
        self.prefixes_proba_next_act = get_prefix_proba(log)
        self.prefixes_proba_next_res = get_prefix_res_proba(log)
        self.arrival_times_kde = get_kde_arrival_time(log)
        self.ex_times_kde = get_kde_ex_times(log)


    def generate_seq(self, N_seq=100):
        """

        This generate sequences of activities from conditional probabilities
        N_seq: number of seuqences to generate
        Output : list of activity sequences
        Output example : with N_seq=2 --> [['act_1','act_2'], ['act_1','act_2', 'act_3]]

        """

        possible_prefixes = list(self.prefixes_proba_next_act.keys())
        gen_seq_log = []
        for _ in tqdm(range(N_seq)):
            prefix = ()
            trace = []
            while True:
                if prefix not in self.prefixes_proba_next_act.keys():
                    prefix = get_more_similar_prefix(prefix, possible_prefixes)
                act = random.choices(list(self.prefixes_proba_next_act[prefix].keys()), weights = self.prefixes_proba_next_act[prefix].values())[0]
                if act == '<END>':
                    break
                trace.append(act)
                prefix = prefix + (act,)
            
            gen_seq_log.append(trace)

        return gen_seq_log
    

    def generate_resources(self, log_seqs_times):

        possible_prefixes = get_possible_prefixes_act(self.prefixes_proba_next_res)
        simulated_traces_act_res = []
        for sim_trace_act in tqdm(log_seqs_times):
            sim_trace_act_res = []
            prefix = tuple()
            for act in sim_trace_act:
                pref_act = (prefix, act)
                if prefix not in possible_prefixes[act]:
                    pref_act = (get_more_similar_prefix(prefix, possible_prefixes[act]), act)
                res = random.choices(list(self.prefixes_proba_next_res[pref_act].keys()), weights = self.prefixes_proba_next_res[pref_act].values())[0]
                sim_trace_act_res.append((act, res))
                prefix = prefix + ((act, res),)
            simulated_traces_act_res.append(sim_trace_act_res)  

        return simulated_traces_act_res
    

    def generate_timestamps(self, log_seqs, start_timestamp):

        arrival_times = sample_arrival_times(self.arrival_times_kde, len(log_seqs))
        ex_times = sample_ex_times(self.ex_times_kde, log_seqs)

        timestamps = []
        for a_t in arrival_times:
            start_timestamp = start_timestamp + timedelta(seconds=a_t)
            timestamps.append([start_timestamp])
        
        for i in tqdm(range(len(log_seqs))):
            for j in range(1, len(log_seqs[i])):
                prev_a = log_seqs[i][j-1]
                cur_a = log_seqs[i][j]
                t_seconds = ex_times[(prev_a, cur_a)].pop()
                timestamps[i].append(timestamps[i][-1] + timedelta(seconds=t_seconds))

        return timestamps
    
    def generate_lifecyle(self, df):

        df['lifecycle:transition'] = df['concept:name'].apply(lambda x: x.split('_lc:')[-1])
        df['concept:name'] = df['concept:name'].apply(lambda x: ''.join(x.split('_lc:')[:-1]))

        return df
    

    def apply(self, N=1000, start_timestamp = "2020-10-15 00:00:00"):

        start_timestamp = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")

        print('Generate sequences...')
        log_seq = self.generate_seq(N)
        print('Generate resources...')
        log = self.generate_resources(log_seq)
        print('Generate timestamps...')
        timestamps_log = self.generate_timestamps(log_seq, start_timestamp)

        ids = [str(i) for i in range(1, len(log)+1) for _ in range(len(log[i-1]))]
        activities = [ev[0] for trace in log for ev in trace]
        resources = [ev[1] for trace in log for ev in trace]
        timestamps = [t for trace in timestamps_log for t in trace]
        
        df = pd.DataFrame({'case:concept:name': ids, 'concept:name': activities, 'time:timestamp': timestamps, 'org:resource': resources})
        df = self.generate_lifecyle(df)

        return df