import streamlit as st
from utils.db import get_models, get_model_by_name, get_node_descriptions
from utils.file import build_network

if "bn_model_gt" not in st.session_state:
    st.session_state["bn_model_gt"] = None

if "bn_model_wip" not in st.session_state:
    st.session_state["bn_model_wip"] = None

if "selected_gt_model_name" not in st.session_state:
    st.session_state["selected_gt_model_name"] = None

if "selected_wip_model_name" not in st.session_state:
    st.session_state["selected_wip_model_name"] = None

def get_extra_nodes(bn_model, type):
    if type == "wip":
        wip_model = bn_model
        gt_model = st.session_state["bn_model_gt"]
        # st.success("WIP Model: "+str(wip_model))
        x_col1, x_col2 = st.columns(2)
        with x_col1:
            with st.container(border=True):
                st.write(f"**Selected WIP Model:** `{st.session_state['selected_wip_model_name']}`")
        # st.success("GT Model: "+str(gt_model))
        with x_col2:
            with st.container(border=True):
                st.write(f"**Selected GT Model:** `{st.session_state['selected_gt_model_name']}`")

        wip_nodes = wip_model.nodes()
        gt_nodes = gt_model.nodes()
        return set(wip_nodes) - set(gt_nodes)

    if type == "gt":
        gt_model = bn_model
        wip_model = st.session_state["bn_model_wip"]
        # st.success("GT Model: "+str(gt_model))
        x_col1, x_col2 = st.columns(2)
        with x_col1:
            with st.container(border=True):
                st.write(f"**Selected GT Model:** `{st.session_state['selected_gt_model_name']}`")
        # st.success("WIP Model: "+str(wip_model))
        with x_col2:
            with st.container(border=True):
                st.write(f"**Selected WIP Model:** `{st.session_state['selected_wip_model_name']}`")

        gt_nodes = gt_model.nodes()
        wip_nodes = wip_model.nodes()
        return set(gt_nodes) - set(wip_nodes)

def get_extra_edges(bn_model, type):
    if type == "wip":
        wip_model = bn_model
        gt_model = st.session_state["bn_model_gt"]

        wip_edges = wip_model.edges()
        gt_edges = gt_model.edges()
        return set(wip_edges) - set(gt_edges)

    if type == "gt":
        gt_model = bn_model
        wip_model = st.session_state["bn_model_wip"]

        gt_edges = gt_model.edges()
        wip_edges = wip_model.edges()
        return set(gt_edges) - set(wip_edges)

def get_extra_entities(bn_model, type):
    if type == "wip":
        wip_model = bn_model
        gt_model = st.session_state["bn_model_gt"]

        wip_entities = {}
        for wip_node in wip_model.nodes():
            node_info_db = get_node_descriptions(wip_node)
            if node_info_db.get("entity_information"):
                # st.write(node_info_db.get("entity_information"))
                for e_i in node_info_db.get("entity_information"):
                    # st.write(e_i)
                    wip_entities[f"{e_i['ontology_name']}$${e_i['label']}"] = e_i
                # break
        wip_distinct_entities = []
        for k, v in wip_entities.items():
            wip_distinct_entities.append(k)

        # st.write(wip_distinct_entities)

        gt_entities = {}
        for gt_node in gt_model.nodes():
            node_info_db = get_node_descriptions(gt_node)
            if node_info_db.get("entity_information"):
                # st.write(node_info_db.get("entity_information"))
                for e_i in node_info_db.get("entity_information"):
                    # st.write(e_i)
                    gt_entities[f"{e_i['ontology_name']}$${e_i['label']}"] = e_i
                # break
        gt_distinct_entities = []
        for k, v in gt_entities.items():
            gt_distinct_entities.append(k)

        # st.write(gt_distinct_entities)
        wip_extra_en = (set(wip_distinct_entities) - set(gt_distinct_entities))
        # st.write(list(wip_extra_en))
        wip_extra_en_list = []
        for k in wip_extra_en:
            # st.write(k)
            wip_extra_en_list.append(wip_entities[k])

        return wip_extra_en_list

    if type == "gt":
        gt_model = bn_model
        wip_model = st.session_state["bn_model_wip"]

        gt_entities = {}
        for gt_node in gt_model.nodes():
            node_info_db = get_node_descriptions(gt_node)
            if node_info_db.get("entity_information"):
                # st.write(node_info_db.get("entity_information"))
                for e_i in node_info_db.get("entity_information"):
                    # st.write(e_i)
                    gt_entities[f"{e_i['ontology_name']}$${e_i['label']}"] = e_i
                # break
        gt_distinct_entities = []
        for k, v in gt_entities.items():
            gt_distinct_entities.append(k)

        wip_entities = {}
        for wip_node in wip_model.nodes():
            node_info_db = get_node_descriptions(wip_node)
            if node_info_db.get("entity_information"):
                # st.write(node_info_db.get("entity_information"))
                for e_i in node_info_db.get("entity_information"):
                    # st.write(e_i)
                    wip_entities[f"{e_i['ontology_name']}$${e_i['label']}"] = e_i
                # break
        wip_distinct_entities = []
        for k, v in wip_entities.items():
            wip_distinct_entities.append(k)

        gt_extra_en = (set(gt_distinct_entities) - set(wip_distinct_entities))
        # st.write(list(wip_extra_en))
        gt_extra_en_list = []
        for k in gt_extra_en:
            # st.write(k)
            gt_extra_en_list.append(gt_entities[k])

        return gt_extra_en_list

