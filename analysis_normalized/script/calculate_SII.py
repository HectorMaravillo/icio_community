# ===========================================================
# PACKAGES
# ===========================================================
import pandas as pd
from tqdm import tqdm
import sys
import numpy as np
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


def community_trade_matrices(icio, nodes):
    """
    Construye dos matrices país-país para una comunidad.

    Retorna
    -------
    T_out : pd.DataFrame
        Flujos internos normalizados por las salidas totales
        de cada país, incluyendo destinos fuera de la comunidad.

    T_in : pd.DataFrame
        Flujos internos normalizados por las entradas totales
        de cada país, incluyendo orígenes fuera de la comunidad.

    En ambas matrices:
        - Filas: país de origen.
        - Columnas: país de destino.
        - Diagonal: flujos nacionales dentro de la comunidad.
        - Fuera de la diagonal: flujos internacionales internos.

    Los denominadores nulos producen NaN.
    """
    matrix = icio.matrix
    external = "EXTERNAL"

    # -------------------------------------------------------
    # 2. Asignar país o EXTERNAL a cada vértice
    # -------------------------------------------------------
    inside_rows = matrix.index.isin(nodes)
    inside_cols = matrix.columns.isin(nodes)

    row_country = matrix.index.get_level_values(0)
    col_country = matrix.columns.get_level_values(0)

    countries = row_country[inside_rows].unique().tolist()

    row_groups = row_country.where(inside_rows, external)
    col_groups = col_country.where(inside_cols, external)

    # -------------------------------------------------------
    # 3. Agregar los flujos por país de origen y destino
    # -------------------------------------------------------
    F = matrix.groupby(row_groups, sort=False).sum()
    F = F.T.groupby(col_groups, sort=False).sum().T

    order = countries + [external]

    F = F.reindex(
        index=order,
        columns=order,
        fill_value=0
    )

    # -------------------------------------------------------
    # 4. Separar flujos internos y calcular denominadores
    # -------------------------------------------------------
    internal = F.loc[countries, countries]

    # Incluyen flujos hacia y desde fuera de la comunidad
    total_out = F.loc[countries, :].sum(axis=1)
    total_in = F.loc[:, countries].sum(axis=0)

    # -------------------------------------------------------
    # 5. Normalizar
    # -------------------------------------------------------
    T_out = internal.div(
        total_out.replace(0, float("nan")),
        axis=0
    )

    T_in = internal.div(
        total_in.replace(0, float("nan")),
        axis=1
    )

    return T_out, T_in


def calculate(T, axis):
    # Verificar estructura y orden de los países
    if not T.index.equals(T.columns):
        raise ValueError(
            "Cada matriz debe ser no vacía y tener los mismos "
            "países, en el mismo orden, en filas y columnas."
        )

    A = T.to_numpy(dtype=float, copy=True)
    n = len(A)

    if (A < 0).any() or (A.sum(axis=axis) > 1 + 1e-10).any():
        raise ValueError(
            "Las matrices deben contener proporciones "
            "no negativas y estar normalizadas."
        )

    # Proporción de flujos fuera del componente nacional
    d = 1.0 - np.diag(A)

    # Eliminar la diagonal y corregir las proporciones.
    # Se cumple:
    # det(I - P) = det(I - T) / prod(1 - T_ii)
    np.fill_diagonal(A, 0.0)

    if axis == 1:
        P = A / d[:, None]       # Corrección por filas
    else:
        P = A / d[None, :]       # Corrección por columnas

    sign, logdet = np.linalg.slogdet(np.eye(n) - P)

    if sign == 0:
        return 1.0

    if sign < 0:
        raise ArithmeticError(
            "Determinante negativo: revisa las matrices "
            "o su precisión numérica."
        )

    if logdet > 1e-10:
        raise ArithmeticError(
            "El determinante normalizado supera uno."
        )

    # Equivale a 1 - exp(logdet / n)
    sii = -np.expm1(logdet / n)

    # Corregir pequeños errores de redondeo
    return float(np.clip(sii, 0.0, 1.0))

def systemic_integration_indices(T_out, T_in):
    """
    Calcula los índices de integración sistémica corregidos
    por los flujos nacionales de la diagonal.

    Parámetros
    ----------
    T_out : pd.DataFrame
        Matriz normalizada por salidas (filas).
    T_in : pd.DataFrame
        Matriz normalizada por entradas (columnas).

    Retorna
    -------
    dict
        {"SII_out": float, "SII_in": float}

    Devuelve NaN cuando una matriz contiene valores no finitos
    o algún país tiene T_ii >= 1, haciendo indefinida la corrección.
    """
    return {
        "SII_out": calculate(T_out, axis=1),
        "SII_in": calculate(T_in, axis=0)
    }


year = 2008
print(f"YEAR: {year}")
icio = ICIO_Network(year,
                    normalize=False,
                    by_output=False,
                    RoW=False,
                    diagonal =True,
                    diagonal_country=True)
path_read = RESULTS_DIR / f"{year}_communities.csv"
communities = pd.read_csv(path_read, index_col=0)

#%%%
community = "DEU"
membership = communities.eq(community).stack()
nodes = membership[membership].index

countries = nodes.get_level_values(0)
counts = countries.value_counts()
selected_countries = counts[counts > 20].index
nodes = nodes[countries.isin(selected_countries)]
T_out, T_in = community_trade_matrices(
    icio=icio,
    nodes = nodes
)
sii = systemic_integration_indices(T_out, T_in)

print(sii["SII_out"])
print(sii["SII_in"])

#%%%
countries = [
    "AUT", "BEL", "BGR", "CYP", "CZE", "DEU", "DNK",
    "ESP", "EST", "FIN", "FRA", "GRC", "HRV", "HUN",
    "IRL", "ITA", "LTU", "LUX", "LVA", "MLT", "NLD",
    "POL", "PRT", "ROU", "SVK", "SVN", "SWE"
]
index = icio.matrix.index
nodes = index[index.get_level_values(0).isin(countries)]
    
T_out, T_in = community_trade_matrices(
    icio=icio,
    nodes = nodes
)
sii = systemic_integration_indices(T_out, T_in)

print(sii["SII_out"])
print(sii["SII_in"])
