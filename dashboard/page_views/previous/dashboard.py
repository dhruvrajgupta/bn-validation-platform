import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

# st.set_page_config(
#     layout="wide",
#     page_title="Dashboard"
# )

from utils.db import get_node_descriptions, get_models, get_model_by_name, save_model
from utils.file import xdsl_to_digraph, extract_xdsl_content, \
    convert_to_vis_super, build_network, convert_to_vis_markov, convert_to_vis
from utils.edges import find_redundant_edges_multiple_paths, \
    print_multiple_paths, redundant_edges_digraph, edge_strength_cpds, \
    g_test_rank_edges, cpd_rank_edges
from utils.cycles import detect_cycles, get_cycles_digraph, print_cycles

from pgmpy.models import BayesianNetwork

@st.cache_data
def get_super_model_g_test(nodes_contents):
    from worker import task_edge_strength_stats
    import pandas as pd
    g_test = task_edge_strength_stats.delay(nodes_contents)
    g_test = pd.read_json(g_test.get(), orient="split")
    return g_test

@st.fragment
def frag_g_test(nodes_contents, key):
    ### Blocker - Pre-requisites - need to have a dataset
    with st.container(border=True):
        with st.spinner("Edge Strength (G-Test)"):
            st.markdown("**Edge Strength (G-Test)**")
            g_test = get_super_model_g_test(nodes_contents)
            g_test_ranked_edges = g_test_rank_edges(g_test)

            grid_builder = GridOptionsBuilder.from_dataframe(g_test_ranked_edges)
            grid_options = grid_builder.build()

            grid_options['pagination'] = True
            grid_options['paginationPageSize'] = 10
            grid_options['paginationPageSizeSelector'] = [10, 20, 30, 40, 50]
            grid_options['rowHeight'] = 35
            grid_options['rowSelection'] = "single"

            ag_grid_return = AgGrid(g_test_ranked_edges, gridOptions=grid_options, key=key)
            selected_row = ag_grid_return.selected_data

            if selected_row is not None:
                st.markdown("**Selected Row:**")
                st.write(selected_row)

                row_content = selected_row.to_dict()

                if st.checkbox("Show Nodes Descriptions", key=f"node-desc-{key}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Source:**")
                        source_desc = get_node_descriptions(row_content["source"]["0"])
                        if source_desc:
                            st.write(source_desc)
                        else:
                            st.write("No descriptions of the node in the database.")
                    with col2:
                        st.markdown("**Target:**")
                        source_desc = get_node_descriptions(row_content["target"]["0"])
                        if source_desc:
                            st.write(source_desc)
                        else:
                            st.write("No descriptions of the node in the database.")

@st.fragment
def frag_edge_cpd_rank(bn_model, key):
    with st.container(border=True):
        st.markdown("**Edge Strength (Using CPDs)**")
        distance_type = st.radio("Type of Distance:", ["Euclidean", "Hellinger", "J-Divergence", "CDF"],
                                 index=0, horizontal=True, key=f"{key}_cpds_distance_type")

        edge_strength = edge_strength_cpds(bn_model, distance_type)
        ranked_edges = cpd_rank_edges(edge_strength)
        st.write(ranked_edges)

@st.fragment
def frag_new_model():
    from streamlit_js_eval import streamlit_js_eval
    # if st.button("Reload page"):
    #     streamlit_js_eval(js_expressions="parent.window.location.reload()")
    file_content = None

    st.write("**New Model :**")
    uploaded_file = st.file_uploader("Choose a file", type=["xdsl"])

    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8")
        nodes_contents = extract_xdsl_content(file_content)
        wip_model_graph = xdsl_to_digraph(file_content)

    # Using the SL model for testing purposes
    # graph is a DiGraph
    # graph = get_horrible_model(threshold=0)

    if file_content:
        with st.expander(f"View Graph"):
            convert_to_vis(wip_model_graph)
            path = "../current_model.html"

            HtmlFile = open(path, 'r', encoding='utf-8')
            source_code = HtmlFile.read()
            st.components.v1.html(source_code, height = 1000, width=1000, scrolling=True)

        # DETECT CYCLES ##
        cycles = detect_cycles(wip_model_graph)
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
            st.success('No cycles detected, can proceed with Saving model as **"Work In Progress"**. After saving more Information on the **"Work In Progress"** tab.')

            ##### SECTION FOR SAVING THE WIP MODEL #####
            if st.checkbox("View contents of XDSL file"):
                with st.container(border=True):
                    st.json(nodes_contents, expanded=False)

            with st.form(key="save-network", border=False):
                name = st.text_input("Name *")
                type = st.radio("Type of Network *", ["Ground Truth", "Work In Progress"], index=None)

                submitted = st.form_submit_button("Submit")

                if submitted:
                    if not name:
                        st.caption(":red[Please enter Name.]")
                    if not type:
                        st.caption(":red[Please select the the type of Network.]")

                    if name and type:
                        ##### Save to Database #####
                        status = save_model(name, type, nodes_contents, file_content)

                        if status == "Present":
                            st.caption(":red[A model already exists with the same name, Please choose a different name for the model.]")
                        elif status == "Failed":
                            st.toast(f'Error in saving **"{name}"** model of type **"{type}"**.', icon="❌")
                        elif status == "Succeded":
                            st.toast(f'**"{name}"** model of type **"{type}"** has been saved.', icon="✅")
                            import time
                            time.sleep(1)
                            streamlit_js_eval(js_expressions="parent.window.location.reload()")

# def main():
if "wip_cpds_distance_type" not in st.session_state:
    st.session_state["wip_cpds_distance_type"] = "Euclidean"

