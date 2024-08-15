# Here we will use the dataset to perform Structure Learning
# so that it can be compared to the best model aka (LC/Mstage xdsl file)
# best model will be stored in the 'best_model' folder

# We will perform NOTEARS Structure Learning as it is the
# current SOTA Structure Learning method
# CausalNex library already contains the method
# https://proceedings.neurips.cc/paper_files/paper/2018/file/e347c51419ffb23ca3fd5050202f9c3d-Paper.pdf


from causalnex.structure import StructureModel
import warnings
from pgmpy.readwrite import BIFReader
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from causalnex.structure.notears import from_pandas
from sklearn.preprocessing import MinMaxScaler

warnings.filterwarnings("ignore")  # silence warnings

sm = StructureModel()

# Learning structure from the best model to get the second best model

reader = BIFReader("/home/dhruv/Desktop/bn-validation-platform/scripts/best_model/best_model_M_stage.bif")
# reader = BIFReader("/Users/dhruv/Desktop/abcd/bn-validation-platform/scripts/best_model/best_model_M_stage.bif")

model = reader.get_model()
print(model)

# Create Network to be read by CausalNex
for edge in model.edges:
    sm.add_edge(*edge)

from causalnex.plots import plot_structure, NODE_STYLE, EDGE_STYLE

viz = plot_structure(
    sm,
    all_node_attributes=NODE_STYLE.WEAK,
    all_edge_attributes=EDGE_STYLE.WEAK,
)
viz.show("M_State_BN.html")

data = pd.read_csv("/home/dhruv/Desktop/bn-validation-platform/datasets/100percent.csv")
# data = pd.read_csv("/Users/dhruv/Desktop/abcd/bn-validation-platform/datasets/100percent.csv")

# print(data.head())
data = data[:1000]
data = data[[c for c in data.columns if c in model.nodes()]]
# print(data.head())

# non_numeric_columns = list(data.select_dtypes(exclude=[np.number]).columns)
# print(len(non_numeric_columns))

le = LabelEncoder()
categorical_mappings = {}

for col in data:
    data[col] = le.fit_transform(data[col])
    label_to_integer = dict(zip(le.classes_, range(len(le.classes_))))
    integer_to_label = dict(enumerate(le.classes_))
    categorical_mappings[col] = integer_to_label

# print(data.head(5))
# print(le.classes_)
# print(le.inverse_transform(data.loc[0]))
# print(categorical_mappings)

sm = from_pandas(data, w_threshold=0.5)
edge_attributes = {}

# Create a dataframe of weights
edges_weights = {
    "edges": [],
    "weight": []
}
for edge in sm.edges(data=True):
    print(edge)
    edge_tuple = (edge[0], edge[1])
    weight = edge[2]["weight"]
    edges_weights["edges"].append(edge_tuple)
    edges_weights["weight"].append(weight)
    # if weight > 0.8:
    edge_attributes[edge_tuple] = {"width": 5*weight}

edges_weights = pd.DataFrame.from_dict(edges_weights)
# Normalize weights using MinMaxScaler
scaler = MinMaxScaler()
edges_weights['normalized_weight'] = scaler.fit_transform(edges_weights[['weight']])
print(edges_weights)

viz = plot_structure(
    sm,
    all_node_attributes=NODE_STYLE.WEAK,
    all_edge_attributes=EDGE_STYLE.WEAK,
    edge_attributes=edge_attributes,
    plot_options={
        "width": "100%",
        "height": "600px",
    }
)

viz.toggle_physics(False)
viz.show_buttons(filter_=['physics'])
viz.show("SL_M_State_BN.html")