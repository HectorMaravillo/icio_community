# ===========================================================
# PACKAGES
# ===========================================================
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from sklearn_extra.cluster import KMedoids
from sklearn.metrics import silhouette_score
from utils import color_continent, draw, isomap, tsne, mds, umap_reducer

from pathlib import Path    
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    
from icio_community import ICIO_Network, countries
  

# ===========================================================
# VARIABLES
# ===========================================================
DATA_DIR = ROOT / "analysis_clustering" / "distance_matrices"

# ===========================================================
# MAIN
# ===========================================================

distance_name = "JS"

year = 2022
print("Importing...")
file_path = DATA_DIR / f"{distance_name}_matrix_{year}.csv"
distance_matrix = pd.read_csv(file_path, index_col=0)
country_names = list(distance_matrix.columns)
distance_matrix = distance_matrix.to_numpy(dtype=float)


# Kmedoids
intertia = []
silhouettes = []
n_values = range(2,20)
for n in n_values:
    kmedoids = KMedoids(
        n_clusters = n,              
        metric="precomputed",
        random_state=42
    )
    labels = kmedoids.fit_predict(distance_matrix)
    intertia.append(kmedoids.inertia_)
    
    score = silhouette_score(
        distance_matrix,
        labels,
        metric="precomputed"
    )
    silhouettes.append(score)
    

# Gráfica del método del codo
plt.figure(figsize=(9, 5))
plt.plot(n_values, intertia, marker="o")
plt.xticks(n_values)
plt.xlabel("Número de clusters")
plt.ylabel("Costo total (inercia)")
plt.title("Método del codo para K-Medoids")
plt.grid(alpha=0.3)

plt.figure(figsize=(9, 5))
plt.plot(n_values, silhouettes, marker="o")
plt.xticks(n_values)
plt.xlabel("Número de clústeres")
plt.ylabel("Coeficiente de silhouette")
plt.title("Silhouette para K-Medoids")
plt.grid(alpha=0.3)
plt.show()



#%%%
kmedoids = KMedoids(
    n_clusters = 8,              
    metric="precomputed",
    random_state=42
)

cluster_labels = kmedoids.fit_predict(distance_matrix)
medoid_indices = kmedoids.medoid_indices_
cmap = plt.get_cmap("tab10")
color_clusters = [
    "lightgray" if cluster == -1 else cmap(cluster % 20)
    for cluster in cluster_labels
]

params = {}
#for n_neighbors in [3, 5, 10, 15, 20, 30, 50]:
#    params["n_neighbors"] = n_neighbors
#    embedding = isomap(distance_matrix, **params)
#    draw(embedding, country_names, color=color_clusters)

#for perplexity in [5, 10, 20, 30, 50]:
#    for early in [1, 3, 5, 10, 12, 15]:
#        params["perplexity"] = perplexity
#        params["early_exaggeration"] = early
#        embedding = tsne(distance_matrix, **params)
#        draw(embedding, country_names, color=color_clusters)
    
for n_neighbors in [5, 10]:
    for min_dist in [0.001, 0.005, .01, 0.05]:
        params["n_neighbors"] = n_neighbors
        params["min_dist"] = min_dist
        embedding = umap_reducer(distance_matrix, **params)
        subtitle = f"umap\nn_neighbors: {params['n_neighbors']}\nmin_dist: {params['min_dist']}"
        draw(embedding, country_names,
             color=color_clusters,
             medoid_indices=medoid_indices,
             subtitle = subtitle)
    
        
        
#embedding = mds(distance_matrix, **params)
#draw(embedding, country_names, color=color_clusters, size = 50)


#%%
import seaborn as sns

medoid_names = [country_names[i] for i in medoid_indices]
icio = ICIO_Network(
    year,
    normalize=False,
    by_output=False,
    RoW=False,
    diagonal=True,
    diagonal_country=True
)

#%%%
matrices = {}
for country in medoid_names:
    matrix = icio.matrix.loc[country, country]
    # normalize national matrices
    national_total = matrix.sum()
    normalized_matrix = matrix / national_total
    matrices[country] = normalized_matrix

bloques = {
    "Agropecuario": ("A",),
    "Extractivos":  ("B",),
    "Industria":    ("C", "D", "E", "F"),
    "Comercio":     ("G",),
    "Transporte":   ("H",),
    "Servicios":    ("I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"),
}

