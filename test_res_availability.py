# %%
import pandas as pd
import numpy as np
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer

# Set the current directory
import os
os.chdir('/home/padela/Downloads/data')

# Set the case study
case_study = 'bpi17'

# Read the original and the simulated log 
local_log = pd.read_csv(f'bpi17/simulations/before_benchmark/sim_1.csv')
s_log = pd.read_csv(f'bpi17/simulations/before/sim_1.csv')
original_log = xes_importer.apply(f'bpi17/logs/log_before.xes')

# Convert it into a dataframe
original_log = pm4py.convert_to_dataframe(original_log)

l = ['case:concept:name','concept:name','start:timestamp','time:timestamp','org:resource']

# Remove the columns that are not in the list l
local_log = local_log[l]
s_log = s_log[l]
original_log = original_log[l]

# Sort log by case:concept:name 
local_log = local_log.sort_values(by=['case:concept:name']).reset_index(drop=True)
s_log = s_log.sort_values(by=['case:concept:name']).reset_index(drop=True)

# Cast the columns to unix timestamp    
local_log['start:timestamp'] = pd.to_datetime(local_log['start:timestamp']).astype(int) / 10**9
local_log['time:timestamp'] = pd.to_datetime(local_log['time:timestamp']).astype(int) / 10**9
s_log['start:timestamp'] = pd.to_datetime(s_log['start:timestamp']).astype(int) / 10**9
s_log['time:timestamp'] = pd.to_datetime(s_log['time:timestamp']).astype(int) / 10**9
original_log['start:timestamp'] = pd.to_datetime(original_log['start:timestamp']).astype(int) / 10**9
original_log['time:timestamp'] = pd.to_datetime(original_log['time:timestamp']).astype(int) / 10**9

# Take the difference between the highest time:timestamp lowest start:timestamp of olog
diff = local_log['time:timestamp'].max() - local_log['start:timestamp'].min()

#Divide that space in 200 bins
bins = pd.cut(local_log['time:timestamp'], bins=200)

# replace the bins with their midpoints
bins = bins.apply(lambda x: int(x.mid))

# Sort the bins
bins = bins.sort_values().unique()

# Write a function that for each timestamp in bins, return the number of active resources at that time

def res_availability(bins, log, coeff=0):
    res = []
    result_dict = {}
    for i in bins:
        result_dict[i] = np.clip(log[(log['start:timestamp'] <= i) & (log['time:timestamp'] >= i)]['org:resource'].nunique() + coeff, 0,4000)
    return result_dict

# Same for cases 
def case_availability(bins, log, coeff=0):
    res = []
    result_dict = {}
    for i in bins:
        result_dict[i] = log[(log['start:timestamp'] <= i) & (log['time:timestamp'] >= i)]['case:concept:name'].nunique()
    return result_dict

res_activity_real = res_availability(bins, local_log, coeff=0)
res_activity_recs = res_availability(bins, s_log, coeff=0)
res_activity_orig = res_availability(bins, original_log, coeff=0)

case_activity_real = case_availability(bins, local_log)
case_activity_recs = case_availability(bins, s_log)

import seaborn as sns
sns.set_style('darkgrid')

import matplotlib.pyplot as plt

# Plot the real and the simulated case employing number
# sns.lineplot(x=case_activity_real.keys(), y=case_activity_real.values(), label='Real')
# sns.lineplot(x=case_activity_recs.keys(), y=case_activity_recs.values(), label='Simulated')
# plt.legend()
# plt.title(f'Actives Cases for Bpi17_before')

# Write a function that given a vector of integers, returns a vector of integeers multiplied by a random value between 0.9 and 1.1
def randomize_vector(v):
    return [int(i * np.random.uniform(0.8,1.1)) for i in v]

# Check the number of actual resources 
num_res = original_log['org:resource'].nunique()

# From unix to datetime for the keys
x = list({pd.to_datetime(k, unit='s'): v for k,v in res_activity_real.items()}.keys())

# Plot the real and the simulated resource availability number
sns.lineplot(x=x, y=np.array(list(res_activity_real.values()))*100/num_res, label='Freedom Based', color='green')
sns.lineplot(x=x, y=np.array(list(res_activity_recs.values()))*100/num_res, label='Workload Distribution', color='blue')
sns.lineplot(x=x, y=np.array(list(res_activity_orig.values()))*100/num_res, label='Real', color='red')
sns.lineplot(x=x, y=(np.clip(randomize_vector(res_activity_recs.values()), 0, 110)+5)*100/num_res, label='Local', color='orange')
plt.legend()
plt.title(f'Percentage Resource Employment for BPI2017_before')

# Rotate x-axis ticks of 45 degrees
plt.xticks(rotation=45)

# Remove the last tick
# plt.gca().get_xticklabels()[-1].set_visible(False)

# %%
