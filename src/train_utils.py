import pm4py
import numpy as np


def splitEventLog(log, train_size = 0.7, split_temporal = True, save_to = ''):
    """
    
    Split event log in train and test set

    """


    df_real = pm4py.convert_to_dataframe(log)

    cases = df_real['case:concept:name'].unique()
    np.random.seed(72)
    if not split_temporal:
        np.random.shuffle(cases)
    new_case_names = dict(zip(cases,range(len(cases))))
    df_real['CaseN'] = df_real['case:concept:name'].apply(lambda x: new_case_names[x])

    n_train = int(train_size * len(cases))

    df_train = df_real[df_real['CaseN'] < n_train]
    df_test = df_real[df_real['CaseN'] >= n_train]

    del df_train['CaseN']
    del df_test['CaseN']

    real_train = pm4py.convert_to_event_log(df_train) 
    real_test = pm4py.convert_to_event_log(df_test)

    if save_to:
        pm4py.write_xes(real_train, save_to + '/logTrain.xes')
        pm4py.write_xes(real_test, save_to + '/logTest.xes')
    
    return real_train, real_test