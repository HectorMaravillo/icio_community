# ===========================================================
# PACKAGES
# ===========================================================
import sys
import pandas as pd

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ===========================================================
# CONFIGURATION
# ===========================================================
BASE_DIR = ROOT / "analysis_normalized"
COMMUNITIES_DIR = BASE_DIR / "communities"


dfs = {}
for file in COMMUNITIES_DIR.glob("*.csv"):
    df = pd.read_csv(file, index_col=0) 
    
    s = df.stack(dropna=False)
    year = file.stem[:4]
    dfs[year] = s
    

resultado = pd.concat(dfs, axis=1)
resultado.index.names = ["country", "year"]