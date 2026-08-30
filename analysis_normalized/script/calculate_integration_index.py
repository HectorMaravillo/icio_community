# ===========================================================
# PACKAGES
# ===========================================================
import pandas as pd
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from icio_community import ICIO_Network

# ===========================================================
# CONFIGURATION
# ===========================================================
BASE_DIR = ROOT / "analysis_normalized"
RESULTS_DIR = BASE_DIR / "results" / "communities" 

year = 2022
print(f"YEAR: {year}")
icio = ICIO_Network(year,
                    normalize=False,
                    by_output=False,
                    RoW=False,
                    diagonal =True,
                    diagonal_country=True)


path_read = RESULTS_DIR / f"{year}_communities.csv"
communities = pd.read_csv(path_read, index_col=0)


name = "DEU"

nodes = communities.eq(name).stack()
nodes = nodes[nodes].index.tolist()
nodes = [f"{c}_{s}" for c, s in nodes]
nodes = icio.g.vs.select(lambda node: node["name"] in nodes)
subg = icio.g.induced_subgraph(nodes)

