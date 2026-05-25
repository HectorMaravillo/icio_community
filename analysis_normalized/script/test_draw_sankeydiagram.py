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

COUNTRY_GROUPS = {
    "asean": ["IDN","MYS","PHL","SGP","THA","VNM","KHM","LAO","MMR","BRN"],
    "asia": ["CHN","HKG","VNM","KHM", "MYS","PHL","SGP","THA","LAO", "TWN","IDN", "BRN","MMR",
             "BGD","PAK","JPN","KOR","SAU", "ARE", "IND"],
    "north_america": ["CAN", "USA","MEX"],
    "south_america": ["BRA","ARG","CHL","PER", "COL","CRI"],
    "africa_subsaharan": ["CMR","CIV","SEN","NGA","COD","ZAF", "STP","AGO"],
    "europe_deu": [
        "DEU", "AUT",  "HRV", "SVN", "HUN", "CZE", "SVK",  "POL",
        "ROU"
        ],
    "rusia": ["BGR", "TUR", "GRC", "CYP", "KAZ", "BLR",  "RUS", "UKR", "LTU", "LVA"],
    "baltic": ["DNK", "FIN", "NOR", "SWE", "ISL","EST",  "LTU", "LVA"],
    "france": ["MAR", "FRA", "TUN", "ESP", "PRT"]
}


# ===========================================================
# CONFIGURATION
# ===========================================================
# -----------------
# Paths
BASE_DIR = ROOT / "analysis_normalized"
COMMUNITIES_DIR = BASE_DIR / "results" / "communities"
SAVE_DIR = BASE_DIR / "sankey_diagrams"

