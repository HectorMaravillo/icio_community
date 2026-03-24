# ===========================================================
# PACKAGES
# ===========================================================
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MultipleLocator

# ===========================================================
# VARIABLES
# ===========================================================

BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "results"
#SAVE_DIR = BASE_DIR / "images" 
NAME_FILE = "TradeTypes"

# Visualization variables
figsize_1 = (12, 12)
figsize_2 = (12, 4)
dpi = 150

left = 0.08
right = 0.88
bottom = 0.12
top = 0.95


# ===========================================================
# MAIN
# ===========================================================
# Leer archivo CSV
df = pd.read_csv(RESULTS_DIR / f"{NAME_FILE}.csv")

# Calcular porcentajes respecto al total
df["%I"] = 100 * df["trade_I"] / df["total"]
df["%II"] = 100 * df["trade_II"] / df["total"]
df["%III"] = 100 * df["trade_III"] / df["total"]
df["%IV"] = 100 * df["trade_IV"] / df["total"]

df["%Internacional"] = 100 * (df["trade_I"] + df["trade_II"]) / df["total"]
df["%Interno"] = 100 * (df["trade_III"] + df["trade_IV"]) / df["total"]

