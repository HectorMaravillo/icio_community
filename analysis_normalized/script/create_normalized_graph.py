# ===========================================================
# PACKAGES
# ===========================================================
import sys
import pickle

from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from icio_community import ICIO_Network


# ===========================================================
# MAIN
# ===========================================================

SAVE_DIR = ROOT / "analysis_normalized" / "networks"

years = range(1995, 2023)
icio = {}

for year in years:
    print(f"YEAR: {year}")
    icio[year] = ICIO_Network(year,
                              normalize = True, # NORMALIZED
                              by_output = False,
                              RoW = False,
                              diagonal = True,
                              diagonal_country = True)
    # SAVE FULL NETWORK IN .PKL FILE
    with open(SAVE_DIR / f"g_{year}.pkl", "wb") as f:
        pickle.dump(icio[year].g, f)
