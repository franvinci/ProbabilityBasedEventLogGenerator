import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from src.train_utils import splitEventLog
from src.eventlog_utils import order_for_trace_start
from EventLogGenerator import EventLogGenerator

import warnings
warnings.filterwarnings('ignore')

import time

case_studies = [
    # 'Purchasing',
    # 'Production',
    # 'Consulta',
    # 'bpi12',
    # 'bpi17',
    # 'sepsis',
    # 'rtf',
    'bpi19'
    ]

N_SIM = 1
k = 4

if __name__ == '__main__':
    for case_study in case_studies:

        # Start time
        start_time = time.time()

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

        if case_study == 'sepsis':
            path_log = 'data/sepsis/sepsis.xes'
            save_split_to = 'data/sepsis'
            save_simulations_to = 'simulations/sepsis'
            label_data_attributes=['InfectionSuspected', 'DiagnosticBlood', 'DisfuncOrg', 'SIRSCritTachypnea', 'Hypotensie', 'SIRSCritHeartRate', 'Infusion', 'DiagnosticArtAstrup', 'Age', 'DiagnosticIC', 'DiagnosticSputum', 'DiagnosticLiquor', 'DiagnosticOther', 'SIRSCriteria2OrMore', 'DiagnosticXthorax', 'SIRSCritTemperature', 'DiagnosticUrinaryCulture', 'SIRSCritLeucos', 'Oligurie', 'DiagnosticLacticAcid', 'Diagnose', 'Hypoxie', 'DiagnosticUrinarySediment', 'DiagnosticECG', 'Leucocytes', 'CRP', 'LacticAcid']

        if case_study == 'rtf':
            path_log = 'data/rtf/rtf.xes'
            save_split_to = 'data/rtf'
            save_simulations_to = 'simulations/rtf'
            label_data_attributes=['amount', 'dismissal', 'vehicleClass', 'totalPaymentAmount', 'article', 'points', 'expense', 'notificationType', 'lastSent', 'paymentAmount', 'matricola']

        if case_study == 'bpi19':
            path_log = 'data/bpi19/bpi19.xes'
            save_split_to = 'data/bpi19'
            save_simulations_to = 'simulations/bpi19'
            label_data_attributes=[
                                    'Cumulative net worth (EUR)', 
                                    'case:Spend area text', 
                                    'case:Company', 
                                    'case:Document Type', 
                                    'case:Sub spend area text',
                                    'case:Purchasing Document', 
                                    'case:Purch. Doc. Category name',
                                    'case:Vendor', 
                                    'case:Item Type', 
                                    'case:Item Category',
                                    'case:Spend classification text', 
                                    'case:Source', 
                                    'case:Name',
                                    'case:GR-Based Inv. Verif.', 
                                    'case:Item',
                                    'case:Goods Receipt'
                                ]


        log = xes_importer.apply(path_log)

        train_log, test_log = splitEventLog(log, train_size = 0.8, split_temporal = True, save_to = save_split_to)

        start_timestamp = test_log[0][0]['time:timestamp']

        generator = EventLogGenerator(train_log, k=k, label_data_attributes=label_data_attributes)
        for i in range(N_SIM):
            simulated_traces = generator.apply(N=len(test_log), start_timestamp = start_timestamp)
            simulated_traces.to_csv(save_simulations_to + f'/sim_{i}.csv', index=False)
            print(f'{case_study} simulation {i} done!')
        
        # End time
        end_time = time.time()

        # Execution time
        execution_time = end_time - start_time

        # Calculate hours, minutes, seconds
        hours = int(execution_time // 3600)  # Divide by 3600 to get hours
        minutes = int((execution_time % 3600) // 60)  # Remainder divided by 60 to get minutes
        seconds = execution_time % 60  # Remainder of seconds

        #Save it into the folder of the simulations
        with open(save_simulations_to + '/execution_time.txt', 'w') as f:
            f.write(f"Execution Time: {hours} hours, {minutes} minutes, {seconds:.6f} seconds")


