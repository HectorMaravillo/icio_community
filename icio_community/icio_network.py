# ===========================================================
# PACKAGES
# ===========================================================
import igraph as ig

from numpy import nan, newaxis, repeat
from pandas import DataFrame, MultiIndex, Series, read_csv

from icio_community.draw import draw_map
from icio_community.utils import ( 
    value_added_names, 
    final_demand_names
    )
from icio_community.config import ICIO_TABLES_DIR


# ===========================================================
# CLASSES
# ===========================================================
class ICIO_Network:
    """
    A class to model and analyze ICIO-OECD tables as weighted directed graph.

    This class loads an inter-country input-output (ICIO) table for a given year,
    processes its intermediate demand matrix, and constructs a directed graph,
    where nodes represent country-activity pairs and edges represent flows
    of intermediate goods or services.

    Attributes
    ----------
    year : int
        The year of the ICIO table.
    matrix : pd.DataFrame
        The intermediate demand matrix 
        (rows and columns as MultiIndex: country-activity).
    g : igraph.Graph
        The directed graph representation  of intermediate flows.
    """
    
    # ------------------------------------------------------------------
    # ATTRIBUTES
    @property
    def year(self) -> int:
        """int: Year of the ICIO table."""
        return self.__year

    @property
    def total_output(self) -> float:
        """float: Total output of the ICIO table."""
        return self.__total_output

    @property
    def matrix(self) -> DataFrame:
        """pd.DataFrame: Intermediate demand matrix of the ICIO table."""
        return self.__intermediate_demand

    @property
    def g(self) -> ig.Graph:
        """igraph.Graph: Directed graph of intermediate demand flows."""
        return self.__g

    # ------------------------------------------------------------------
    # CONSTRUCTOR
    def __init__(self,
                 year: int,
                 normalize: bool = True,
                 by_output: bool = False, 
                 RoW: bool = False,
                 diagonal: bool = True,
                 diagonal_country: bool = True) -> None: 
        """
        Initialize the ICIO_Network object.

        Parameters
        ----------
        year : int
            Year of the ICIO table to load (must be between 1995 and 2022).
        normalize : bool, optional
            Whether to normalize edge weights. Default is True.
        by_output : bool, optional
            If True, normalize edge weights using total output.
            If False, use total intermediate demand.
            Only relevant if `normalize` is True. Default is False.
        RoW : bool, optional
            Whether to include Rest of the World (ROW) in the graph.
            Default is False.
        diagonal : bool, optional
            Whether to keep same country-activity self-links.
            Default is True.
        diagonal_country : bool, optional
            Whether to keep within-country blocks.
            If False, all same-country flows are removed.
            Default is True.

        Raises
        ------
        ValueError
            If the year is not within the range valid range [1995, 2022].
        """
        # Validate year range
        if (year < 1995) or (year > 2022):
            raise ValueError('Invalid year')
        # Initialize ICIO_Network class
        self.__year = year
        self.__import_data(year, RoW)
        self.__g = self.__build_network(
            normalize = normalize, 
            by_output = by_output,
            diagonal = diagonal,
            diagonal_country = diagonal_country
            )

    # ------------------------------------------------------------------
    # METHODS
    def __import_data(self,
                      year: int,
                      RoW: bool) -> DataFrame:
        """
        Load and preprocess the ICIO table for the specified year.

        Parameters
        ----------
        year : int
            Year of the ICIO table.
        RoW : bool
            Whether to include Rest of the World (ROW).

        Returns
        -------
        pd.DataFrame
            The full ICIO table with MultiIndex rows and columns.
        """
        
        # Import data
        print(f'Reading ICIO-OECD table ({self.year})')
        filepath = ICIO_TABLES_DIR / f"{self.year}_SML.csv"
        matrix = read_csv(filepath, index_col='V1')
        
        # Build  MultiIndex to rows  (country-activity)
        index = [i.split('_', 1) for i in matrix.index]
        matrix.index = MultiIndex.from_arrays(
            [
                [i[0] for i in index],
                [i[1] if len(i) == 2 else None for i in index]
            ],
            names=['country', 'activity']
        )
        # Build  MultiIndex to columns  (country-activity)
        columns = [i.split('_', 1) for i in matrix.columns]
        matrix.columns = MultiIndex.from_arrays(
            [
                [i[0] for i in columns],
                [i[1] if len(i) == 2 else None for i in columns]
            ],
            names=['country', 'activity']
        )

        # Identify final demand columns
        cols_activity = matrix.columns.get_level_values('activity')
        cols_final_demand = cols_activity.isin(final_demand_names + [nan])
        # Extract value-added components
        self.__value_added = {"VA": matrix.loc["VA", None][~cols_final_demand],
                     "TLS": matrix.loc["TLS", None].drop(("OUT", nan)),
                     "OUT": matrix.loc["OUT", None][~cols_final_demand]
                     }
        for name, value in self.__value_added.items():
            value.name = name
        
        # Remove value-added rows
        indices_country = matrix.index.get_level_values('country')
        matrix = matrix[~indices_country.isin(value_added_names)]
        
        # Extract final demand
        self.__final_demand = {"FD": matrix.loc[:, cols_final_demand].drop(columns=("OUT",nan)),
                               "OUT": matrix["OUT"].iloc[:, 0]}
        for name, value in self.__final_demand.items():
            value.name = name
         
        # Keep only intermediate demand columns
        matrix = matrix.loc[:, ~cols_final_demand]    
        
        # Optionally remove Rest of the World
        if not RoW:
            idx = matrix.index.get_level_values(0) != "ROW"
            cols = matrix.columns.get_level_values(0) != "ROW"
            matrix = matrix.loc[idx, cols]

        self.__intermediate_demand = matrix
           
        # Compute total output        
        self.__total_output = self.__value_added["OUT"].sum()

        return matrix


    def __build_network(self,
                        normalize: bool,
                        by_output: bool,
                        diagonal: bool,
                        diagonal_country: bool) -> ig.Graph:
        """
        Construct the intermediate demand graph from the ICIO table.

        Parameters
        ----------
        normalize : bool
            Whether to normalize edge weights (as percentage of flow).
        by_output : bool
            If True, normalize using total output,
            otherwise using total intermediate demand.
        diagonal : bool
            Whether to keep country-activity self-links.
        diagonal_country : bool
            Whether to keep within-country blocks.

        Returns
        -------
        igraph.Graph
            A directed igraph.Graph with country-activity as nodes,
            and intermediate flows as weighted edges.
        """
        matrix = self.__intermediate_demand
        
        print(f'Creating ICIO network ({self.year})')
        
        # Stack the matrix into edge list form
        icio_stack = matrix.stack(level=[0, 1], future_stack=True)
        
        # Remove within-country blocks if requested
        if not diagonal_country: 
            # Remove diagonal blocks by country 
            idx = icio_stack.index
            mask = idx.get_level_values(0) == idx.get_level_values(2)
            icio_stack.loc[mask] = 0
        # Remove exact diagonal if requested
        elif not diagonal: 
            idx = icio_stack.index
            idx = icio_stack.index
            mask = (idx.get_level_values(0) == idx.get_level_values(2)) & \
                   (idx.get_level_values(1) == idx.get_level_values(3))
            icio_stack.loc[mask] = 0
        
        # Normalize edge weights if requested
        if normalize:
            if by_output:
                # Normalize using total output
                total = self.__total_output 
            else:
                # Normalize total intermediate demand
                total = icio_stack.sum()
            icio_stack = icio_stack * 100 / total
            
        # Filter positive flows
        icio_stack = icio_stack[icio_stack > 0]
         
        
        # Create vertex and edge lists
        idxs = DataFrame(list(icio_stack.index))
        vs_from = list(idxs[0]+'_'+idxs[1])
        vs_to = list(idxs[2]+'_'+idxs[3])
        vertices = list(set(vs_from+vs_to))
        edges = zip(vs_from, vs_to)
        
        # Build directed graph
        g = ig.Graph(directed=True)
        g.add_vertices(vertices)
        g.add_edges(edges)
        g.es['weight']  = icio_stack.values
        g.vs["In_Strength"] = g.strength(weights=g.es['weight'], mode='IN')
        g.vs["Out_Strength"] = g.strength(weights=g.es['weight'], mode='OUT')
        
        # Add node metadata
        vs_names = Series(g.vs['name']).str.split("_", n=1, expand=True)
        g.vs["country"] = vs_names[0]
        g.vs["activity"] =  vs_names[1]
        
        return g   
    
    def __calculate_trade(self,
                          trade_type,
                          countries,
                          activities,
                          n):
        """
        Compute total flow for a given trade-type partition.
        """
        row_country = repeat(countries.to_numpy()[:, newaxis], n, axis=1)
        row_activity = repeat(activities.to_numpy()[:, newaxis], n, axis=1)
        col_country = repeat(countries.to_numpy()[newaxis, :], n, axis=0)
        col_activity = repeat(activities.to_numpy()[newaxis, :], n, axis=0)
    
        if trade_type == "I":
            mask = (row_country != col_country) & (row_activity != col_activity)
        elif trade_type == "II":
            mask = (row_country != col_country) & (row_activity == col_activity)
        elif trade_type == "III":
            mask = (row_country == col_country) & (row_activity != col_activity)
        elif trade_type == "IV":
            mask = (row_country == col_country) & (row_activity == col_activity)
            
        return self.__intermediate_demand.where(mask).sum().sum()
    
    def calculate_trade_types(self):
        """
        Compute aggregate flows for the four trade-type categories.
        """
        n = self.__intermediate_demand.shape[0]
        
        countries = self.matrix.index.get_level_values('country')
        activities = self.matrix.index.get_level_values('activity')

    
        # Sum flows by type
        trade_I   = self.__calculate_trade("I", countries, activities, n)
        trade_II  = self.__calculate_trade("II", countries, activities, n)
        trade_III = self.__calculate_trade("III", countries, activities, n)
        trade_IV  = self.__calculate_trade("IV", countries, activities, n)
    
        return trade_I, trade_II, trade_III, trade_IV
    
    
    def draw_map(self, 
                 path_save: str = None,
                 save_name: str = "",
                 threshold: float = None,
                 projection: str = 'natural earth') -> None:
        """
        Create and save an interactive map of the ICIO network.
    
        Parameters
        ----------
        path_save : str, optional
           Path where the HTML file will be saved.
           If not, the map will be displayed in the browser.
        save_name : Path, optional
            Output file or directory name.
        threshold : float
            Minimum edge weight to be visualized.
            Edges below this threshold are ignored.
        projection : {'natural earth', 'orthographic'}, optional
            Type of geographic projection to use:
            - 'natural earth': standard flattened world map.
            - 'orthographic': 3D globe-like view.
    
        Returns
        -------
        None
        """
        draw_map(g = self.g,
                 year = self.year,
                 path_save = path_save,
                 save_name = save_name,
                 threshold = threshold,
                 projection = projection)    
   
