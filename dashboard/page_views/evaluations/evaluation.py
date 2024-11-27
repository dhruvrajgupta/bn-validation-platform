## Evaluations will be run only for N Staging

## TODO: Run the script individual, right now it triggers with streamlit run
import streamlit as st

from utils.db import get_model_by_name, save_evaluation, get_evaluation, get_models
from utils.file import build_network
from utils.edges import edge_dependency_check

from utils.evaluation_functions import baseline_only_node_id_causes

correct_edges = []
incorrect_edges = []

def save_to_db_callback(eval_name, model_name, llm_model_name, eval_res_dict):
    status = save_evaluation(eval_name, model_name, llm_model_name, eval_res_dict)
    if status == "Same":
        st.toast("Same Data already present in the Database. Not Added !!", icon="🚫")
    elif status == "Updated":
        st.toast(f"Evaluation: `{eval_name}` of `{model_name}` updated in the Database", icon="⚓")
    elif status == "Added":
        st.toast(f"Evaluation: `{eval_name}` of `{model_name}` added to the Database", icon="✅")

def trigger_evaluation(function_name, evaluation_name):
    with st.container(border=True):
        st.markdown(f"**Evaluation ID:** `{evaluation_name}`")

        llm_model_name = st.radio("**LLM Model Name:**", ["gpt-4o-mini", "gpt-4o"], horizontal=True)

        # Check Evaluation present in the database
        evaluation = get_evaluation(evaluation_name, selected_model_name, llm_model_name)

        if not evaluation:
            st.markdown("**Evaluation not present in database**")

        btn_run_eval = st.button("Run Evaluation",
                                 key=f"Run Evaluation - {evaluation_name} - {selected_model_name}")

        if btn_run_eval:
            with st.spinner("Evaluating Edges only using Node identifiers ..."):

                eval_res_dict = function_name(incorrect_edges, evaluation_name)
                evaluation["eval_result"] = eval_res_dict

        if evaluation:
            st.markdown("**Evaluation Result:**")
            # st.json(evaluation, expanded=False)
            st.data_editor(
                evaluation["eval_result"]["evaluation_data"],
                disabled=True,
                column_config={
                    "prompt": st.column_config.TextColumn(width="medium"),
                    "reasoning": st.column_config.TextColumn(width="medium"),
                },
            )
            st.markdown("**Evaluation Summary:**")
            st.data_editor(evaluation["eval_result"]["eval_scorer_summary"], disabled=True)
            # st.json(eval_res_dict["eval_scorer_summary"], expanded=False)

            # Save to Database
            st.button("Save to Database", type="primary", on_click=save_to_db_callback,
                      args=[evaluation_name, selected_model_name, llm_model_name, evaluation["eval_result"]],
                      key=f"Save to DB - {evaluation_name} - {selected_model_name}")

def display_valid_edges(model):
    edges = model.edges()
    for edge in edges:
        # Only consider edges that have passed rule based validation checks
        if not edge_dependency_check(edge, nodes_contents):
            continue

        incorrect_edges.append(edge)
        correct_edges.append((edge[1],edge[0]))

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("**Incorrect Edges:**")
            for inc_e in incorrect_edges:
                st.write(inc_e)

    with col2:
        with st.container(border=True):
            st.markdown("**Correct Edges:**")
            for c_e in correct_edges:
                st.write(c_e)


##### START OF PAGE #####

st.markdown("#### Evaluations on Modified BN (Reversed Edges of Original Network)")

available_models = get_models(type="Ground Truth")
model_names = [model['name'] for model in available_models]

# selected_model_name = "Lymph Node Staging of the TNM Staging of Laryngeal Cancer (WIP)"
selected_model_name = st.selectbox("Select a ground truth model", model_names,
                                     key="Selected GT Model", index=None)

# selected_model_name = "Lymph Node Staging of the TNM Staging of Laryngeal Cancer (WIP)"
st.markdown(f"**Selected Model: `{selected_model_name}`**")
model = get_model_by_name(selected_model_name)

if not model:
    st.write("**Please select a Model to run evaluations.**")
else:
    try:
        nodes_contents = model['nodes_content']
        model_bn = build_network(nodes_contents)
        st.info(model_bn)

        from utils.models import reverse_bayesian_network
        reversed_bn = reverse_bayesian_network(model_bn)

    except Exception as e:
        st.error(f"ERROR: \n{str(e)}")

    with st.container(border=True):
        st.markdown("**Valid Edges based on Edge Dependencies schema**")
        display_valid_edges(reversed_bn)


    #### USING ONLY NODE IDENTIFIERS AND CAUSAL RELATION (CAUSES) ####
    if st.checkbox("Only using Node Identifiers and causal verb `causes`"):
        evaluation_name = "baseline_only_node_id_causes"
        evaluation_function = baseline_only_node_id_causes
        trigger_evaluation(evaluation_function, evaluation_name)