LINK_WIDTH = 0.1

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
        save = False,
        path_save = None,
        save_name = None,
    ):
    if save:
        if path_save is None or save_name is None:
            raise ValueError("Falta ruta o nombre para guardar imágenes")
    
    
    
    if years is None:
        years = list(df.columns)

    # --------------------------------------------------
    # Transformación de datos
    # --------------------------------------------------
    # Convier DataFrame de formato ancho a formato largo
    long = (
        df.reset_index()
          .melt(
              id_vars=["country", "activity"],
              var_name="year",
              value_name="group"
          )
    )
    
    # Identificador único por combinación país-actividad
    long["unit"] = (
        long["country"].astype(str)
        + " | "
        + long["activity"].astype(str)
    )
    # Renombrar claves de actividad por nombres
    long["activity"] = (
        long["activity"].map(activities_names)
        + " (" +  long["activity"] + ")"
    )

    # --------------------------------------------------
    # Construcción de nodos
    # --------------------------------------------------
    node_labels = []
    node_keys = []
    node_colors = []

    # Nodos iniciales: países
    for country in sorted(long["country"].unique()):
        node_keys.append(("country", country))
        node_labels.append(countries_names[country]+f" ({country})")
        node_colors.append(colors[country])
    
    # Nodos por cada año y grupo
    for year in years:
        values = long.loc[long["year"] == year, "group"].dropna().unique()
        for value in values:
            node_keys.append((year, value))
            node_labels.append(str(value))
            node_colors.append(colors[value])

    # Diccionario para mapear cada nodo a un ID numérico
    node_id = {key: i for i, key in enumerate(node_keys)}

    links = []
    
    # --------------------------------------------------
    # Primer conjunto de enlaces:
    # país -> grupo del primer año
    # --------------------------------------------------
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
    # Etiquetas auxiliares para hover
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
        
    # --------------------------------------------------
    # Construcción de transiciones entre años consecutivos
    # --------------------------------------------------
    wide = (
        long.pivot_table(
            index=["unit", "country", "activity"],
            columns="year",
            values="group",
            aggfunc="first"
        )
        .reset_index()
    )

    # Crear enlaces entre y0 -> y1
    for y0, y1 in zip(years[:-1], years[1:]):
    
        link_df = (
            wide[["country", "activity", y0, y1]]
            .dropna()
            .copy()
            )
    
        link_df["value"] = LINK_WIDTH
        # Nodo origen
        link_df["source"] = link_df[y0].map(
            lambda g: node_id[(y0, g)]
            )
        # Nodo destino
        link_df["target"] = link_df[y1].map(
            lambda g: node_id[(y1, g)]
            )
        # Labels para hover
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
    # Ordenar enlaces
    link_df = link_df.sort_values(
        ["country", "source_label", "target_label"]
    )
    # Unir todos los enlaces en un solo dataframe
    links = pd.concat(links, ignore_index=True)
    links["color"] = links["country"].map(
        lambda x: hex_to_rgba(colors[x])
    )
    # Reemplazar códigos de país por nombres
    links["country"] = links["country"].map(countries_names)
    # Información personalizada para tooltips
    links["customdata"] = links[
        ["country", "activity", "source_label", "target_label"]
    ].values.tolist()
    
    # --------------------------------------------------
    # Posicionamiento horizontal de nodos
    # --------------------------------------------------
    node_x = []
    node_y = []
    
    # +1 porque existe una columna inicial para country
    n_levels = len(years) + 1  
    left_margin = 0.25
    
    # Posición de nodos de países
    for _ in long["country"].unique():
        node_x.append(0.0)
        node_y.append(None)
    
    # Posición de nodos por año
    for i, year in enumerate(years):
        values = long.loc[long["year"] == year, "group"].dropna().unique()
    
        x = (i + 1) / (n_levels - 1)
    
        for _ in values:
            node_x.append(x)
            node_y.append(None)
            
    # --------------------------------------------------
    # Construcción de diagrama Sankey
    # --------------------------------------------------      
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                # Configuración de nodos
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
                
                # Configuración de enlaces
                link=dict(
                    source=links["source"],
                    target=links["target"],
                    value=links["value"],
                    color="rgba(120,120,120,0.1)",
#                    color=links["color"],
                    customdata=links["customdata"],
                    # Tooltip personalizado
                    hovercolor=links["color"],
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
    # --------------------------------------------------
    # Etiquetas superiores por año
    # -------------------------------------------------- 
    for i, year in enumerate(years):
        x = (i + 1) / (n_levels - 1)
        
        fig.add_annotation(
            x=x,
            y=1.08,
            xref="paper",
            yref="paper",
            text=f"<b>{str(year).upper()}</b>",
            showarrow=False,
            font=dict(size=14)
        )
    fig.update_layout(
        width=2000,
        height=900
    )
    if save:
        # Plotly config for output behavio
        config = {'scrollZoom': True, 
                  'responsive': False,
                  'displayModeBar': True,
                  'modeBarButtonsToRemove': ['select2d', 'lasso2d']}
        print("Saving ... ", save_name)
        fig.write_html(
            path_save / f"{save_name}.html",
            config=config
            )
    else:
        fig.show()

#%%

years = range(1995, 2023)
countries_sel = COUNTRY_GROUPS["asean"]
df = membership_by_year.loc[countries_sel]
sankey_membership_by_year(
    df,
    years,
    True,
    SAVE_DIR,
    "asean_all")

#%%
#countries_sel = ["IDN","MYS","PHL","SGP","THA","VNM","KHM","LAO","MMR","BRN", "TWN","HKG"]
years = (1995, 2000, 2005, 2010, 2015, 2020, 2022)
countries_sel = COUNTRY_GROUPS["baltic"]
df = membership_by_year.loc[countries_sel]
sankey_membership_by_year(
    df,
    years,
    True,
    SAVE_DIR,
    "baltic")


#%%
for name, values in COUNTRY_GROUPS.items():
    countries_sel = values
    df = membership_by_year.loc[countries_sel]
    sankey_membership_by_year(
        df,
        years,
        True,
        SAVE_DIR,
        name)
    