import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio

from math import sin, cos
from shapely import Point
from pandas import DataFrame, Series, unique
from geopandas import GeoDataFrame
from plotly.express import scatter_geo
from igraph import Graph
from matplotlib.colors import rgb2hex
from matplotlib.patches import Patch
from seaborn import color_palette, heatmap
from numpy import array, pi, dot, sqrt, nan, percentile

from icio_community.utils import ( 
    countries, 
    countries_names, 
    countries_centers, 
    final_demand_names, 
    activities, 
    activities_names
    )


def create_colors(by = "country", n = 100):
    if by == "country":
        palette = color_palette("tab20", 20)
        palette += color_palette("pastel", 20) 
        palette += color_palette("bright", 20)
        palette += color_palette("deep", 21)
        colors = dict(zip(countries, palette))
    elif by == "activity":
        palette = color_palette("tab20", 17)
        palette += color_palette("bright", 17)
        palette += color_palette("deep", 16)
        colors = dict(zip(activities, palette))
    else:
        palette = color_palette("tab20", n)
        colors = dict(zip(range(n), palette))  
    return colors

def radial_angles(categories: list[str]) -> dict[str, float]:
    """
    Compute evenly spaced angles for a list of categories.

    Parameters
    ----------
    categories : list of str
        List of categories.

    Returns
    -------
    dict of str to float
        Mapping from label to angle in radians.
    """
    n = len(categories)
    rank = array(range(n))
    angles = dict(zip(categories, rank*(2*pi/n)))
    return angles

def position(v_country: str, v_demand: str) -> Point:
    """
    Compute the geographic position of a node based on country and activity.
    
    Parameters
    ----------
    v_country : str
        ISO 3-letter country code.
    v_demand : str
        Activity or final demand label.
    
    Returns
    -------
    shapely.geometry.Point
        The position of the node in longitude-latitude space.
    """
    # Determine the angle of rotation based on the type of activity or demand
    # Use different radii to space out activities and final demand categories
    if v_demand in activities:
        activities_angles = radial_angles(activities)
        angle = activities_angles[v_demand]
        plus = array([0,.5])
    elif v_demand in final_demand_names:
        final_demand_angles = radial_angles(final_demand_names)
        angle = final_demand_angles[v_demand]
        plus = array([0,.1])
    else:
        raise ValueError(f"'{v_demand}' is not a recognized activity name.")
        
    # Construct a 2D rotation matrix to place the node around the country center
    cos_theta = cos(angle)
    sin_theta = sin(angle)
    rotation_m = array([[cos_theta, sin_theta],
                        [-sin_theta, cos_theta]])
    
    # Rotate and translate the point from origin to country center
    v_pos = dot(rotation_m, plus) + countries_centers[v_country]

    return Point(v_pos)

def position_nodes(g: Graph) -> dict[str, Point]:
    """
    Compute geographic positions for all nodes in a graph.

    Parameters
    ----------
    g : igraph.Graph
        Input-output network, whose nodes are labeled as 'COUNTRY_ACTIVITY'.

    Returns
    -------
    dict of str to Point
        Mapping from node name to geographic position.
    """
    nodes = Series(g.vs["name"])
    nodes_split = nodes.str.split('_', n=1, expand=True)
    nodes_split.columns = ['country', 'activity']
    pos =  nodes_split.apply(lambda x: position(x['country'], x['activity']),
                             axis=1)
    return dict(zip(nodes, pos))


def create_gdf_nodes(g: Graph) -> GeoDataFrame:
    """
    Create a data frame with nodes on a circle centered on each country.
    
    Parameters
    ----------
    g : igraph.Graph
        Input-output network.
    
    Returns
    -------
    geopandas.GeoDataFrame
        Nodes in a circular layout centered by country.
    """
    pos = position_nodes(g)
    gdf = GeoDataFrame(DataFrame(pos.keys(), columns=["NAME"]),
                           geometry=list(pos.values()), crs=4326)
    gdf["Country"] = g.vs["country"]
    gdf["Activity"] = g.vs["activity"]
    gdf["Country"] =  gdf["Country"].apply(lambda x: countries_names[x])
    gdf["Activity"] =  gdf["Activity"].apply(lambda x: activities_names[x])
    return gdf

