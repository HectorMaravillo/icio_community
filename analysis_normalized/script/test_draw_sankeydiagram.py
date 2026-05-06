# ===========================================================
# PACKAGES
# ===========================================================
import sys
import pandas as pd

from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    
from icio_community import create_colors, activities_names, countries_names
# ===========================================================
# CONFIGURATION
# ===========================================================
# -----------------
# Paths
BASE_DIR = ROOT / "analysis_normalized"
COMMUNITIES_DIR = BASE_DIR / "results" / "communities"

LINK_WIDTH = 0.2

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

colors = create_colors()
colors = {
    k: '#%02x%02x%02x' % tuple(
        int(x * 255) for x in v
    )
    for k, v in colors.items()
}

#%%%
import pandas as pd
import plotly.graph_objects as go

import plotly.io as pio

pio.renderers.default = "browser"
def hex_to_rgba(hex_color, alpha=0.15):
    hex_color = hex_color.lstrip("#")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return f"rgba({r},{g},{b},{alpha})"


def sankey_membership_by_year(
    df,
    years = None,
    title="Membership by year"
):
    if years is None:
        years = list(df.columns)

    # Pasamos el MultiIndex a columnas
    long = (
        df.reset_index()
          .melt(
              id_vars=["country", "activity"],
              var_name="year",
              value_name="group"
          )
    )

    # Nos quedamos con una trayectoria por country.
    # Si tienes varias activities por country, aquí hay que decidir cómo agregarlas.
    # Esta versión conserva activity como parte de la unidad de flujo.
    long["unit"] = (
        long["country"].astype(str)
        + " | "
        + long["activity"].astype(str)
    )
    long["activity"] = long["activity"].map(activities_names) + " (" +  long["activity"] + ")"

    # Nodos: país inicial + grupo por año
    node_labels = []
    node_keys = []
    node_colors = []

    for country in long["country"].unique():
        node_keys.append(("country", country))
        node_labels.append(countries_names[country])
        node_colors.append(colors[country])

    for year in years:
        values = long.loc[long["year"] == year, "group"].dropna().unique()
        for value in values:
            node_keys.append((year, value))
            node_labels.append(str(value))
            node_colors.append(colors[value])

    node_id = {key: i for i, key in enumerate(node_keys)}

    links = []
    
    # Primer salto: country inicial -> grupo del primer año
    first_year = years[0]
    tmp = long[long["year"] == first_year].dropna(subset=["group"])

    first_links = tmp[["country", "activity", "group"]].copy()
    
    first_links["value"] = LINK_WIDTH
    
    first_links["source"] = first_links["country"].map(
        lambda c: node_id[("country", c)]
    )
    
    first_links["target"] = first_links["group"].map(
        lambda g: node_id[(first_year, g)]
    )
    
    first_links["source_label"] = first_links["country"]
    first_links["target_label"] = first_links["group"]

    links.append(
        first_links[
            [
                "source",
                "target",
                "value",
                "country",
                "activity",
                "source_label",
                "target_label"
            ]
        ]
    )
        
    # Saltos entre años consecutivos
    wide = (
        long.pivot_table(
            index=["unit", "country", "activity"],
            columns="year",
            values="group",
            aggfunc="first"
        )
        .reset_index()
    )

    for y0, y1 in zip(years[:-1], years[1:]):
    
        link_df = (
            wide[["country", "activity", y0, y1]]
            .dropna()
            .copy()
        )
    
        link_df["value"] = LINK_WIDTH
    
        link_df["source"] = link_df[y0].map(
            lambda g: node_id[(y0, g)]
        )
    
        link_df["target"] = link_df[y1].map(
            lambda g: node_id[(y1, g)]
        )
    
        link_df["source_label"] = link_df[y0]
        link_df["target_label"] = link_df[y1]
    
        links.append(
            link_df[
                [
                    "source",
                    "target",
                    "value",
                    "country",
                    "activity",
                    "source_label",
                    "target_label"
                ]
            ]
        )
    link_df = link_df.sort_values(
        ["source_label", "target_label"]
    )
    links = pd.concat(links, ignore_index=True)
    links["country"] = links["country"].map(countries_names)
    links["customdata"] = links[
        ["country", "activity", "source_label", "target_label"]
    ].values.tolist()
    node_x = []
    node_y = []
    
    n_levels = len(years) + 1  # +1 por columna inicial country
    
    # columna inicial
    for _ in long["country"].unique():
        node_x.append(0.0)
        node_y.append(None)
    
    # columnas de años
    for i, year in enumerate(years):
        values = long.loc[long["year"] == year, "group"].dropna().unique()
    
        x = (i + 1) / (n_levels - 1)
    
        for _ in values:
            node_x.append(x)
            node_y.append(None)
            
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=10,
                    x = node_x,
                    y = node_y,
                    thickness=15,
                    line=dict(width=0.5),
                    label=node_labels,
                    color=node_colors,
                    hovertemplate="%{label}<extra></extra>"
                ),
                link=dict(
                    source=links["source"],
                    target=links["target"],
                    value=links["value"],
                    color="rgba(120,120,120,0.15)",
                    customdata=links["customdata"],
                    hovertemplate=(
                        "Country: %{customdata[0]}<br>"
                        "Activity: %{customdata[1]}<br>"
                        "Source: %{customdata[2]}<br>"
                        "Target: %{customdata[3]}<br>"
                        "<extra></extra>"
                    )
                ),
            )
        ]
    )
    for i, year in enumerate(years):
        x = (i + 1) / (n_levels - 1)
    
        fig.add_annotation(
            x=x,
            y=1.08,
            xref="paper",
            yref="paper",
            text=str(year),
            showarrow=False,
            font=dict(size=14)
        )

    fig.update_layout(
        title_text=title,
        font_size=11,
        height=900,
        width=1400,
    )

    return fig
#%%
#countries_sel = ["IDN","MYS","PHL","SGP","THA","VNM","KHM","LAO","MMR","BRN", "TWN","HKG"]
countries_sel =  ["CHN","HKG","VNM","KHM", "MYS","PHL","SGP","THA","LAO", "TWN","IDN", "BRN","MMR",
         "BGD","PAK","JPN","KOR","SAU", "ARE", "IND"]
if countries_sel is not None:
    df = membership_by_year.loc[countries_sel]
else:
    df = membership_by_year
years = (1995, 2000, 2005, 2010, 2015, 2020, 2022)
#years = tuple(range(1995, 2023, 5))
fig = sankey_membership_by_year(df, years)
fig.show()