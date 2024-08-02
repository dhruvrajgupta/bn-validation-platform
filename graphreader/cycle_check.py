import xmltodict
import networkx as nx

def parse_xdsl(file_path):
    with open(file_path, 'r') as file:
        data = xmltodict.parse(file.read())
    return data

def build_graph(xdsl_data):
    graph = nx.DiGraph()
    
    nodes = xdsl_data['smile']['nodes']['cpt']
    for node in nodes:
        node_id = node['@id']
        graph.add_node(node_id)
        
    for node in nodes:
        node_id = node['@id']
        parents = node.get('parents', []).split(" ")
        for parent in parents:
            graph.add_edge(parent, node_id)
    return graph

def detect_cycles(graph):
    try:
        cycle = nx.find_cycle(graph, orientation='original')
        return True, cycle
    except nx.exception.NetworkXNoCycle:
        return False, []

def main(file_path):
    xdsl_data = parse_xdsl(file_path)
    graph = build_graph(xdsl_data)
    has_cycle, cycle = detect_cycles(graph)
    if has_cycle:
        print("Graph has a cycle:", cycle)
    else:
        print("No cycles detected in the graph.")

if __name__ == "__main__":
    file_path = '/home/dhruv/Desktop/Network2.xdsl'  # Change this to your file path
    main(file_path)