def draw_nodes(g: Graph,
               label: str,
               fig: go.Figure,
               c: str) -> None:
    """
    Add graph nodes to a Plotly figure as geographic scatter points.

    Parameters
    ----------
    g : igraph.Graph
        Input-output network.
    label : str
        Community label associated with the subgraph.
    fig : plotly.graph_objs.Figure
        The base Plotly figure.
    c : str
        Color for the nodes.
        
    Returns
    -------
    None
    """
    print('Adding vertices...')
    # Create a GeoDataFrame with node positions and metadata
    gdf = create_gdf_nodes(g)
    gdf["Community"] = label
    gdf["In_Strength"] = g.vs["In_Strength"]
    gdf["In_Strength"] = gdf["In_Strength"].round(3)
    gdf["Out_Strength"] = g.vs["Out_Strength"]
    gdf["Out_Strength"] = gdf["Out_Strength"].round(3)
    # Create Plotly scatter geo trace for the nodes
    fig_nodes = scatter_geo(
        data_frame=gdf, 
        lat=gdf.geometry.y,
        lon=gdf.geometry.x,
        hover_name="NAME",
        color_discrete_sequence=[c]
        )
    # Customize tooltip and trace metadata for each node
    fig_nodes.update_traces(
        hovertemplate=(
            '<b>%{hovertext}</b><br>'
            'Community: %{customdata[0]}<br>'
            'Country: %{customdata[1]}<br>'
            'Activity: %{customdata[2]}<br>'
            'In_Strength: %{customdata[3]}<br>'
            'Out_Strength: %{customdata[4]}<extra></extra>'
            ),
        customdata=gdf[[
            'Community', 
            'Country', 
            'Activity', 
            'In_Strength', 
            'Out_Strength']].values,
        name = label,
        legendgroup=label,
        showlegend=True,
        visible=True  
    )
    # Add the node trace to the figure
    fig.add_traces(fig_nodes.data)
    
    # Update geographic layout to enhance map appearance
    fig.update_layout(showlegend=True)
    fig.update_geos(showcountries=True,
                    showframe=False,
                    showocean=True,  
                    showcoastlines=True,
                    showlakes=True,
                    showland=True,
                    oceancolor="rgb(145, 213, 255)",
                    landcolor="rgb(250, 250, 250)")
    
def draw_edges(g: Graph,
               fig: go.Figure,
               threshold: float,
               weight_max: float) -> None: 
    """
    Add graph edges as curved lines on a geographic Plotly figure.

    Parameters
    ----------
    g : igraph.Graph
        Input-output network.
    fig : plotly.graph_objs.Figure
        The base Plotly figure.
    threshold : float
        Minimum edge weight to show.
    weight_max : float
        Maximum edge weight used for opacity normalization.
    """
    print('Adding edges...')
    pos = position_nodes(g)
    weights = array(g.es["weight"])
    if weight_max is None:
        weight_max = weights.max()
    if threshold is None:
        threshold = weights.mean()
    # Filter edges with weight above the threshold
    edges = array([e for e in g.es if e["weight"]>=threshold])
    weights = weights[weights>=threshold]
    # Get the names of source and target nodes for the filtered edges
    sources_idx = [g.vs[e.source]["name"] for e in edges]
    targets_idx = [g.vs[e.target]["name"] for e in edges]
    # Compute coordinates for the source and target points
    sources_pos = array([[pos[v].x, pos[v].y] for v in sources_idx])
    targets_pos = array([[pos[u].x, pos[u].y] for u in targets_idx])
    
    color_edges = ["red" if s==t else "black" for s, t in zip(sources_idx, targets_idx)]
    # Plot each edge as a straight line segment
    [ fig.add_trace(
            go.Scattergeo(
                lon = [v[0], u[0]],
                lat = [v[1], u[1]],
                mode = 'lines',
                line = dict(width = 1, color = c),
                opacity = sqrt(w / weight_max), # Softening opacity contrast
                hoverinfo='skip',
                showlegend=False
            )
        ) for v, u, w, c in zip(sources_pos, targets_pos, weights, color_edges)
        #tqdm(zip(sources_pos, targets_pos, weights))
    ]

def draw_subgraph_map(subgraph: Graph,
                      label: str,
                      fig: go.Figure,
                      threshold:float,
                      weight_max: float,
                      color):
    """
    Draw a full ICIO network on a geographic map using Plotly.
    
    Parameters
    ----------
    subgraph : igraph.Graph
        Input-output network.
    label : str
        Community label to assign to the nodes.
    fig : plotly.graph_objs.Figure
        The base Plotly figure.
    c : str
        Color for nodes.
    threshold : float, optional
        Minimum edge weight to show.
    weight_max : float, optional
        Maximum edge weight for opacity normalization.
    
    Returns
    -------
    plotly.graph_objs.Figure
        Plotly figure with the subgraph drawn.
    """
    # Add edges
    draw_edges(subgraph, fig, threshold, weight_max)
    # Add Nodes
    draw_nodes(subgraph, label, fig, color)
    return fig

    
