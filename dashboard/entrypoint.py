import streamlit as st

##### Pages

## Instructions Manual
instructions_manual = st.Page("page_views/👋_Instructions_Manual.py")

## Models
new_model = st.Page("page_views/models/new_model.py", title="New Model")
# label_descriptions_nodes_contents = st.Page("page_views/models/label_description_nodes_contents.py", title="Label and Descriptions")

## Nodes


pg = st.navigation(
    {
        "Instructions Manual": [instructions_manual],
        "Models": [new_model],
    }
)

pg.run()