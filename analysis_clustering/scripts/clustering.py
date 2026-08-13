# ===========================================================
# PACKAGES
# ===========================================================
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn_extra.cluster import KMedoids
from pathlib import Path    

from utils import color_continent, draw, isomap, tsne, mds

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    
from icio_community import countries
    
# ===========================================================
# VARIABLES
# ===========================================================
DATA_DIR = ROOT / "analysis_clustering" / "distance_matrices"

countries = [country for country in countries if country != "ROW"]

# ===========================================================
# MAIN
# ===========================================================

distance_name = "Frobenius"

year = 1995
print("Importing...")
file_path = DATA_DIR / f"{distance_name}_matrix_{year}.csv"
distance_matrix = pd.read_csv(file_path, index_col=0)
country_names = list(distance_matrix.columns)
distance_matrix = distance_matrix.to_numpy(dtype=float)


# DBSCAN
dbscan = DBSCAN(
    eps=0.10,              # Depende de la escala de tus distancias
    min_samples=3,
    metric="precomputed"
)
cluster_labels = dbscan.fit_predict(distance_matrix)
cmap = plt.get_cmap("tab10")
color_clusters = [
    "lightgray" if cluster == -1 else cmap(cluster % 20)
    for cluster in cluster_labels
]

params = {}
params["n_neighbors"] = 10
embedding = isomap(distance_matrix, **params)
draw(embedding, country_names, color=color_clusters)

params["perplexity"] = 10
params["early_exaggeration"] = 3
embedding = tsne(distance_matrix, **params)
draw(embedding, country_names, color=color_clusters)
    

embedding = mds(distance_matrix, **params)
draw(embedding, country_names, color=color_clusters)
