import sys
from igraph import VertexClustering
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SAVE_DIR = ROOT / "analysis_normalized" / "subgraphs"

from icio_community.icio_network import ICIO_Network
from icio_community.communities import Communities
from icio_community.draw import draw_subgraph_network

year = 2022
print(f"YEAR: {year}")
icio = ICIO_Network(year,
                    normalize=False,
                    by_output=False,
                    RoW=False,
                    diagonal =True,
                    diagonal_country=True)
#%%%


region = "southamerica"

selection = {
    "tmec": ["MEX", "USA", "CAN"],
    "asean": ["IDN","MYS","PHL","SGP","THA","VNM","KHM","LAO","MMR","BRN", "TWN","HKG"],
    "europe_central": ["DEU", "AUT", "CZE", "HUN",  "SVN",  "SVK", "POL", "HRV", "ROU"],
    "nordic": ["DNK", "NOR", "SWE", "FIN", "ISL", "EST", "LVA", "LTU"],
    "rusia": ["RUS", "BLR", "UKR", "BGR",  "CYP", "GRC", "TUR"],
    "southamerica": ["BRA", "ARG", "CHL", "PER", "COL"]
    }

g = icio.g
select_nodes = [v.index for v in g.vs if v["country"] in selection[region]]
select_nodes = [v.index for v in g.vs]
region = "world"
g_sub = g.induced_subgraph(select_nodes)

membership = [0] * g_sub.vcount()
p = VertexClustering(g_sub, membership=membership)
community = Communities(p, year)


strength = "out"
by = "country"
percentil = 99.9
draw_subgraph_network(community, 0,
                      path_save = SAVE_DIR,
                      save_name = f"{region}_{year}_{percentil}", 
                      strength = strength, 
                      by = by,
                      percentil = percentil,
                      niter = 5000,
                      width=900,
                      height=600,
                      show_country_labels=True)


#%%%
countries = g_sub.vs["country"]
mapping = {c: i for i, c in enumerate(sorted(set(countries)))}
membership = [mapping[c] for c in countries]
p = VertexClustering(g_sub, membership=membership)
community = Communities(p, year)
labels = dict(enumerate(community.labels))


for i in [0, 1, 2]:
    strength = "out"
    by = "activity"
    percentil = 90
    draw_subgraph_network(community, i,
                          path_save = None,
                          save_name = None, 
                          strength = strength, 
                          by = "activity",
                          percentil = percentil)
community.draw_map(pct_threshold=99)
