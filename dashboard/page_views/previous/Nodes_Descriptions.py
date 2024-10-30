import streamlit as st
from pydantic import BaseModel
import json
import urllib.parse

from utils.db import get_models, get_model_by_name, get_node_descriptions
from utils.file import build_network

# st.set_page_config(
#     layout="wide",
#     page_title="Node Descriptions"
# )

MESH_LINK = "https://meshb.nlm.nih.gov/search?searchMethod=FullWord&searchInField=termDescriptor&sort=&size=20&searchType=exactMatch&from=0&"
SNOMED_CT_LINK = "https://browser.ihtsdotools.org/snowstorm/snomed-ct/browser/MAIN/2024-10-01/descriptions?&limit=100&active=true&conceptActive=true&lang=english&searchMode=WHOLE_WORD&groupByConcept=true&"
WIKIDATA_LINK = "https://www.wikidata.org/w/index.php?go=Go&title=Special%3ASearch&ns0=1&ns120=1&"

from pgmpy.factors.discrete.CPD import TabularCPD
def print_full(cpd):
    backup = TabularCPD._truncate_strtable
    TabularCPD._truncate_strtable = lambda self, x: x
    st.write(cpd)
    TabularCPD._truncate_strtable = backup

# @st.cache_data
def get_desc_from_gpt(node_id, node_info):
    from typing import List
    from utils.cpg import ask_llm_response_schema
    from utils.prompts2 import EXTRACT_NODE_DESCRIPTION, NodeDescription
    prompt = EXTRACT_NODE_DESCRIPTION.format(node_id=node_id, states=node_info['states'])

    gpt_node_info = json.loads(ask_llm_response_schema(prompt, response_format=NodeDescription))

    node_info['label'] = gpt_node_info['label']
    node_info['description'] = gpt_node_info['description']
    node_info['node_states_description'] = gpt_node_info['node_states_description']
    node_info['entity_information'] = gpt_node_info['entity_information']

    return node_info

def save_to_db_callback(node_id, label, description, node_states_description, ent_info):
    from utils.db import save_node_desc_data
    status = save_node_desc_data(node_id, label, description, node_states_description, ent_info)
    if status == "Same":
        st.toast("Same Data already present in the Database. Not Added !!", icon="🚫")
    elif status == "Updated":
        st.toast(f"Node: {node_id} updated in the Database", icon="⚓")
    elif status == "Added":
        st.toast(f"Node: {node_id} added to the Database", icon="✅")


def display_node_descriptions(bn_model, model_type):
    nodes = bn_model.nodes()
    for node in nodes:
        # Get information of the node from the database
        node_info_db = get_node_descriptions(node)

        if node_info_db:
            status_icon = "✅"
        else:
            status_icon = "🚫"

        if st.checkbox(f"{status_icon} {node}", key=f"{model_type} - {node} - Description"):
            if node_info_db:
                node_info = {
                    'node_id': node,
                    'states': bn_model.states[node],
                    'label': node_info_db['label'],
                    'description': node_info_db['description'],
                    'node_states_description': node_info_db['node_states_description'],
                    'entity_information': node_info_db['entity_information']
                }
            else:
                node_info = {
                    'node_id': node,
                    'states': bn_model.states[node],
                    'label': None,
                    'description': None,
                    'node_states_description': None,
                    'entity_information': None
                }

            # st.json(node_info, expanded=False)

            with st.container(border=True):
                if st.button("Get Information using GPT", key=f"{model_type} - GPT Node Info for : {node}"):
                    with st.spinner(f"Extracting Node information for '{node_info['node_id']}' ..."):
                        node_info = get_desc_from_gpt(node, node_info)
                st.markdown(f"**ID:** {node_info['node_id']}")
                st.markdown(f"**STATES:** {node_info['states']}")
                label = st.text_input("**Label:**", value=str(node_info["label"]), key=f"Label - {model_type} - {node}")
                description = st.text_area("**Description:**", value=str(node_info['description']),
                                           key=f"gt-desc-{node}")
                st.markdown("**Node States & Descriptions**")
                node_states_description = st.data_editor(node_info['node_states_description'],
                                                         key=f"{model_type} - {node_info['node_id']} - STATES - DESC")
                st.markdown("**Entity Information:**")

                if node_info['entity_information']:
                    # Assigning Links to each entities
                    for id, entity_dict in enumerate(node_info['entity_information']):
                        if entity_dict['ontology_name'] == "MeSH":
                            node_info['entity_information'][id]['link'] = MESH_LINK + urllib.parse.urlencode(
                                {"q": entity_dict['label']})
                        elif entity_dict['ontology_name'] == "SNOMED-CT":
                            node_info['entity_information'][id]['link'] = SNOMED_CT_LINK + urllib.parse.urlencode(
                                {"term": entity_dict['label']})
                        elif entity_dict['ontology_name'] == "Wikidata":
                            node_info['entity_information'][id]['link'] = WIKIDATA_LINK + urllib.parse.urlencode(
                                {"search": entity_dict['label']})

                ent_info = st.data_editor(node_info['entity_information'], use_container_width=True,
                                          key=f"{model_type} - Entity Information - {node}")

                st.write("**Condtional Probability Table :**")
                print_full(bn_model.get_cpds(node))

                st.button("Save to Database", type="primary", on_click=save_to_db_callback,
                          args=[node, label, description, node_states_description, ent_info], key=f"{model_type} - Save to DB - {node}")


# def main():
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

        display_node_descriptions(gt_model_bn, "GT Model")

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

        display_node_descriptions(wip_model_bn, "WIP Model")


with st.expander("Session Info"):
    st.json(st.session_state, expanded=False)

# if __name__ == "__main__":
#     main()