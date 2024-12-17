from scipy.stats import wasserstein_distance
from collections import Counter
import pandas as pd
import numpy as np


def emd_categ(a: list, b: list):
    
    a_counts = Counter(a)
    b_counts = Counter(b)

    unique_elements = sorted(set(a + b))

    a_hist = [a_counts[elem] for elem in unique_elements]
    b_hist = [b_counts[elem] for elem in unique_elements]

    mapping = {elem: i for i, elem in enumerate(unique_elements)}
    numeric_positions = [mapping[elem] for elem in unique_elements]

    distance = wasserstein_distance(numeric_positions, numeric_positions, u_weights=a_hist, v_weights=b_hist)

    return distance


def emd_attributes(df_real: pd.DataFrame, df_sim:pd.DataFrame, attr_names=[]):
    
    for a in attr_names:
        if a not in df_real.columns:
            raise Exception(f"{a} not in df_real columns")
        if a not in df_sim.columns:
            raise Exception(f"{a} not in df_sim columns")
        
    emds = []
    for a in attr_names:
        if df_real[a].dtype == float:
            emds.append(wasserstein_distance(df_real[a].dropna(), df_sim[a].dropna()))
        else:
            emds.append(emd_categ(list(df_real[a].fillna("N/A")), list(df_sim[a].fillna("N/A"))))

    return np.mean(emds)