colores = {
    "Agropecuario": "#2ca02c",
    "Extractivos":  "#8c564b",
    "Industria":    "#d62728",
    "Comercio":     "#ff7f0e",
    "Transporte":   "#9467bd",
    "Servicios":    "#111111",
}


def codigo_sector(etiqueta):
    """Obtiene la letra inicial del código sectorial."""
    return str(etiqueta).strip()[0].upper()


for country, v in matrices.items():
    fig, ax = plt.subplots(figsize=(12, 10))

    sns.heatmap(
        v,
        ax=ax,
        cmap="Blues",
        vmin=0,
        vmax=1,
        square=True,
        linewidths=0.5,
        xticklabels=v.columns,
        yticklabels=v.index,
    )

    row_codes = [codigo_sector(x) for x in v.index]
    col_codes = [codigo_sector(x) for x in v.columns]

    # Dibujar un rectángulo alrededor de cada bloque diagonal
    for nombre, letras in bloques.items():
        filas = [i for i, code in enumerate(row_codes) if code in letras]
        columnas = [i for i, code in enumerate(col_codes) if code in letras]

        if not filas or not columnas:
            continue

        y0 = min(filas)
        x0 = min(columnas)
        alto = max(filas) - y0 + 1
        ancho = max(columnas) - x0 + 1

        rect = patches.Rectangle(
            (x0, y0),
            ancho,
            alto,
            fill=False,
            edgecolor=colores[nombre],
            linewidth=2.5,
            label=nombre,
        )
        ax.add_patch(rect)

    ax.set_title(str(country))
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_aspect("equal")

    ax.set_xticklabels(
        ax.get_xticklabels(),
        rotation=90,
        ha="center",
    )
    ax.set_yticklabels(
        ax.get_yticklabels(),
        rotation=0,
        ha="right",
    )

    # Leyenda sin entradas duplicadas
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        labels,
        title="Bloques",
        bbox_to_anchor=(1.18, 1),
        loc="upper left",
        frameon=False,
    )

    plt.tight_layout()
    plt.show()

#%%

def nombre_bloque(etiqueta):
    codigo = str(etiqueta).strip()[0].upper()

    if codigo == "A":
        return "Agropecuario"
    elif codigo == "B":
        return "Extractivos"
    elif codigo in ("C", "D", "E", "F"):
        return "Industria"
    elif codigo == "G":
        return "Comercio"
    elif codigo == "H":
        return "Transporte"
    else:
        return "Servicios"


colores = {
    "Agropecuario": "#2ca02c",
    "Extractivos":  "#8c564b",
    "Industria":    "#d62728",
    "Comercio":     "#ff7f0e",
    "Transporte":   "#9467bd",
    "Servicios":    "#4c78a8",
}


for country, v in matrices.items():

    produccion = v.sum(axis=1)

    datos = pd.DataFrame({
        "Sector": produccion.index.astype(str),
        "Produccion": produccion.values,
    })

    datos["Bloque"] = datos["Sector"].apply(nombre_bloque)

    plt.figure(figsize=(14, 6))

    ax = sns.barplot(
        data=datos,
        x="Sector",
        y="Produccion",
        hue="Bloque",
        palette=colores,
        dodge=False,
    )

    ax.set_title(f"Producción sectorial normalizada — {country}")
    ax.set_xlabel("Sector")
    ax.set_ylabel("Participación en la producción nacional")
    ax.tick_params(axis="x", rotation=90)
    ax.legend(title="Bloque", bbox_to_anchor=(1.02, 1), loc="upper left")

    plt.tight_layout()
    plt.show()
    
    #%%
    
for country, v in matrices.items():

    produccion = v.sum(axis=1)

    datos = pd.DataFrame({
        "Sector": produccion.index.astype(str),
        "Produccion": produccion.values,
    })

    datos["Bloque"] = datos["Sector"].apply(nombre_bloque)

    produccion_bloque = (
        datos.groupby("Bloque", sort=False)["Produccion"]
        .sum()
        .reindex(colores.keys())
    )

    plt.figure(figsize=(9, 5))

    ax = sns.barplot(
        x=produccion_bloque.index,
        y=produccion_bloque.values,
        hue=produccion_bloque.index,
        palette=colores,
        legend=False,
    )

    ax.set_title(f"Producción por bloque — {country}")
    ax.set_xlabel("")
    ax.set_ylabel("Participación en la producción nacional")
    ax.tick_params(axis="x", rotation=30)

    plt.tight_layout()
    plt.show()