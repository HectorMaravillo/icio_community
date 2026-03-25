# ===========================================================
# PACKAGES
# ===========================================================
import sys
import pickle
import pandas as pd

from igraph import VertexClustering

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    
from icio_community import leiden_algorithm
from icio_community import Communities
#from icio_community import draw_map_test

# ===========================================================
# CONFIGURATION
# ===========================================================
BASE_DIR = ROOT / "analysis_normalized"
RESULTS_DIR = BASE_DIR / "results"
NETWORKS_DIR = BASE_DIR / "networks"
COMMUNITIES_DIR = BASE_DIR / "communities"
MAPS_DIR = BASE_DIR / "maps" 

# ===========================================================
# MAIN
# ===========================================================
# Load the best Leiden result
results_leiden = pd.read_csv(RESULTS_DIR / "Modularity_Leiden.csv")
idx_max  = results_leiden.groupby("year")["modularity"].idxmax()
best_results  = results_leiden.loc[idx_max].set_index("year")



year = 1995

best_seed  = best_results.loc[year]["seed"]
best_initial  = best_results.loc[year]["initial"]
best_modularity  = best_results.loc[year]["modularity"]
best_n_clusters  = best_results.loc[year]["clusters"]
with open(NETWORKS_DIR / f"g_{year}.pkl", "rb") as f:
    g = pickle.load(f)
modularity_params = {
    "weights": g.es["weight"],
    "directed": True
    }
p, _ = leiden_algorithm(g=g,
                        initial_by = best_initial,
                        seed = best_seed )
partition = VertexClustering(graph = g,
                             membership = p.membership,
                             modularity_params=modularity_params) 
community_max = Communities(p, year)

communities = community_max


select = ["MMR", "LAO", "THA", "MYS", "IDN", "VNM"]
communities_df = community_max.select(select)
community_max.draw_map(path_save = BASE_DIR, select = select, pct_threshold=99)


#community_max.draw_subgraphs()
