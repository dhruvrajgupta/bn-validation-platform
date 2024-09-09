import networkx as nx
from streamlit_agraph import agraph, Node, Edge, Config
from pgmpy.models import BayesianNetwork
import itertools

def find_redundant_edges_multiple_paths(graph):
    def is_redundant_edge(G, edge):
        # Checking if removal of edges still has connectivity
        G_prime = G.copy()
        G_prime.remove_edge(*edge)
        # Check if there is still a path between the nodes
        is_redundant = nx.has_path(G_prime, edge[0], edge[1])
        return is_redundant

    redundant_edges  = [edge for edge in graph.edges() if is_redundant_edge(graph, edge)]

    return redundant_edges

def print_multiple_paths(graph, redundant_edges):
    output = ""
    for index, edge in enumerate(redundant_edges):
        output += f"Edge #{index + 1}: {edge}\n"
        output += "-" * 100 + "\n"
        for index, path in enumerate(nx.all_simple_paths(graph, edge[0], edge[1])):
            output += f"Path #{index + 1}: {path}\n"
        output += "\n"

    return output

def redundant_edges_digraph(graph, redundant_edges):
    G = nx.DiGraph()
    for edge in redundant_edges:
        for path in nx.all_simple_paths(graph, edge[0], edge[1]):
            for i in range(len(path) - 1):
                G.add_edge(path[i], path[i + 1])

    nodes = []
    edges = []
    for node in G.nodes:
        nodes.append(Node(id=node, label=node))
    for edge in G.edges:
        edges.append(Edge(source=edge[0], target=edge[1]))

    config = Config(width=1000, height=600, directed=True, physics=True)
    return agraph(nodes=nodes, edges=edges, config=config)

def find_redundant_edges_d_separation(graph, debug=False):

    import time
    start = time.time()
    print(f"Start: {start}")

    # Function to check for d-separation
    def check_d_separation(model, X, Y, Z):
        # Returns True if X and Y are independent given Z (i.e., d-separated)
        return not model.is_dconnected(X, Y, Z)
    
    # Function to check if an edge is redundant
    def is_edge_redundant(model, edge, X, Y, Z):
        # Check conditional independence before removing the edge
        before_removal = check_d_separation(model, X, Y, Z)

        # Remove the edge
        model.remove_edge(*edge)

        # Check conditional independence after removing the edge
        after_removal = check_d_separation(model, X, Y, Z)

        # Add the edge back to the model
        model.add_edge(*edge)

        # If removing the edge does not affect d-separation, it is redundant
        return before_removal == after_removal

    # graph = BayesianNetwork([
    #     ('Burglary', 'Alarm'),
    #     ('Earthquake', 'Alarm'),
    #     ('Alarm', 'JohnCalls'),
    #     ('Alarm', 'MaryCalls'),
    #     ('Burglary', 'Earthquake'), # <-- Redundant Edge
    #     # Burglary and Earthquake were already independent in the original graph unless conditioned on Alarm.
    #     # The new edge does not change this independence, as the two variables are still blocked by the collider at the Alarm unless the Alarm is observed.
    #     # Therefore, this edge does not add new information or change the probabilistic relationships between variables. It’s redundant in terms of the conditional independencies in the graph.
    # ])

    # List of redundant edges
    redundant_edges = []

    # List of nodes in the graph
    nodes = [node for node in graph.nodes()]
    
    # Checking each edge in the graph
    for edge in graph.edges():
        X = edge[0]
        Y = edge[1]

        # Removing the nodes already in the edge
        nodes_cp = nodes.copy()
        nodes_cp.remove(edge[0])
        nodes_cp.remove(edge[1])

        # Accumulating list that aggregrates is edge redundant given a set of variables
        # Only When all is True the edge is truly redundant given all combination of variables
        is_edge_redundant_given_variables = []

        flag_combi_break = False
        for i in range(len(nodes_cp)):
            if flag_combi_break:
                break
            for combination in itertools.combinations(nodes_cp, i):
                Z = list(combination)
                if not Z:
                    continue

                # Check if the edge is redundant
                is_redundant = is_edge_redundant(graph.copy(), edge, X, Y, Z)
                if is_redundant == False:
                    flag_combi_break = True
                    is_edge_redundant_given_variables.append(is_redundant)
                    break
                # if debug:
                #     print(f"Is the edge {edge} redundant given {list(combination)}? {is_redundant}")
                is_edge_redundant_given_variables.append(is_redundant)
        
        if debug:
            print(f"Is the edge {edge} redundant? {all(is_edge_redundant_given_variables)}")
        if all(is_edge_redundant_given_variables):
            redundant_edges.append(edge)

    end = time.time()
    print(f"End: {end}")
    print(f"Time: {end - start}")

    return redundant_edges

# find_redundant_edges_d_separation(None, debug=True)