import sys
from igraph import VertexClustering

ROOT = r"C:\Users\Saib\Projects\icio_community"

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
    
from icio_community.icio_network import ICIO_Network
from icio_community.utils import countries_names
from icio_community.communities import Communities
from icio_community.draw import draw_subgraph_network, create_colors

#%%

year = 2022
print(f"YEAR: {year}")
icio = ICIO_Network(year,
                    normalize=False,
                    by_output=False,
                    RoW=False,
                    diagonal =True,
                    diagonal_country=True)
#%%%
selection = ["MEX", "USA", "CAN"]
#selection = ["IDN","MYS","PHL","SGP","THA","VNM","KHM","LAO","MMR","BRN", "TWN","HKG"]
#selection = ["DEU", "AUT", "CZE", "HUN",  "SVN",  "SVK", "POL", "HRV", "ROU"]
#selection = ["DNK", "NOR", "SWE", "FIN", "ISL", "EST", "LVA", "LTU"]
#selection = ["BEL", "NLD", "LUX", "GBR", "IRL", "MLT"]
selection = ["RUS", "BLR", "UKR", "BGR",   "CYP", "GRC", "TUR"]
selection =  ["BRA", "ARG", "CHL", "PER", "COL"]
g = icio.g
select_nodes = [v.index for v in g.vs if v["country"] in selection]
g_sub = g.induced_subgraph(select_nodes)

membership = [0] * g_sub.vcount()
p = VertexClustering(g_sub, membership=membership)
community = Communities(p, year)


strength = "out"
by = "country"
percentil = 95
draw_subgraph_network(community, 0,
                      path_save = None,
                      save_name = None, 
                      strength = strength, 
                      by = by,
                      percentil = percentil,
                      niter = 500,
                      width=900,
                      height=600)


#%%%
countries = g_sub.vs["country"]
mapping = {c: i for i, c in enumerate(sorted(set(countries)))}
membership = [mapping[c] for c in countries]
p = VertexClustering(g_sub, membership=membership)
community = Communities(p, year)
labels = dict(enumerate(community.labels))


for i in [77, 50, 14, 22]:
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
