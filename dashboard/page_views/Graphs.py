import streamlit as st

from utils.db import get_models, get_model_by_name
from utils.file import build_network
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle

st.set_page_config(
    layout="wide",
    page_title="Models"
)

model_type = st.radio("Type of Model", ["Ground Truth", "Work In Progress"], horizontal=True,
                      label_visibility="collapsed")
existing_models = get_models(type=model_type)
model_names = [model['name'] for model in existing_models]
selected_model = st.selectbox("Select a ground truth model", model_names, key="select_gt_models", index=None)
selected_model_dict = get_model_by_name(selected_model)

bn_model = build_network(selected_model_dict["nodes_content"])

col1, col2 = st.columns([0.80, 0.20])

val = None

with col1:
    with st.container(border=True):
        st.markdown("**Graph**")
        nodes = []
        edges = []
        for node in bn_model.nodes():
            nodes.append({"data": {"id": node, "label": "PERSON"}})

        for idx, edge in enumerate(bn_model.edges()):
            if edge[0] == "other_location_M_diagnostic__patient" or edge[1] == "other_location_M_diagnostic__patient":
                st.write(edge)
            edges.append({"data": {"id": idx, "label": "FOLLOWS", "source": edge[0], "target": edge[1]}})

        # Sample Data
        elements = {
            "nodes": 
            # [
            #     {"data": {"id": 1, "label": "PERSON", "name": "Streamlit"}},
            #     {"data": {"id": 2, "label": "PERSON", "name": "Hello"}},
            #     {"data": {"id": 3, "label": "PERSON", "name": "World"}},
            #     {"data": {"id": 4, "label": "POST", "content": "x"}},
            #     {"data": {"id": 5, "label": "POST", "content": "y"}},
            # ]
            nodes
            ,
            "edges": 
            # [
                # {"data": {"id": 6, "label": "FOLLOWS", "source": 1, "target": 2}},
                # {"data": {"id": 7, "label": "FOLLOWS", "source": 2, "target": 3}},
                # {"data": {"id": 8, "label": "POSTED", "source": 3, "target": 4}},
                # {"data": {"id": 9, "label": "POSTED", "source": 1, "target": 5}},
                # {"data": {"id": 10, "label": "QUOTES", "source": 5, "target": 4}},
            # ]
            edges,
        }

        # Style node & edge groups
        node_styles = [
            NodeStyle("PERSON", "#FF7F3E", "name", "person"),
            NodeStyle("POST", "#2A629A", "content", "description"),
        ]

        edge_styles = [
            EdgeStyle("FOLLOWS", caption='label', directed=True),
            EdgeStyle("POSTED", caption='label', directed=True),
            EdgeStyle("QUOTES", caption='label', directed=True),
        ]

        # Render the component
        st.markdown("### st-link-analysis: Example")
        st_link_analysis(elements, "cose", node_styles, edge_styles)

with col2:
    with st.container(border=True):
        st.markdown("**More Information**")
        st.write(val)