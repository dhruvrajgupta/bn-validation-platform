import streamlit as st
import pymongo
import gridfs
from io import BytesIO
import pandas as pd
import json

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])

#### FOR GUIDELINES PAGES ####
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


#### FOR NODES OF MODELS ####
def get_node_descriptions(node_id):
    db = init_connection()["bn-validation"]
    node_descriptions = db.nodes_descriptions

    return node_descriptions.find_one({"node_id": node_id})

def save_node_desc_data(node_id, node_type, node_observability, label, description, node_states_description, entity_information):
    db = init_connection()["bn-validation"]
    nodes_desc = db.nodes_descriptions

    node_dict = {
        "node_id": node_id,
        "type": node_type,
        "observability": node_observability,
        "label": label,
        "description": description,
        "node_states_description": node_states_description,
        "entity_information": entity_information
    }

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
def save_model(name, type, nodes_content, file_content, label, description, uploaded_dataset_file):
    db = init_connection()["bn-validation"]
    models = db.models

    if models.find_one({"name": name}):
        return "Present"

    fs = gridfs.GridFS(db)

    # Save file_content using GridFS
    file_content_data = BytesIO(file_content.getvalue())
    file_content_data.seek(0)
    file_content_id = fs.put(file_content_data, filename=file_content.name)

    nodes_content_data = json.dumps(nodes_content, ensure_ascii=False)
    nodes_content_id = fs.put(nodes_content_data.encode("utf-8"), filename=file_content.name)

    model_dict = {
        "name": name,
        "type": type,
        "nodes_content_id": nodes_content_id,
        "file_content_id": file_content_id,
        "label": label,
        "description": description
    }

    if uploaded_dataset_file is not None:
        dataset_file_data = BytesIO(uploaded_dataset_file.getvalue())
        dataset_file_data.seek(0)
        dataset_file_id = fs.put(dataset_file_data, filename=uploaded_dataset_file.name)
        model_dict["dataset_file"] = dataset_file_id
        model_dict["dataset_filename"] = uploaded_dataset_file.name

    if models.insert_one(model_dict):
        return "Succeded"
    else:
        return "Failed"

def get_model_dataset_file(name):
    db = init_connection()["bn-validation"]
    models = db.models

    model_dict = models.find_one({"name": name})

    if "dataset_file" in model_dict.keys():
        fs = gridfs.GridFS(db)

        # File content
        file_data_from_fs = fs.get(model_dict["dataset_file"])
        file_content = file_data_from_fs.read()

        file_data_io = BytesIO(file_content)
        df_from_fs = pd.read_csv(file_data_io)

        return df_from_fs

    else:
        return None

def update_model_label_description(name, type, label, description):
    db = init_connection()["bn-validation"]
    models = db.models

    model_dict = {
        "name": name,
        "type": type,
        "label": label,
        "description": description
    }

    if models.find_one(model_dict):
        return "Same"

    result = models.update_one(
        {"name": name, "type": type},
        {"$set": {"label": label, "description": description}}
    )

    if result.modified_count > 0:
        return "Updated"

def get_models(type):
    db = init_connection()["bn-validation"]
    models = db.models

    return list(models.find({"type": type}))

def get_model_by_name(name):
    db = init_connection()["bn-validation"]
    models = db.models

    model = models.find_one({"name": name})

    if not model:
        return None

    ## Get file content
    fs = gridfs.GridFS(db)
    file_content = fs.get(model["file_content_id"]).read()
    model["file_content"] = file_content

    ## Get nodes content
    nodes_content = fs.get(model["nodes_content_id"]).read()
    model["nodes_content"] = json.loads(nodes_content)

    return model


#### FOR EDGES OF MODELS ####
def get_edge_rationality(edge):
    db = init_connection()["bn-validation"]
    edges_rationality = db.edges_rationality

    return edges_rationality.find_one({"edge": edge})

def save_edge_rationality(edge, edge_rationality_info):
    db = init_connection()["bn-validation"]
    edges_rationality = db.edges_rationality

    edge_dict = {
        "edge": edge,
        "edge_rationality_info": edge_rationality_info
    }

    if edges_rationality.find_one(edge_dict):
        return "Same"

    result = edges_rationality.replace_one(
        {"edge": edge},
        edge_dict,
        upsert=True
    )

    if result.matched_count > 0:
        return "Updated"
    else:
        return "Added"