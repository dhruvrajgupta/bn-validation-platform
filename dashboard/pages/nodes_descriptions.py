import streamlit as st
from pydantic import BaseModel
import json

from utils.db import get_models, get_model_by_name, get_node_descriptions
from utils.file import build_network

# @st.cache_data
def get_desc_from_gpt(node_id, node_info):
    from typing import List
    from utils.cpg import ask_llm_response_schema
    from utils.prompts import EXTRACT_NODE_DESCRIPTION
    prompt = EXTRACT_NODE_DESCRIPTION.format(node_id=node_id, states=node_info['states'])

    class ENTITY_INFO(BaseModel):
        ontology_name: str
        label: str
        description: str

    class NODE_INFO(BaseModel):
        id: str
        label: str
        description: str
        entity_information: List[ENTITY_INFO]

    gpt_node_info = json.loads(ask_llm_response_schema(prompt, response_format=NODE_INFO))

    node_info['label'] = gpt_node_info['label']
    node_info['description'] = gpt_node_info['description']
    node_info['entity_information'] = gpt_node_info['entity_information']

    return node_info

def save_to_db_callback(node_id, label, description, ent_info):
    from utils.db import save_node_desc_data
    status = save_node_desc_data(node_id, label, description, ent_info)
    if status == "Same":
        st.toast("Same Data already present in the Database. Not Added !!", icon="🚫")
    elif status == "Updated":
        st.toast(f"Node: {node} updated in the Database", icon="⚓")
    elif status == "Added":
        st.toast(f"Node: {node} added to the Database", icon="✅")


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
                gt_model = build_network(nodes_contents)
                st.info(gt_model)
            except Exception as e:
                st.error(f"ERROR: \n{str(e)}")

        nodes = gt_model.nodes()
        for node in nodes:
            # Get information of the node from the database
            node_info_db = get_node_descriptions(node)
            edges = []
            for edge in gt_model.edges():
                if edge[0] == node or edge[1] == node:
                    edges.append(edge)

            if node_info_db:
                status_icon = "✅"
            else:
                status_icon = "🚫"

            if st.checkbox(f"{status_icon} {node}", key=f"gt-{node}-desc"):
                if node_info_db:
                    node_info = {
                        'node_id': node,
                        'states': None,
                        'label': node_info_db['label'],
                        'description': node_info_db['description'],
                        'entity_information': node_info_db['entity_information']
                    }
                else:
                    node_info = {
                        'node_id': node,
                        'states': edges,
                        'label': None,
                        'description': None,
                        'entity_information': None
                    }

                with st.container(border=True):
                    if st.button("Get Information using GPT", key=f"gpt-for-{node}"):
                        with st.spinner(f"Extracting Node information for '{node_info['node_id']}'..."):
                            node_info = get_desc_from_gpt(node, node_info)
                    st.markdown(f"**ID:** {node_info['node_id']}")
                    st.markdown(f"**STATES:** {node_info['states']}")
                    st.markdown(f"**EDGES:** {node_info['edges']}")
                    # st.write(node_info)
                    label = st.text_input("**Label:**", value=str(node_info["label"]), key=f"lbl-{node}")
                    description = st.text_area("**Description:**", value=str(node_info['description']), key=f"desc-{node}")
                    st.markdown("**Entity Information:**")
                    ent_info = st.data_editor(node_info['entity_information'], use_container_width=True, key=f"ent-{node}")

                    st.button("Save to Database", type="primary", on_click=save_to_db_callback, args=[node, label, description, ent_info], key=f"sv-db-{node}")

    with wip_model:
        wip_model = st.session_state["bn_model"]
        nodes = wip_model.nodes()
        for node in nodes:
            # Get information of the node from the database
            # from utils.db import get_node_descriptions
            node_info_db = get_node_descriptions(node)
            edges = []
            for edge in gt_model.edges():
                if edge[0] == node or edge[1] == node:
                    edges.append(edge)
            if node_info_db:
                status_icon ="✅"
            else:
                status_icon = "🚫"
            if st.checkbox(f"{status_icon} {node}", key=f"bn-{node}"):
                if node_info_db:
                    node_info = st.session_state.bn_node_contents[node]
                    node_info['node_id'] = node
                    node_info['edges'] = edges
                    node_info['label'] = node_info_db['label']
                    node_info['description'] = node_info_db['description']
                    node_info['entity_information'] = node_info_db['entity_information']
                else:
                    node_info = st.session_state.bn_node_contents[node]
                    node_info['node_id'] = node
                    node_info['edges'] = edges
                    node_info['label'] = None
                    node_info['description'] = None
                    node_info['entity_information'] = None

                if st.button("Get Information using GPT", key=f"gpt-for-{node}"):
                    with st.spinner(f"Extracting Node information for '{node_info['node_id']}'..."):
                        node_info = get_desc_from_gpt(node, node_info)
                with st.container(border=True):
                    st.markdown(f"**ID:** {node_info['node_id']}")
                    st.markdown(f"**STATES:** {node_info['states']}")
                    st.markdown(f"**EDGES:** {node_info['edges']}")
                    # st.write(node_info)
                    label = st.text_input("**Label:**", value=str(node_info["label"]), key=f"lbl-{node}")
                    description = st.text_area("**Description:**", value=str(node_info['description']), key=f"desc-{node}")
                    st.markdown("**Entity Information:**")
                    ent_info = st.data_editor(node_info['entity_information'], use_container_width=True, key=f"ent-{node}")

                    st.button("Save to Database", type="primary", on_click=save_to_db_callback, args=[node, label, description, ent_info], key=f"sv-db-{node}")


    with st.expander("Session Info"):
        st.json(st.session_state, expanded=False)

if __name__ == "__main__":
    main()