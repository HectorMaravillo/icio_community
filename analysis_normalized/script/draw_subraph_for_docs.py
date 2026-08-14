# ===========================================================
# PACKAGES
# ===========================================================
import sys
from igraph import VertexClustering
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SAVE_DIR = ROOT / "docs" / "subgraphs"

from icio_community.icio_network import ICIO_Network
from icio_community.communities import Communities
from icio_community.draw import draw_subgraph_network


# ===========================================================
# VARIABLES
# ===========================================================
selection = {
    "tmec": ["MEX", "USA", "CAN"],
    "asean": ["IDN","MYS","PHL","SGP","THA","VNM","KHM","LAO","MMR","BRN", "TWN","HKG"],
    "europe_central": ["DEU", "AUT", "CZE", "HUN",  "SVN",  "SVK", "POL", "HRV", "ROU"],
    "nordic": ["DNK", "NOR", "SWE", "FIN", "ISL", "EST", "LVA", "LTU"],
    "rusia": ["RUS", "BLR", "UKR", "BGR",  "CYP", "GRC", "TUR"],
    "southamerica": ["BRA", "ARG", "CHL", "PER", "COL"],
    "europe_benelux": ["BEL", "NLD", "LUX", "GBR", "IRL"],
    "africa_subsaharan": ["CMR","CIV","SEN","NGA","COD","ZAF", "STP","AGO"],
    }
strength = "out"
by = "country"
percentil = 95
niter = 1000

year = 2022


# ===========================================================
# FUNCTIONS
# ===========================================================
def extract_subraphs(g, year, countries_sel):
    select_nodes = [v.index for v in g.vs if v["country"] in countries_sel]
    g_sub = g.induced_subgraph(select_nodes)

    membership = [0] * g_sub.vcount()
    p = VertexClustering(g_sub, membership=membership)
    community = Communities(p, year)
    return community

# ===========================================================
# MAIN
# ===========================================================

for year in range(1995, 2022):
    print(f"YEAR: {year}")
    icio = ICIO_Network(year,
                        normalize=False,
                        by_output=False,
                        RoW=False,
                        diagonal =True,
                        diagonal_country=True)
    g = icio.g
    
    for region, countries_region in selection.items():
        print(f"Region: {region}")
        community = extract_subraphs(g, year, countries_region)
        draw_subgraph_network(community, 0,
                              path_save = SAVE_DIR,
                              save_name = f"{region}_{percentil}", 
                              strength = strength, 
                              by = by,
                              percentil = percentil,
                              niter = niter,
                              width=900,
                              height=900,
                              show_country_labels=True)
        del community
    del icio, g