import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import time

from utils.db import get_models, get_model_by_name, update_model_label_description

model_selected_flag = False

st.markdown("#### Label, Descriptions and Nodes Contents")

model_type = st.radio("Type of Network *", ["Ground Truth", "Work In Progress"], index=0, horizontal=True)
available_models = get_models(type=model_type)

model_names = [model['name'] for model in available_models]

if model_type == "Ground Truth":
    selected_model = st.selectbox("Select a ground truth model", model_names,
                                     key="Selected GT Model", index=None)
    model = get_model_by_name(selected_model)
    if model:
        model_selected_flag = True

else:
    selected_model = st.selectbox("Select a work in progress model", model_names,
                                  key="Selected WIP Model", index=None)
    model = get_model_by_name(selected_model)
    if model:
        model_selected_flag = True

if not model_selected_flag:
    st.write("**Please select a Model.**")
else:
    with st.form(key=f"Update Label and Description of Network - {model['type']} - {model['name']}"):
        st.write(f"**Name :** {model['name']}")
        label = st.text_input("Label for the Network *",
                              placeholder="Please give a proper label for the Network. This is essential for Bayesian Network Validation",
                              value=model['label'])
        description = st.text_area("Description for the Network *",
                                   placeholder="Please give a proper description for the Network. This is essential for Bayesian Network Validation",
                                   value=model['description'])
        if "dataset_file" in model.keys():
            st.write(f"**Dataset filenames :** {model['dataset_filename']}")
        st.write("**Nodes Contents :**")
        st.json(model['nodes_content'], expanded=False)

        update_network = st.form_submit_button("Update Model")

        if update_network:
            if not label:
                st.caption(":red[Please enter the label for the Network.]")
            if not description:
                st.caption(":red[Please enter the description for the Network.]")

            if label and description:
                ##### Update the Database #####

                status = update_model_label_description(model['name'], model['type'], label, description)

                if status == "Same":
                    st.toast("Same Data already present in the Database. Not Added !!", icon="🚫")
                elif status == "Updated":
                    st.toast(f"Model: {model['name']} updated in the Database", icon="⚓")
                    time.sleep(1)
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")

with st.expander("Session States", expanded=False):
    st.json(st.session_state, expanded=False)