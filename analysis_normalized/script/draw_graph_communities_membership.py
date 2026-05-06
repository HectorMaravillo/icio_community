# ===========================================================
# PACKAGES
# ===========================================================
import sys
import textwrap
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.ticker import MultipleLocator
from numpy import ceil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from icio_community import create_colors, countries_names
countries_names["Otros"] = "Otros"
countries_names["BRN"] = "Brunei"
countries_names["CHN"]  = "China"
countries_names["COD"] = "Congo (RDC)"
countries_names["GBR"] = "UK"
countries_names["LAO"] = "Laos"
countries_names["TWN"] = "Taiwan"
countries_names["USA"] = "USA"
countries_names["RUS"] = "Rusia"
countries_names["STP"] = "Saõ Tomé\nand Príncipe"


# ===========================================================
# CONFIGURATION
# ===========================================================
# -----------------
# Paths
BASE_DIR = ROOT / "analysis_normalized"
COMMUNITIES_DIR = BASE_DIR / "results" / "communities"
IMAGES_DIR = BASE_DIR / "images" / "communities_membership"

# -----------------
# General display settings
FIGSIZE_X = 16
DPI  = 150

# Base font sizes
FONTSIZE = 14
FONTSIZE_LABELS = FONTSIZE
FONTSIZE_LEGEND = FONTSIZE - 3
FONTSIZE_LEGEND_TITLE = FONTSIZE - 2
FONTSIZE_TICKS = FONTSIZE - 4
FONTSIZE_FOOTNOTE = FONTSIZE - 6

# Visualization styles
GRID_STYLE = {
    "visible": True,
    "which": "both",
    "axis": "y",
    "linestyle": "--",
    "linewidth": 0.5,
    "alpha": 0.8,
    }
WIDTH_BARS = 0.7
COLORS = create_colors()
COLORS["Otros"] = (0.1, 0.1, 0.1)  

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
    ax.grid(**{**GRID_STYLE, "which": "major"})
    ax.grid(**{**GRID_STYLE, "which": "minor", "axis": "y", "alpha": 0.1})
    ax.tick_params(axis='both', labelsize = FONTSIZE_TICKS)
    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Draw gridlines below lines and markers
    ax.set_axisbelow(True)

# ===========================================================
# MAIN
# ===========================================================
# Read and stack communities dataframe
aux = []
for file in COMMUNITIES_DIR.glob("*.csv"):
    df = pd.read_csv(file, 
                     header = 0, index_col=0) 
    stack = df.stack(future_stack=True)
    stack.name = int(file.stem[:4])
    aux.append(stack)
    
# Create a dataframe of community membership by year
membership_by_year = pd.concat(aux, axis=1)
membership_by_year.index.names = ["country", "activity"]
membership_by_year.columns.name = "year"
#%%%

# ===========================================================
# DRAW  GRAPH
# ===========================================================
# Define x-axis and y-axis parameters
years = membership_by_year.columns
x_ticks = range(years[0], years[-1], 5)
x_ticks_minor = range(years[0], years[-1])
xlabel = "Año" # "Year"
ylabel = "Número de nodos"


def draw_community_membership(community, threshold=10):
    # Build a timeline counting occurrences per country and year
    timeline = (
        membership_by_year
        .eq(community)             # True where the cell matches the selected community
        .groupby(level="country")  # group by the first index level (country)
        .sum()                     # count occurrences per country and year
        .loc[lambda df: (df != 0).any(axis=1)] # keep only countries with at least one occurrence
    )
    
    # Compute total counts per year
    total = timeline.sum(axis=0)
    max_tot = max(total)
    
    # Identify countries with totals below the threshold
    small_mask = timeline.sum(axis=1) < threshold
    # List of countries grouped into "Others"
    small_contributors =  timeline.index[small_mask].tolist()
    small_contributors = [countries_names[l] for l in small_contributors]
    if len(small_contributors) > 0:
        # Separate large contributors
        large = timeline.loc[~small_mask]
        # Aggregate small contributors into a single "Others" categor
        # Combine large contributors with the aggregated "Others"
        others = timeline.loc[small_mask].sum(axis=0).to_frame(name="Otros").T
        timeline = pd.concat([large, others])
    # Re-sort after aggregation
    timeline = timeline.loc[
        timeline.sum(axis=1).sort_values(ascending=False).index
    ]
    
    # Assign colors based on country
    colors_sel = [COLORS[country] for country in timeline.index]
    
    # Create stacked bar chart
    figsize_y = ceil(max_tot / 50) + 1
    fig, ax = plt.subplots(figsize=(FIGSIZE_X, figsize_y),
                           constrained_layout=True)
    timeline.T.plot(
        ax = ax,
        kind = "bar",
        stacked = True,
        width = WIDTH_BARS,
        color = colors_sel,
        edgecolor="black",  
        linewidth=0.1
    )
    # Add total labels on top of each bar
    for i, t in enumerate(total):
        if t>0:
            ax.text(i, t, str(int(t)), ha='center', va='bottom')
    # Configure legend
    handles, labels = ax.get_legend_handles_labels()
    labels = [countries_names[l] for l in labels]
    ax.legend(
        handles,
        labels,
        fontsize = FONTSIZE_LEGEND,
        loc = 'upper right',
        bbox_to_anchor = (1.12, 1),
        borderaxespad=0,
        frameon=True,
        title="País",
        title_fontsize = FONTSIZE_LEGEND_TITLE
        )
    # Add footnote with grouped countries
    if len(small_contributors) > 0:
        text = "Otros incluye: " + ", ".join(small_contributors)
        text = textwrap.fill(text, width=80)
        fig.text(
            0.88, -0.01,  # position (centered below figure)
            text,
            ha='right',
            va='bottom',
            fontsize=FONTSIZE_FOOTNOTE
        )
    # Apply custom axis formatting
    format_axis(ax, x_ticks, x_ticks_minor)
    # Configure x-axis ticks (major and minor)
    ax.set_xticks(range(0, len(years), 5))
    ax.set_xticks(range(0, len(years), 1), minor = True)
    ax.set_xticklabels(years[::5], rotation=0)
    
    if max_tot < 150:
        y_lim = (0, max_tot+55)
        ax.set_ylim(y_lim)
    ax.yaxis.set_major_locator(MultipleLocator(50))
    ax.yaxis.set_minor_locator(MultipleLocator(10))
    
    # Set axis labels
    ax.set_xlabel(xlabel, fontsize=FONTSIZE_LABELS)
    ax.set_ylabel(ylabel, fontsize=FONTSIZE_LABELS)
    plt.savefig(IMAGES_DIR / f"{community}.png",
                dpi=DPI,
                bbox_inches="tight")
    plt.show()

communities = membership_by_year.stack().unique()
for community in communities:
    if pd.notna(community):
        print(community)
        draw_community_membership(community, threshold=25)
