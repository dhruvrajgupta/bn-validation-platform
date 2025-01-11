import xmltodict
import networkx as nx
import matplotlib.pyplot as plt
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
import numpy as np

def xdsl_to_digraph(xdsl_content: str) -> nx.DiGraph:
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


def extract_xdsl_content(xdsl_content):
    nodes = {}
    additional_nodes_contents = None
    xdsl_dict = xmltodict.parse(xdsl_content)
    nodes_contents = xdsl_dict['smile']['nodes']['cpt']
    if xdsl_dict['smile'].get('extensions'):
        additional_nodes_contents = xdsl_dict['smile']['extensions']['genie']['node']

    if isinstance(nodes_contents, list):
        for node in nodes_contents:
            # print(node)
            node_id = node['@id']
            # print(node_id)

            states_content = node['state']
            states = []
            parents_contents = node.get('parents', [])
            parents = []
            probabilities = [float(x) for x in node['probabilities'].split(" ")]

            if isinstance(states_content, list):
                for state in states_content:
                    state = state['@id']
                    states.append(state)

            if parents_contents:
                parents.extend(parents_contents.split(" "))

            # print(probabilities)
            # print(parents)
            nodes[node_id] = {
                'states': states,
                'parents': parents,
                'probabilities': probabilities
            }
            # import json
            # print(json.dumps(nodes[node_id], indent=2))

        if isinstance(additional_nodes_contents, list):
            for node_info in additional_nodes_contents:
                # print(node_info)
                node_id = node_info['@id']
                node_color = node_info['interior']['@color']
                # print(node_color)
                # print(node_id)
                # print()
                if node_color == "ff9900" or node_color == "bf2d13" or node_color == "ffffff":
                    node_type = 'Patient Situation'
                    observability = "Unobserved"
                elif node_color == "ffff00" or node_color == "F6FF00" or node_color == "f6ff00":
                    node_type = 'Examination Result'
                    observability = "Observed"
                elif node_color == "ff00ff" or node_color == "cc99ff":
                    node_type = 'Decision Node'
                    observability = "Needs to be Predicted"
                else:
                    node_type = 'Unknown'
                    observability = "Unknown"

                nodes[node_id]['node_type'] = node_type
                nodes[node_id]['observability'] = observability

    return nodes

def convert_to_vis(graph):
    from causalnex.plots import plot_structure, NODE_STYLE, EDGE_STYLE

    viz = plot_structure(
        graph,
        all_node_attributes=NODE_STYLE.WEAK,
        all_edge_attributes=EDGE_STYLE.WEAK,
    )
    viz.toggle_physics(False)
    viz.show_buttons(filter_=['physics'])
    viz.show("dashboard/pyvis_htmls/current_model.html")


def convert_to_vis_super(graph):
    from causalnex.plots import plot_structure, NODE_STYLE, EDGE_STYLE

    viz = plot_structure(
        graph,
        all_node_attributes=NODE_STYLE.WEAK,
        all_edge_attributes=EDGE_STYLE.WEAK,
    )
    viz.toggle_physics(False)
    viz.show_buttons(filter_=['physics'])
    viz.show("dashboard/pyvis_htmls/super_model.html")

def convert_to_vis_markov(graph):
    from causalnex.plots import plot_structure, NODE_STYLE, EDGE_STYLE

    viz = plot_structure(
        graph,
        all_node_attributes=NODE_STYLE.WEAK,
        all_edge_attributes=EDGE_STYLE.WEAK,
    )
    viz.toggle_physics(False)
    viz.show_buttons(filter_=['physics'])
    viz.show("markov.html")


def build_network(nodes):
    model = BayesianNetwork()

    # Add nodes and edges
    for node_id, details in nodes.items():
        model.add_node(node_id)
        for parent in details['parents']:
            model.add_edge(parent, node_id)

    # Add CPDs
    for node_id, details in nodes.items():
        node_states_card = len(details['states'])
        parents = details['parents']
        parent_states = [len(nodes[parent]['states']) for parent in parents]
        values = details['probabilities']

        state_names = {}

        if parents:
            num_of_cols = node_states_card
            # num_of_cols = int(len(values)/states)
            num_of_rows = int(len(values) / node_states_card)
            x = np.array(values)
            x = x.reshape(num_of_rows, num_of_cols)
            su = x.sum(axis=1)
            # print(su)
            x = x.transpose()
            values = x
            # values = x.tolist()
            # values = [values[i:i + states] for i in range(0, len(values), states)]
        else:
            values = [[value] for value in values]
            values = np.array(values)
            su = values.sum(axis=0)
            # print(su)

        state_names[node_id] = details['states']
        if parents:
            for parent in parents:
                state_names[parent] = nodes[parent]['states']

        # print(f"Node_ID: {node_id}")
        # print(f"Node States Cardinality: {node_states_card}")
        # print(f"Evidence / Parents: {parents}")
        # print(f"Evidence Cardinality: {parent_states}")
        # print(f"State Names: {json.dumps(state_names, indent=2)}")
        # print(f"CPD Values: \n{values}")
        # print("-" * 50)

        cpd = TabularCPD(variable=node_id, variable_card=node_states_card, values=values,
                         evidence=parents, evidence_card=parent_states, state_names=state_names)
        model.add_cpds(cpd)

    return model
