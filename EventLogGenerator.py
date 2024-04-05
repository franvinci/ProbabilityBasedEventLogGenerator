from src.gen_seq_utils import get_prefix_proba
import random

class EventLogGenerator:
    def __init__(self, log):
        self.log = log

        # compute conditional probabilities: probability to execute an activity given a prefix
        self.prefixes_proba_next_act = get_prefix_proba(log)


    def generate_seq(self, N_seq=100):
        """

        This generate sequences of activities from conditional probabilities
        N_seq: number of seuqences to generate
        Output : list of activity sequences
        Output example : with N_seq=2 --> [['act_1','act_2'], ['act_1','act_2', 'act_3]]

        """

        gen_seq_log = []
        for _ in range(N_seq):
            prefix = ()
            trace = []
            while True:
                act = random.choices(list(self.prefixes_proba_next_act[prefix].keys()), weights = self.prefixes_proba_next_act[prefix].values())[0]
                if act == '<END>':
                    break
                trace.append(act)
                prefix = prefix + (act,)
            
            gen_seq_log.append(trace)

        return gen_seq_log
    

    def generate_timestamps(self, log_seqs):
        return None
    

    def generate_resources(self, log_seqs_times):
        return None
    

    def apply(self, N=1000):

        log = self.generate_seq(N)
        # log = self.generate_timestamps(log)
        # log = self.generate_resources(log)

        return log