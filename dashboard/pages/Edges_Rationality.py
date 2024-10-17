import streamlit as st

from utils.db import get_models, get_model_by_name, get_node_descriptions, get_edge_rationality
from utils.file import build_network


st.set_page_config(
    layout="wide",
    page_title="Edges Rationality"
)

@st.fragment
def display_node_information(node, source_target):
    with st.container(border=True):
        st.markdown(f"**{source_target} :**  ")
        st.markdown(f"**ID :** {node}")
        node_desc = get_node_descriptions(node)
        if node_desc:
            st.markdown(f"**Label :** {node_desc['label']}")
            st.markdown(f"**Description :** {node_desc['description']}")
            st.data_editor(node_desc['entity_information'], use_container_width=True, disabled=True, key=f"DataEditor - Entity - {source_target} - {node}")
        else:
            st.markdown("**No information on the node is available in our database.**")

def display_edge_rationality(bn_model, model_type):
    edges = bn_model.edges()
    for edge in edges:
        edge_rationality_info = get_edge_rationality(edge)

        if edge_rationality_info:
            status_icon ="✅"
        else:
            status_icon = "🚫"

        if st.checkbox(f"{status_icon} {edge[0]} --> {edge[1]}", key=f"{model_type} - Edge Rationality - ({edge[0]})-->({edge[1]})"):
            source = edge[0]
            target = edge[1]
            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    display_node_information(source, "SOURCE")
                with col2:
                    display_node_information(target, source_target="TARGET")

                if st.button("Get Edge Rationality using GPT", key=f"GPT - {model_type} - Edge Rationality - ({edge[0]})-->({edge[1]})"):
                    with st.spinner(f"Extracting Node information for edge '{edge}' ..."):
                        edge_rationality_info = get_edge_rationality_from_gpt(edge)

                if not edge_rationality_info:
                    st.markdown("**No information on the edge rationality is available in our database.**")
                else:
                    with st.container(border=True):
                        if isinstance(edge_rationality_info, dict):
                            edge_rationality_info = edge_rationality_info["edge_rationality_info"]
                            st.write(edge_rationality_info)
                        else:
                            st.write(edge_rationality_info)
                    st.button("Save to Database", type="primary", on_click=save_to_db_callback, args=[edge, edge_rationality_info], key=f"Save to DB - {model_type} - Edge Rationality - ({edge[0]}, {edge[1]})")


