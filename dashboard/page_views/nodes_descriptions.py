import urllib.parse

import streamlit as st
import json
from pgmpy.factors.discrete.CPD import TabularCPD

from utils.db import get_models, get_model_by_name, get_node_descriptions, save_node_desc_data
from utils.file import build_network
from utils.cpg import ask_llm_response_schema
from utils.prompts.nodes_description import EXTRACT_NODE_DESCRIPTION, NodeDescription

MESH_LINK = "https://meshb.nlm.nih.gov/search?searchMethod=FullWord&searchInField=termDescriptor&sort=&size=20&searchType=exactMatch&from=0&"
SNOMED_CT_LINK = "https://browser.ihtsdotools.org/snowstorm/snomed-ct/browser/MAIN/2024-10-01/descriptions?&limit=100&active=true&conceptActive=true&lang=english&searchMode=WHOLE_WORD&groupByConcept=true&"
WIKIDATA_LINK = "https://www.wikidata.org/w/index.php?go=Go&title=Special%3ASearch&ns0=1&ns120=1&"

def print_full(cpd):
    backup = TabularCPD._truncate_strtable
    TabularCPD._truncate_strtable = lambda self, x: x
    st.write(cpd)
    TabularCPD._truncate_strtable = backup

def save_to_db_callback(node_id, node_type, node_observability, label, description, node_states_description, ent_info):
    status = save_node_desc_data(node_id, node_type, node_observability, label, description, node_states_description, ent_info)
    if status == "Same":
        st.toast("Same Data already present in the Database. Not Added !!", icon="🚫")
    elif status == "Updated":
        st.toast(f"Node: {node_id} updated in the Database", icon="⚓")
    elif status == "Added":
        st.toast(f"Node: {node_id} added to the Database", icon="✅")

def get_desc_from_gpt(node_id, node_info):
    prompt = EXTRACT_NODE_DESCRIPTION.format(node_id=node_id, node_type=node_info['node_type'],
                                             node_observability=node_info['observability'], states=node_info['states'])

    gpt_node_info = json.loads(ask_llm_response_schema(prompt, response_format=NodeDescription))

    node_info['label'] = gpt_node_info['label']
    node_info['description'] = gpt_node_info['description']
    node_info['node_states_description'] = gpt_node_info['node_states_description']
    node_info['entity_information'] = gpt_node_info['entity_information']

    return node_info

def display_node_descriptions(bn_model, model_type, nodes_contents):
    nodes = bn_model.nodes()
    for node in nodes:
        # Get information of the node from the database
        node_info_db = get_node_descriptions(node)

        if node_info_db:
            status_icon = "✅"
        else:
            status_icon = "🚫"

        if st.checkbox(f"{status_icon} {node}", key=f"{model_type} - {node} - Description Checkbox"):
            if node_info_db:
                node_info = {
                    'node_id': node,
                    'node_type': nodes_contents[node]['node_type'],
                    'observability': nodes_contents[node]['observability'],
                    'states': bn_model.states[node],
                    'label': node_info_db['label'],
                    'description': node_info_db['description'],
                    'node_states_description': node_info_db['node_states_description'],
                    'entity_information': node_info_db['entity_information']
                }
            else:
                node_info = {
                    'node_id': node,
                    'node_type': nodes_contents[node]['node_type'],
                    'observability': nodes_contents[node]['observability'],
                    'states': bn_model.states[node],
                    'label': None,
                    'description': None,
                    'node_states_description': None,
                    'entity_information': None
                }


            if st.button("Get Information using GPT", key=f"{model_type} - GPT Node Info for : {node}"):
                with st.spinner(f"Extracting Node information for '{node_info['node_id']}' ..."):
                    node_info = get_desc_from_gpt(node, node_info)

            with st.container(border=True):
                st.markdown(f"**ID:** `{node_info['node_id']}`")
                st.markdown(f"**TYPE:** `{node_info['node_type']}`")
                st.markdown(f"**OBSERVABILITY:** `{node_info['observability']}`")
                st.markdown(f"**STATES:** `{node_info['states']}`")
                # from utils.nodes import source_connected_nodes, target_connected_nodes
                # st.markdown(f"**INCOMING EDGES NODES:** `{source_connected_nodes(bn_model, node_info['node_id'])}`")
                # st.markdown(f"**OUTGOING EDGES NODES:** `{target_connected_nodes(bn_model, node_info['node_id'])}`")
                label = st.text_input("**Label:**", value=str(node_info["label"]))
                description = st.text_area("**Description:**", value=str(node_info["description"]), height=250)
                st.markdown("**Node States & Descriptions**")
                node_states_description = st.data_editor(node_info['node_states_description'],
                                                            key=f"{model_type} - {node_info['node_id']} - STATES - DESC", use_container_width=True)
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
                            args=[node, node_info['node_type'], node_info['observability'], label, description, node_states_description, ent_info], key=f"{model_type} - Save to DB - {node}")


##### START OF PAGE #####

st.markdown("#### Nodes Descriptions")
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
    # st.json(model, expanded=False)
    try:
        nodes_contents = model['nodes_content']
        model_bn = build_network(nodes_contents)
        st.info(model_bn)
    except Exception as e:
        st.error(f"ERROR: \n{str(e)}")

    display_node_descriptions(model_bn, model_type, nodes_contents)

with st.expander("Session Info"):
    st.json(st.session_state, expanded=False)