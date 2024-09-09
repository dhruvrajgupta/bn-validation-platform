import networkx as nx
from streamlit_agraph import agraph, Node, Edge, Config

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