def draw_map(g: Graph,
             year: int,
             communities = None,
             select : list[str] = None,
             path_save: str = None,
             save_name: str = "",
             pct_threshold: float = None,
             projection: str = "natural earth",
             static: bool = False) -> None:
    """
    Create and save an interactive map of the ICIO network.

    Parameters
    ----------
    g : igraph.Graph
        Input-output network graph.
    year : int
        Year of the ICIO table.
    path_save : str, optional
        Directory to save the resulting HTML file.
        If None, the map will open in browser.
    pct_threshold : float, optional
        Minimum edge weight to show..
    projection : {'natural earth', 'orthographic'}, optional
        Type of geographic projection to use:
        - 'natural earth': standard flattened world map.
        - 'orthographic': 3D globe-like view.
        
    Returns
    -------
    None
    """
    print('Creating the map...')
    fig = scatter_geo(projection=projection)

    if communities is not None:
        if select is not None:
            h = communities.g.induced_subgraph(
                communities.g.vs.select(country_in = select)
                )
        # Use maximum edge weight across all communities for opacity normalization
        weights  = array(communities.g.es["weight"])
        weight_max = max(weights)
        threshold = percentile(weights, pct_threshold)

        year = communities.year
        # Get community labels and subgraphs
        labels = communities.labels()
        subgraphs = communities.subgraphs
        if set(labels).issubset(set(countries)):
            colors = create_colors()
        else:
            colors = create_colors(by=None, n=len(labels))
        # Draw each community subgraph with its label
        for i in range(communities.n_subgraphs):
            label = labels[i]
            if label is not None:
                color = rgb2hex(colors[label])
            else:
                color = "grey"
            sub_g = subgraphs[i]
            if select is not None:
                sub_g = sub_g.induced_subgraph(
                    sub_g.vs.select(country_in = select)
                    )
            if sub_g.vcount() > 0:
                fig = draw_subgraph_map(
                    subgraph = sub_g, 
                    label = label, 
                    fig = fig,
                    threshold = threshold,
                    weight_max = weight_max,
                    color=color
                )
        # Title and save name based on year in community object
        title = str(year)
        # Create list of visibility options for buttons
        nodo_traces = [i for i, trace in enumerate(fig.data)
                       if trace.legendgroup in labels]
        visible_all = [True if i in nodo_traces else trace.visible
                       for i, trace in enumerate(fig.data)]
        visible_none = ["legendonly" if i in nodo_traces else trace.visible
                        for i, trace in enumerate(fig.data)]
        # Add toggle button to show/hide node communities
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    showactive=False,
                    x=0.1,
                    y=1.15,
                    buttons=[
                        dict(
                            label="Show nodes",
                            method="update",
                            args=[{"visible": visible_all}]
                        )
                    ]
                ),
                dict(
                    type="buttons",
                    direction="right",
                    showactive=False,
                    x=0.3,
                    y=1.15,
                    buttons=[
                        dict(
                            label="Hide nodes",
                            method="update",
                            args=[{"visible": visible_none}]
                        )
                    ]
                )
            ]
        )
    else:
        # Draw full graph with single label
        h = g.copy()
        if select is not None:
            h = h.induced_subgraph(
                h.vs.select(country_in = select)
                )
        # Use maximum edge weight across all communities for opacity normalization
        weights  = array(g.es["weight"])
        weight_max = max(weights)
        threshold = percentile(weights, pct_threshold)
        fig = draw_subgraph_map(
            subgraph = h, 
            label = None, 
            fig = fig,
            threshold = threshold,
            weight_max = weight_max,
            color="gray"
        )
        title = "ICIO: "+str(year)    
    # Update geographic layout parameters
    fig.update_geos(fitbounds = "locations")
    
    # Add title to the layout
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {
                'size': 20,
                'family': 'Arial Black'
            }
        }
    )
    
    # Plotly config for output behavio
    config = {'scrollZoom': True, 
              'responsive': False,
              'displayModeBar': True,
              'modeBarButtonsToRemove': ['select2d', 'lasso2d']}
    
    # Save or display the figure
    print('Saving the map...')
    if path_save is None:
        pio.renderers.default = "browser"
        fig.show()
    else:
        if static:
            fig.write_image(
                path_save / f"{year}_{save_name}.png",
                format = "png"
                )
        fig.write_html(
            path_save / f"{year}_{save_name}.html",
            config=config
            )

