import streamlit as st

from utils.file import xdsl_to_digraph, convert_to_vis_super, build_network
from utils.db import get_models, get_model_by_name, update_model_label_description
from utils.components import frag_edge_cpd_rank
from utils.edges import edge_schema_validation_check

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


    ##### EDGE SCHEMA VALIDATION CHECK #####
    st.markdown("#### Edge Schema Validation Check")
    with st.container(border=True):
        if st.checkbox("Check Schema Valid Edges"):
            schema_validation_result = edge_schema_validation_check(bn_model, nodes_contents)
            st.markdown("**Valid Edges:**")
            st.json(schema_validation_result["valid"], expanded=False)
            st.markdown("**Invalid Edges:**")
            st.json(schema_validation_result["invalid"], expanded=False)

    ##### NODE TYPES #####
    st.markdown("#### Node Types")
    with st.container(border=True):
        if st.checkbox("Check Node Types"):
            node_type = st.radio("Select Node Type:", ["Patient Situation", "Examination Result", "Decision Node", "Unknown"], index=0, horizontal=True)
            from utils.nodes import get_nodes_by_type
            nodes_by_type = get_nodes_by_type(node_type, nodes_contents)
            st.write(nodes_by_type)