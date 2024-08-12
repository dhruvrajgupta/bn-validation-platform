from causalnex.structure import StructureModel
import warnings
warnings.filterwarnings("ignore")  # silence warnings

sm = StructureModel()

sm.add_edges_from([
    ('health', 'absences'),
    ('health', 'G1')
])

print(sm.edges)

from causalnex.plots import plot_structure, NODE_STYLE, EDGE_STYLE

viz = plot_structure(
    sm,
    all_node_attributes=NODE_STYLE.WEAK,
    all_edge_attributes=EDGE_STYLE.WEAK,
)
viz.show("01_simple_plot.html")

import pandas as pd

data = pd.read_csv('student/student-por.csv', delimiter=';')
# print(data.head(5))

drop_col = ['school', 'sex', 'age', 'Mjob', 'Fjob', 'reason', 'guardian']
data = data.drop(columns=drop_col)
# print(data.shape)
# print(data.head(5))

import numpy as np

struct_data = data.copy()
non_numeric_columns = list(struct_data.select_dtypes(exclude=[np.number]).columns)

print(non_numeric_columns)
print(data.head())

from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()

for col in non_numeric_columns:
    struct_data[col] = le.fit_transform(struct_data[col])

# struct_data.head(5)

from causalnex.structure.notears import from_pandas

sm = from_pandas(struct_data, tabu_edges=[("higher", "Medu")], w_threshold=0.8)

sm.add_edge("failures", "G1")
sm.remove_edge("Pstatus", "G1")
sm.remove_edge("address", "G1")

sm = sm.get_largest_subgraph()
viz = plot_structure(
    sm,
    all_node_attributes=NODE_STYLE.WEAK,
    all_edge_attributes=EDGE_STYLE.WEAK,
)
viz.show("01_largest_subgraph.html")

from causalnex.network import BayesianNetwork

bn = BayesianNetwork(sm)

discretised_data = data.copy()

data_vals = {col: data[col].unique() for col in data.columns}

failures_map = {v: 'no-failure' if v == [0]
else 'have-failure' for v in data_vals['failures']}
studytime_map = {v: 'short-studytime' if v in [1, 2]
else 'long-studytime' for v in data_vals['studytime']}

discretised_data["failures"] = discretised_data["failures"].map(failures_map)
discretised_data["studytime"] = discretised_data["studytime"].map(studytime_map)

from causalnex.discretiser import Discretiser

discretised_data["absences"] = Discretiser(method="fixed",
                                           numeric_split_points=[1, 10]).transform(discretised_data["absences"].values)
discretised_data["G1"] = Discretiser(method="fixed",
                                     numeric_split_points=[10]).transform(discretised_data["G1"].values)
discretised_data["G2"] = Discretiser(method="fixed",
                                     numeric_split_points=[10]).transform(discretised_data["G2"].values)
discretised_data["G3"] = Discretiser(method="fixed",
                                     numeric_split_points=[10]).transform(discretised_data["G3"].values)

absences_map = {0: "No-absence", 1: "Low-absence", 2: "High-absence"}

G1_map = {0: "Fail", 1: "Pass"}
G2_map = {0: "Fail", 1: "Pass"}
G3_map = {0: "Fail", 1: "Pass"}

discretised_data["absences"] = discretised_data["absences"].map(absences_map)
discretised_data["G1"] = discretised_data["G1"].map(G1_map)
discretised_data["G2"] = discretised_data["G2"].map(G2_map)
discretised_data["G3"] = discretised_data["G3"].map(G3_map)

# Split 90% train and 10% test
from sklearn.model_selection import train_test_split

train, test = train_test_split(discretised_data, train_size=0.9, test_size=0.1, random_state=7)

bn = bn.fit_node_states(discretised_data)

bn = bn.fit_cpds(discretised_data, method="BayesianEstimator", bayes_prior="K2")
print(bn.cpds["G1"])

print(discretised_data.loc[18, discretised_data.columns != 'G1'])
predictions = bn.predict(discretised_data, "G1")
print(f"The prediction is '{predictions.loc[18, 'G1_prediction']}'")


from causalnex.evaluation import classification_report

print(classification_report(bn, test, "G1"))
# For the predictions where the student fails, the precision is good, but recall is bad. This implies that we can rely on predictions for this class when they are made, but we are likely to miss some of the predictions we should have made. Perhaps these missing predictions are as a result of something missing in our structure - this could be an interesting area to explore.
# Does not have quantites involved (to use this??) can be modified to our advantage
# {'G1_Fail': {'precision': 0.7777777777777778, 'recall': 0.5833333333333334, 'f1-score': 0.6666666666666666, 'support': 12.0}, 'G1_Pass': {'precision': 0.9107142857142857, 'recall': 0.9622641509433962, 'f1-score': 0.9357798165137615, 'support': 53.0}, 'accuracy': 0.8923076923076924, 'macro avg': {'precision': 0.8442460317460317, 'recall': 0.7727987421383649, 'f1-score': 0.8012232415902141, 'support': 65.0}, 'weighted avg': {'precision': 0.8861721611721611, 'recall': 0.8923076923076924, 'f1-score': 0.8860973888496825, 'support': 65.0}}

from causalnex.evaluation import roc_auc
roc, auc = roc_auc(bn, test, "G1")
print(auc)

from causalnex.inference import InferenceEngine

ie = InferenceEngine(bn)
marginals = ie.query()
print(marginals["G1"])

marginals_short = ie.query({"studytime": "short-studytime"})
marginals_long = ie.query({"studytime": "long-studytime"})
print("Marginal G1 | Short Studtyime", marginals_short["G1"])
print("Marginal G1 | Long Studytime", marginals_long["G1"])