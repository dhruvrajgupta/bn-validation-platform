import streamlit as st

from utils.db import save_model, get_models
from utils.file import extract_xdsl_content

st.set_page_config(
    layout="wide",
    page_title="Models"
)

with st.container(border=True):
    file_content = None

    st.write("**New Model :**")
    uploaded_file = st.file_uploader("Choose a file", type=["xdsl"])

    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8")
        nodes_contents = extract_xdsl_content(file_content)

    if file_content:
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
                        uploaded_file = None

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