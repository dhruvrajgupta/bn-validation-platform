import streamlit as st

from utils.edges import edge_strength_cpds, cpd_rank_edges, g_test_rank_edges
from utils.db import get_model_by_name

@st.cache_data
def get_model_g_test(nodes_contents):
    from worker import task_edge_strength_stats
    import pandas as pd
    g_test = task_edge_strength_stats.delay(nodes_contents)
    g_test = pd.read_json(g_test.get(), orient="split")
    return g_test

@st.fragment
def frag_edge_cpd_rank(bn_model, key):
    with st.container(border=True):
        st.markdown("**Edge Strength (Using CPDs)**")
        distance_type = st.radio("Type of Distance:", ["Euclidean", "Hellinger", "J-Divergence", "CDF"],
                                 index=0, horizontal=True, key=f"{key} - CPDs Distance Type")

        edge_strength = edge_strength_cpds(bn_model, distance_type)
        ranked_edges = cpd_rank_edges(edge_strength)
        st.write(ranked_edges)

@st.fragment
def frag_g_test(model):
    with st.container(border=True):
        if model.get("dataset_filename", None):
            with st.spinner("Computing G-Test ..."):
                nodes_contents = get_model_by_name(model['name'])["nodes_content"]
                g_test = get_model_g_test(nodes_contents)
                g_test_ranked_edges = g_test_rank_edges(g_test)
                st.dataframe(g_test_ranked_edges)
        else:
            st.markdown("**G-Test requires a dataset file. No dataset file associated with this model.**")