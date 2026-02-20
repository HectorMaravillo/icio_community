import leidenalg as la
from igraph import VertexClustering

from time import time
from igraph import Graph


def partition_initial(g: Graph, by: str) -> list[int]:
    """
    Generate an initial node partition for community detection.

    Parameters
    ----------
    g : igraph.Graph
        Input-output network.
    by : {'country', 'activity', 'single'}
        Criterion to assign initial group labels:
        - 'country': group by country attribute.
        - 'activity': group by activity attribute.
        - 'single': assign each node to its own group (identity partition).

    Returns
    -------
    list of int
        List of initial community labels for each node.
        
    Raises
    ------
    ValueError
        If an invalid value is provided for `by`.
    """
    if by == 'country':
        v_countries = g.vs["country"]
        countries_id = {c: i for (i, c) in enumerate(set(v_countries))}
        partition_init = [countries_id[v] for v in v_countries]
    elif by == 'activity':
        v_activities = g.vs['activity']
        activities_id = {c: i for (i, c) in enumerate(set(v_activities))}
        partition_init = [activities_id[v] for v in v_activities]
    elif by == 'single':
        return g.vs.indices
    else:
        raise ValueError(f"Invalid partitioning method: '{by}'")
    return partition_init   

def leiden_algorithm(g: Graph, initial_by: str = 'single', seed: int = 1, verbose=False):
    """
    Run the Leiden community detection algorithm on a graph.
    
    Parameters
    ----------
    g : igraph.Graph
        Input-output network.
    initial_by : {'single', 'country', 'activity'}, optional
        Method for initializing the node partition. Default is 'single'.
    seed : int, optional
        Random seed for reproducibility. Default is 1.
    
    Returns
    -------
    tuple
        - partition : leidenalg.VertexPartition
            Community structure found by the Leiden algorithm.
        - t_final : float
            Execution time in seconds.
    """
    initial = partition_initial(g, initial_by)
    if verbose:
        print(f'Calculating partition using Leiden Algorithm (seed: {seed})')
    t_initial = time()
    partition = la.find_partition(
        g,
        initial_membership=initial,
        partition_type=la.ModularityVertexPartition,
        weights='weight',
        seed=seed,
        n_iterations=-1 # Run until there is no improvement
    )
    t_final = time() - t_initial
    partition = VertexClustering(graph = g,
                                 membership = partition.membership,
                                 modularity_params={"weights": g.es["weight"],
                                        "directed": True})  
    if verbose:
        print(f"Leiden algorithm completed in {t_final:.2f} seconds.")
    return partition, t_final

def louvian_algorithm(g: Graph, initial_by: str = 'single', seed: int = 1, verbose=False):
    """
    Run the Louvain community detection algorithm on a graph.
    
    Parameters
    ----------
    g : igraph.Graph
        Input-output network.
    initial_by : {'single', 'country', 'activity'}, optional
        Method for initializing the node partition. Default is 'single'.
    seed : int, optional
        Random seed for reproducibility. Default is 1.
    
    Returns
    -------
    tuple
        - partition : leidenalg.VertexPartition
            Community structure found by the Louvain algorithm.
        - t_final : float
            Execution time in seconds.
    """
    initial = partition_initial(g, initial_by)
    if verbose:
        print('Calculating partition using Louvain Algorithm  (seed: {seed})')
    optimiser = la.Optimiser()
    optimiser.set_rng_seed(seed)
    t_initial = time()
    partition = la.ModularityVertexPartition(g, 
                                             initial_membership=initial,
                                             weights='weight')
    partition_agg = partition.aggregate_partition()
    it = 1
    while optimiser.move_nodes(partition_agg,
                               consider_comms=la.ALL_COMMS) > 0:
        if verbose:
            print('it ', str(it), 'Modularity: ', partition.modularity)
        partition.from_coarse_partition(partition_agg)
        partition_agg = partition_agg.aggregate_partition()
        it += 1
    t_final = time() - t_initial
    partition = VertexClustering(graph = g,
                                 membership = partition.membership,
                                 modularity_params={"weights": g.es["weight"],
                                    "directed": True})  
    if verbose:
        print(f"Louvain algorithm completed in {t_final:.2f} seconds.")
    return partition, t_final
