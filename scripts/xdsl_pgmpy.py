from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
import xmltodict
import numpy as np
import pandas as pd
import json
from joblib import Parallel, delayed
from tqdm.auto import tqdm

nodes = {}


# Default predict of pgmpy BayesianNetwork in predict does not handle missing node values
# https://github.com/pgmpy/pgmpy/pull/1119
def predict(self, data, stochastic=False, n_jobs=-1):
    """
    Predicts states of all the missing variables.

    Parameters
    ----------
    data: pandas DataFrame object
        A DataFrame object with column names same as the variables in the model.

    stochastic: boolean
        If True, does prediction by sampling from the distribution of predicted variable(s).
        If False, returns the states with the highest probability value (i.e. MAP) for the
            predicted variable(s).

    n_jobs: int (default: -1)
        The number of CPU cores to use. If -1, uses all available cores.

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> from pgmpy.models import BayesianNetwork
    >>> values = pd.DataFrame(np.random.randint(low=0, high=2, size=(1000, 5)),
    ...                       columns=['A', 'B', 'C', 'D', 'E'])
    >>> train_data = values[:800]
    >>> predict_data = values[800:]
    >>> model = BayesianNetwork([('A', 'B'), ('C', 'B'), ('C', 'D'), ('B', 'E')])
    >>> model.fit(train_data)
    >>> predict_data = predict_data.copy()
    >>> predict_data.drop('E', axis=1, inplace=True)
    >>> y_pred = model.predict(predict_data)
    >>> y_pred
        E
    800 0
    801 1
    802 1
    803 1
    804 0
    ... ...
    993 0
    994 0
    995 1
    996 1
    997 0
    998 0
    999 0
    """
    from pgmpy.inference import VariableElimination

    if set(data.columns) == set(self.nodes()):
        raise ValueError("No variable missing in data. Nothing to predict")

    elif set(data.columns) - set(self.nodes()):
        raise ValueError("Data has variables which are not in the model")

    missing_variables = set(self.nodes()) - set(data.columns)
    model_inference = VariableElimination(self)

    if stochastic:
        data_unique_indexes = data.groupby(list(data.columns)).apply(
            lambda t: t.index.tolist()
        )
        data_unique = data_unique_indexes.index.to_frame()

        pred_values = Parallel(n_jobs=n_jobs)(
            delayed(model_inference.query)(
                variables=missing_variables,
                evidence=data_point.dropna().to_dict(),
                show_progress=False,
            )
            for index, data_point in tqdm(
                data_unique.iterrows(), total=data_unique.shape[0]
            )
        )
        predictions = pd.DataFrame()
        for i, row in enumerate(data_unique_indexes):
            p = pred_values[i].sample(n=len(row))
            p.index = row
            predictions = pd.concat((predictions, p), copy=False)

        return predictions.reindex(data.index)

    else:
        data_unique = data.drop_duplicates()
        pred_values = []

        # Send state_names dict from one of the estimated CPDs to the inference class.
        pred_values = Parallel(n_jobs=n_jobs)(
            delayed(model_inference.map_query)(
                variables=missing_variables,
                evidence=data_point.dropna().to_dict(),
                show_progress=False,
            )
            for index, data_point in tqdm(
                data_unique.iterrows(), total=data_unique.shape[0]
            )
        )

        df_results = pd.DataFrame(pred_values, index=data_unique.index)
        print(df_results)
        data_with_results = pd.concat([data_unique, df_results], axis=1)
        print(data_with_results)

        x = data.merge(data_with_results, how="left").loc[
               :, list(missing_variables)
               ]

        print(x)

        return data.merge(data_with_results, how="left").loc[
               :, list(missing_variables)
               ]


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

        print(f"Node_ID: {node_id}")
        print(f"Node States Cardinality: {node_states_card}")
        print(f"Evidence / Parents: {parents}")
        print(f"Evidence Cardinality: {parent_states}")
        print(f"State Names: {json.dumps(state_names, indent=2)}")
        print(f"CPD Values: \n{values}")
        print("-" * 50)

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

dataset_paths = [
    # "/home/dhruv/Desktop/bn-validation-platform/datasets/40percent.csv",
    # "/home/dhruv/Desktop/bn-validation-platform/datasets/60percent.csv",
    "/home/dhruv/Desktop/bn-validation-platform/datasets/80percent.csv",
    # "/home/dhruv/Desktop/bn-validation-platform/datasets/100percent.csv"
]

target = "M_state__patient"

for dataset_path in dataset_paths:
    df = pd.read_csv(dataset_path)[:30]
    df = df[[c for c in df.columns if c in model.nodes()]]
    df = df.replace(to_replace="*", value=np.nan)
    # df = df[df[target].notna()]
    print(df)
    X = df.loc[:, df.columns != target]
    Y = df[target]
    print(Y)

    y_pred = predict(model, data=X, stochastic=False)
    comparison_df = pd.DataFrame({'Y': Y, 'y_pred': y_pred[target]})
    print(comparison_df)
    print(len(comparison_df))
    comparison_df = comparison_df.dropna(subset=['Y'])
    print(comparison_df)
    print(len(comparison_df))
    comparison_df['Equal'] = comparison_df['Y'] == comparison_df['y_pred']
    print(comparison_df)
    print(len(comparison_df))
    accuracy = comparison_df['Equal'].mean()
    print(f"Dataset: {dataset_path}")
    print("\nAccuracy:")
    print(f"{target} = {accuracy}")
    target_state_counts = Y.value_counts().to_dict()
    for state, actual_state_count in target_state_counts.items():
        pred_count = len(comparison_df[comparison_df['Equal'] == True])
        # print(state)
        # print(pred_count)
        # print(actual_state_count)
        if actual_state_count:
            print(f"\t{state} = {pred_count / actual_state_count} ({pred_count}/{actual_state_count})")
        else:
            print(f"\t{state} = 0.0 ({pred_count}/{actual_state_count})")
