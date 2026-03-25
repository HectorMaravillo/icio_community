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
# CONFIG CONSTANTS
# ===========================================================

# -----------------
# Paths
BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "results"
IMAGES_DIR = BASE_DIR / "images"
NAME_FILE = "TradeTypes"

NAME_SAVE_LINEGRAPH = "TipoComercio.png"
NAME_SAVE_STACKGRAPH = "Comercio_InternoExterno.png"

# -----------------
# General display settings
FIGSIZE_LINEGRAPH  = (12, 12)
FIGSIZE_STACKGRAPH =  (12, 4)
# Figure export settings
DPI  = 150

# Base font sizes
FONTSIZE = 14
FONTSIZE_LABELS = FONTSIZE
FONTSIZE_LEGEND = FONTSIZE - 3
FONTSIZE_LEGEND_TITLE = FONTSIZE - 2
FONTSIZE_ANNOTATE = FONTSIZE - 4
FONTSIZE_TICKS = FONTSIZE - 4

# Visualization styles
MARGINS = {
    "left": 0.08,
    "right": 0.88,
    "bottom": 0.12,
    "top": 0.95,
    }
GRID_STYLE = {
    "visible": True,
    "which": "both",
    "axis": "both",
    "linestyle": "--",
    "linewidth": 0.5,
    "alpha": 0.8,
    }

# Vertical reference lines
HIGHLIGHT_YEARS  = [1995, 2001, 2008, 2016, 2020]
BASE_YEARS  = [1995, 2000, 2005, 2010, 2015, 2020]
HIGHLIGHT_YEAR_STYLE  = {
    "linestyle": ":",
    "linewidth": 1.5,
    "color": "red",
    "alpha": 0.8
    }
BASE_YEAR_STYLE  = {
    "linestyle": "--",
    "linewidth": 0.6,
    "color": "gray"
    }

# Annotation Styles
BBOX_STYLE  = dict(
    boxstyle='round,pad=0.3',
    fc="salmon", 
    ec='black', 
    alpha=0.7,
    linewidth=1.2
    )
ANNOTATE_TEXT_STYLE = dict(
    fontsize = FONTSIZE_ANNOTATE,
    ha = "center",
    va = "top",
    )
ARROW_STYLE = dict(
    arrowstyle='->', 
    color='red', 
    lw=1
    )

# Stack Styles
STACK_COLORS = ["#A5C9EB", "#F7B673"]

# Series to plot: data column, label, color and y-axis range
SERIES_CONFIG = [
    {"col": "%III", "label": "Tipo III: Insumo-producto nacional", "color": "darkred", "ymin": 65, "yrange": 7},
    {"col": "%IV", "label": "Tipo IV: Autoconsumo industrial", "color": "purple", "ymin": 16, "yrange": 6},
    {"col": "%I", "label": "Tipo I: Inter-Industria (internacional)", "color": "green", "ymin": 8, "yrange": 6},
    {"col": "%II", "label": "Tipo II: Intra-Industria (internacional)", "color": "darkturquoise", "ymin": 0, "yrange": 6},
    ]



# ===========================================================
# FUNCTIONS
# ===========================================================
def compute_shares(df):
    """
   Compute trade-type shares as percentages of total trade 
   and  aggregate measures (%Internacional, %Interno).
   """
    df = df.copy()
    # Individual trade-type shares
    df["%I"] = 100 * df["trade_I"] / df["total"]
    df["%II"] = 100 * df["trade_II"] / df["total"]
    df["%III"] = 100 * df["trade_III"] / df["total"]
    df["%IV"] = 100 * df["trade_IV"] / df["total"]
    # Aggregate trade shares
    df["%Internacional"] = 100 * (df["trade_I"] + df["trade_II"]) / df["total"]
    df["%Interno"] = 100 * (df["trade_III"] + df["trade_IV"]) / df["total"]
    return df

def add_reference_lines(ax):
    """
   Add vertical reference lines to a subplot.
   """
    for year in HIGHLIGHT_YEARS:
        ax.axvline(x=year, **HIGHLIGHT_YEAR_STYLE)
    for year in BASE_YEARS:
        ax.axvline(x=year, **BASE_YEAR_STYLE)

def format_axis(ax, x_ticks, x_ticks_minor):
    """
    Apply common axis formatting to a subplot: 
        grid display, major and minor x-axis ticks, legend placement,
        spine visibility, and drawing gridlines
    """
    # Add background grid
    ax.grid(**GRID_STYLE)
    # Set major and minor ticks on the x-axis
    ax.set_xticks(list(x_ticks))
    ax.set_xticks(list(x_ticks_minor), minor = True)
    ax.tick_params(axis='both', labelsize = FONTSIZE_TICKS)
    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Draw gridlines below lines and markers
    ax.set_axisbelow(True)
    
def add_event_annotation(ax, event):
    """
    Add a event annotation to a subplot.
    """
    # Select reference point based
    y_min, y_max = ax.get_ylim()
    y_ref = y_min if event["anchor"] == "bottom" else y_max
    # Add annotation box 
    ax.annotate(event["text"],
                xy = (event["x"], y_ref + event["y_offset_point"]),
                xytext = (event["x_text"], y_ref + event["y_offset_text"]),
                textcoords = 'data',
                arrowprops = ARROW_STYLE,
                bbox = BBOX_STYLE,
                **ANNOTATE_TEXT_STYLE
                )  

# ===========================================================
# MAIN
# ===========================================================
# Leer archivo CSV
df = pd.read_csv(RESULTS_DIR / f"{NAME_FILE}.csv")
df = compute_shares(df)

