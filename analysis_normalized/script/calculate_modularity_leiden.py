# ===========================================================
# PACKAGES
# ===========================================================
import sys
import pickle

from igraph import VertexClustering

from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from icio_community import leiden_algorithm
from icio_community import export_dictionary

# ===========================================================
# VARIABLES
# ===========================================================

BASE_DIR = ROOT / "analysis_normalized"
NETWORK_DIR = BASE_DIR / "networks"
SAVE_DIR = BASE_DIR / "results"

iterations = range(0, 30)
labels = ["year", "algorithm", "initial", "seed", "modularity", "clusters","time"]

# ===========================================================
# VARIABLES
# ===========================================================

file_path = SAVE_DIR / "Modularity_Leiden.csv"
if not file_path.exists() or file_path.stat().st_size == 0:
    export_dictionary(dict(enumerate(labels)), file_path)

years = range(1995, 2023)
for year in years:
    # Cargar datos
    print(f"YEAR: {year}")
    with open(NETWORK_DIR / f"g_{year}.pkl", "rb") as f:
        g = pickle.load(f)
    
    modularity_params = {
        "weights": g.es["weight"],
        "directed": True
        }
    
    for by in ["activity",  "country", "single"]:
        print(f"initial: {by}")
        for i in iterations:
            print(f"{i}")
            p, t = leiden_algorithm(g = g,
                                    initial_by = by,
                                    seed = i)
            partition = VertexClustering(
                graph = g,
                membership = p.membership,
                modularity_params = modularity_params
                ) 
            results = {}    
            results["year"] = year
            results["algorithm"] = "Leiden"
            results["initial"] = by
            results["seed"] = i
            results["modularity"] = partition.modularity
            results["clusters"] = len(partition)
            results["time"] = t
            export_dictionary(results, file_path)
    del g
    print("\n")
