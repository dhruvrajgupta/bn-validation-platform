import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import time

from utils.db import save_model, get_models, get_model_dataset_file, update_model_label_description
from utils.file import extract_xdsl_content, xdsl_to_digraph, convert_to_vis
from utils.cycles import detect_cycles, get_cycles_digraph, print_cycles

file_content = None
save_flag = False

st.write("#### New Model")
with st.container(border=True):
    uploaded_file_content = st.file_uploader("Choose a file", type=["xdsl"])

    if uploaded_file_content:
        file_content = uploaded_file_content.read().decode("utf-8")
        nodes_contents = extract_xdsl_content(file_content)
        wip_model_graph = xdsl_to_digraph(file_content)

    # Using the SL model for testing purposes
    # graph is a DiGraph
    # graph = get_horrible_model(threshold=0)

    if file_content:
        with st.expander(f"View Graph"):
            convert_to_vis(wip_model_graph)
            path = "dashboard/pyvis_htmls/current_model.html"

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

            st.error("!! Cycles detected, Can't proceed with saving this Bayesian Network. !!")

        else:
            save_flag = True
            st.success('No cycles detected, can proceed with Saving model as **"Work In Progress"**. After saving more Information on the **"Work In Progress"** tab.')

            ##### SECTION FOR SAVING THE WIP MODEL #####
            if st.checkbox("View contents of XDSL file"):
                with st.container(border=True):
                    st.json(nodes_contents, expanded=False)

if save_flag:
    st.write("#### Save Model")
    with st.form(key="save-network", border=True):
        name = st.text_input("Name *")
        type = st.radio("Type of Network *", ["Ground Truth", "Work In Progress"], index=None)
        label = st.text_input("Label for the Network *", placeholder="Please give a proper label for the Network. This is essential for Bayesian Network Validation")
        description = st.text_area("Description for the Network *", placeholder="Please give a proper description for the Network. This is essential for Bayesian Network Validation", height=400)
        uploaded_dataset_file = st.file_uploader("Upload the Dataset :", type=["csv"])


        submitted = st.form_submit_button("Submit")

        if submitted:
            if not name:
                st.caption(":red[Please enter Name.]")
            if not type:
                st.caption(":red[Please select the type of Network.]")
            if not label:
                st.caption(":red[Please enter the label for the Network.]")
            if not description:
                st.caption(":red[Please enter the description for the Network.]")

            if name and type and label and description:
                ##### Save to Database #####
                status = save_model(name, type, nodes_contents, uploaded_file_content, label, description, uploaded_dataset_file)

                if status == "Present":
                    st.caption(":red[A model already exists with the same name, Please choose a different name for the model.]")
                elif status == "Failed":
                    st.toast(f'Error in saving **"{name}"** model of type **"{type}"**.', icon="❌")
                elif status == "Succeded":
                    st.toast(f'**"{name}"** model of type **"{type}"** has been saved.', icon="✅")
                    time.sleep(1)
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")