def get_edge_rationality_from_gpt(edge):
    from typing import List
    from utils.cpg import ask_llm
    from utils.prompts.edge_rationality import EDGE_RATIONALITY

    source_node_info = get_node_descriptions(edge[0])
    target_node_info = get_node_descriptions(edge[1])

    prompt = EDGE_RATIONALITY.format(
        source_node_id = source_node_info['node_id'],
        source_node_label = source_node_info['label'],
        source_node_description = source_node_info['description'],
        target_node_id = target_node_info['node_id'],
        target_node_label = target_node_info['label'],
        target_node_description = target_node_info['description']
    )

    gpt_edge_rationality = ask_llm(prompt)


    # Separated Prompts
    # from utils.prompts.edge_rationality import EDGE_RATIONALITY2
    #
    # prompt = EDGE_RATIONALITY2.format(
    #     source_node_id = source_node_info['node_id'],
    #     source_node_label = source_node_info['label'],
    #     source_node_description = source_node_info['description'],
    #     target_node_id = target_node_info['node_id'],
    #     target_node_label = target_node_info['label'],
    #     target_node_description = target_node_info['description']
    # )
    #
    # gpt_edge_rationality1 = ask_llm(prompt)
    #
    # source_node_info = get_node_descriptions(edge[1])
    # target_node_info = get_node_descriptions(edge[0])
    #
    # prompt = EDGE_RATIONALITY2.format(
    #     source_node_id=source_node_info['node_id'],
    #     source_node_label=source_node_info['label'],
    #     source_node_description=source_node_info['description'],
    #     target_node_id=target_node_info['node_id'],
    #     target_node_label=target_node_info['label'],
    #     target_node_description=target_node_info['description']
    # )
    #
    # gpt_edge_rationality2 = ask_llm(prompt)
    #
    # gpt_edge_rationality = gpt_edge_rationality1 + "\n"*5 + gpt_edge_rationality2

    ## Structured with Causality Decomposition
    # from utils.cpg import ask_llm_response_schema
    # from utils.prompts.edge_rationality import VERIFY_EDGE, EdgeVerification
    # import json
    #
    # prompt = VERIFY_EDGE.format(
    #     source_id=source_node_info['node_id'],
    #     source_label=source_node_info['label'],
    #     source_description=source_node_info['description'],
    #     target_id=target_node_info['node_id'],
    #     target_label=target_node_info['label'],
    #     target_description=target_node_info['description'],
    #     causal_relation_type="causes"
    # )
    #
    # gpt_edge_rationality1 = json.loads(ask_llm_response_schema(prompt, response_format=EdgeVerification))
    #
    # st.json(gpt_edge_rationality1, expanded=False)
    #
    # source_node_info = get_node_descriptions(edge[1])
    # target_node_info = get_node_descriptions(edge[0])
    #
    # prompt = VERIFY_EDGE.format(
    #     source_id=source_node_info['node_id'],
    #     source_label=source_node_info['label'],
    #     source_description=source_node_info['description'],
    #     target_id=target_node_info['node_id'],
    #     target_label=target_node_info['label'],
    #     target_description=target_node_info['description'],
    #     causal_relation_type="causes"
    # )
    #
    # gpt_edge_rationality2 = json.loads(ask_llm_response_schema(prompt, response_format=EdgeVerification))
    #
    # st.json(gpt_edge_rationality2, expanded=False)

    return gpt_edge_rationality

def save_to_db_callback(edge, edge_rationality_info):
    from utils.db import save_edge_rationality
    status = save_edge_rationality(edge, edge_rationality_info)
    if status == "Same":
        st.toast("Same Data already present in the Database. Not Added !!", icon="🚫")
    elif status == "Updated":
        st.toast(f"Edge Rationality: {edge} updated in the Database", icon="⚓")
    elif status == "Added":
        st.toast(f"Edge Rationality: {edge} added to the Database", icon="✅")

def main():
    ground_truth_model, wip_model = st.tabs(['Ground Truth Model', "WIP Model"])

    with ground_truth_model:
        ground_truth_models = get_models("Ground Truth")
        model_names = [model['name'] for model in ground_truth_models]
        selected_gt_model = st.selectbox("Select a ground truth model", model_names, key="select_gt_models", index=None)

        selected_gt_model_dict = get_model_by_name(selected_gt_model)

        if not selected_gt_model:
            st.write("**Please select a Ground Truth Model.**")
        else:
            try:
                nodes_contents = selected_gt_model_dict['nodes_content']
                gt_model_bn = build_network(nodes_contents)
                st.info(gt_model_bn)
            except Exception as e:
                st.error(f"ERROR: \n{str(e)}")

            display_edge_rationality(gt_model_bn, model_type="GT Model")

    with wip_model:
        ground_truth_models = get_models("Work In Progress")
        model_names = [model['name'] for model in ground_truth_models]
        selected_wip_model = st.selectbox("Select a work in progress model", model_names, key="select_wip_models", index=None)

        selected_wip_model_dict = get_model_by_name(selected_wip_model)

        if not selected_wip_model:
            st.write("**Please select a Work In Progress Model.**")
        else:
            try:
                nodes_contents = selected_wip_model_dict['nodes_content']
                wip_model_bn = build_network(nodes_contents)
                st.info(wip_model_bn)
            except Exception as e:
                st.error(f"ERROR: \n{str(e)}")

            from utils.models import reverse_bayesian_network

            rep = reverse_bayesian_network(wip_model_bn)

            display_edge_rationality(rep, model_type="WIP Model")


    with st.expander("Session State", expanded=False):
        st.json(st.session_state, expanded=False)

if __name__ == "__main__":
    main()