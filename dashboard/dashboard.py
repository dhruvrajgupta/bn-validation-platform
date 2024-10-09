import streamlit as st

from utils.db import get_node_descriptions
from utils.file import xdsl_to_digraph, extract_xdsl_content, convert_to_vis, convert_to_vis_super, build_network, convert_to_vis_markov
from utils.cycles import detect_cycles, get_cycles_digraph, print_cycles
from utils.edges import find_redundant_edges_multiple_paths, print_multiple_paths, redundant_edges_digraph, find_redundant_edges_d_separation, edge_strength_stats, edge_strength_cpds, \
    g_test_rank_edges, cpd_rank_edges

st.set_page_config(layout="wide")

if "d_separation_btn" not in st.session_state:
    st.session_state["d_separation_btn"] = False

if "working_model_cpds_distance_type" not in st.session_state:
    st.session_state["working_model_cpds_distance_type"] = "Euclidean"

if "ground_truth_cpds_distance_type" not in st.session_state:
    st.session_state["ground_truth_cpds_distance_type"] = "Euclidean"

if "gt_node_contents" not in st.session_state:
    st.session_state["gt_node_contents"] = None

if "bn_node_contents" not in st.session_state:
    st.session_state["bn_node_contents"] = None

def redundant_edge_d_separation_btn_callback():
    st.session_state["d_separation_btn"] = True

@st.cache_data
def get_super_model_g_test(nodes_contents):
    from worker import task_edge_strength_stats
    import pandas as pd
    g_test = task_edge_strength_stats.delay(nodes_contents)
    g_test = pd.read_json(g_test.get(), orient="split")
    return g_test

super_model, wip_model, bn_info = st.tabs(["Ground Truth Model", "Check Valid XDSL", "Bayesian Network Info"])

