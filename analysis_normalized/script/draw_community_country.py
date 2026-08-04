# ===========================================================
# PACKAGES
# ===========================================================
import sys
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.patches import Patch
from pandas import unique
from seaborn import  heatmap
from pathlib import Path
from numpy import  nan
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    
from country_groups import COUNTRY_ORDER
from icio_community import create_colors, countries

# ===========================================================
# CONFIGURATION
# ===========================================================
# -----------------
# Paths
BASE_DIR = ROOT / "analysis_normalized"
COMMUNITIES_DIR = BASE_DIR / "results" / "communities"
RESULTS_DIR = BASE_DIR / "results"
IMAGES_DIR = BASE_DIR / "images" 

DPI  = 150

years = range(1995, 2023)

# Base font sizes
FONTSIZE = 30
FONTSIZE_LABELS = FONTSIZE
FONTSIZE_TICKS = FONTSIZE - 6
FONTSIZE_LEGEND = FONTSIZE - 6
FONTSIZE_LEGEND_TITLE = FONTSIZE - 4

# ===========================================================
# MAIN
# ===========================================================
path_file = RESULTS_DIR / "Community_by_country.csv"

if path_file.exists():
    country_communities = pd.read_csv(path_file, index_col=0)
    communities_unique = set(
        pd.Series(country_communities.values.ravel()).dropna()
    )
else:
    country_communities = pd.DataFrame()
    communities_unique = set()
    for file in COMMUNITIES_DIR.glob("*.csv"):
        df = pd.read_csv(file, header = 0, index_col=0) 
        communities_unique.update(unique(df.values.ravel()))
        community_membership = {}
        for idx, row in df.iterrows():
            row = row[~row.isna()]
            n_tot = len(row)
            value_counts = row.value_counts()
            community = value_counts.index[0]
            community_membership[idx] = community
        year = int(file.stem[:4])
        country_communities[year] = pd.Series(community_membership)
        del df
    country_communities.index.name = "country"
    country_communities.columns.name = "year"
    country_communities.to_csv(RESULTS_DIR / "Community_by_country.csv")
    
COUNTRY_ORDER = ["IDN","MYS","PHL","SGP","THA","VNM","KHM","LAO","MMR","BRN", "TWN","HKG"]
COUNTRY_ORDER = ["CAN", "USA", "MEX"]
COUNTRY_ORDER = [ "DEU", "AUT", "CZE", "HUN",  "SVN",  "SVK", "POL", "HRV", "ROU"]
COUNTRY_ORDER = ["DNK", "NOR", "SWE", "FIN", "ISL", "EST", "LVA", "LTU"]
COUNTRY_ORDER = ["BEL", "NLD", "LUX", "GBR", "IRL", "MLT"]
COUNTRY_ORDER =  ["RUS", "BLR", "UKR", "BGR",   "CYP", "GRC", "TUR"]
COUNTRY_ORDER =  ["BRA", "ARG", "CHL", "PER", "COL"]
#COUNTRY_ORDER = ["TUR", "GRC" ,"CYP",  "BGR",  "KAZ", "BLR",  "RUS", "UKR", "LVA", "LTU", "EST"]
country_communities = country_communities.loc[COUNTRY_ORDER]

communities_unique = set(communities_unique)-{nan}

if communities_unique.issubset(set(countries)):
    # Assign unique IDs to each country for coloring the heatmap
    countries_id = dict(zip(countries, range(len(countries))))  
    # Convert community names in df to numeric IDs (or -1 if not found)
    df_id = country_communities.map(lambda x: countries_id.get(x, -1))
    colors = create_colors()

annotate = False
xlabel = "Año"
ylabel = "País"
label_title = "Comunidad"
scale = 0.7

shape = df_id.shape
figsize=((scale+1) * shape[1],
         scale * shape[0])

fig, ax = plt.subplots(figsize=figsize)
heatmap(df_id, ax=ax,
        annot=False, cbar =False)
# For each non-masked cell, assing label and color community
for i in df_id.columns:
    for j in df_id.index:
        if df_id[i][j] >=0:
            col = country_communities.columns.get_loc(i)
            row = country_communities.index.get_loc(j)
            if annotate:
                ax.annotate(country_communities[i][j],
                            (col+.5, row+.5),
                            ha='center', va='center',
                            fontsize=9)
            ax.add_patch(plt.Rectangle((col, row), 1.01, 1.01, 
                                       color=colors[country_communities[i][j]]))

# Set axis titles and format ticks
ax.set_xlabel(xlabel, fontsize=FONTSIZE_LABELS)
ax.set_ylabel(ylabel, fontsize=FONTSIZE_LABELS)
ax.set_xticklabels(ax.get_xticklabels(), fontsize=FONTSIZE_TICKS, rotation=0, ha='center')
ax.set_yticklabels(ax.get_yticklabels(), fontsize=FONTSIZE_TICKS, rotation=0, ha='right')    
ax.tick_params(axis='x', bottom=False, top=False)
ax.tick_params(axis='y', left=False, right=False)


# Set legend
communities_unique = set(country_communities.to_numpy().ravel())
community_names = sorted(communities_unique)
legend_elements = [
    Patch(facecolor=colors[country], edgecolor=None, label=country)
    for country in community_names
] 
ax.legend(handles=legend_elements, bbox_to_anchor=(1,1),
           loc='upper left',
           title=label_title,
           fontsize=FONTSIZE_LEGEND,
           title_fontsize=FONTSIZE_LEGEND_TITLE,
           handleheight=1,
           handlelength=1,
           borderpad=0.1)

#plt.savefig(IMAGES_DIR / "ComunidadesPorPais.png",
#            dpi=DPI,
#            bbox_inches="tight")
plt.show()