def draw_communities(communities,
                     df: DataFrame,
                     path_save: str = None,
                     save_name: str = "communities",
                     scale: int = 0.4,
                     **kwargs) -> None:
    """
    Draw a heatmap matrix of communities (countries vs. activities).
    
    Parameters
    ----------
    communities : object
        Community detection result.
    df : pandas.DataFrame
        DataFrame of community assignments indexed by country and activity.
    path_save : str, optional
        File path to save the figure. If None, the plot is displayed.
    scale : float, default=0.4
        Scaling factor for figure size.
    
    Returns
    -------
    None
    """       
    unique_values = unique(df.values.ravel())
    unique_values = set(unique_values)-{nan}
    if unique_values.issubset(set(countries)):
        # Assign unique IDs to each country for coloring the heatmap
        countries_id = dict(zip(countries, range(len(countries))))  
        # Convert community names in df to numeric IDs (or -1 if not found)
        df_id = df.map(lambda x: countries_id.get(x, -1))
        colors = create_colors()
    else:
        df_id = df.fillna(-1)
        colors = create_colors(None, len(unique_values))
        
    # Set defaults kwargs
    xlabel = kwargs.get("xlabel", "Activity")
    ylabel = kwargs.get("ylabel", "Country")
    label_title = kwargs.get("label_title", "Community")

    # Create figure with size based on DataFrmae shape
    shape = df.shape
    figsize=(scale * shape[1],
             scale * shape[0])
    fig, ax = plt.subplots(figsize=figsize)
    
    # Draw base heatmap
    heatmap(df_id, ax=ax, annot=False,
            cbar =False, mask = df_id<-0.5)
    
    # For each non-masked cell, assing label and color community
    for i in df_id.columns:
        for j in df_id.index:
            if df_id[i][j] >=0:
                col = df.columns.get_loc(i)
                row = df.index.get_loc(j)
                ax.annotate(df[i][j], (col+.5, row+.5),
                            ha='center', va='center',
                            fontsize=9)
                ax.add_patch(plt.Rectangle((col, row), 1, 1, 
                                           color=colors[df[i][j]]))
                
    
    # Highlight the strongest nodes (strength-in and strength-out)
    strongest = communities.strongest()
    for cell in strongest:
        # Strenght-in
        row_in, col_in = cell[0].split('_', 1)
        if row_in in df.index and col_in in df.columns:
            row_in = df_id.index.get_loc(row_in)
            col_in = df_id.columns.get_loc(col_in)
            patch_in = plt.Rectangle((col_in+.1, row_in+.1), 
                                  0.8, 0.8,
                                  fill=False,
                                  edgecolor="yellow",
                                  lw=3)
            ax.add_patch(patch_in)
        # Strenght-out
        row_out, col_out = cell[1].split('_', 1)
        if row_out in df.index and col_out in df.columns:
            row_out = df_id.index.get_loc(row_out)
            col_out = df_id.columns.get_loc(col_out)
            patch_out = plt.Rectangle((col_out, row_out), 
                                  1, 1,
                                  fill=False,
                                  edgecolor="black",
                                  lw=3)
            ax.add_patch(patch_out)
    
    # Set axis titles and format ticks
    ax.set_title(communities.year, fontsize=28)
    ax.set_xlabel(xlabel, fontsize=24)
    ax.set_ylabel(ylabel, fontsize=24)
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=18, rotation=90, ha='center')
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=18, rotation=0, ha='right')    
    ax.tick_params(axis='x', bottom=False, top=False)
    ax.tick_params(axis='y', left=False, right=False)
    
    # Set legend
    community_names = sorted(unique(df.stack()))
    legend_elements = [
        Patch(facecolor=colors[country], edgecolor=None, label=country)
        for country in community_names
    ] + [
        plt.Rectangle((0.1, 0.1), 
                      .8, .8,
                      fill=False,
                      edgecolor="yellow",
                      lw=3,
                      label = "Strongest-In"),
        plt.Rectangle((0, 0),
                      1, 1,
                      fill=False,
                      edgecolor="black",
                      lw=3,
                      label = "Strongest-Out"),
         ]
    ax.legend(handles=legend_elements, bbox_to_anchor=(1,1),
               loc='upper left',
               title=label_title,
               fontsize=16,
               title_fontsize=18,
               handleheight=1,
               handlelength=1,
               borderpad=0.1)
    
    # Save or display the figure
    if path_save is None:
        plt.show()
        plt.close()
    else:
        save_name = str(communities.year) + f"_{save_name}.png"
        fig.savefig(path_save+save_name, dpi=200, bbox_inches='tight')
        plt.close()


