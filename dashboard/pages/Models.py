import streamlit as st

from utils.db import save_model, get_models
from utils.file import extract_xdsl_content, xdsl_to_digraph, convert_to_vis
from utils.cycles import detect_cycles, get_cycles_digraph, print_cycles

st.set_page_config(
    layout="wide",
    page_title="Models"
)

@st.fragment
def frag_new_model():
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
            path = "./current_model.html"

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
                            from streamlit_js_eval import streamlit_js_eval
                            streamlit_js_eval(js_expressions="parent.window.location.reload()")
def main():

    with st.container(border=True):
        frag_new_model()

    with st.container(border=True):
        st.write("**Existing Models :**")

        model_type = st.radio("Type of Model", ["Ground Truth", "Work In Progress"], horizontal=True, label_visibility="collapsed")
        existing_models = get_models(type=model_type)

        for model in existing_models:
            with st.container(border=True):
                st.write(f"**Name :** {model['name']}")
                st.write("**Nodes Contents :**")
                st.json(model['nodes_content'], expanded=False)
                if st.checkbox("**View file content**", key=f"view_file_content - {model['name']}"):
                    st.code(model['file_content'], language="xmlDoc", line_numbers=True)

    with st.expander("Session State", expanded=False):
        st.json(st.session_state, expanded=False)


if __name__ == "__main__":
    main()