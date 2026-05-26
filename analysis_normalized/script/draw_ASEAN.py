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
    
from icio_community import leiden_algorithm, Communities

# ===========================================================
# CONFIGURATION
# ===========================================================
BASE_DIR = ROOT / "analysis_normalized"
RESULTS_DIR = BASE_DIR / "results"
NETWORKS_DIR = BASE_DIR / "networks"
COMMUNITIES_DIR =  RESULTS_DIR / "communities"
MAPS_DIR = BASE_DIR / "maps" 
IMAGES_DIR = BASE_DIR / "images" / "communities"

# ===========================================================
# VARIABLES
# ===========================================================

MAPS_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================================
# MAIN
# ===========================================================
# Load the best Leiden result
results_leiden = pd.read_csv(RESULTS_DIR / "Modularity_Leiden.csv")
idx_max  = results_leiden.groupby("year")["modularity"].idxmax()
best_results  = results_leiden.loc[idx_max].set_index("year")


draw = {
        "communities": True,
        "communities_csv": False,
        "maps": False,
        "regional_maps": False
        }

year = 2007
row = best_results.loc[year]
best_seed  = row["seed"]
best_initial  = row["initial"]
best_modularity  = row["modularity"]
best_n_clusters  = row["clusters"]

select = []

print(f"YEAR: {year}")
print("Loading network ...")
with open(NETWORKS_DIR / f"g_{year}.pkl", "rb") as f:
    g = pickle.load(f)
    
modularity_params = {
    "weights": g.es["weight"],
    "directed": True
    }
print("Running Leiden solution ...")
p, _ = leiden_algorithm(g=g,
                        initial_by = best_initial,
                        seed = best_seed )
partition = VertexClustering(graph = g,
                             membership = p.membership,
                             modularity_params=modularity_params) 

region = ["HKG","VNM","KHM", "MYS","PHL","SGP","THA","LAO", "TWN","IDN", "BRN","MMR"]

community_max = Communities(p, year)
communities_df = community_max.select()


print("Draw communities ...")   
community_max.draw_map(select = region, pct_threshold=50, static = False)