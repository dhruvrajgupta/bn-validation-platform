## Evaluations will be run only for N Staging

## TODO: Run the script individual, right now it triggers with streamlit run
import streamlit as st

from utils.db import get_model_by_name
from utils.file import build_network
from utils.edges import edge_dependency_check

correct_edges = []
incorrect_edges = []

def display_valid_edges(model):
    edges = model.edges()
    for edge in edges:
        # Only consider edges that have passed rule based validation checks
        if not edge_dependency_check(edge, nodes_contents):
            continue

        incorrect_edges.append(edge)
        correct_edges.append((edge[1],edge[0]))

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("**Incorrect Edges:**")
            for inc_e in incorrect_edges:
                st.write(inc_e)

    with col2:
        with st.container(border=True):
            st.markdown("**Correct Edges:**")
            for c_e in correct_edges:
                st.write(c_e)


##### START OF PAGE #####

st.markdown("#### Evaluations on Modified BN (Reversed Edges of Original Network)")

model_name = "Lymph Node Staging of the TNM Staging of Laryngeal Cancer (WIP)"
st.markdown(f"**Selected Model: `{model_name}`**")
model = get_model_by_name(model_name)

if not model:
    st.write("**Please select a Model to run evaluations.**")
else:
    try:
        nodes_contents = model['nodes_content']
        model_bn = build_network(nodes_contents)
        st.info(model_bn)

        from utils.models import reverse_bayesian_network
        reversed_bn = reverse_bayesian_network(model_bn)

    except Exception as e:
        st.error(f"ERROR: \n{str(e)}")

    with st.container(border=True):
        st.markdown("**Valid Edges based on Edge Dependencies schema**")
        display_valid_edges(reversed_bn)

    if st.checkbox("Only using Node Identifiers and causal verb `causes`"):
        with st.container(border=True):
            from utils.evaluation_functions import baseline_only_node_id_causes
            baseline_only_node_id_causes(incorrect_edges)