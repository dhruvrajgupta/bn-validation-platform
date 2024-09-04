import xmltodict
import networkx as nx
import matplotlib.pyplot as plt
from streamlit_agraph import agraph, Node, Edge, Config
from typing import List, Tuple

def parse_xdsl(xdsl_content: str) -> nx.DiGraph:
    try:
        # with open(file.name, 'r') as f:
        # xdsl_content = f.read()

        xdsl_dict = xmltodict.parse(xdsl_content)
        graph = nx.DiGraph()

        nodes = xdsl_dict['smile']['nodes']['cpt']
        # print(nodes)
        if isinstance(nodes, list):
            for node in nodes:
                node_id = node['@id']
                graph.add_node(node_id)
                if 'parents' in node:
                    parents = node['parents'].split()
                    # print(parents)
                    for parent in parents:
                        graph.add_edge(parent, node_id)
        else:
            node_id = nodes['@id']
            graph.add_node(node_id)
            if 'parents' in nodes:
                parents = nodes['parents'].split()
                for parent in parents:
                    graph.add_edge(parent, node_id)

        return graph

        # Draw the directed graph
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(graph)  # Position nodes using Fruchterman-Reingold force-directed algorithm
        nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color='gray', font_size=15,
                font_weight='bold', arrowsize=20)
        plt.title('Directed Graph')
        plt.savefig("full_directed_graph.png")
        # plt.show()

        return "File read successfully. Graph has been parsed.", xdsl_content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def convert_to_vis(graph):
    from causalnex.plots import plot_structure, NODE_STYLE, EDGE_STYLE

    viz = plot_structure(
        graph,
        all_node_attributes=NODE_STYLE.WEAK,
        all_edge_attributes=EDGE_STYLE.WEAK,
    )
    viz.toggle_physics(False)
    viz.show_buttons(filter_=['physics'])
    viz.show("current_model.html")


def detect_cycles(graph):

    def is_sublist(small, big):
        it = iter(big)
        x = all(item in it for item in small)
        return x

    def dfs(node, visited, stack):
        visited.add(node)
        stack.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor, visited, stack)
            elif neighbor in stack:
                cycle = stack[stack.index(neighbor):] + [neighbor]
                cycle_procesed = False
                # Check if the cycle has already been included before
                for collected_cycle in all_cycles:
                    if len(collected_cycle) >= len(cycle):
                        if is_sublist(cycle, collected_cycle):
                            cycle_procesed = True
                            break
                if not cycle_procesed:
                    all_cycles.append(cycle + stack[stack.index(neighbor) + 1:])
        stack.pop()

    all_cycles = []
    for start_node in graph.nodes:
        visited = set()
        stack = []
        dfs(start_node, visited, stack)

    return all_cycles

def get_cycles_digraph(all_cycles):

    cycle_graph = nx.DiGraph()

    for cycle in all_cycles:
        # print(cycle)
        for i in range(len(cycle)-1):
            if (cycle[i], cycle[i+1]) not in cycle_graph.edges:
                cycle_graph.add_edge(cycle[i], cycle[i+1])
                # print(cycle[i], "->", cycle[i+1])

    nodes = []
    edges = []
    for node in cycle_graph.nodes:
        nodes.append(Node(id=node, label=node))
    for edge in cycle_graph.edges:
        edges.append(Edge(source=edge[0], target=edge[1]))

    config = Config(width=600, height=600, directed=True, physics=False)
    return agraph(nodes=nodes, edges=edges, config=config)

def print_cycles(cycles):
    output_list = []
    for idx, cycle in enumerate(cycles):
        output = f"Cycle: #{idx+1}\n"
        output += f'{"-"*20}\n'
        first_element = cycle[0]
        cycle.pop(0)
        till = cycle.index(first_element) + 1
        cycle.insert(0, first_element)
        for i in range(till):
            output += f"{cycle[i]} -> {cycle[i+1]}\n"

        output_list.append(output)
    return output_list

def get_horrible_model(threshold=0):

    # DiGraph 45 Nodes and 1980 edges (990 cycles)
    if threshold == 0:
        path = "/home/dhruv/Desktop/bn-validation-platform/scripts/horrible_model/sl_without_threshold.pkl"


    import pickle
    with open(path, 'rb') as inp:
        sm = pickle.load(inp)
    print(sm)

    return sm