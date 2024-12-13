import numpy as np

from numpy import dot
from numpy.linalg import norm
from transformers import AutoTokenizer, AutoModel


def get_bert_based_similarity(sentence_pairs, model, tokenizer):
    """
    computes the embeddings of each sentence and its similarity with its corresponding pair
    Args:
        sentence_pairs(dict): dictionary of lists with the similarity type as key and a list of two sentences as value
        model: the language model
        tokenizer: the tokenizer to consider for the computation

    Returns:
        similarities(dict): dictionary with similarity type as key and the similarity measure as value
    """
    similarities = dict()
    for sim_type, sent_pair in sentence_pairs.items():
        inputs_1 = tokenizer(sent_pair[0], return_tensors='pt')
        inputs_2 = tokenizer(sent_pair[1], return_tensors='pt')
        sent_1_embed = np.mean(model(**inputs_1).last_hidden_state[0].detach().numpy(), axis=0)
        sent_2_embed = np.mean(model(**inputs_2).last_hidden_state[0].detach().numpy(), axis=0)
        similarities[sim_type] = dot(sent_1_embed, sent_2_embed) / (norm(sent_1_embed) * norm(sent_2_embed))
    return similarities


# if __name__ == "__main__":
#     sentence_pairs = {'similar': ['the MRI of the abdomen is normal and without evidence of malignancy',
#                                   'no significant abnormalities involving the abdomen is observed'],
#                       'dissimilar': ['mild scattered paranasal sinus mucosal thickening is observed',
#                                      'deformity of the ventral thecal sac is observed']}
#
#     bio_clinical_bert_model = AutoModel.from_pretrained('emilyalsentzer/Bio_ClinicalBERT')
#     bio_clinical_bert_tokenizer = AutoTokenizer.from_pretrained('emilyalsentzer/Bio_ClinicalBERT')
#     print(get_bert_based_similarity(sentence_pairs, bio_clinical_bert_model, bio_clinical_bert_tokenizer))
#
#     # ouput:
#     # {'similar': 0.8878437, 'dissimilar': 0.8917133}

if __name__ == "__main__":
    sentence_pairs = {'similar': ['the MRI of the abdomen is normal and without evidence of malignancy',
                                  'no significant abnormalities involving the abdomen is observed'],
                     'dissimilar': ['mild scattered paranasal sinus mucosal thickening is observed',
                                   'deformity of the ventral thecal sac is observed']}

    coder_model = AutoModel.from_pretrained('GanjinZero/UMLSBert_ENG')
    coder_tokenizer = AutoTokenizer.from_pretrained('GanjinZero/UMLSBert_ENG')
    print(get_bert_based_similarity(sentence_pairs, coder_model, coder_tokenizer))
    # output:
    # {similar': 0.92078525, 'dissimilar': 0.7726508}