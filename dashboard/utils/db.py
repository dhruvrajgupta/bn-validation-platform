import io

import streamlit as st
import pymongo
import gridfs
from io import BytesIO
import pandas as pd
import json

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])

#### USER ####
def get_user(username):
    db = init_connection()["bn-validation"]
    users = db.users

    return users.find_one({"username": username})

#### FOR GUIDELINES PAGES ####
def save_page_sections_data(page_no, page_section_data, chunk_data):
    db = init_connection()["bn-validation"]
    pages = db.pages

    data_dict = {}
    data_dict["page_no"] = page_no
    data_dict["thinking"] = page_section_data["thinking"]
    data_dict["sections"] = page_section_data["sections"]
    data_dict["dense_retrieval_chunk"] = chunk_data

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
    entities = db.entities

    db_entity_objects = []

    node_description = node_descriptions.find_one({"node_id": node_id})
    if node_description:
        for ontology_name, entity_list in node_description["entity_information"].items():
            for entity_id in entity_list:
                entity = get_entity_by_id(entity_id)
                del entity["_id"]
                db_entity_objects.append(entity)

        node_description["entity_information"] = db_entity_objects

    return node_description

def save_node_desc_data(node_id, node_type, node_observability, label, description, node_states_description, entity_information, thinking):
    db = init_connection()["bn-validation"]
    nodes_desc = db.nodes_descriptions

    node_dict = {
        "node_id": node_id,
        "type": node_type,
        "observability": node_observability,
        "label": label,
        "description": description,
        "node_states_description": node_states_description,
        "entity_information": entity_information,
        "thinking": thinking
    }

    new_entities_labels = []

    processed_entity_information = {
        "MeSH": [],
        "SNOMED-CT": [],
        "Wikidata": []
    }

    for entity in entity_information:
        # Process Entity Information
        # 1. Check whether the entity already exists in the db
        # 2. If present then store the ID
        # 3. Else create a new entity and store the ID
        check_entity = search_entity(entity["label"], entity["ontology_name"])

        if check_entity:
            processed_entity_information[entity["ontology_name"]].append(check_entity["_id"])
        else:
            new_entity_id = save_entity(entity)
            new_entities_labels.append(entity["label"])
            processed_entity_information[entity["ontology_name"]].append(new_entity_id)

    node_dict["entity_information"] = processed_entity_information

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

    ## Get Dataset content
    if model.get("dataset_filename", None):
        dataset_content = fs.get(model["dataset_file"]).read()
        model["dataset_file"] = dataset_content.decode("utf-8")
        file_string = io.StringIO(model["dataset_file"])
        df = pd.read_csv(file_string)
        model["dataset_file"] = df

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


#### GET DISTINCT ENTITIES ####
def get_distinct_entities():
    db = init_connection()["bn-validation"]
    entities = db.entities

    result = {}
    query = {"ontology_name": "MeSH"}
    distinct_labels = entities.distinct("label", query)
    result["MeSH"] = distinct_labels

    query = {"ontology_name": "SNOMED-CT"}
    distinct_labels = entities.distinct("label", query)
    result["SNOMED-CT"] = distinct_labels

    query = {"ontology_name": "Wikidata"}
    distinct_labels = entities.distinct("label", query)
    result["Wikidata"] = distinct_labels

    return result

def save_entity(entity):
    db = init_connection()["bn-validation"]
    entities = db.entities

    result = entities.insert_one(entity)
    return result.inserted_id

def search_entity(entity_label, ontology_name):
    db = init_connection()["bn-validation"]
    entities = db.entities

    # Performing Search with Case Insensitive
    return entities.find_one({
        "label": {"$regex": entity_label, "$options": "i"},
        "ontology_name": ontology_name
    })

def get_entity_by_id(id):
    db = init_connection()["bn-validation"]
    entities = db.entities

    return entities.find_one({
        "_id": id
    })

def get_node_entities(node_id):
    db = init_connection()["bn-validation"]
    node_descriptions = db.nodes_descriptions

    current_node_description = node_descriptions.find_one({"node_id": node_id})

    if not current_node_description:
        return None
    else:
        return current_node_description["entity_information"]

def get_entities_of_model(bn_model):
    ont_list = []
    nodes_list = []
    ent_id_list = []
    # ent_label_list = []
    # ent_desc_lsit = []
    for node in bn_model.nodes():
        node_entities_ids_list = get_node_entities(node)
        # print(node_entities_ids_list)
        if node_entities_ids_list:
            for ontology_name, entity_list in node_entities_ids_list.items():
                # print(ontology_name)
                # print(entity_list)
                for entity in entity_list:
                    nodes_list.append(node)
                    ont_list.append(ontology_name)
                    ent_id_list.append(entity)
                    ent_det = get_entity_by_id(entity)
                    # ent_label_list.append(ent_det["label"])
                    # ent_desc_lsit.append(ent_det["description"])

    # print(nodes_list)
    # print(ent_id_list)
    # print(ont_list)
    # print(len(ent_id_list))
    # print(len(ent_id_list))
    # print(len(nodes_list))

    data = {
        "nodes_list": nodes_list,
        "ontology_name": ont_list,
        "entity_id": ent_id_list,
        # "entity_label": ent_label_list,
        # "entity_desc": ent_desc_lsit
    }

    result = pd.DataFrame(data=data)

    return result


#### EVALUATIONS ####
def get_evaluation(name, model, llm_model_name):
    db = init_connection()["bn-validation"]
    evaluations = db.evaluations

    current_evaluation = evaluations.find_one(
        {
            "name": name,
            "model_name": model,
            "llm_model_name": llm_model_name
        })

    if not current_evaluation:
        return {}
    else:
        return current_evaluation

def save_evaluation(name, model_name, llm_model_name, eval_res_dict):
    db = init_connection()["bn-validation"]
    evaluations = db.evaluations

    eval_dict = {
        "name": name,
        "model_name": model_name,
        "llm_model_name": llm_model_name,
        "eval_result": eval_res_dict
    }

    if evaluations.find_one(eval_dict):
        return "Same"

    result = evaluations.replace_one(
        {"name": name, "model_name": model_name, "llm_model_name": llm_model_name},
        eval_dict,
        upsert=True
    )

    if result.matched_count > 0:
        return "Updated"
    else:
        return "Added"