if "gt_cpds_distance_type" not in st.session_state:
    st.session_state["gt_cpds_distance_type"] = "Euclidean"

super_model, wip_model, check_valid_xdsl = st.tabs(["Ground Truth Model", "Work In Progress Models", "Check Valid XDSL"])

##### GROUND TRUTH MODEL TAB #####
with super_model:
    ground_truth_models = get_models("Ground Truth")
    model_names = [model['name'] for model in ground_truth_models]
    selected_gt_model = st.selectbox("Select a ground truth model", model_names, key="select_gt_models", index=None)

    selected_gt_model_dict = get_model_by_name(selected_gt_model)

    if not selected_gt_model:
        st.write("**Please select a Ground Truth Model.**")
    else:
        selected_gt_model_graph = xdsl_to_digraph(selected_gt_model_dict['file_content'])
        convert_to_vis_super(selected_gt_model_graph)

        # Building the BN for this super graph
        try:
            nodes_contents = selected_gt_model_dict['nodes_content']
            bn_model = build_network(nodes_contents)
            st.info(bn_model)

        except Exception as e:
            st.error(f"ERROR: \n{str(e)}")

        with st.expander("View Graph"):
            path = "dashboard/pyvis_htmls/super_model.html"
            HtmlFile = open(path, 'r', encoding='utf-8')
            source_code = HtmlFile.read()
            st.components.v1.html(source_code, height = 1000, width=1000, scrolling=True)

        ##### EDGE RANKINGS #####
        st.markdown("#### Edge Rankings")
        with st.container(border=True):
            # 1. Using Dataset stats (G-Test)
            if st.checkbox("Compute Edge Strength (G-Test)"):
                frag_g_test(nodes_contents, key="gt_g_test")

            # 2. Using CPDs of the Bayesian Network
            if st.checkbox("Compute Edge Strength (Using CPDs)", key="gt_cpd_rank"):
                frag_edge_cpd_rank(bn_model, key="gt")


##### WORK IN PROGRESS TAB #####
with wip_model:
    wip_models = get_models("Work In Progress")
    model_names = [model['name'] for model in wip_models]
    selected_wip_model = st.selectbox("Select a ground truth model", model_names, key="select_wip_models", index=None)

    if not selected_wip_model:
        st.write("**Please select a Work in Progress Model.**")
    else:
        selected_wip_model_dict = get_model_by_name(selected_wip_model)

        ## First get the bayesian network of the xdsl file
        try:
            nodes_contents = extract_xdsl_content(selected_wip_model_dict['file_content'])
            bn_model = build_network(nodes_contents)
            st.info(bn_model)

        except Exception as e:
            st.error(f"ERROR: \n{str(e)}")

        ## DETECT REDUNDANT EDGES ##
        st.markdown("#### Redundant Edges")
        # 1. Using Multiple Paths
        with st.container(border=True):
            st.markdown("**Multiple Paths**")
            selected_wip_model_graph = xdsl_to_digraph(selected_wip_model_dict['file_content'])
            redundant_edges_multiple_paths = find_redundant_edges_multiple_paths(selected_wip_model_graph)
            if redundant_edges_multiple_paths:
                if st.checkbox(f"Edges with multiple paths - :red[{len(redundant_edges_multiple_paths)} detected]"):
                    with st.container(border=True):
                        redundant_edges_digraph(selected_wip_model_graph, redundant_edges_multiple_paths)
                        st.text(print_multiple_paths(selected_wip_model_graph, redundant_edges_multiple_paths))
            else:
                st.success("No Multiple Paths detected.")

        # 2. Using D-separation (Needs a Bayesian Network)
        with st.container(border=True):
            st.markdown("**Using D-Separation technique**")

            if bn_model:
                st.write("**:blue[Computing Redundant edges using D-Separation very computationally expensive. Use only when needed. !!]**")

                if st.checkbox("Click the checkbox to run computations for finding redundant edges using D-separation"):
                    with st.spinner("Running finding Redundant Edges (D-separation) ..."):
                        from worker import task_compute_redundant_edges_d_separation
                        # This Process is computationally expensive. Needs to be made into a background task (worker) (eg, TNM Staging Laryngeal Cancer - 54 mins approx)
                        redundant_edges_d_separation = task_compute_redundant_edges_d_separation.delay(nodes_contents)
                        redundant_edges_d_separation = redundant_edges_d_separation.get()

                        if redundant_edges_d_separation:
                            st.error(f"{len(redundant_edges_d_separation)} redundant edges detected")
                            st.json(redundant_edges_d_separation, expanded=False)

                            # FOR TEMP PURPOSE MARKOV VISUALIZATION
                            bn_model = BayesianNetwork([
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
                                for edge in bn_model.edges():
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

        ## EDGE RANKINGS ##
        st.markdown("#### Edge Rankings")
        with st.container(border=True):
            # 1. Using Dataset stats (G-Test)
            if st.checkbox("Compute Edge Strength (G-Test) "):
                frag_g_test(nodes_contents, key="wip_g_test")

            # 2. Using CPDs of the Bayesian Network
            if st.checkbox("Compute Edge Strength (Using CPDs)", key="wip_cpd_rank"):
                frag_edge_cpd_rank(bn_model, key="wip")

##### CHECK VALID XDSL TAB #####
with check_valid_xdsl:
    with st.container(border=True):
        frag_new_model()


with st.expander(f"Session Info"):
    st.write(st.session_state)

# with st.sidebar:
#     with st.echo():
#         st.write("This code will be printed to the sidebar.")

#     with st.spinner("Loading..."):
#         time.sleep(5)
#     st.success("Done!")

# if __name__ == "__main__":
#     main()