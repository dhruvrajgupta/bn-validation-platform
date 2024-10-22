import streamlit as st

st.set_page_config(layout="wide")

##### Pages

## Instructions Manual
instructions_manual = st.Page("page_views/instructions_manual.py", title="Instructions Manual", default=True)

## Models
new_model = st.Page("page_views/models/new_model.py", title="New Model")
gt_model = st.Page("page_views/models/label_descriptions_nodes_contents.py", title="Label, Descriptions and Nodes Contents")

## Nodes
nodes_descriptions = st.Page("page_views/nodes_descriptions.py", title="Nodes Descriptions")

## Edge Rationality
edge_rationality = st.Page("page_views/edge_rationality.py", title="Edge Rationality")

pg = st.navigation(
    {
        "Instructions Manual": [instructions_manual],
        "Models": [new_model, gt_model],
        "Nodes Descriptions": [nodes_descriptions],
        "Edge Rationality": [edge_rationality]
    }
)

pg.run()