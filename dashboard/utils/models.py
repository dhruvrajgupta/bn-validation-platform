from pgmpy.models import BayesianNetwork

def get_horrible_model(threshold=0):

    # DiGraph 45 Nodes and 1980 edges (990 cycles)
    if threshold == 0:
        path = "/home/dhruv/Desktop/bn-validation-platform/scripts/horrible_model/sl_without_threshold.pkl"


    import pickle
    with open(path, 'rb') as inp:
        sm = pickle.load(inp)
    print(sm)

    return sm

def reverse_bayesian_network(bn: BayesianNetwork) -> BayesianNetwork:
    """
    Reverses the edges of a given Bayesian Network.

    Parameters:
    bn (BayesianNetwork): The input Bayesian Network.

    Returns:
    BayesianNetwork: A new Bayesian Network with reversed edges.
    """
    # Create a new Bayesian Network
    reversed_bn = BayesianNetwork()

    # Add all the nodes from the original network to the new network
    reversed_bn.add_nodes_from(bn.nodes())

    # Reverse the edges and add them to the new network
    for edge in bn.edges():
        reversed_bn.add_edge(edge[1], edge[0])

    return reversed_bn
