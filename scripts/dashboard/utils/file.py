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