# ===========================================================
# VARIABLES
# ===========================================================
from sklearn.manifold import Isomap, TSNE, MDS

import matplotlib.pyplot as plt


# ===========================================================
# FUNCTIONS
# ===========================================================
def draw(embedding,
         labels = None,
         color="black",
         size = 30):
    fig, ax = plt.subplots(figsize=(12, 10), dpi=150)
    ax.scatter(embedding[:, 0], embedding[:, 1],
                    s=size, color=color, 
                    edgecolors='black',  # color del borde
                    linewidths=0.1,
                    alpha = 0.7,
                    )
    if labels is not None:
        for i, country in enumerate(labels):
            ax.annotate(
                str(country),
                xy=(embedding[i, 0], embedding[i, 1]),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=7,
                color="black",
                alpha=0.9,
                bbox=dict(
                    boxstyle="round,pad=0.15",
                    facecolor="white",
                    edgecolor="none",
                    alpha=0.65
                )
            )
    ax.grid(True,
        which='major',     # 'major', 'minor', or 'both'
        axis='both',        # 'x', 'y', or 'both'
        color='gray',       # Color de las líneas
        linestyle='--',     # Tipo de línea: '-', '--', '-.', ':'
        linewidth=0.3,      # Grosor de las líneas
        alpha=0.7
        )
    ax.set_axis_off()
    plt.tight_layout()
    plt.show()
    plt.close()
    
def isomap(distance_matrix, **params):
    reducer = Isomap(
        n_components=2,
        metric="precomputed",
        n_neighbors=params["n_neighbors"]
    )
    embedding = reducer.fit_transform(distance_matrix)
    return embedding

def tsne(distance_matrix, **params):
    reducer = TSNE(
        n_components=2,
        metric="precomputed",
        perplexity=params["perplexity"],
        early_exaggeration=params["early_exaggeration"],
        init="random",
        random_state=42
    )
    embedding = reducer.fit_transform(distance_matrix)
    return embedding

def mds(distance_matrix, **params):        
    reducer = MDS(
        n_components=2,
        dissimilarity="precomputed",
        random_state=42,
        n_init=10
    )
    embedding = reducer.fit_transform(distance_matrix)
    return embedding

    
# ===========================================================
# VARIABLES
# ===========================================================
color_continent = [
    "orange",      # AGO - África
    "red",         # ARE - Asia
    "green",       # ARG - América del Sur
    "gray",        # AUS - Oceanía
    "purple",      # AUT - Europa
    "purple",      # BEL - Europa
    "red",         # BGD - Asia
    "purple",      # BGR - Europa
    "purple",      # BLR - Europa
    "green",       # BRA - América del Sur
    "red",         # BRN - Asia
    "blue",        # CAN - América del Norte
    "purple",      # CHE - Europa
    "green",       # CHL - América del Sur
    "red",         # CHN - Asia
    "orange",      # CIV - África
    "orange",      # CMR - África
    "orange",      # COD - África
    "green",       # COL - América del Sur
    "blue",        # CRI - América del Norte
    "purple",      # CYP - Europa
    "purple",      # CZE - Europa
    "purple",      # DEU - Europa
    "purple",      # DNK - Europa
    "orange",      # EGY - África
    "purple",      # ESP - Europa
    "purple",      # EST - Europa
    "purple",      # FIN - Europa
    "purple",      # FRA - Europa
    "purple",      # GBR - Europa
    "purple",      # GRC - Europa
    "red",         # HKG - Asia
    "purple",      # HRV - Europa
    "purple",      # HUN - Europa
    "red",         # IDN - Asia
    "red",         # IND - Asia
    "purple",      # IRL - Europa
    "purple",      # ISL - Europa
    "red",         # ISR - Asia
    "purple",      # ITA - Europa
    "red",         # JOR - Asia
    "red",         # JPN - Asia
    "red",         # KAZ - Asia
    "red",         # KHM - Asia
    "red",         # KOR - Asia
    "red",         # LAO - Asia
    "purple",      # LTU - Europa
    "purple",      # LUX - Europa
    "purple",      # LVA - Europa
    "orange",      # MAR - África
    "blue",        # MEX - América del Norte
    "purple",      # MLT - Europa
    "red",         # MMR - Asia
    "red",         # MYS - Asia
    "orange",      # NGA - África
    "purple",      # NLD - Europa
    "purple",      # NOR - Europa
    "gray",        # NZL - Oceanía
    "red",         # PAK - Asia
    "green",       # PER - América del Sur
    "red",         # PHL - Asia
    "purple",      # POL - Europa
    "purple",      # PRT - Europa
    "purple",      # ROU - Europa
    "purple",      # RUS - Europa
    "red",         # SAU - Asia
    "orange",      # SEN - África
    "red",         # SGP - Asia
    "orange",      # STP - África
    "purple",      # SVK - Europa
    "purple",      # SVN - Europa
    "purple",      # SWE - Europa
    "red",         # THA - Asia
    "orange",      # TUN - África
    "red",         # TUR - Asia
    "red",         # TWN - Asia
    "purple",      # UKR - Europa
    "blue",        # USA - América del Norte
    "red",         # VNM - Asia
    "orange"       # ZAF - África
]