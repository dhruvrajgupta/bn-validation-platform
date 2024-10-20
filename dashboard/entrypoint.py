import streamlit as st

st.set_page_config(layout="wide")

if "gt_model" not in st.session_state:
    st.session_state.gt_model = None

if "wip_model" not in st.session_state:
    st.session_state.wip_model = None

with st.sidebar:
    st.write(f"**Ground Truth Model:**  `{st.session_state.gt_model}`")
    st.write(f"**Work In Progress Model:** `{st.session_state.wip_model}`")

##### Pages

## Instructions Manual
instructions_manual = st.Page("page_views/👋_Instructions_Manual.py", default=True)

## Models
new_model = st.Page("page_views/models/new_model.py", title="New Model")
gt_model = st.Page("page_views/models/gt_model.py", title="Ground Truth Model")
# label_descriptions_nodes_contents = st.Page("page_views/models/label_description_nodes_contents.py", title="Label and Descriptions")

## Nodes


pg = st.navigation(
    {
        "Instructions Manual": [instructions_manual],
        "Models": [new_model, gt_model],
    }
)

pg.run()