#### START OF PAGE

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("#### Ground Truth Model")

        model_type_gt = "Ground Truth"
        available_models_gt = get_models(type=model_type_gt)

        model_names_gt = [model['name'] for model in available_models_gt]

        selected_model = st.selectbox("Select a ground truth model", model_names_gt,
                                         key="Selected GT Model", index=None)
        model_gt = get_model_by_name(selected_model)

        if not model_gt:
            st.write("**Please select a Ground Truth Model.**")
        else:
            # Building the BN for this super graph
            try:
                nodes_contents = model_gt['nodes_content']
                bn_model_gt = build_network(nodes_contents)
                st.info(bn_model_gt)
                st.session_state["bn_model_gt"] = bn_model_gt
                st.session_state["selected_gt_model_name"] = model_gt["name"]

            except Exception as e:
                st.error(f"ERROR: \n{str(e)}")

            gt_extra_nodes = get_extra_nodes(bn_model_gt, "gt")
            st.markdown("#### Nodes present in GT Model but not in WIP Model: ")
            st.write(gt_extra_nodes)

            gt_extra_edges = get_extra_edges(bn_model_gt, "gt")
            st.markdown("#### Edges present in GT Model but not in WIP Model: ")
            st.write(gt_extra_edges)

            gt_extra_entities = get_extra_entities(bn_model_gt, "gt")
            st.markdown("#### Entities present in GT Model but not in WIP Model: ")
            st.data_editor(gt_extra_entities, key="gt")

with col2:
    with st.container(border=True):
        st.markdown("#### Work In Progress Model")

        model_type_wip = "Work In Progress"
        available_models_wip = get_models(type=model_type_wip)

        model_names_wip = [model['name'] for model in available_models_wip]

        selected_model = st.selectbox("Select a work in progress model", model_names_wip,
                                      key="Selected WIP Model", index=None)
        model_wip = get_model_by_name(selected_model)

        if not model_wip:
            st.write("**Please select a Work in Progress Model.**")
        else:
            # Building the BN for this super graph
            try:
                nodes_contents = model_wip['nodes_content']
                bn_model_wip = build_network(nodes_contents)
                st.info(bn_model_wip)
                st.session_state["bn_model_wip"] = bn_model_wip
                st.session_state["selected_wip_model_name"] = model_wip["name"]

            except Exception as e:
                st.error(f"ERROR: \n{str(e)}")

            wip_extra_nodes = get_extra_nodes(bn_model_wip, "wip")
            st.markdown("#### Nodes present in WIP Model but not in GT Model: ")
            st.write(wip_extra_nodes)

            wip_extra_edges = get_extra_edges(bn_model_wip, "wip")
            st.markdown("#### Edges present in WIP Model but not in GT Model: ")
            st.write(wip_extra_edges)

            wip_extra_entities = get_extra_entities(bn_model_wip, "wip")
            st.markdown("#### Entities present in WIP Model but not in GT Model: ")
            st.data_editor(wip_extra_entities, key="wip")