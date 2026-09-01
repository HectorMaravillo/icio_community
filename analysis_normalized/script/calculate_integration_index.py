# ===========================================================
# PACKAGES
# ===========================================================
import pandas as pd
from tqdm import tqdm
import sys
import gc
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

def type_trade_for_community(icio, communities, community):
    nodes = communities.eq(community).stack()
    nodes = nodes[nodes].index.tolist()
    node_names = {f"{c}_{s}" for c, s in nodes}
    selected_nodes = icio.g.vs.select(lambda node: node["name"] in node_names)
    selected_ids = set(selected_nodes.indices)
    
    national = 0
    regional= 0
    external_out = 0
    external_in = 0
    
    for e in tqdm(icio.g.es):
        u, v = e.tuple
        
        if u in selected_ids and v not in selected_ids:
            external_out += e["weight"]
        elif u not in selected_ids and v in selected_ids:
            external_in += e["weight"]
        elif u in selected_ids and v in selected_ids:
            if icio.g.vs[u]["country"] == icio.g.vs[v]["country"]:
                national  += e["weight"]
            else:
                regional += e["weight"]
                
    return national, regional, external_out, external_in

years = range(1995, 2023)
records = []

for year in years:
    print(f"YEAR: {year}")
    icio = ICIO_Network(year,
                        normalize=False,
                        by_output=False,
                        RoW=False,
                        diagonal =True,
                        diagonal_country=True)
    
    path_read = RESULTS_DIR / f"{year}_communities.csv"
    communities = pd.read_csv(path_read, index_col=0)
    
    community_names = pd.unique(communities.to_numpy().ravel())
    community_names = [c for c in community_names if pd.notna(c)]

    
    for community in community_names:
        national, regional, external_out, external_in = type_trade_for_community(
            icio, communities, community
            ) 

        records.append({
            "community": community,
            "year": year,
            "national": national,
            "regional": regional,
            "external_out": external_out,
            "external_in": external_in
        })
    del icio
    gc.collect()

trade = (
    pd.DataFrame(records)
    .sort_values(["community", "year"])
    .reset_index(drop=True)
)

trade.to_csv(RESULTS_DIR / "type_trade_by_community.csv")