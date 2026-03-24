# ===========================================================
# PACKAGES
# ===========================================================
import warnings

from igraph import VertexClustering
from numpy import argmax, sum
from pandas import DataFrame

from icio_community.utils import countries, activities
from icio_community.draw import (
    draw_communities,
    draw_map,
    draw_subgraph_network
    )

# ===========================================================
# CLASSES
# ===========================================================
class Communities(VertexClustering):

    # ATTRIBUTES
    @property
    def n(self) -> int:
        """
       int: Number of vertices in the graph.
       """
        return self.p.n
    
    @property
    def n_subgraphs(self) -> int:
        """
        int: Number of communities (subgraphs).
        """
        return len(self.subgraphs)
    
    @property
    def modularity(self) -> float:
        return self.p.modularity
    
    @property
    def W(self) -> float:
        return self.__W

    def __init__(self, partition: VertexClustering, year: int):
        """
        Initialize the Communities object from a VertexClustering partition.
        
        Parameters
        ----------
        partition : igraph.VertexClustering
            Result of a community detection algorithm.
        year : int
            Year associated with the graph.
        """
        self.p = partition
        self.g = partition.graph.copy()
        self.g.vs['cluster'] = partition.membership # revisar hacer initial_partition  VertexClustering
        self.year = year
        self.__W = float(sum(self.g.es["weight"]))
        self.subgraphs = self.p.subgraphs()
        
    def strongest(self) -> list[tuple[str, str]]:
        """
        Identify the most central nodes (by in/out strength) in each community.
        
        Returns
        -------
        list of tuple
            Each tuple contains (node_with_max_in_strength, node_with_max_out_strength)
            for a community.
        """
        strongest = []
        for sub_g in self.p.subgraphs():
            in_strength = sub_g.strength(weights=sub_g.es['weight'], mode='IN')
            out_strength = sub_g.strength(weights=sub_g.es['weight'], mode='OUT')
            max_in = sub_g.vs[argmax(in_strength)]['name']
            max_out = sub_g.vs[argmax(out_strength)]['name']
            strongest.append((max_in, max_out))
        return strongest
    
    def labels(self) -> list[str]:
        """
        Generate unique labels (country code) for each community 
        based on dominant nodes (the highest out-strength node)
        
        Returns
        -------
        list of str
            List of unique labels (country codes) for each community.
        
        Raises
        ------
        ValueError
            If any label is repeated.
        """
        strongest = self.strongest()
        labels = [i[1].split("_")[0] for i in strongest]
        if len(labels) != len(set(labels)):
            warnings.warn('ERROR: Duplicate community labels', UserWarning)
            return list(range(len(labels)))
        return labels
    
    @property
    def local_modularity(self) -> dict[str, float]:
        if not hasattr(self, "_local_modularity"):
            self._local_modularity = {
                i: (sum(subg_g.es["weight"], dtype=float) / self.W) -
                   (sum(subg_g.vs["Out_Strength"], dtype=float) *
                    sum(subg_g.vs["In_Strength"], dtype=float)) / (self.W**2)
                for i, subg_g in zip(self.labels(), self.subgraphs)
            }
        return self._local_modularity

    
    def select(self, countries_sel=[], activities_sel=[]):   
        if activities_sel == []:
            activities_sel = activities
        if countries_sel == []: 
            countries_sel = countries
        df = DataFrame(columns=activities_sel, index=countries_sel)
        labels = self.labels()
        memberships = self.p.membership
        for v in self.g.vs():
            country = v["country"]
            activity = v["activity"]
            if country in  countries_sel and  activity in  activities_sel:
                df.loc[country, activity] = labels[memberships[v.index]]
        df = df.dropna(how='all', axis=0) 
        df = df.dropna(how='all', axis=1) 
        return df    
    
    
    def draw(self,
             path_save: str = None,
             save_name: str = "",
             select = None,
             countries_sel: list = [],
             activities_sel: list = [],
             **kwargs):
        
        if select is None:
            select = self.select(countries_sel, activities_sel)
        draw_communities(self, select, path_save, save_name, **kwargs)
        
    def draw_map(self, 
                 path_save: str = None,
                 save_name: str = "communities",
                 threshold: float = None,
                 projection: str = 'natural earth') -> None:
        draw_map(g = None,
                 year=None,
                 communities=self,
                 path_save=path_save,
                 save_name=save_name,
                 threshold=threshold,
                 projection=projection)
        
    def draw_subgraphs(self,
                       path_save=None,
                       strength="out",
                       by = "country",
                       percentil = 99,
                       niter=50):
        labels = self.labels()
        for i in range(self.n_subgraphs):
            draw_subgraph_network(self, i,
                                  path_save=path_save,
                                  save_name=str(labels[i]), 
                                  strength=strength, 
                                  by = by,
                                  percentil = percentil,
                                  niter=niter)
