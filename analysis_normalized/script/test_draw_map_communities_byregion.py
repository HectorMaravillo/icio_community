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
