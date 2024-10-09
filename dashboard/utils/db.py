import streamlit as st
import pymongo

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])


def save_page_sections_data(page_no, page_section_data):
    db = init_connection()["bn-validation"]
    pages = db.pages

    data_dict = {}
    data_dict["page_no"] = page_no
    data_dict["sections_data"] = page_section_data
    if pages.find_one(data_dict):
        return "Same"

    result = pages.replace_one(
        {"page_no": page_no},
        data_dict,
        upsert=True
    )

    if result.matched_count > 0:
        return "Updated"
    else:
        return "Added"


def get_page_info(page_no):
    db = init_connection()["bn-validation"]
    pages = db.pages

    return pages.find_one({"page_no": page_no})

def get_node_descriptions(node_id):
    db = init_connection()["bn-validation"]
    nodes_descriptions = db.nodes_descriptions

    return nodes_descriptions.find_one({"node_id": node_id})

def save_node_desc_data(node_id, label, description, entity_information):
    db = init_connection()["bn-validation"]
    nodes_desc = db.nodes_descriptions

    node_dict = {
        "node_id": node_id,
        "label": label,
        "description": description,
        "entity_information": entity_information
    }

    print(node_dict)

    if nodes_desc.find_one(node_dict):
        return "Same"

    result = nodes_desc.replace_one(
        {"node_id": node_id},
        node_dict,
        upsert=True
    )

    if result.matched_count > 0:
        return "Updated"
    else:
        return "Added"


#### FOR NETWORKS OR MODELS ####
def save_model(name, type, model_content):
    db = init_connection()["bn-validation"]
    models = db.models

    if models.find_one({"name": name}):
        return "Present"

    models_dict = {
        "name": name,
        "type": type,
        "model_content": model_content
    }

    if models.insert_one(models_dict):
        return "Succeded"
    else:
        return "Failed"

def get_models(type):
    db = init_connection()["bn-validation"]
    models = db.models

    return list(models.find({"type": type}))