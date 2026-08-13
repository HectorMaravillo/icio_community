# ===========================================================
# PACKAGES
# ===========================================================
import sys
import numpy as np
import pandas as pd

from itertools import combinations
from scipy.spatial.distance import jensenshannon

from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from icio_community import ICIO_Network, countries

countries.remove("ROW")


# ===========================================================
# MAIN
# ===========================================================

year = 2022

icio = {}
icio[year] = ICIO_Network(year,
                          normalize = False, 
                          by_output = False,
                          RoW = False,
                          diagonal = True,
                          diagonal_country = True)

matrices = {}

for country in countries:
    aux = icio[year].matrix.loc[country, country] 
    national_total = aux.sum().sum()
    matrices[country] = aux / national_total
    matrices[country] = matrices[country].to_numpy(dtype=float)
    
    if np.any(matrices[country] < 0):
        raise ValueError( f"Hay valores negativos en {country}")
    if not np.isclose(matrices[country].sum(), 1.0):
        raise ValueError(f"La matriz de {country} no suma uno")
        
        
# Matriz cuadrada de distancias
JS_matrix = pd.DataFrame(
    0.0,
    index=countries,
    columns=countries
)

for country_a, country_b in combinations(countries, 2):
    A = matrices[country_a]
    B = matrices[country_b]

    if A.shape != B.shape:
        raise ValueError(
            f"Las matrices de {country_a} y {country_b} "
            f"tienen dimensiones diferentes: {A.shape} y {B.shape}"
        )

    distance = jensenshannon(
        A.ravel(),
        B.ravel(),
        base=2
    )

    JS_matrix.loc[country_a, country_b] = distance
    JS_matrix.loc[country_b, country_a] = distance
    
    
#%%%
##############
# Funciones
##############
#import umap

import matplotlib.pyplot as plt
def draw(embedding, color="black"):
    fig, ax = plt.subplots(figsize=(12, 10), dpi=150)
    ax.scatter(embedding[:, 0], embedding[:, 1],
                    s=15, color=color, 
                    edgecolors='black',  # color del borde
                    linewidths=0.1,
                    alpha = 0.7,
                    )
    ax.grid(True,
        which='major',     # 'major', 'minor', or 'both'
        axis='both',        # 'x', 'y', or 'both'
        color='gray',       # Color de las líneas
        linestyle='--',     # Tipo de línea: '-', '--', '-.', ':'
        linewidth=0.3,      # Grosor de las líneas
        alpha=0.7
        )
    # Etiqueta de cada país
    for i, country in enumerate(countries):
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
    ax.text(0.85, 0.9,
        subtitle,
        transform=ax.transAxes,
        ha='center', fontsize=8,
        bbox=dict(
            facecolor='white',
            edgecolor='lightgray',
            boxstyle='round,pad=0.3',
            alpha=0.8 
            )
        )
    ax.set_xlabel(f"{title} 1", fontsize=14)
    ax.set_ylabel(f"{title} 2", fontsize=14)
    """   for i in select:
        print(i, ": ", names[i])
        text = names[i]
        idx = np.where(indices == i)[0][0]
        if embedding[idx][1] > 7:
            xytext=(85, 10)
        elif embedding[idx][1] > 2.5:
            if embedding[idx][0] > 0:
                xytext=(25, 20)
            else:
                xytext=(-35, 15)
        elif embedding[idx][0] <3:
            xytext=(-60, -20)
        elif embedding[idx][0] >3:
            xytext=(20, -20)
        else:
            xytext=(10, 10)
        ax.annotate(text, 
                    xy = embedding[idx],
                    xytext=xytext,
                    textcoords='offset points',
                    fontsize=7,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none",
                              alpha=.8),
                    arrowprops=dict(
                                    arrowstyle='->',
                                    color="gray",
                                    lw=0.5)
                    )"""
    plt.tight_layout()
    plt.show()
    plt.close()
    
    
from sklearn.manifold import Isomap, TSNE, MDS
D_JS = JS_matrix.loc[countries, countries].to_numpy(dtype=float)
n_countries = len(countries)

params = {}
###################
# ISOMAP
###################

neighbor_values = [
    n for n in [3, 5, 10, 15, 20, 30, 50, 100]
    if n < n_countries
]

for n_neighbors in neighbor_values:
    print(n_neighbors)

    params["n_neighbors"] = n_neighbors

    reducer = Isomap(
        n_components=2,
        metric="precomputed",
        n_neighbors=params["n_neighbors"]
    )

    embedding = reducer.fit_transform(D_JS)

    title = "ISOMAP — Jensen-Shannon"
    subtitle = f"neighbors: {params['n_neighbors']}"

    draw(embedding, color="darkblue")
    
    
###################
# t-SNE
###################

perplexity_values = [
    p for p in [5, 10, 20, 30, 50]
    if p < n_countries
]

early_values = [1, 3, 5, 10, 12, 15]

for perplexity in perplexity_values:
    for early in early_values:
        print(perplexity, early)

        params["perplexity"] = perplexity
        params["early_exaggeration"] = early

        reducer = TSNE(
            n_components=2,
            metric="precomputed",
            perplexity=params["perplexity"],
            early_exaggeration=params["early_exaggeration"],
            init="random",
            random_state=42
        )

        embedding = reducer.fit_transform(D_JS)

        title = "t-SNE — Jensen-Shannon"
        subtitle = (
            f"perplexity: {params['perplexity']},\n"
            f"early exaggeration: "
            f"{params['early_exaggeration']}"
        )

        draw(embedding, color="darkblue")
        
    ###################
# MDS
###################

reducer = MDS(
    n_components=2,
    dissimilarity="precomputed",
    random_state=42,
    n_init=10
)

embedding = reducer.fit_transform(D_JS)

title = "MDS — Jensen-Shannon"
subtitle = f"stress: {reducer.stress_:.6f}"

draw(embedding, color="darkblue")