# ===========================================================
# DRAW LINE GRAPH
# ===========================================================
# Define x-axis
x_ticks = range(df["year"].min(), df["year"].max() + 1, 5)
x_ticks_minor = range(df["year"].min(), df["year"].max() + 1)
xlim = [1994.4, 2022.6]
# Define shared axis labels
xlabel = "Año" # "Year"
ylabel = "Porcentaje del comercio intermedio global" #"% of Total Global Intermediate Trade"

# Define percentage formatter for y-axis labels
y_label_format = FuncFormatter(lambda y, _: f'{y:.0f}%')

# Define event annotations
events_lines = [
    {
     "ax_index": 2,
     "text": f"2016: Comunidad\nEconómica\nde la ASEAN",
     "x": 2016,
     "x_text": 2013,
     "anchor": "top",
     "y_offset_point": - 0.5,
     "y_offset_text": - 1.25
    },
    {
     "ax_index": 0,
     "text": f"2001: Ingreso de China\na la OMC",
     "x": 2001,
     "x_text": 1998,
     "anchor": "bottom",
     "y_offset_point": 0.4,
     "y_offset_text": 2
    }
]

# -----------------
# Create figure and subplots
fig, axes = plt.subplots(4, figsize = FIGSIZE_LINEGRAPH, sharex = True)

for ax, cfg in zip(axes, SERIES_CONFIG):
    # Add vertical lines
    add_reference_lines(ax)
    # Draw data
    ax.plot(df["year"],
               df[cfg["col"]],
               label = cfg["label"],
               color = cfg["color"],
               marker = 'o',
               markersize = 7)
    # Add legend
    ax.legend(fontsize = FONTSIZE_LEGEND,
              loc = 'lower right',
              bbox_to_anchor = (1, -0.01))
    # Set format axis
    format_axis(ax, x_ticks, x_ticks_minor)
    # Set limits
    ax.set_xlim(xlim)
    ax.set_ylim([cfg["ymin"], cfg["ymin"] + cfg["yrange"]])
    ax.yaxis.set_major_formatter(y_label_format)
# Add event annotations
for event in events_lines:
    add_event_annotation(axes[event["ax_index"]], event)

# Adjust figure layout
# Add shared axis labels
fig.supxlabel(xlabel, fontsize=FONTSIZE_LABELS,  y=0.07)
fig.supylabel(ylabel, fontsize=FONTSIZE_LABELS)
# Adjust subplot layout
fig.subplots_adjust(**MARGINS)
plt.savefig(IMAGES_DIR / NAME_SAVE_LINEGRAPH, dpi=DPI)
plt.show()

# ===========================================================
# DRAW STACK GRAPH
# ===========================================================
# Define x-axis
xlim = [1994.85, 2022.15]
ylim_int = (10, 16)
ylim_nac = (100 - ylim_int[1], 100 - ylim_int[0])
    
ylabel_l = "Comercio internacional (%)" #"% of Total Global Intermediate Trade"
ylabel_r = "Comercio nacional (%)"

legend_stack = [
    Patch(facecolor=STACK_COLORS[1], label="Nacional"),
    Patch(facecolor=STACK_COLORS[0], label="Internacional")
]


events_stack = [
    {
        "text": "1995: Creación de\nla OMC",
        "x": 1995,
        "x_text": 1998,
        "anchor": "top",
        "y_offset_point": -0.5,
        "y_offset_text": -1.25,
    },
    {
        "text": "2020: Pandemia\nde COVID-19",
        "x": 2020,
        "x_text": 2018,
        "anchor": "bottom",
        "y_offset_point": 0.3,
        "y_offset_text": 1.2,
    },
    {
        "text": "2008: Crisis financiera\nglobal",
        "x": 2008,
        "x_text": 2005,
        "anchor": "bottom",
        "y_offset_point": 0.5,
        "y_offset_text": 1.5,
    }
]


# -----------------
# Create figure and main axis
fig, ax = plt.subplots(figsize=FIGSIZE_STACKGRAPH)

# Add vertical reference lines
add_reference_lines(ax)

ax.stackplot(
        df["year"],
        df["%Internacional"],
        df["%Interno"],
        labels=["Internacional", "Nacional"],
        colors=STACK_COLORS,
        alpha=0.5,
    )
# Add legend
ax.legend(handles = legend_stack,
          fontsize = FONTSIZE_LEGEND,
          title_fontsize = FONTSIZE_LEGEND_TITLE,
          frameon=True,
          loc = 'upper right',
          title="Comercio intermedio",
          bbox_to_anchor = (0.965, 1))

format_axis(ax, x_ticks, x_ticks_minor)
ax.set_xlim(xlim)
ax.set_ylim(ylim_int)
ax.yaxis.set_major_formatter(y_label_format)

ax.plot(df["year"],
        df["%Internacional"],
        color="black", marker='o', markersize=5,
        alpha=0.5, linewidth=2)

for event in events_stack:
    add_event_annotation(ax, event)
    
# Create  secondary y-axis
ax_right = ax.twinx()
ax_right.set_ylim(ylim_nac)  
ax_right.yaxis.set_major_formatter(y_label_format)
ax_right.spines['top'].set_visible(False)
ax_right.tick_params(axis='y', labelsize=FONTSIZE_TICKS)
ax_right.set_ylabel(ylabel_r, fontsize=FONTSIZE_LABELS)

# Adjust figure layout
# Add shared axis labels
ax.set_xlabel(xlabel, fontsize=FONTSIZE_LABELS)
ax.set_ylabel(ylabel_l, fontsize=FONTSIZE_LABELS, y = 0.53)
# Adjust subplot layout
fig.subplots_adjust(**MARGINS)
plt.savefig(IMAGES_DIR / NAME_SAVE_STACKGRAPH, dpi=DPI)
plt.show()
