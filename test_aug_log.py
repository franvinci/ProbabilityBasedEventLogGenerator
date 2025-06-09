# %%
import pandas as pd
import os 
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer

from src.eventlog_utils import convert_log

curr_dir = '/home/padela/Scrivania/ProbabilityBasedEventLogGenerator'
case_study = 'bpi17'
os.chdir(curr_dir)

case_studies = {
    1: 'Purchasing',
    2: 'Production',
    3: 'Consulta',
    4: 'bpi12',
    5: 'bpi17',
    6: 'sepsis',
    7: 'rtf',
    8: 'bpi19'
}


target_act = 'W_Handle leads'  # choose target activity for the case study

# Choose if our approach or Sota
our_approach = True
Sota = not(our_approach)
approach = 'SIMOD' if Sota else None
print(f'Case study: {case_study}, our approach = {our_approach}')

log_real = xes_importer.apply(f'data/{case_study}/logTest.xes')
log_real = pm4py.convert_to_dataframe(log_real)

if our_approach:
    log_sim = pd.read_csv(f'simulations/{case_study}/sim_0.csv')
    print('imported log from our approach')

# convert event log format lifecycles
if 'lifecycle:transition' in log_real.columns:
    log_real = convert_log(log_real)
    log_real.rename(columns={'START': 'start:timestamp', 'END': 'time:timestamp'}, errors='ignore', inplace=True)
    log_real.reset_index(inplace=True)
if 'lifecycle:transition' in log_sim.columns:
    log_sim = convert_log(log_sim)
    log_sim.reset_index(inplace=True)

# Extract the traces in which the target activity occurs
target_traces = log_sim[log_sim['concept:name'] == target_act]['case:concept:name'].unique()
log_sim = log_sim[log_sim['case:concept:name'].isin(target_traces)]

# Filter the log real only maintaining the columns of log_sim
log_real = log_real[log_sim.columns]
log = pd.concat([log_real, log_sim], ignore_index=True)

# print the percentage of traces in which the target activity occurs in the obtained log
print('Percentage of traces in which the target activity occurs in the obtained log:')
percentage = len(log[log['concept:name'] == target_act]['case:concept:name'].unique()) / len(log['case:concept:name'].unique()) * 100
print(f'{percentage:.2f}%')

log.to_csv(f'simulations/{case_study}/log_sim_augmented.csv', index=False)
print(f'Log saved to simulations/{case_study}/log_sim_augmented.csv')







# %%
