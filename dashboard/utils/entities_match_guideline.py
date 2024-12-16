import json
import numpy as np
from transformers import AutoTokenizer, AutoModel
import pickle

from utils.db import get_all_entities_guideline

threshold = 0.93
top_k_pages = 5

def list_unique_entity_score(matching_entities):
    # matching_entities = [
    #     {'Neoplasm Staging': 0.9342785},
    #     {'Neoplasm Staging': 0.9338578285675354},
    #     {'Neoplasm Staging': 0.937621},
    #     {'Cancer Staging': 0.92}
    # ]

    ## Output: [{'Neoplasm Staging': 0.937621}, {'Cancer Staging': 0.92}]

    max_values = {}
    for item in matching_entities:
        for key, value in item.items():
            max_values[key] = max(max_values.get(key, float('-inf')), value)

    result = []
    for key, value in max_values.items():
        result.append({key: value})

    return result

def matching_entites_to_pages(matched_entities):
    # print(matched_entities)
    mayching_page_entities_info = {}
    page_all_entities = get_all_entities_guideline()
    for page_no, page_entities in page_all_entities.items():
        page_entities = [entity.upper() for entity in page_entities]
        # print(page_entities)
        matching_page_entities = []
        for matched_entity, matched_entity_score in matched_entities.items():
            if matched_entity in page_entities:
                matching_page_entities.append({matched_entity: matched_entity_score})

        if matching_page_entities:
            # print(matching_page_entities)
            matching_page_entities = list_unique_entity_score(matching_page_entities)
            matching_page_entities = sorted(matching_page_entities, key=lambda x: max(x.values()), reverse=True)
            # print(page_no)
            # print(page_entities)
            mayching_page_entities_info[page_no] = {"matching_entities": matching_page_entities, "count": len(matching_page_entities)}

    # Sort on the basis of count
    sorted_data = dict(sorted(mayching_page_entities_info.items(), key=lambda x: x[1]['count'], reverse=True))
    # print(json.dumps(sorted_data, indent=2))
    return sorted_data


def merge_matching_entities(dict1, dict2):
    merged = {}
    all_keys = set(dict1.keys()) | set(dict2.keys())

    for key in all_keys:
        val1 = dict1.get(key, float('-inf'))
        val2 = dict2.get(key, float('-inf'))

        merged[key] = max(val1, val2)

    return merged

def get_matching_entities_from_guideline(sentence):
    entity_label_score = {}
    coder_model = AutoModel.from_pretrained('GanjinZero/UMLSBert_ENG')
    coder_tokenizer = AutoTokenizer.from_pretrained('GanjinZero/UMLSBert_ENG')

    sentence_input = coder_tokenizer(sentence, return_tensors='pt')
    sentence_embed = np.mean(coder_model(**sentence_input).last_hidden_state[0].detach().numpy(), axis=0)

    with open('/usr/src/app/entity_embeddings.pkl', 'rb') as f:
        entity_dict_embeddings = pickle.load(f)

    for ont_entity, embed in entity_dict_embeddings.items():
        onto_ent_embed = np.array(embed)
        sim = np.dot(sentence_embed, onto_ent_embed) / (np.linalg.norm(sentence_embed) * np.linalg.norm(onto_ent_embed))
        if sim > threshold:
            ent = ont_entity.split('$$')[1]
            entity_label_score[ent.upper()] = sim

    return entity_label_score

def get_top_10_pages_most_matching_entities(nodes_entities):
    # import streamlit as st
    # st.write(nodes_entities)

    all_matching_entities = {}

    nodes_entities_dict = {}
    for entity in nodes_entities:
        entity_label_upper = entity["label"].upper()
        if nodes_entities_dict.get(entity_label_upper, None):
            if len(nodes_entities_dict[entity_label_upper]) < len(entity["description"]):
                nodes_entities_dict[entity_label_upper] = entity["description"]
        else:
            nodes_entities_dict[entity_label_upper] = entity["description"]

    # print(json.dumps(nodes_entities_dict, indent=2))

    for entity_label, entity_desc in nodes_entities_dict.items():
        # print(entity_label)
        entity_matches = get_matching_entities_from_guideline(f"{entity_label} which means {entity_desc}")
        all_matching_entities = merge_matching_entities(all_matching_entities, entity_matches)
    page_with_matching_entities_info = matching_entites_to_pages(all_matching_entities)
    # print(json.dumps(page_with_matching_entities_info, indent=2))

    top_10_pages = {}

    # Only the Top 10 Pages
    count = 0
    for page_no in page_with_matching_entities_info:
        top_10_pages[page_no] = page_with_matching_entities_info[page_no]
        if len(top_10_pages) == top_k_pages:
            break

    # print(json.dumps(top_10_pages, indent=2))
    return top_10_pages