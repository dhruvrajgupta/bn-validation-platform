from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
import xmltodict
import numpy as np
import pandas as pd
import json

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
        node_states_card = len(details['states'])
        parents = details['parents']
        parent_states = [len(nodes[parent]['states']) for parent in parents]
        values = details['probabilities']

        state_names = {}

        if parents:
            num_of_cols = node_states_card
            # num_of_cols = int(len(values)/states)
            num_of_rows = int(len(values)/node_states_card)
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

        print(f"Node_ID: {node_id}")
        print(f"Node States Cardinality: {node_states_card}")
        print(f"Evidence / Parents: {parents}")
        print(f"Evidence Cardinality: {parent_states}")
        print(f"State Names: {json.dumps(state_names, indent=2)}")
        print(f"CPD Values: \n{values}")
        print("-"*50)

        cpd = TabularCPD(variable=node_id, variable_card=node_states_card, values=values,
                         evidence=parents, evidence_card=parent_states, state_names=state_names)
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
# for cpd in model.get_cpds():
#     print(cpd)



# viz = model.to_graphviz()
# viz.draw('Mstate.png', prog='sfdp')

# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg

# img = mpimg.imread('Mstate.png')

# # Display the image
# plt.figure(figsize=(10, 10))
# plt.imshow(img)
# plt.axis('off')
# plt.show()

# Get all the nodes/random variables in the model
all_nodes = model.nodes()
# print(f"Nodes: {all_nodes} \n")

# Get all the edges in the model.
all_edges = model.edges()
# print(f"Edges: {all_edges} \n")

# Get all the CPDs.
all_cpds = model.get_cpds()

# Get parents of a specific node
# akt_parents = model.get_parents('Akt')
# print(f"Parents of Akt: {akt_parents} \n")

# # Get children of a specific node
# pka_children = model.get_children('PKA')
# print(f"Children of PKA: {pka_children} \n")

# Get all the leaf nodes of the model
leaves = model.get_leaves()
# print(f"Leaf nodes in the model: {leaves} \n")

# Get the root nodes of the model
roots = model.get_roots()
# print(f"Root nodes in the model: {roots} \n")

df = pd.read_csv("/home/dhruv/Desktop/bn-validation-platform/datasets/100percent.csv")
target = "M_state__patient"
df = df[[c for c in df.columns if c in model.nodes()]]
X = df.loc[:, df.columns != target]
Y = df[target]

y_pred = model.predict(X, stochastic=False)
comparison_df = pd.DataFrame({'Y': Y, 'y_pred': y_pred[target]})
comparison_df['Equal'] = comparison_df['Y'] == comparison_df['y_pred']
accuracy = comparison_df['Equal'].mean()
print("\nAccuracy:")
print(f"{target} = {accuracy}")
for state, pred_count in y_pred.value_counts().to_dict().items():
    state = state[0]
    actual_state_count = len(comparison_df[comparison_df['Y'] == state])
    # print(state)
    # print(pred_count)
    # print(actual_state_count)
    print(f"\t{state} = {pred_count/actual_state_count} ({pred_count}/{actual_state_count})")