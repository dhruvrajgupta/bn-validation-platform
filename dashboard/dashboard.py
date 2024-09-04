import streamlit as st
# import time
from utils.file import xdsl_to_digraph, extract_xdsl_content
from utils.cycles import convert_to_vis, detect_cycles, get_cycles_digraph, print_cycles
from utils.edges import find_redundant_edges, print_multiple_paths, redundant_edges_digraph

st.set_page_config(layout="wide")

super_model, wip_model, bn_info = st.tabs(["Super Model", "Check Valid XDSL", "Bayesian Network Info"])

with super_model:
    st.header("A cat")
    st.image("https://static.streamlit.io/examples/cat.jpg", width=200)


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

    redundant_edges = find_redundant_edges(graph)
    if redundant_edges:
        with st.expander(f"View Redundant Edges: {len(redundant_edges)} detected"):
            redundant_edges_digraph(graph, redundant_edges)
            st.text(print_multiple_paths(graph, redundant_edges))


    # nodes_contents = extract_xdsl_content(file_content)


    with st.expander(f"Session Info"):
        st.write(st.session_state)


# with st.sidebar:
#     with st.echo():
#         st.write("This code will be printed to the sidebar.")

#     with st.spinner("Loading..."):
#         time.sleep(5)
#     st.success("Done!")