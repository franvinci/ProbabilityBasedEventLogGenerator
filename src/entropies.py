#%% 
import math
from collections import Counter
import numpy as np
import pandas as pd
from scipy.stats import entropy as et
from src.eventlog_utils import convert_log_from_lc_to_se
import pm4py

def convert_and_clean(df):
    if 'lifecycle:transition' in df.columns:
        df = convert_log_from_lc_to_se(df)
        df.rename(columns={'START': 'start:timestamp', 'END': 'time:timestamp'}, inplace=True, errors='ignore')
    for col in ['start:timestamp', 'time:timestamp']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    df.reset_index(inplace=True, drop=True)
    return df
    
def compute_entropy(sequences):
    # Flatten all symbols from all sequences
    all_symbols = [symbol for seq in sequences for symbol in seq]
    
    # Count frequencies
    total = len(all_symbols)
    freq = Counter(all_symbols)
    prob = [count / total for count in freq.values()]

    # Compute probabilities and entropy
    entropy = et(prob, base=10)  # Using base 2 for bits
    return entropy

def get_all_prefixes(sequences):
    
    all_prefixes = []
    for seq in sequences:
        for i in range(1, len(seq) + 1):
            all_prefixes.append(seq[:i])
    return all_prefixes


def cf_entropy(log, prefix=True, activity_name='concept:name', case_id_name='case:concept:name'):

    # Make a list of sequence of activities for each case
    cases = {}
    for index, row in log.iterrows():
        case_id = row[case_id_name]
        activity = row[activity_name]
        
        if case_id not in cases:
            cases[case_id] = []
        cases[case_id].append(activity)

    if prefix:
        # Get all prefixes of the sequences
        sequences = get_all_prefixes(list(cases.values()))

    else:
        sequences = list(cases.values())

    return compute_entropy(sequences)

def compute_etd_entropy(df_log: pd.DataFrame) -> float:

    # Needed to do bucketing
    if "start:timestamp" not in df_log.columns or "time:timestamp" not in df_log.columns:
        return "NO START TIMESTAMPS"

    # Cast the timestamps to datetime if they are not already
    if not pd.api.types.is_datetime64_any_dtype(df_log["start:timestamp"]):
        df_log["start:timestamp"] = pd.to_datetime(df_log["start:timestamp"])
    if not pd.api.types.is_datetime64_any_dtype(df_log["time:timestamp"]):
        df_log["time:timestamp"] = pd.to_datetime(df_log["time:timestamp"])

    activities = list(df_log["concept:name"].unique())
    etd_entropies = []
    for act in activities:
        df_log_act = df_log[df_log["concept:name"] == act]
        ex_times = (df_log_act["time:timestamp"] - df_log_act["start:timestamp"]).apply(lambda x: x.total_seconds() // 60)
        hist, _ = np.histogram(list(ex_times), bins='auto', density=True)
        probs = hist / np.sum(hist)
        etd_entropies.append(et(probs))

    return np.mean(etd_entropies)

def compute_ctd_entropy(df_log: pd.DataFrame) -> float:

    log = pm4py.convert_to_event_log(df_log)
    cycle_times = []
    for trace in log:
        start = trace[0]['start:timestamp']
        end = trace[-1]['time:timestamp']
        cycle_times.append((end-start).total_seconds()//60)
    
    hist, _ = np.histogram(cycle_times, bins='auto', density=True)
    probs = hist / np.sum(hist)
    ctd_entr = et(probs)

    return ctd_entr
# %%
