#%% Import the packages
import pandas as pd
from src.eventlog_utils import convert_log
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer

#%% Load the data
# Select the case study
case_studies = {
    1: 'Consulta',
    2: 'Production',
    3: 'Purchasing',
    4: 'bpi12',
    5: 'bpi17'
}

case_study = case_studies[1]

# Import the current case study log, preprocessed in this case


# %%


