import streamlit as st

from utils.db import get_models, get_model_by_name, update_model_label_description



##### START OF PAGE

st.markdown("#### XDSL File Contents")

model_selected_flag = False

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
    # st.write(model['file_content'])
    with st.spinner("Loading the XDSL file contents ..."):
        st.code(model['file_content'].decode("utf-8"), language="xmlDoc", line_numbers=True, wrap_lines=True)