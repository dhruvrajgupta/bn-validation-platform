import streamlit as st
# import time
from utils.file import xdsl_to_digraph, extract_xdsl_content, convert_to_vis, convert_to_vis_super, build_network
from utils.cycles import detect_cycles, get_cycles_digraph, print_cycles
from utils.edges import find_redundant_edges_multiple_paths, print_multiple_paths, redundant_edges_digraph, find_redundant_edges_d_separation
from utils.models import get_horrible_model

st.set_page_config(layout="wide")

super_model, wip_model, bn_info = st.tabs(["Super Model", "Check Valid XDSL", "Bayesian Network Info"])

with super_model:
    selected_model = st.selectbox("Select a ground truth model", ["Mstage Laryngeal Cancer", "TNM Staging Laryngeal Cancer"])

    model_path_mapping = {
        "Mstage Laryngeal Cancer": "./ground_truth_models/Mstage.xdsl",
        "TNM Staging Laryngeal Cancer": "./../scripts/ST-10.xdsl"
    }

    path = model_path_mapping[selected_model]

    with open(path, "r") as file:
        xdsl_content = file.read()
        graph = xdsl_to_digraph(xdsl_content)
        st.session_state["super_graph"] = graph
        convert_to_vis_super(graph)
    
    with st.expander("View Graph"):
        path = "./super_model.html"
        HtmlFile = open(path, 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        st.components.v1.html(source_code, height = 1000, width=1000, scrolling=True)


with wip_model:

    uploaded_file = st.file_uploader("Choose a file", type=["xdsl"])

    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8")
        graph = xdsl_to_digraph(file_content)
        st.write(graph)
        st.session_state["graph"] = graph

    # Using the SL model for testing purposes
    # graph is a DiGraph
    # graph = get_horrible_model(threshold=0)

        with st.expander(f"View Graph"):
            convert_to_vis(graph)
            path = "./current_model.html"

            HtmlFile = open(path, 'r', encoding='utf-8')
            source_code = HtmlFile.read()
            st.components.v1.html(source_code, height = 1000, width=1000, scrolling=True)

        ## DETECT CYCLES ##
        cycles = detect_cycles(graph)
        if len(cycles) > 0:
            with st.expander(f"View Cycles: {len(cycles)} detected"):
                graph, cycle_list = st.columns(2)

                with graph:
                    get_cycles_digraph(cycles)
                with cycle_list:
                    for cycle_print in print_cycles(cycles):
                        st.text(cycle_print)

            st.error("!! Cycles detected, Can't proceed with Creation of Bayesian Network. !!")

        else:
            st.success("No cycles detected, Can proceed with Creation of Bayesian Network")
            st.success("More Information on the **'Bayesian Network Info'** tab")


    with st.expander(f"Session Info"):
        st.write(st.session_state)


with bn_info:
    ## CHECK MULTIPLE EDGES BETWEEN NODES ##

    if "graph" not in st.session_state:
        st.error("No graph found, Please upload a XDSL file first")
        st.stop()

    graph = st.session_state["graph"]

    ## DETECT REDUNDANT EDGES ##
    # 1. Using Multiple Paths
    redundant_edges_multiple_paths = find_redundant_edges_multiple_paths(graph)
    if redundant_edges_multiple_paths:
        with st.expander(f"View Redundant Edges (Multiple Paths): {len(redundant_edges_multiple_paths)} detected"):
            redundant_edges_digraph(graph, redundant_edges_multiple_paths)
            st.text(print_multiple_paths(graph, redundant_edges_multiple_paths))
    else:
        st.success("No Multiple Paths detected.")

    # 2. Using D-separation (Needs to be converted into Bayesian Network)
    try:
        nodes_contents = extract_xdsl_content(file_content)
        bn_model = build_network(nodes_contents)
        if bn_model.check_model():
            st.session_state["bn_model"] = bn_model
        st.write(bn_model)

        # This Process is computationally expensive. Needs to be made into a background task (eg, TNM Staging Laryngeal Cancer - 54 mins approx)
        # redundant_edges_d_separation = find_redundant_edges_d_separation(bn_model, debug=True)
        # st.write(redundant_edges_d_separation)
        # if redundant_edges_d_separation:
        #     with st.expander(f"View Redundant Edges (D-separation): {len(redundant_edges_d_separation)} detected"):
        #         redundant_edges_digraph(bn_model, redundant_edges_d_separation)
        # else:
        #     st.success("No D-separation detected.")
    except Exception as e:
        st.error(f"ERROR: \n{str(e)}")



    # nodes_contents = extract_xdsl_content(file_content)


    with st.expander(f"Session Info"):
        st.write(st.session_state)


# with st.sidebar:
#     with st.echo():
#         st.write("This code will be printed to the sidebar.")

#     with st.spinner("Loading..."):
#         time.sleep(5)
#     st.success("Done!")