## Evaluations will be run only for N Staging

## TODO: Run the script individual, right now it triggers with streamlit run
import streamlit as st
from attr.validators import disabled

from utils.db import get_model_by_name, save_evaluation, get_evaluation, get_models
from utils.file import build_network
from utils.edges import edge_dependency_check

# Table for correct edges and incorrect edges along with indicaation of rule based schema valid/invalid
correct_edges = []
incorrect_edges = []
num_options = 2

# list_causal_verbs = [
#         "causes", "provokes", "triggers", "leads to", "induces", "results in",
#         "brings about", "yields", "generates", "initiates", "produces", "stimulates",
#         "instigates", "fosters", "engenders", "promotes", "catalyzes",
#         "gives rise to", "spurs", "sparks", "increases likelihood"
#     ]
list_causal_verbs = ["causes", "increases likelihood of", "leads to", "triggers", "generates", "produces", "catalyzes"]

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

        llm_model_name = st.radio("**LLM Model Name:**", ["gpt-4o-mini", "gpt-4o"], horizontal=True, key=f"LLM Radio - {evaluation_name}")

        # Check Evaluation present in the database
        evaluation = get_evaluation(evaluation_name, selected_model_name, llm_model_name)

        if not evaluation:
            st.markdown("**Evaluation not present in database**")

        btn_run_eval = st.button("Run Evaluation",
                                 key=f"Run Evaluation - {evaluation_name} - {selected_model_name}")

        if btn_run_eval:
            with st.spinner("Evaluating Edges only using Node identifiers ..."):

                eval_res_dict = function_name(incorrect_edges, evaluation_name, llm_model_name, model_bn)
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
                    "schema_dep_validity": st.column_config.TextColumn(width="small"),
                },
                key=f"{evaluation_name} - {llm_model_name} - Detailed Evaluation"
            )
            st.markdown("**Evaluation Summary:**")
            st.data_editor(evaluation["eval_result"]["eval_scorer_summary"], disabled=True,
                           key=f"{evaluation_name} - {llm_model_name} - Evaluation Summary")
            # st.json(eval_res_dict["eval_scorer_summary"], expanded=False)

            # Save to Database
            st.button("Save to Database", type="primary", on_click=save_to_db_callback,
                      args=[evaluation_name, selected_model_name, llm_model_name, evaluation["eval_result"]],
                      key=f"Save to DB - {evaluation_name} - {selected_model_name}")

def display_valid_edges(model):
    # The model here is Reversed Model
    edges = model.edges()
    for id, edge in enumerate(edges):
        # Only consider edges that have passed rule based validation checks

        incorrect_edge_dict = {
            "id": id,
            "edge": edge,
            "schema_dep_validity": "valid" if edge_dependency_check(edge, nodes_contents) else "invalid"
        }

        correct_edge_dict = {
            "id": id,
            "edge": (edge[1], edge[0]),
            "schema_dep_validity": "valid" if edge_dependency_check((edge[1], edge[0]), nodes_contents) else "invalid"
        }

        # st.table(edge_dict)

        # if not edge_dependency_check(edge, nodes_contents):
        #
        #     continue

        incorrect_edges.append(incorrect_edge_dict)
        correct_edges.append(correct_edge_dict)

    col1, col2 = st.columns(2)

    with col1:
        # with st.container(border=True):
        st.markdown("**Incorrect Edges: (Reversed to the Original)**")
        st.data_editor(incorrect_edges, disabled=True)
        # for inc_e in incorrect_edges:
        #     st.write(inc_e)

    with col2:
        # with st.container(border=True):
        st.markdown("**Correct Edges:**")
        st.data_editor(correct_edges, disabled=True)
        # for c_e in correct_edges:
        #     st.write(c_e)


##### START OF PAGE #####

st.markdown("#### Evaluations on Modified BN (Reversed Edges of Original Network)")

available_models = get_models(type="Ground Truth")
model_names = [model['name'] for model in available_models]

