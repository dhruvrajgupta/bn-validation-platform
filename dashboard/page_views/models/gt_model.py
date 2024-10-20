import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import time

from utils.db import get_models, get_model_by_name, update_model_label_description

def select_callback():
    if "selected_gt_model" in st.session_state:
        st.session_state.gt_model = st.session_state.selected_gt_model

model_type = "Ground Truth"
ground_truth_models = get_models(type=model_type)

model_names = [model['name'] for model in ground_truth_models]
selected_gt_model = st.selectbox("Select a ground truth model", model_names,
                                 key="selected_gt_model",
                                 index= model_names.index(st.session_state.gt_model) if st.session_state.gt_model else None,
                                 on_change=select_callback)
st.session_state.gt_model = selected_gt_model
model = get_model_by_name(selected_gt_model)

if not model:
    st.write("**Please select a Ground Truth Model.**")
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