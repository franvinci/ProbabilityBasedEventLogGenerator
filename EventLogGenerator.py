from src.gen_seq_utils import get_prefix_proba
from src.gen_res_utils import get_prefix_res_proba, get_possible_prefixes_res_act
from src.gen_attr_utils import get_prefix_attr_proba, get_possible_prefixes_attr_act, get_trace_attribute_labels, get_trace_attribute_proba
from src.gen_time_utils import get_distr_arrival_time, get_distr_ex_times, sample_arrival_times, sample_ex_times
from src.prefix_utils import get_more_similar_prefix
from src.preprocess_utils import add_lc_to_act
from src.calendar_utils import discover_arrival_calendar, discover_res_calendars, add_minutes_with_calendar
import random
import pandas as pd
from datetime import datetime
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import pm4py

class EventLogGenerator:
    def __init__(self, log, k, label_data_attributes=[]):

        # sort event log by time:timestamp
        df_log = pm4py.convert_to_dataframe(log)
        df_log['time:timestamp'] = pd.to_datetime(df_log['time:timestamp'])
        df_log.sort_values(by='time:timestamp', inplace=True)
        df_log.index = range(len(df_log))
        self.log = pm4py.convert_to_event_log(df_log)
        self.k = k
        self.log = add_lc_to_act(log)

        self.label_data_attributes = label_data_attributes


        # compute conditional probabilities
        self.prefixes_proba_next_act = get_prefix_proba(self.log, k)
        self.prefixes_proba_next_res = get_prefix_res_proba(self.log, k)

        if label_data_attributes:
            self.trace_attribute_labels = get_trace_attribute_labels(self.log, self.label_data_attributes)
            self.event_attributes_labels = list(set(self.label_data_attributes) - set(self.trace_attribute_labels))

            self.prob_trace_attributes = get_trace_attribute_proba(self.log, self.trace_attribute_labels)
            self.prefixes_proba_next_attr = get_prefix_attr_proba(self.log, self.event_attributes_labels, k)

        # calendars discovery
        self.arrival_calendar = discover_arrival_calendar(self.log)
        self.res_calendars = discover_res_calendars(self.log)

        # compute durations distributions
        self.arrival_times_distr = get_distr_arrival_time(self.log, self.arrival_calendar)
        self.ex_times_distr = get_distr_ex_times(self.log, self.res_calendars)


    # def generate_single_sequence(self, args):
    #     possible_prefixes, similar_prefixes = args
    #     prefix = ()
    #     trace = []
    #     while True:
    #         if prefix not in self.prefixes_proba_next_act.keys():
    #             if prefix not in similar_prefixes.keys():
    #                 similar_prefixes[prefix] = get_more_similar_prefix(prefix, possible_prefixes)
    #             prefix = similar_prefixes[prefix]
    #         act = random.choices(
    #             list(self.prefixes_proba_next_act[prefix].keys()),
    #             weights=self.prefixes_proba_next_act[prefix].values()
    #         )[0]
    #         if act == '<END>':
    #             break
    #         trace.append(act)
    #         prefix = prefix + (act,)
    #     return trace

    # def generate_seq(self, N_seq=100):
    #     """

    #     This generate sequences of activities from conditional probabilities
    #     N_seq: number of seuqences to generate
    #     Output : list of activity sequences
    #     Output example : with N_seq=2 --> [['act_1','act_2'], ['act_1','act_2', 'act_3]]

    #     """

    #     possible_prefixes = list(self.prefixes_proba_next_act.keys())
    #     similar_prefixes = dict()

    #     with Pool(processes=cpu_count()) as pool:
    #         args = [(possible_prefixes, similar_prefixes)] * N_seq
    #         gen_seq_log = list(tqdm(pool.imap_unordered(self.generate_single_sequence, args), total=N_seq))

    #     return gen_seq_log


    def generate_seq(self, N_seq=100):
        """

        This generate sequences of activities from conditional probabilities
        N_seq: number of seuqences to generate
        Output : list of activity sequences
        Output example : with N_seq=2 --> [['act_1','act_2'], ['act_1','act_2', 'act_3]]

        """

        possible_prefixes = list(self.prefixes_proba_next_act.keys())
        gen_seq_log = []
        similar_prefixes = dict()
        for _ in tqdm(range(N_seq)):
            prefix = ()
            trace = []
            while True:
                if prefix not in self.prefixes_proba_next_act.keys():
                    if prefix not in similar_prefixes.keys():   
                        similar_prefixes[prefix] = get_more_similar_prefix(prefix, possible_prefixes)
                    prefix = similar_prefixes[prefix]
                act = random.choices(list(self.prefixes_proba_next_act[prefix].keys()), weights = self.prefixes_proba_next_act[prefix].values())[0]
                if act == '<END>':
                    break
                trace.append(act)
                prefix = prefix + (act,)
                prefix = prefix[-self.k:]
            gen_seq_log.append(trace)

        return gen_seq_log
    

    # def generate_single_resource(self, args):
    #     sim_trace_act, possible_prefixes, similar_prefixes = args
    #     sim_trace_act_res = []
    #     prefix = tuple()
    #     for act in sim_trace_act:
    #         pref_act = (prefix, act)
    #         if prefix not in possible_prefixes[act]:
    #             if prefix not in similar_prefixes.keys():
    #                 similar_prefixes[prefix] = dict()
    #             if act not in similar_prefixes[prefix].keys():
    #                 similar_prefixes[prefix][act] = get_more_similar_prefix(prefix, possible_prefixes[act])
    #             pref_act = (similar_prefixes[prefix][act], act)
    #         res = random.choices(
    #             list(self.prefixes_proba_next_res[pref_act].keys()),
    #             weights=self.prefixes_proba_next_res[pref_act].values()
    #         )[0]
    #         sim_trace_act_res.append((act, res))
    #         prefix = prefix + ((act, res),)
    #     return sim_trace_act_res

    # def generate_resources(self, log_seqs):
    #     possible_prefixes = get_possible_prefixes_res_act(self.prefixes_proba_next_res)
    #     similar_prefixes = dict()

    #     with Pool(processes=cpu_count()) as pool:
    #         args = [(sim_trace_act, possible_prefixes, similar_prefixes) for sim_trace_act in log_seqs]
    #         simulated_traces_act_res = list(tqdm(pool.imap_unordered(self.generate_single_resource, args), total=len(log_seqs)))

    #     return simulated_traces_act_res
    

    def generate_resources(self, log_seqs):

        possible_prefixes = get_possible_prefixes_res_act(self.prefixes_proba_next_res)
        simulated_traces_act_res = []
        similar_prefixes = dict()
        for sim_trace_act in tqdm(log_seqs):
            sim_trace_act_res = []
            prefix = tuple()
            for act in sim_trace_act:
                pref_act = (prefix, act)
                if prefix not in possible_prefixes[act]:
                    if prefix not in similar_prefixes.keys():
                        similar_prefixes[prefix] = dict()
                    if act not in similar_prefixes[prefix].keys():
                        similar_prefixes[prefix][act] = get_more_similar_prefix(prefix, possible_prefixes[act])
                    pref_act = (similar_prefixes[prefix][act], act)
                res = random.choices(list(self.prefixes_proba_next_res[pref_act].keys()), weights = self.prefixes_proba_next_res[pref_act].values())[0]
                sim_trace_act_res.append((act, res))
                prefix = prefix + ((act, res),)
                prefix = prefix[-self.k:]
            simulated_traces_act_res.append(sim_trace_act_res)  

        return simulated_traces_act_res
    

    # def generate_single_attribute(self, args):
    #     i, sim_trace_act, log_seqs_res, possible_prefixes, similar_prefixes = args
    #     sim_trace_act_res_attr = []
    #     prefix = tuple()
    #     for j, act in enumerate(sim_trace_act):
    #         pref_act = (prefix, act)
    #         if prefix not in possible_prefixes[act]:
    #             if prefix not in similar_prefixes.keys():
    #                 similar_prefixes[prefix] = dict()
    #             if act not in similar_prefixes[prefix].keys():
    #                 similar_prefixes[prefix][act] = get_more_similar_prefix(prefix, possible_prefixes[act])
    #             pref_act = (similar_prefixes[prefix][act], act)
    #         attr = random.choices(
    #             list(self.prefixes_proba_next_attr[pref_act].keys()),
    #             weights=self.prefixes_proba_next_attr[pref_act].values()
    #         )[0]
    #         sim_trace_act_res_attr.append((act, log_seqs_res[i][j][1], attr))
    #         prefix = prefix + ((act, attr),)
    #     return sim_trace_act_res_attr

    # def generate_attributes(self, log_seqs, log_seqs_res):
    #     possible_prefixes = get_possible_prefixes_attr_act(self.prefixes_proba_next_attr)
    #     similar_prefixes = dict()

    #     with Pool(processes=cpu_count()) as pool:
    #         args = [
    #             (i, sim_trace_act, log_seqs_res, possible_prefixes, similar_prefixes)
    #             for i, sim_trace_act in enumerate(log_seqs)
    #         ]
    #         simulated_traces_act_res_attr = list(tqdm(pool.imap_unordered(self.generate_single_attribute, args), total=len(log_seqs)))

    #     return simulated_traces_act_res_attr
    

    def generate_attributes(self, log_seqs, log_seqs_res):

        possible_prefixes = get_possible_prefixes_attr_act(self.prefixes_proba_next_attr)
        simulated_traces_act_res_attr = []
        similar_prefixes = dict()
        for i, sim_trace_act in tqdm(enumerate(log_seqs), total=len(log_seqs)):
            sim_trace_act_res_attr = []
            prefix = tuple()
            for j, act in enumerate(sim_trace_act):
                pref_act = (prefix, act)
                if prefix not in possible_prefixes[act]:
                    if prefix not in similar_prefixes.keys():
                        similar_prefixes[prefix] = dict()
                    if act not in similar_prefixes[prefix].keys():
                        similar_prefixes[prefix][act] = get_more_similar_prefix(prefix, possible_prefixes[act])
                    pref_act = (similar_prefixes[prefix][act], act)
                attr = random.choices(list(self.prefixes_proba_next_attr[pref_act].keys()), weights = self.prefixes_proba_next_attr[pref_act].values())[0]
                sim_trace_act_res_attr.append((act, log_seqs_res[i][j][1], attr))
                prefix = prefix[-self.k:]
                prefix = prefix + ((act, attr),)
            simulated_traces_act_res_attr.append(sim_trace_act_res_attr)  

        return simulated_traces_act_res_attr
    

    def generate_timestamps(self, log_seqs, start_timestamp):

        arrival_times = sample_arrival_times(self.arrival_times_distr[0], self.arrival_times_distr[1], len(log_seqs)-1)
        ex_times = sample_ex_times(self.ex_times_distr, log_seqs)

        timestamps = [[start_timestamp]]
        for i, a_t in enumerate(arrival_times):
            start_timestamp = add_minutes_with_calendar(start_timestamp, a_t, self.arrival_calendar)
            timestamps.append([start_timestamp])
        
        for i in tqdm(range(len(log_seqs))):
            for j in range(1, len(log_seqs[i])):
                prev_a = log_seqs[i][j-1][0]
                cur_a = log_seqs[i][j][0]
                res = log_seqs[i][j][1]
                t_seconds = ex_times[(prev_a, cur_a)].pop()
                t = add_minutes_with_calendar(timestamps[i][-1], t_seconds, self.res_calendars[res])
                timestamps[i].append(t)

        return timestamps
    
    def generate_lifecyle(self, df):

        df['lifecycle:transition'] = df['concept:name'].apply(lambda x: x.split('_lc:')[-1])
        df['concept:name'] = df['concept:name'].apply(lambda x: ''.join(x.split('_lc:')[:-1]))

        return df
    

    def apply(self, N, start_timestamp):

        # start_timestamp = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")

        print('Generate sequences...')
        log_seq = self.generate_seq(N)
        print('Generate resources...')
        log_seq_res = self.generate_resources(log_seq)
        if self.label_data_attributes:
            print('Generate attributes...')
            trace_attributes = random.choices(list(self.prob_trace_attributes.keys()), weights=self.prob_trace_attributes.values(), k=N)
            log_seq = self.generate_attributes(log_seq, log_seq_res)
        else:
            log_seq = log_seq_res

        print('Generate timestamps...')
        timestamps_log = self.generate_timestamps(log_seq, start_timestamp)

        ids = [str(i) for i in range(1, len(log_seq)+1) for _ in range(len(log_seq[i-1]))]
        activities = [ev[0] for trace in log_seq for ev in trace]
        roles = [ev[1] for trace in log_seq for ev in trace]
        if self.label_data_attributes:
            attributes_dict = {l: [] for l in self.label_data_attributes}
            for i, l in enumerate(self.event_attributes_labels):
                attributes_dict[l] = [ev[2][i] for trace in log_seq for ev in trace]
            for k, l in enumerate(self.trace_attribute_labels):
                for i in range(len(trace_attributes)):
                    for _ in range(len(log_seq[i])):
                        attributes_dict[l].append(trace_attributes[i][k])
        else:
            attributes_dict = dict()
        timestamps = [t for trace in timestamps_log for t in trace]
        
        df = pd.DataFrame({'case:concept:name': ids, 'concept:name': activities, 'time:timestamp': timestamps, 'org:resource': roles} | attributes_dict)
        df = self.generate_lifecyle(df)

        return df