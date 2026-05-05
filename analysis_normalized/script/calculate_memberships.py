# ===========================================================
# PACKAGES
# ===========================================================
import sys
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from icio_community import create_colors

# ===========================================================
# CONFIGURATION
# ===========================================================
BASE_DIR = ROOT / "analysis_normalized"
COMMUNITIES_DIR = BASE_DIR / "communities"

GRID_STYLE = {
    "visible": True,
    "which": "both",
    "axis": "both",
    "linestyle": "--",
    "linewidth": 0.5,
    "alpha": 0.8,
    }
FIGSIZE_STACKGRAPH =  (16, 6)
FONTSIZE = 14
FONTSIZE_LABELS = FONTSIZE
FONTSIZE_LEGEND = FONTSIZE - 3
FONTSIZE_TICKS = FONTSIZE - 4
FONTSIZE_LEGEND_TITLE = FONTSIZE - 2

# ===========================================================
# FUNCTIONS
# ===========================================================
def format_axis(ax, x_ticks, x_ticks_minor):
    """
    Apply common axis formatting to a subplot: 
        grid display, major and minor x-axis ticks, legend placement,
        spine visibility, and drawing gridlines
    """
    # Add background grid
    ax.grid(**GRID_STYLE)
    # Set major and minor ticks on the x-axis
  #  ax.set_xticks(list(x_ticks))
  #  ax.set_xticks(list(x_ticks_minor), minor = True)}
    ax.set_xticks(range(0, len(years), 5))
    ax.set_xticks(range(0, len(years), 1), minor = True)
    ax.set_xticklabels(years[::5], rotation=0)
    ax.tick_params(axis='both', labelsize = FONTSIZE_TICKS)
    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Draw gridlines below lines and markers
    ax.set_axisbelow(True)


aux = []
for file in COMMUNITIES_DIR.glob("*.csv"):
    df = pd.read_csv(file, index_col=0) 
    
    stack = df.stack(future_stack=True)
    stack.name = file.stem[:4]
    aux.append(stack)
    
membership_by_year = pd.concat(aux, axis=1)
membership_by_year.index.names = ["country", "activity"]
membership_by_year.columns.name = "year"

years = [int(year) for year in membership_by_year.columns]
membership_by_year.columns = years

#%%%
x_ticks = range(years[0], years[-1], 5)
x_ticks_minor = range(years[0], years[-1])
xlabel = "Año" # "Year"
ylabel = "Número de actividades por país"

colors = create_colors()
colors["Otros"] = (0.1, 0.1, 0.1)  

country_sel = "AUS"
timeline = (
    membership_by_year
    .eq(country_sel)                  # True donde la celda es ESP
    .groupby(level="country")   # agrupa por primer nivel del índice
    .sum()                      # cuenta actividades por país y año
    .loc[lambda df: (df != 0).any(axis=1)]
    .loc[lambda df: df.sum(axis=1).sort_values(ascending=False).index]
)
total = timeline.sum(axis=0)

# países cuyo total individual es menor a threshold
threshold = 20
small_mask = timeline.sum(axis=1) < threshold
large = timeline.loc[~small_mask]
others = timeline.loc[small_mask].sum(axis=0).to_frame(name="Otros").T
timeline = pd.concat([large, others])
# ordenar de mayor a menor
timeline = timeline.loc[
    timeline.sum(axis=1).sort_values(ascending=False).index
]
colors_sel = [colors[country] for country in timeline.index]


fig, ax = plt.subplots(figsize=FIGSIZE_STACKGRAPH)
timeline.T.plot(
    ax = ax,
    kind = "bar",
    stacked = True,
    width = .7,
    color = colors_sel
)
for i, t in enumerate(total):
    ax.text(i, t, str(int(t)), ha='center', va='bottom')
ax.legend(fontsize = FONTSIZE_LEGEND,
          loc = 'upper right',
          bbox_to_anchor = (1.08, .98),
          borderaxespad=0,
          frameon=True,
          title="País",
          title_fontsize = FONTSIZE_LEGEND_TITLE)
format_axis(ax, x_ticks, x_ticks_minor)

ax.set_xlabel(xlabel, fontsize=FONTSIZE_LABELS)
ax.set_ylabel(ylabel, fontsize=FONTSIZE_LABELS)
