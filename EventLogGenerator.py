from src.gen_seq_utils import get_prefix_proba
from src.gen_res_utils import get_prefix_res_proba, get_possible_prefixes_act
from src.prefix_utils import get_more_similar_prefix
import random
import pandas as pd

class EventLogGenerator:
    def __init__(self, log):
        self.log = log

        # compute conditional probabilities: probability to execute an activity given a prefix
        self.prefixes_proba_next_act = get_prefix_proba(log)
        self.prefixes_proba_next_res = get_prefix_res_proba(log)


    def generate_seq(self, N_seq=100):
        """

        This generate sequences of activities from conditional probabilities
        N_seq: number of seuqences to generate
        Output : list of activity sequences
        Output example : with N_seq=2 --> [['act_1','act_2'], ['act_1','act_2', 'act_3]]

        """

        possible_prefixes = list(self.prefixes_proba_next_act.keys())
        gen_seq_log = []
        for _ in range(N_seq):
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
        for sim_trace_act in log_seqs_times:
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
    

    def generate_timestamps(self, log_seqs):
        return None
    

    def apply(self, N=1000):

        log = self.generate_seq(N)
        log = self.generate_resources(log)
        # log = self.generate_timestamps(log)

        ids = [str(i) for i in range(1, len(log)+1) for _ in range(len(log[i-1]))]
        activities = [ev[0] for trace in log for ev in trace]
        resources = [ev[1] for trace in log for ev in trace]    
        # timestamps = []
        
        df = pd.DataFrame({'case:concpet:name': ids, 'concept:name': activities, 'org:resources': resources})

        return df