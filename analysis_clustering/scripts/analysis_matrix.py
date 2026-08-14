# ===========================================================
# PACKAGES
# ===========================================================

import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from icio_community import ICIO_Network, countries


# ===========================================================
# VARIABLES
# ===========================================================

countries = [country for country in countries if country != "ROW"]

SAVE_DIR = ROOT / "analysis_clustering" / "distance_matrices"

# ===========================================================
# FUNCTIONS
# ===========================================================

def import_national_matrices(year):
    icio = ICIO_Network(
        year,
        normalize=False,
        by_output=False,
        RoW=False,
        diagonal=True,
        diagonal_country=True
    )
    matrices = {}
    for country in countries:
        matrix = icio.matrix.loc[country, country].to_numpy(dtype=float)       
        # normalize national matrices
        national_total = matrix.sum()
        normalized_matrix = matrix / national_total
        matrices[country] = normalized_matrix

    return matrices

def compute_distance_matrices(matrices, distance):
    distance_matrix = pd.DataFrame(0.0, index = countries, columns = countries)
    for country_a, country_b in combinations(countries, 2):
        matrix_a = np.asarray(matrices[country_a], dtype=float)
        matrix_b = np.asarray(matrices[country_b], dtype=float)
        value = distance(matrix_a, matrix_b)
        distance_matrix.loc[country_a, country_b] = value
        distance_matrix.loc[country_b, country_a] = value

    return distance_matrix


# ===========================================================
# MAIN
# ===========================================================

#distance = lambda a, b: jensenshannon(
#    a.ravel(),
#    b.ravel(),
#    base=2)
#distance_name = "JS"

distance = lambda a, b: np.linalg.norm(a - b, ord="fro")
distance_name = "Frobenius"

for year in range(1995, 2023):
    print(f"Year: {year}")
    print("Importing data...")
    matrices = import_national_matrices(year)
    print("Computing distance matrix...")
    distance_matrix = compute_distance_matrices(
        matrices,
        distance
    )
    print("Exporting...")
    distance_matrix.to_csv(SAVE_DIR / f"{distance_name}_matrix_{year}.csv")
    del matrices, distance_matrix