def draw_subgraph_network(communities, i,
                          path_save=None,
                          save_name = None,
                          strength="out", 
                          by = "country",
                          percentil = 99,
                          niter=50):
    # Filtrar subgrafica
    sub_g = communities.p.subgraphs()[i]
    
    # Calcular coordenadas de nodos
    layout = sub_g.layout_fruchterman_reingold(
        niter=niter,
        weights="weight"
    )
    coords = array(layout.coords)
    x, y = coords[:, 0], coords[:, 1]
    
    # Calcular tamaño de nodos
    min_size = 3
    max_size = 20
    if strength == "out":
        s = array(sub_g.vs["Out_Strength"])
    elif strength == "in":
        s = array(sub_g.vs["In_Strength"])
        
    sizes = min_size + (s - s.min()) / (s.max() - s.min()) * (max_size - min_size)

    # Establecer info
    sub_g.vs["CountryName"] = [countries_names[c] for c in sub_g.vs["country"]]
    sub_g.vs["ActivityName"] = [activities_names[c] for c in sub_g.vs["activity"]]
    hovertext = [
        f"<b>{v['name']}</b><br>"
        f"Country: {v['CountryName']}<br>"
        f"Activity: {v['ActivityName']}<br>"
        f"In_Strength: {v['In_Strength']:.5f}<br>"
        f"Out_Strength: {v['Out_Strength']:.5f}"
        for v in sub_g.vs
        ]
    
    # Crear traza de aristas
    # Filtrar aristas en el percentil 
    weights  = array(sub_g.es["weight"])
    threshold = percentile(weights, percentil)
    x_domestic, y_domestic = [], []   # Aristas gris (mismo país)
    x_interntl, y_interntl = [], []   # Aristas rojo (distinto país)
    
    countries = sub_g.vs['country']  # Lista de países de cada nodo
    for edge in sub_g.es:
        if edge['weight'] >= threshold:
            src, tgt = edge.tuple  # índices de los nodos conectados por esta arista
            x0, y0 = coords[src]   # coordenadas del nodo fuente
            x1, y1 = coords[tgt]   # coordenadas del nodo destino
            if countries[src] == countries[tgt]:
                x_domestic += [x0, x1, None]
                y_domestic += [y0, y1, None]
            else:
                x_interntl += [x0, x1, None]
                y_interntl += [y0, y1, None]
    # Crear traza de aristas domesticas
    edge_trace_domestic = go.Scatter(
        x=x_domestic, y=y_domestic,
        mode='lines',
        line=dict(width=0.3, color='gray'),
        opacity = 0.9,
        hoverinfo='none',
        showlegend=True,
        visible="legendonly",
        name="Domestic trade"
    )
    # Crear traza de aristas internacionales
    edge_trace_interntl = go.Scatter(
        x=x_interntl, y=y_interntl,
        mode='lines',
        line=dict(width=0.8, color='red'),
        opacity = 0.9,
        hoverinfo='none',
        showlegend=True,
        name="International trade"
    )
    
    # Crear figura y agregar aristas
    fig = go.Figure()
    fig.add_trace(edge_trace_domestic)
    fig.add_trace(edge_trace_interntl)
    
    # Crear traza de nodos
    colors = create_colors(by = by)
    
    # Crear nodos por codigo
    for code in sorted(set(sub_g.vs[by])):
        indices = [i for i, c in enumerate(sub_g.vs[by]) if c == code]
        name = code
        color = rgb2hex(colors[code])   
        scatter = go.Scatter(
            x=x[indices],
            y=y[indices],
            mode='markers',
            name=name,  # Aparece en la leyenda
            marker=dict(
                size=sizes[indices],
                color=color,
                opacity=0.8,
                line=dict(width=0.3, color='black')
            ),
            text=[hovertext[i] for i in indices],
            hoverinfo='text',
            legendgroup=name,
            showlegend=True
        )
        fig.add_trace(scatter)
    
    fig.update_layout(
          xaxis=dict(showgrid=False, zeroline=False, visible=False, scaleanchor="x"),
          yaxis=dict(showgrid=False, zeroline=False, visible=False),
          plot_bgcolor='white',
          hoverlabel=dict(bgcolor="white", font_size=6),
          width=600,
          height=600,
          legend=dict(
              font={"size": 6}
          )
      )

    # Save or display the figure
    if path_save is None:
        pio.renderers.default = "browser"
        fig.show()
    else:
       if save_name == None:
           save_name = str(communities.year) + f"_C{str(i)}_net"
       else: 
           save_name = str(communities.year) + "_" + save_name + "_net"
       fig.write_html(path_save / f"{save_name}.html")
       
