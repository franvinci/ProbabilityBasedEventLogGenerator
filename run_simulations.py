import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from src.train_utils import splitEventLog
from src.eventlog_utils import order_for_trace_start
from EventLogGenerator import EventLogGenerator

import warnings
warnings.filterwarnings('ignore')

case_studies = [
    'Purchasing',
    'Production',
    'Consulta',
    'bpi12',
    'bpi17',
    ]


for case_study in case_studies:

    if case_study == 'bpi12':
        path_log = 'data/bpi12/bpi12w.xes'
        save_split_to = 'data/bpi12'
        save_simulations_to = 'simulations/bpi12'
        label_data_attributes=['AMOUNT_REQ']

    if case_study == 'bpi17':
        path_log = 'data/bpi17/bpi17w.xes'
        save_split_to = 'data/bpi17'
        save_simulations_to = 'simulations/bpi17'
        label_data_attributes=['LoanGoal', 'ApplicationType', 'RequestedAmount']

    if case_study == 'Consulta':
        path_log = 'data/Consulta/ConsultaDataMining201618.xes'
        save_split_to = 'data/Consulta'
        save_simulations_to = 'simulations/Consulta'
        label_data_attributes=[]

    if case_study == 'Production':
        path_log = 'data/Production/production.xes'
        save_split_to = 'data/Production'
        save_simulations_to = 'simulations/Production'
        label_data_attributes=['Work Order  Qty', 'Part Desc.', 'Report Type', 'Qty Completed', 'Qty Rejected', 'Qty for MRB', 'Rework']

    if case_study == 'Purchasing':
        path_log = 'data/Purchasing/PurchasingExample.xes'
        save_split_to = 'data/Purchasing'
        save_simulations_to = 'simulations/Purchasing'
        label_data_attributes=[]


    log = xes_importer.apply(path_log)

    train_log, test_log = splitEventLog(log, train_size = 0.8, split_temporal = True, save_to = save_split_to)

    start_timestamp = test_log[0][0]['time:timestamp']

    generator = EventLogGenerator(train_log, label_data_attributes=label_data_attributes)
    simulated_traces = generator.apply(N=len(test_log), start_timestamp = start_timestamp)
    simulated_traces.to_csv(save_simulations_to + '/sim.csv', index=False)
    print(f'{case_study} simulation done!')