import streamlit as st

from utils.edges import edge_strength_cpds, cpd_rank_edges

@st.fragment
def frag_edge_cpd_rank(bn_model, key):
    with st.container(border=True):
        st.markdown("**Edge Strength (Using CPDs)**")
        distance_type = st.radio("Type of Distance:", ["Euclidean", "Hellinger", "J-Divergence", "CDF"],
                                 index=0, horizontal=True, key=f"{key} - CPDs Distance Type")

        edge_strength = edge_strength_cpds(bn_model, distance_type)
        ranked_edges = cpd_rank_edges(edge_strength)
        st.write(ranked_edges)