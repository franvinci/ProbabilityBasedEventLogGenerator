from pm4py.objects.log.importer.xes import importer as xes_importer
from src.train_utils import splitEventLog
from EventLogGenerator import EventLogGenerator


case_studies = [
    'Purchasing',
    'Production',
    'Consulta',
    'bpi12',
    'bpi17'
    ]


for case_study in case_studies:

    if case_study == 'bpi12':
        path_log = 'data/bpi12/BPI_Challenge_2012_W_Two_TS.xes'
        save_split_to = 'data/bpi12'
        save_simulations_to = 'simulations/bpi12'

    if case_study == 'bpi17':
        path_log = 'data/bpi17/BPI_Challenge_2017_W_Two_TS.xes'
        save_split_to = 'data/bpi17'
        save_simulations_to = 'simulations/bpi17'

    if case_study == 'Consulta':
        path_log = 'data/Consulta/ConsultaDataMining201618.xes'
        save_split_to = 'data/Consulta'
        save_simulations_to = 'simulations/Consulta'

    if case_study == 'Production':
        path_log = 'data/Production/Production.xes'
        save_split_to = 'data/Production'
        save_simulations_to = 'simulations/Production'

    if case_study == 'Purchasing':
        path_log = 'data/Purchasing/PurchasingExample.xes'
        save_split_to = 'data/Purchasing'
        save_simulations_to = 'simulations/Purchasing'


    log = xes_importer.apply(path_log)
    train_log, test_log = splitEventLog(log, train_size = 0.8, split_temporal = True, save_to = save_split_to)

    start_timestamp = test_log[0][0]['time:timestamp'].strftime('%Y-%m-%d %H:%M:%S')

    generator = EventLogGenerator(train_log)
    simulated_traces = generator.apply(N=len(test_log), start_timestamp = start_timestamp)
    simulated_traces.to_csv(save_simulations_to + '/sim.csv', index=False)