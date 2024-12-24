import json
import numpy as np
from transformers import AutoTokenizer, AutoModel
import pickle

threshold = 0.93

def create_entity_embeddings():
    page_ont_ent_desc = {}
    with open("/home/dhruv/Desktop/bn-validation-platform/pg_entities_dict.json", "r") as f:
        page_ont_ent_desc = json.loads(f.read())

    ont_ent_desc_dict = {}
    for page_no, ent_list in page_ont_ent_desc.items():
        print(page_no)
        print(ent_list)
        for ent_info in ent_list:
            key = f"{ent_info['ontology_name']}$${ent_info['label']}"
            print(key)
            if key in ont_ent_desc_dict.keys():
                pass
            else:
                ont_ent_desc_dict[key] = ent_info['description']

    print(len(ont_ent_desc_dict))

def merge_matching_entities(dict1, dict2):
    merged = {}
    all_keys = set(dict1.keys()) | set(dict2.keys())

    for key in all_keys:
        val1 = dict1.get(key, float('-inf'))
        val2 = dict2.get(key, float('-inf'))

        merged[key] = max(val1, val2)

    return merged

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

def get_matching_entities_from_guideline(sentence):
    entity_label_score = {}
    coder_model = AutoModel.from_pretrained('GanjinZero/UMLSBert_ENG')
    coder_tokenizer = AutoTokenizer.from_pretrained('GanjinZero/UMLSBert_ENG')

    sentence_input = coder_tokenizer(sentence, return_tensors='pt')
    sentence_embed = np.mean(coder_model(**sentence_input).last_hidden_state[0].detach().numpy(), axis=0)

    with open('/home/dhruv/Desktop/bn-validation-platform/entity_embeddings.pkl', 'rb') as f:
        entity_dict_embeddings = pickle.load(f)
        print(len(entity_dict_embeddings.keys())) # 982

    with open('/home/dhruv/Desktop/bn-validation-platform/entity_embeddings_part.pkl', 'rb') as f:
        entity_dict_embeddings = pickle.load(f)
        print(len(entity_dict_embeddings.keys())) # 546

    for ont_entity, embed in entity_dict_embeddings.items():
        onto_ent_embed = np.array(embed)
        sim = np.dot(sentence_embed, onto_ent_embed) / (np.linalg.norm(sentence_embed) * np.linalg.norm(onto_ent_embed))
        if sim > threshold:
            onto = ont_entity.split('$$')[0]
            ent = ont_entity.split('$$')[1]
            # print(onto)
            # print(f"{ont_entity.split('$$')[1]}\t\t\t{sim}")
            entity_label_score[ent] = sim
            # matched_entities.append({
            #     "ontology_name": onto,
            #     "label": ent,
            #     "similarity": sim
            # })

    return entity_label_score


def matching_entites_to_pages(matched_entities):
    existing_matched_pages_info = {}

    with open('/home/dhruv/Desktop/bn-validation-platform/data.json') as f:
        page_entity_data = json.loads(f.read())

    for page_no, page_entities in page_entity_data.items():
        matching_page_entities = []
        # notx = []
        for page_entity in page_entities:
            if page_entity['label'] in matched_entities:
                # print(page_entity)
                matching_page_entities.append({page_entity['label']: matched_entities[page_entity['label']]})
            # else:
            #     notx.append(page_entity)

        print(matching_page_entities)
        # convert it to a set
        if matching_page_entities:
            matching_page_entities = list_unique_entity_score(matching_page_entities)
            matching_page_entities = sorted(matching_page_entities, key=lambda x: max(x.values()), reverse=True)

            print(matching_page_entities)
            print(page_no)
            existing_matched_pages_info[page_no] = {"matching_entities": matching_page_entities, "count": len(matching_page_entities)}


        # break
    # print(existing_matched_pages_info)

    # Sort on the basis of count
    sorted_data = dict(sorted(existing_matched_pages_info.items(), key=lambda x: x[1]['count'], reverse=True))
    return sorted_data

if __name__ == "__main__":
    sent1 = "Computed Tomography which means A diagnostic imaging procedure that uses a combination of X-rays and computer technology to produce cross-sectional images of the body"
    sent2 = "Tumor Staging which means A process of determining the extent to which a cancer has grown and spread"
    sent3 = "Biopsy which means medical test involving extraction of sample cells or tissues for examination to determine the presence or extent of a disease."
    sent4 = "Endoscopic Resection which means a technique used to remove cancerous or other abnormal lesions found in the digestive tract."
    sent5 = "Magnetic Resonance Imaging which means Uses strong magnetic fields and radio waves to generate detailed images."

    sent_arr = [sent1, sent2, sent3, sent4, sent5]

    # create_entity_embeddings()

    all = {}

    for idx, sent in enumerate(sent_arr):
        sent_match_entities = get_matching_entities_from_guideline(sent)
        all = merge_matching_entities(all, sent_match_entities)
        print(json.dumps(all, indent=2))

    print(matching_entites_to_pages(all))

    print(json.dumps(matching_entites_to_pages(all), indent=2))


    # matching_entities = get_matching_entities_from_guideline(sent2)
    #
    # print(json.dumps(matching_entities, indent=2))
    # print(get_matching_entities_from_guideline(sent3))
    #
    # matching_entites_to_pages(matching_entities)

    # 93