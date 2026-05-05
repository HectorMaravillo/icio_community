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
COMMUNITIES_DIR =  RESULTS_DIR / "communities"
MAPS_DIR = BASE_DIR / "maps" 


# ===========================================================
# VARIABLES
# ===========================================================
COUNTRY_GROUPS = {
    # Sudeste Asiático (ASEAN)
    "asean": ["IDN","MYS","PHL","SGP","THA","VNM","KHM","LAO","MMR","BRN", "TWN","HKG"],
    
    # Asia (sin Medio Oriente ni ASEAN)
    "asia": ["IDN","MYS","PHL","SGP","THA","VNM","KHM","LAO","MMR","BRN", "TWN","HKG",
             "CHN","JPN","KOR", "IND","BGD","PAK","SAU", "ARE"],
    
    # América del norte
    "north_america": ["CAN", "USA","MEX"],

    # América del sur y centroamérica
    "south_america": ["BRA","ARG","CHL","COL","PER","CRI"],

    # África Subsahariana
    "africa_subsaharan": ["NGA","CIV","SEN","CMR","COD","AGO","STP","ZAF"],
    
    "central_eastern_europe": [
        "LUX", "DEU", "AUT", "CZE", "HRV", "HUN", "SVK", "SVN", "POL",
        "CHE", "NLD", "BEL", 
        "DNK", "FIN", "NOR", "SWE",
        "ROU", "BGR", "BLR", "RUS", "UKR", "LTU", "LVA", "EST"
        ],

    # Europa + Norte de África + Medio Oriente
    "europe_extended": [
        "LUX", "DEU", "AUT", "CZE", "HRV", "HUN", "SVK", "SVN", "POL",
        "ROU", "BGR", "TUR", "GRC", "CYP", "BLR", "KAZ", "RUS", "UKR", "LTU", "LVA", "EST",
        "CHE", "NLD", "BEL", "IRL", "MLT", "GBR",
        "DNK", "FIN", "NOR", "SWE",
        "ESP", "PRT", "MAR", "ITA", "TUN", "FRA",
        "ISR", "EGY", "JOR"
        ],
}

MAPS_DIR.mkdir(parents=True, exist_ok=True)
for region_name in COUNTRY_GROUPS.keys():
    (MAPS_DIR / region_name).mkdir(exist_ok=True)

# ===========================================================
# MAIN
# ===========================================================
# Load the best Leiden result
results_leiden = pd.read_csv(RESULTS_DIR / "Modularity_Leiden.csv")
idx_max  = results_leiden.groupby("year")["modularity"].idxmax()
best_results  = results_leiden.loc[idx_max].set_index("year")

# Compute best solution and export communities and maps
for year, row in best_results.iterrows():
    
    if year > 2016:
        best_seed  = row["seed"]
        best_initial  = row["initial"]
        best_modularity  = row["modularity"]
        best_n_clusters  = row["clusters"]
        
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
        
        community_max = Communities(p, year)
        communities_df = community_max.select()
    #    print("Saving communities ...")
    #    communities_df.to_csv(COMMUNITIES_DIR /  f"{year}_communities.csv")
        print("Saving world map ...")
        community_max.draw_map(MAPS_DIR, save_name = "thr99",
                                pct_threshold=99, static = False)   
        
        for region_name, region in COUNTRY_GROUPS.items():
            print(f"Saving {region_name} map ...")
            community_max.draw_map(path_save = MAPS_DIR / region_name, save_name = region_name,
                                   select = region, pct_threshold=50, static = True)
        
        del g, p, partition