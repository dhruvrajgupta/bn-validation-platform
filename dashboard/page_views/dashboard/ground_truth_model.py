import streamlit as st

from utils.file import xdsl_to_digraph, convert_to_vis_super, build_network
from utils.db import get_models, get_model_by_name, update_model_label_description
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


#### START OF PAGE

st.markdown("#### Ground Truth Model")

model_type = "Ground Truth"
available_models = get_models(type=model_type)

model_names = [model['name'] for model in available_models]

selected_model = st.selectbox("Select a ground truth model", model_names,
                                 key="Selected GT Model", index=None)
model = get_model_by_name(selected_model)

if not model:
    st.write("**Please select a Ground Truth Model.**")
else:
    selected_gt_model_graph = xdsl_to_digraph(model['file_content'])
    convert_to_vis_super(selected_gt_model_graph)

    # Building the BN for this super graph
    try:
        nodes_contents = model['nodes_content']
        bn_model = build_network(nodes_contents)
        st.info(bn_model)

    except Exception as e:
        st.error(f"ERROR: \n{str(e)}")

    with st.expander("View Graph"):
        path = "dashboard/pyvis_htmls/super_model.html"
        HtmlFile = open(path, 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        st.components.v1.html(source_code, height=1000, width=1000, scrolling=True)

    ##### EDGE RANKINGS #####
    st.markdown("#### Edge Rankings")
    with st.container(border=True):
        # 1. Using Dataset stats (G-Test)
        if st.checkbox("Compute Edge Strength (G-Test)"):
            # TODO: Link with appropriate Dataset
            # frag_g_test(nodes_contents, key="gt_g_test")
            pass

        # 2. Using CPDs of the Bayesian Network
        if st.checkbox("Compute Edge Strength (Using CPDs)", key="gt_cpd_rank"):
            frag_edge_cpd_rank(bn_model, key="Ground Truth Model")