# selected_model_name = "Lymph Node Staging of the TNM Staging of Laryngeal Cancer (WIP)"
selected_model_name = st.selectbox("Select a ground truth model", model_names,
                                     key="Selected Ground Truth Model", index=None)

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
        # st.markdown("**Valid Edges based on Edge Dependencies schema**")
        display_valid_edges(reversed_bn)

    ##### CHECKBOX FOR ANALYSIS TO INCLUDE RULE BASED SCHEMA VALID EDGES
    ##### CHECKBOX FOR NUMBER OF OPTIONS - DEFAULT 2 OPTIONS
    with st.container(border=True):
        if st.checkbox("**Evaluations should include all edges (both Rule Based Schema `Valid` and `Invalid` edges) - [Default `only Valid edges`]**"):
            pass
        else:
            # get only the valid edges
            filtered_incorrect_edges = []
            count = 0
            for edge_item in incorrect_edges:
                if edge_item["schema_dep_validity"] == "valid":
                    filtered_incorrect_edges.append({
                        "id": count,
                        "edge": edge_item["edge"],
                        "schema_dep_validity": edge_item["schema_dep_validity"]
                    })
                    count += 1
            # st.data_editor(filtered_incorrect_edges, disabled=True)
            incorrect_edges = filtered_incorrect_edges

        # if st.checkbox("**Evaluations should be performed on three options `(A, B and C)` - [Default - Using two options `(A and B)`]**"):
        #     num_options = 3
        #     # st.write("Three options")
        # else:
        #     num_options = 2
        #     # st.write("Two Options")
        #
        # # st.info(num_options)



    with st.container(border=True):
        st.markdown("**Evaluations Panel:**")

        with st.container(border=True):
            st.markdown("**Type 1: `Node1 {causal_verb} Node2`**")
            selected_causal_verb = st.radio("**Causal Verb:** ", list_causal_verbs,
                                            horizontal=True)


            # #### USING ONLY NODE IDENTIFIERS,ITS STATE NAMES AND CAUSAL RELATION (CAUSES) ####
            # if st.checkbox("**Only using Node Identifiers, State Names and causal verb `causes`**"):
            #     evaluation_name = "baseline_node_id_state_names_causes"
            #     from utils.evaluation_functions import baseline_only_node_id_state_names_causes
            #     evaluation_function = baseline_only_node_id_state_names_causes
            #     trigger_evaluation(evaluation_function, evaluation_name)

            #### USING ONLY NODE IDENTIFIERS ####
            if st.checkbox(f"**Only using Node identifiers but different causal verbs**"):
                evaluation_name = f"type1_baseline_node_id_causalverb_{selected_causal_verb}"
                if num_options == 2:
                    # evaluation_name += "_options_2"
                    from utils.evaluation_functions_type1_options2 import baseline_only_node_id_causal_verb
                    evaluation_function = baseline_only_node_id_causal_verb
                    trigger_evaluation(evaluation_function, evaluation_name)
                # elif num_options == 3:
                #     evaluation_name += "_options_3"
                #     from utils.evaluation_functions_type1_options3 import baseline_only_node_id_causal_verb
                #     evaluation_function = baseline_only_node_id_causal_verb
                #     trigger_evaluation(evaluation_function, evaluation_name)

            #### USING ONLY NODE IDENTIFIERS,ITS STATE NAMES ####
            if st.checkbox(f"**Using Node identifiers and their state names**"):
                evaluation_name = f"type1_node_id_state_names_causalverb_{selected_causal_verb}"
                if num_options == 2:
                    from utils.evaluation_functions_type1_options2 import node_id_state_names_causal_verb
                    evaluation_function = node_id_state_names_causal_verb
                    trigger_evaluation(evaluation_function, evaluation_name)

            if st.checkbox(f"**Using Node identifiers, their state names and their direct connected Nodes**"):
                evaluation_name = f"type1_node_id_state_names_connected_nodes_causalverb_{selected_causal_verb}"
                from utils.evaluation_functions_type1_options2 import node_id_state_names_connected_nodes_causal_verb
                evaluation_function = node_id_state_names_connected_nodes_causal_verb
                trigger_evaluation(evaluation_function, evaluation_name)

            if st.checkbox(f"**[Augmentation] Node Type `{{Patient Situation, Examination Result, Decision Node}}`**"):
                evaluation_name = f"type1_node_id_state_names_node_type_causalverb_{selected_causal_verb}"
                from utils.evaluation_functions_type1_options2 import node_id_state_names_node_type
                evaluation_function = node_id_state_names_node_type
                trigger_evaluation(evaluation_function, evaluation_name)

            if st.checkbox(f"**[Augmentation] Node Type, Observability `{{Observed [Examination Result], Unobserved [Patient Situation]}}`**"):
                evaluation_name = f"type1_node_id_state_names_node_type_observability_causalverb_{selected_causal_verb}"
                from utils.evaluation_functions_type1_options2 import node_id_state_names_node_type_observablity
                evaluation_function = node_id_state_names_node_type_observablity
                trigger_evaluation(evaluation_function, evaluation_name)

            if st.checkbox(f"**[Augmentation] Node Type, Observability and Node Labels**"):
                evaluation_name = f"type1_node_id_state_names_node_type_observability_node_labels_causalverb_{selected_causal_verb}"
                from utils.evaluation_functions_type1_options2 import node_id_state_names_node_type_observablity_node_labels
                evaluation_function = node_id_state_names_node_type_observablity_node_labels
                trigger_evaluation(evaluation_function, evaluation_name)

            if st.checkbox(f"**[Augmentation] Node Type, Observability, Node Labels and Descriptions**"):
                evaluation_name = f"type1_node_id_state_names_node_type_observability_node_labels_descriptions_causalverb_{selected_causal_verb}"
                from utils.evaluation_functions_type1_options2 import node_id_state_names_node_type_observablity_node_labels_descriptions
                evaluation_function = node_id_state_names_node_type_observablity_node_labels_descriptions
                trigger_evaluation(evaluation_function, evaluation_name)


        ##### TYPE 2 PROMPT STARTS HERE #####
        with st.container(border=True):
            st.markdown("**Type 2: `changing {Node1} causes a change in {Node2}`**")

            #### USING ONLY NODE IDENTIFIERS ####
            if st.checkbox(f"**Only using Node identifiers**"):
                evaluation_name = f"type2_baseline_node_id"
                if num_options == 2:
                    # evaluation_name += "_options_2"
                    from utils.evaluation_functions_type2_options2 import baseline_only_node_id
                    evaluation_function = baseline_only_node_id
                    trigger_evaluation(evaluation_function, evaluation_name)
                # elif num_options == 3:
                #     evaluation_name += "_options_3"
                #     from utils.evaluation_functions_type2_options3 import baseline_only_node_id
                #     evaluation_function = baseline_only_node_id
                #     trigger_evaluation(evaluation_function, evaluation_name)

            #### USING ONLY NODE IDENTIFIERS,ITS STATE NAMES ####
            evaluation_name = f"type2_node_id_state_names"
            if st.checkbox(f"**Using Node identifiers and their state names**", key=evaluation_name):
                from utils.evaluation_functions_type2_options2 import node_id_state_names
                evaluation_function = node_id_state_names
                trigger_evaluation(evaluation_function, evaluation_name)

            evaluation_name = f"type2_node_id_state_names_connected_nodes"
            if st.checkbox(f"**Using Node identifiers, their state names and their direct connected Nodes**", key=evaluation_name):
                from utils.evaluation_functions_type2_options2 import node_id_state_names_connected_nodes
                evaluation_function = node_id_state_names_connected_nodes
                trigger_evaluation(evaluation_function, evaluation_name)

            evaluation_name = f"type2_node_id_state_names_node_type"
            if st.checkbox(f"**[Augmentation] Node Type `{{Patient Situation, Examination Result, Decision Node}}`**", key=evaluation_name):
                from utils.evaluation_functions_type2_options2 import node_id_state_names_node_type
                evaluation_function = node_id_state_names_node_type
                trigger_evaluation(evaluation_function, evaluation_name)

            evaluation_name = f"type2_node_id_state_names_node_type_observability"
            if st.checkbox(
                f"**[Augmentation] Node Type, Observability `{{Observed [Examination Result], Unobserved [Patient Situation]}}`**", key=evaluation_name):
                from utils.evaluation_functions_type2_options2 import node_id_state_names_node_type_observability
                evaluation_function = node_id_state_names_node_type_observability
                trigger_evaluation(evaluation_function, evaluation_name)