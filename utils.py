from pandas import read_csv
from pathlib import Path
from numpy import log2
from scipy.stats import entropy
from sklearn.metrics.cluster import contingency_matrix


path_data = Path(__file__).parent

aux = read_csv(path_data/"codes\\countries.csv", 
                     encoding="latin-1",
                     header=None,
                     index_col = 0,
                     names=["name", "longitude", "latitude"])
countries =sorted( list(aux.index))
countries_names = aux["name"].to_dict()
countries_centers = aux[["longitude", "latitude"]].apply(tuple, axis=1).to_dict()

aux = read_csv(path_data/"codes\\demand.csv", 
               encoding="latin-1",
               header=None,
               index_col = 0,
               names=["name"])
activities = list(aux.index)
activities_names = aux["name"].to_dict()

value_added_names = ["TLS", "VA", "OUT"]
final_demand_names = ['HFCE',  'NPISH',   'GGFC', 
                      'GFCF', 'INVNT',  'DPABR']

def variation_info(labels_1, labels_2):
    # Contingency matrix (n_ij)
    contingency = contingency_matrix(labels_1, labels_2)
    
    # Calculate joint distribution P(U, V)
    P_UV = contingency / contingency.sum()
    
    # Calculate marginal distributions
    P_U = P_UV.sum(axis=1)
    P_V = P_UV.sum(axis=0)

    # Calculate entropy
    H_U = entropy(P_U, base=2)
    H_V = entropy(P_V, base=2)
    
    # Calculate mutual information
    # I(U;V) = sum_{i,j} P(i,j) log_2 (P(i,j) / (P(i)*P(j)))
    I_UV = 0
    for i in range(P_UV.shape[0]):
        for j in range(P_UV.shape[1]):
            pij = P_UV[i, j]
            if pij > 0:
                I_UV += pij * log2(pij / (P_U[i] * P_V[j]))
    
    # Calculate variation of information 
    VI = H_U + H_V - 2 * I_UV
    return VI, H_U, H_V, I_UV
    