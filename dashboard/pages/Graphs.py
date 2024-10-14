import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

from utils.db import get_models, get_model_by_name
from utils.file import build_network

from streamlit_agraph.config import ConfigBuilder

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

        for node in bn_model.nodes:
            nodes.append(Node(id=node, label=node))
        for edge in bn_model.edges:
            edges.append(Edge(source=edge[0], target=edge[1]))

        # config = Config(width=1000, height=600, directed=True, physics=True, bgcolor="#001521")
        config_builder = ConfigBuilder(None)
        config = config_builder.build()
        val = agraph(nodes=nodes, edges=edges, config=config)

with col2:
    with st.container(border=True):
        st.markdown("**More Information**")
        st.write(val)