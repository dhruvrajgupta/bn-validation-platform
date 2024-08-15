import xmltodict
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
import numpy as np

def parse_xdsl(file_path):
    """
    This function parses an XDSL file and returns a dictionary of nodes.

    Parameters:
        file_path (str): The path to the XDSL file to be parsed.

    Returns:
        dict: A dictionary where each key is a node ID and each value is another dictionary
            containing the node's states, parents, and probabilities.
    """
    nodes = {}
    with open(file_path, 'r') as f:
        xdsl_content = f.read()
    # print(xdsl_content)
    xdsl_dict = xmltodict.parse(xdsl_content)
    nodes_contents = xdsl_dict['smile']['nodes']['cpt']

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
    return nodes


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
            x = x.transpose()
            values = x
            # values = x.tolist()
            # values = [values[i:i + states] for i in range(0, len(values), states)]
        else:
            values = [[value] for value in values]
            values = np.array(values)
            su = values.sum(axis=0)

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