with super_model:
    selected_model = st.selectbox("Select a ground truth model", ["Mstage Laryngeal Cancer", "TNM Staging Laryngeal Cancer"])

    model_path_mapping = {
        "Mstage Laryngeal Cancer": "/usr/src/app/dashboard/ground_truth_models/Mstage.xdsl",
        "TNM Staging Laryngeal Cancer": "/usr/src/app/dashboard/ground_truth_models/validationPaper_TNM-Model_28012016.xdsl"
    }

    path = model_path_mapping[selected_model]

    with open(path, "r") as file:
        xdsl_content = file.read()
        ground_truth_graph = xdsl_to_digraph(xdsl_content)
        # st.session_state["ground_truth_graph"] = ground_truth_graph
        convert_to_vis_super(ground_truth_graph)

    # Building the BN for this super graph
    try:
        nodes_contents = extract_xdsl_content(xdsl_content)
        st.session_state.gt_node_contents = nodes_contents
        bn_model = build_network(nodes_contents)
        if bn_model.check_model():
            st.session_state["ground_truth_bn_model"] = bn_model
        st.write(bn_model)

    except Exception as e:
        st.error(f"ERROR: \n{str(e)}")

    with st.expander("View Graph"):
        path = "./super_model.html"
        HtmlFile = open(path, 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        st.components.v1.html(source_code, height = 1000, width=1000, scrolling=True)

    if "ground_truth_bn_model" in st.session_state:
        ## EDGE RANKINGS ##
        # 1. Using Dataset stats (G-Test)
        if st.checkbox("Compute Edge Strength (G-Test)"):
            with st.container(border=True):
                with st.spinner("Edge Strength (G-Test)"):
                    st.markdown("###### Edge Strength (G-Test)")
                    super_g_test = get_super_model_g_test(nodes_contents)
                    g_test_ranked_edges = g_test_rank_edges(super_g_test)
                    event = st.dataframe(
                            g_test_ranked_edges,
                            on_select="rerun",
                            selection_mode="single-row"
                        )
                    selection = event.selection
                    if len(selection["rows"]):
                        st.markdown("**Selected Row:**")
                        selected_row = selection["rows"][0]
                        st.write(g_test_ranked_edges.iloc[selected_row])
                        row_content = g_test_ranked_edges.iloc[selected_row].to_dict()

                        if st.checkbox("Show Nodes Descriptions"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Source:**")
                                source_desc = get_node_descriptions(row_content["source"])
                                if source_desc:
                                    st.write(source_desc)
                                else:
                                    st.write("No descriptions of the node in the database.")
                            with col2:
                                st.markdown("**Target:**")
                                source_desc = get_node_descriptions(row_content["target"])
                                if source_desc:
                                    st.write(source_desc)
                                else:
                                    st.write("No descriptions of the node in the database.")

        if st.checkbox("Compute Edge Strength (Using CPDs)"):
            with st.container(border=True):
                st.markdown("**Edge Strength (Using CPDs)**")
                distance_type_name = st.session_state["working_model_cpds_distance_type"]
                if distance_type_name == "Euclidean":
                    distance_type_index = 0
                elif distance_type_name == "Hellinger":
                    distance_type_index = 1
                elif distance_type_name == "J-Divergence":
                    distance_type_index = 2
                elif distance_type_name == "CDF":
                    distance_type_index = 3
                distance_type = st.radio("Type of Distance:", ["Euclidean", "Hellinger", "J-Divergence", "CDF"], index=distance_type_index, horizontal=True, key="ground_truth_cpds_distance_type")
                edge_strength = edge_strength_cpds(bn_model, distance_type)
                # with st.expander("Dataframe"):
                #     st.write(edge_strength)
                ranked_edges = cpd_rank_edges(edge_strength)
                st.write(ranked_edges)


    with st.expander(f"Session Info"):
        st.write(st.session_state)


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


    try:
        nodes_contents = extract_xdsl_content(file_content)
        st.session_state.bn_node_contents = nodes_contents
        bn_model = build_network(nodes_contents)
        if bn_model.check_model():
            st.session_state["bn_model"] = bn_model
        st.write(bn_model)

    except Exception as e:
        st.error(f"ERROR: \n{str(e)}")


    # 2. Using D-separation (Needs a Bayesian Network)
    if "bn_model" in st.session_state:
        st.button("Compute Redundant Edges (D-separation)", on_click=redundant_edge_d_separation_btn_callback, disabled=st.session_state["d_separation_btn"], type="primary")

        with st.status("Redundant Edges (D-separation)"):
            if st.session_state["d_separation_btn"]:
                # redundant_edges_d_separation = run_in_background(long_computation, 5)
                from worker import task_compute_redundant_edges_d_separation
                # This Process is computationally expensive. Needs to be made into a background task (eg, TNM Staging Laryngeal Cancer - 54 mins approx)
                redundant_edges_d_separation = task_compute_redundant_edges_d_separation.delay(nodes_contents)
                redundant_edges_d_separation = redundant_edges_d_separation.get()

                if redundant_edges_d_separation:
                    st.error(f"{len(redundant_edges_d_separation)} redundant edges detected")
                    st.write(redundant_edges_d_separation)

                    # FOR TEMP PURPOSE MARKOV VISUALIZATION
                    from pgmpy.models import BayesianNetwork

                    graph = BayesianNetwork([
                        ('Burglary', 'Alarm'),
                        ('Earthquake', 'Alarm'),
                        ('Alarm', 'JohnCalls'),
                        ('Alarm', 'MaryCalls'),
                        ('Burglary', 'Earthquake'),  # <-- Redundant Edge
                        # Burglary and Earthquake were already independent in the original graph unless conditioned on Alarm.
                        # The new edge does not change this independence, as the two variables are still blocked by the collider at the Alarm unless the Alarm is observed.
                        # Therefore, this edge does not add new information or change the probabilistic relationships between variables. It’s redundant in terms of the conditional independencies in the graph.
                    ])

                    vis_set = []
                    for r_edges in redundant_edges_d_separation:
                        markov_source = r_edges["markov_source"]
                        markov_target = r_edges["markov_target"]
                        vis_set.extend(markov_source)
                        vis_set.extend(markov_target)

                    vis_set = set(vis_set)
                    vis_graph_edges = []

                    for node in vis_set:
                        for edge in graph.edges():
                            if node in edge:
                                if edge not in vis_graph_edges:
                                    vis_graph_edges.append(edge)

                    vis_graph = BayesianNetwork(vis_graph_edges)

                    convert_to_vis_markov(vis_graph)
                    path = "./markov.html"

                    HtmlFile = open(path, 'r', encoding='utf-8')
                    source_code = HtmlFile.read()
                    st.components.v1.html(source_code, height=1000, width=1000, scrolling=True)

                else:
                    st.success("No redundant edges detected.")



    if "bn_model" in st.session_state:
        ## EDGE RANKINGS ##
        # 1. Using Dataset stats (G-Test)
        if st.button("Compute Edge Strength (G-Test)", type="primary", key="g_test_btn_wip"):
            with st.status("Edge Strength (G-Test)"):
                from worker import task_edge_strength_stats
                import pandas as pd
                edge_strength = task_edge_strength_stats.delay(nodes_contents)
                edge_strength = pd.read_json(edge_strength.get(), orient="split")
                with st.expander("Dataframe"):
                    st.write(edge_strength)
                with st.expander("Edge Rankings"):
                    ranked_edges = g_test_rank_edges(edge_strength)
                    st.write(ranked_edges)

        with st.expander("Edge Strength (Using CPDs)"):
            distance_type_name = st.session_state["ground_truth_cpds_distance_type"]
            if distance_type_name == "Euclidean":
                distance_type_index = 0
            elif distance_type_name == "Hellinger":
                distance_type_index = 1
            elif distance_type_name == "J-Divergence":
                distance_type_index = 2
            elif distance_type_name == "CDF":
                distance_type_index = 3
            distance_type = st.radio("Type of Distance:", ["Euclidean", "Hellinger", "J-Divergence", "CDF"], index=0, horizontal=True, key="working_model_cpds_distance_type")
            edge_strength = edge_strength_cpds(bn_model, distance_type)
            with st.expander("Dataframe"):
                st.write(edge_strength)
            with st.expander("Edge Rankings"):
                ranked_edges = cpd_rank_edges(edge_strength)
                st.write(ranked_edges)


    with st.expander(f"Session Info"):
        st.write(st.session_state)


# with st.sidebar:
#     with st.echo():
#         st.write("This code will be printed to the sidebar.")

#     with st.spinner("Loading..."):
#         time.sleep(5)
#     st.success("Done!")