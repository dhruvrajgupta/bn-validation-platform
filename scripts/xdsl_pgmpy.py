from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
import xmltodict
import numpy as np

nodes = {}


def parse_xdsl(file_path):
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
        states = len(details['states'])
        parents = details['parents']
        parent_states = [len(nodes[parent]['states']) for parent in parents]
        values = details['probabilities']

        if parents:
            num_of_cols = states
            # num_of_cols = int(len(values)/states)
            num_of_rows = int(len(values)/states)
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

        cpd = TabularCPD(variable=node_id, variable_card=states, values=values,
                         evidence=parents, evidence_card=parent_states)
        model.add_cpds(cpd)

    return model


# Usage
xdsl_file_path = "/home/dhruv/Documents/Mstage.xdsl"
# xdsl_file_path = "/home/dhruv/Documents/validationPaper_TNM-Model_28012016.xdsl"


parse_xdsl(xdsl_file_path)
model = build_network(nodes)

# Verify the model
if model.check_model():
    print("The model is valid.")
else:
    print("The model is invalid.")

# Print the model to verify
print("Nodes:", model.nodes())
print("Edges:", model.edges())
for cpd in model.get_cpds():
    print(cpd)



viz = model.to_graphviz()
viz.draw('Mstate.png', prog='sfdp')

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

img = mpimg.imread('Mstate.png')

# Display the image
plt.figure(figsize=(10, 10))
plt.imshow(img)
plt.axis('off')
plt.show()