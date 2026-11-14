import pandas as pd
import numpy as np


from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
BASE_DIR = ROOT / "analysis_normalized"

SAVE_DIR = BASE_DIR / "results"


# =====================================================
# 1. IMPORTAR DATOS
# =====================================================

df = pd.read_csv(SAVE_DIR / "Modularity_Leiden_Normalizada.csv")
#%%%
# =====================================================
# 2. ESTADÍSTICAS POR AÑO
# Independientemente de la inicialización
# =====================================================

estadisticas_anuales = (
    df.groupby("year", as_index=False)
    .agg(
        max_modularity=("modularity", "max"),
        mean_modularity=("modularity", "mean"),
        std_modularity=("modularity", lambda x: x.std(ddof=0))
    )
)

# =====================================================
# 3. ESTADÍSTICAS POR AÑO E INICIALIZACIÓN
# =====================================================

estadisticas_inicializacion = (
    df.groupby(["year", "initial"])["modularity"]
    .agg(
        max_modularity="max",
        mean_modularity="mean",
        std_modularity=lambda x: x.std(ddof=0)
    )
    .unstack("initial")
    .swaplevel(0, 1, axis=1)
    .sort_index(axis=1, level=0, sort_remaining=False)
)

# =====================================================
# 4. FRECUENCIA DE MÁXIMOS ANUALES
# =====================================================

# Máxima modularidad anual para cada observación
df["max_anual"] = (
    df.groupby("year")["modularity"].transform("max")
)

# Comparación utilizando tolerancia numérica
df["es_max_anual"] = np.isclose(
    df["modularity"],
    df["max_anual"],
    rtol=1e-9,
    atol=1e-12
)

# Contar coincidencias por año e inicialización
frecuencia_maximos = (
    df.groupby(["year", "initial"])["es_max_anual"]
    .agg(frecuencia_max_anual="sum")
    .unstack("initial")
    .swaplevel(0, 1, axis=1)
    .sort_index(axis=1, level=0)
)

frecuencia_maximos_anuales = (
    df.groupby("year")["es_max_anual"]
    .agg(frecuencia_max_anual="sum")
)

porcentaje_maximos_anuales = (
    df.groupby("year")["es_max_anual"]
    .agg(porcentaje_max_anual=lambda x: x.sum() / 90 * 100)
)

# =====================================================
# 6. EXPORTAR RESULTADOS
# =====================================================
"""
SAVE_DIR = ""

# Estadísticas anuales
estadisticas_anuales.to_csv(
    SAVE_DIR / "Estadisticas_Anuales.csv",
    index=False
)

# Estadísticas por año e inicialización
estadisticas_inicializacion.to_csv(
    SAVE_DIR / "Estadisticas_Inicializacion.csv",
    index=True
)

# Frecuencia de máximos por año e inicialización
frecuencia_maximos.to_csv(
    SAVE_DIR / "Frecuencia_Maximos_Inicializacion.csv",
    index=True
)

# Frecuencia de máximos anuales
frecuencia_maximos_anuales.to_csv(
    SAVE_DIR / "Frecuencia_Maximos_Anuales.csv",
    index=True
)

# Porcentaje de máximos anuales
porcentaje_maximos_anuales.to_csv(
    SAVE_DIR / "Porcentaje_Maximos_Anuales.csv",
    index=True
)
"""
# =====================================================
# 7. MOSTRAR RESULTADOS
# =====================================================

print("\n" + "=" * 60)
print("ESTADÍSTICAS ANUALES")
print("=" * 60)
print(estadisticas_anuales.to_string(index=False))

print("\n" + "=" * 60)
print("ESTADÍSTICAS POR AÑO E INICIALIZACIÓN")
print("=" * 60)
print(estadisticas_inicializacion.to_string())

print("\n" + "=" * 60)
print("FRECUENCIA DE MÁXIMOS POR INICIALIZACIÓN")
print("=" * 60)
print(frecuencia_maximos.to_string())

print("\n" + "=" * 60)
print("FRECUENCIA DE MÁXIMOS ANUALES")
print("=" * 60)
print(frecuencia_maximos_anuales.to_string())

print("\n" + "=" * 60)
print("PORCENTAJE DE MÁXIMOS ANUALES")
print("=" * 60)
print(porcentaje_maximos_anuales.to_string())