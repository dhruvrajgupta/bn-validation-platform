import streamlit as st

st.set_page_config(layout="wide")

##### Pages

## Instructions Manual
instructions_manual = st.Page("page_views/👋_Instructions_Manual.py", default=True)

## Models
new_model = st.Page("page_views/models/new_model.py", title="New Model")
gt_model = st.Page("page_views/models/label_descriptions_nodes_contents.py", title="Label, Descriptions and Nodes Contents")
# label_descriptions_nodes_contents = st.Page("page_views/models/label_description_nodes_contents.py", title="Label and Descriptions")

## Nodes


pg = st.navigation(
    {
        "Instructions Manual": [instructions_manual],
        "Models": [new_model, gt_model],
    }
)

pg.run()