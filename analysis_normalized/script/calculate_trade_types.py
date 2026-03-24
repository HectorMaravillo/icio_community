# ===========================================================
# PACKAGES
# ===========================================================
import sys

from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from icio_community import ICIO_Network
from icio_community import export_dictionary

# ===========================================================
# MAIN
# ===========================================================

SAVE_DIR = ROOT / "analysis_normalized" / "results" 

years = range(1995, 2023)
trade = {} 

for year in years:
    print(f"YEAR: {year}")
    icio = ICIO_Network(year,
                        normalize = False,
                        by_output = False,
                        RoW = False,
                        diagonal = True,
                        diagonal_country = True)
    trade["year"] = year
    trade["total"] = icio.matrix.sum().sum()
    trade_values = icio.calculate_trade_types()
    del icio
    trade["trade_I"] = trade_values[0]
    trade["trade_II"] = trade_values[1]
    trade["trade_III"] = trade_values[2]
    trade["trade_IV"] = trade_values[3]
    export_dictionary(trade, SAVE_DIR / "TradeTypes")