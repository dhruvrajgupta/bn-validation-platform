from pydantic import BaseModel
from typing import List

class ListCauseEffect(BaseModel):
    result: List[str]

# MODIFIED
# Causality extraction from medical text using Large Language Models (LLMs), Gopalkrishnan et al.
EXTRACT_CAUSALITY = """\
You are an advanced text processing assistant with expertise in clinical data mining, specifically designed to analyze oncology clinical practitioner guidelines. 
Your task is to meticulously extract and tag causes, effects, conditions, and actions from complex clinical texts.

Perform the following actions:
#####
1 - You will be provided with text delimited by triple quotes. Extract the cause, effect, condition and action from the given sentence. 
2. Enclose the begnining and the end with tags as given in the examples below. Use A for action, C for cause, CO for condition and E for effect.
Cause (C): The reason or origin that leads to an effect. Causes often involve disease conditions, risk factors, or underlying mechanisms.
Effect (E): The outcome or result of a cause. Effects usually represent clinical outcomes, complications, or results of a specific cause.
Condition (CO): The circumstance or prerequisite required for an action or effect to occur. Conditions may include patient characteristics, clinical scenarios, or specific diagnostic criteria.
Action (A): The recommended or described response or activity to address a cause or condition. Actions typically involve clinical interventions, diagnostic procedures, or treatment recommendations.

3. Identify and tag all relevant elements within each sentence, ensuring no critical information is overlooked.
4. If a sentence contains multiple elements (e.g., both cause and effect), ensure all are tagged accordingly.
5. Use separate tags for each element, even if they are part of the same sentence.
6. Each tagged element should be clear and precise, representing standalone information that can be easily understood without additional context.
7. Maintain an understanding of clinical context to ensure accurate interpretation of complex medical terminology and guidelines.
8. Prioritize clinical relevance and accuracy when identifying elements in the text.
9. Output the result in JSON format.

EXAMPLES:
#####
Patients with advanced-stage lung cancer have a higher risk of metastasis, particularly if they have a history of smoking. Regular screening and early intervention are recommended for high-risk individuals.

2 - Output should be in JSON format.
Example Output:
'result': [
    '<C> Patients with advanced-stage lung cancer </C> <E> have a higher risk of metastasis </E>, particularly <CO> if they have a history of smoking </CO>. <A> Regular screening and early intervention </A> are recommended for high-risk individuals.'
    ...
]

Text:
SECTION_NAME: {section_name}

SECTION_CONTENT:
```
{text}
```

Let's think step by step
"""

# '<C> Pregnant persons with gestational diabetes </C> <E> are at increased risk for maternal and fetal complications, including preeclampsia, fetal macrosomia (which can cause shoulder dystocia and birth injury), and neonatal hypoglycemia </E>.',
# '<C> Gestational diabetes </C> has also been <A> associated </A> with <E> an increased risk of several long-term health outcomes in pregnant persons and intermediate outcomes in their offspring </E>.',
#         '<O> EVIDENCE ASSESSMENT The USPSTF concludes </O> <CO> with moderate certainty </CO> that there is <E> a moderate net benefit to screening for gestational diabetes at 24 weeks of gestation or after to improve maternal and fetal outcomes </E>.',
#         '<O> RECOMMENDATION The USPSTF recommends </O> <A> screening for gestational diabetes </A> <CO> in asymptomatic pregnant persons at 24 weeks of gestation or after </CO>.',



# ATOMIC_FACTS_AND_KEY_ELEMENTS = """\
# You are now an intelligent assistant tasked with meticulously extracting atomic facts from a long text.
# 1. Atomic Facts: The smallest, indivisible facts, presented as concise sentences. These include
# propositions, theories, existences, concepts, and implicit elements like logic, causality, event
# sequences, interpersonal relationships, timelines, etc.
# Requirements:
# #####
# 1. You should extract key atomic facts comprehensively, especially those that are
# important and potentially query-worthy and do not leave out details.
# 2. Whenever applicable, mention the specific explicit subject of the atomic fact in relation to the SECTION NAME and SUMMARY
# 3. Ensure that the atomic facts you extract are presented in the same language as
# the original text (e.g., English or Chinese).
# 4. You should output a total of atomic facts that do not exceed 1024 tokens.
# 5. You should output the atomic facts as a python list of strings.
# #####
# Example:
# #####
# User:

# SUMMARY:
# This page details the AJCC TNM staging system for laryngeal cancers (8th edition, 2017). It categorizes the primary tumor (T) stages
# for different regions of the larynx: supraglottis, glottis, and subglottis. Each section describes the progression of tumor
# invasion, from limited local spread to advanced disease involving surrounding tissues and structures. T1 represents localized
# tumors, while T4 is divided into T4a for moderately advanced and T4b for very advanced disease, indicating extensive invasion
# into critical areas such as the thyroid cartilage, prevertebral space, or carotid artery encasement. Non-epithelial tumors
# are excluded from this staging system.

# SECTION NAME: Primary Tumor - Glottis

# SECTION CONTENT:
# The tumor invades soft tissues ......


# Assistant:
# [
#     "The tumor in stage T4a of the Glottis invades soft tissues of the neck, including deep extrinsic muscle of the tongue."
#     ......
# ]
# #####
# Please strictly follow the above format. Let’s begin.

# LONG TEXT:
# ```
# SUMMARY:
# {summary}

# SECTION NAME: {section_name}

# SECTION CONTENT:
# {section_content}
# ```
# """

# Here Structured Output was not giving good results
EXTRACT_ATOMIC_FACTS = """\
You are now an intelligent assistant tasked with meticulously extracting atomic facts from a long text.
1. Atomic Facts: An atomic fact is a simple, standalone statement that conveys a single piece of information. 
Each fact should be a clear and concise sentence, free from any unnecessary details or compound structures.
The smallest, indivisible facts, presented as concise sentences. These include propositions, theories, 
existences, concepts, and implicit elements like logic, causality, event
sequences, interpersonal relationships, timelines, etc.
Requirements:
#####
1. (!! Important !!) Break down the sentences into individual facts. 
2. Each fact should only contain one subject and one predicate.
3. Ensure that each fact is easy to understand on its own, without requiring context from the paragraph.
4. Each fact should be a grammatically complete sentence.
5. You should extract key atomic facts comprehensively, especially those that are
important and potentially query-worthy and do not leave out details.
6. Whenever applicable, mention the specific explicit subject of the atomic fact in relation to the SECTION NAME
7. Ensure that the atomic facts you extract are presented in the same language as
the original text (e.g., English or Chinese).
8. Your answer format for each line should be: [Serial Number], [Atomic Facts].
#####
Example:
#####
User:
SECTION NAME: Primary Tumor - Glottis

SECTION CONTENT:
The tumor invades soft tissues ......


Assistant:
1. The tumor in stage T4a of the Glottis invades soft tissues of the neck, including deep extrinsic muscle of the tongue.
......

#####
Please strictly follow the above format. Let’s begin.

LONG TEXT:
```
SECTION NAME: {section_name}

SECTION CONTENT:
{section_content}
```
"""

class SectionData(BaseModel):
    section_name: str
    paragraph: List[str]

class ListSectionData(BaseModel):
    result: List[SectionData]

DATA_EXTRACTOR = """\
INSTRUCTIONS:
1. Extract the important contents of this page.
2. Extract the contents in meaningful sentences so that it can be used for clinical data mining.
3. Do not summarize.
4. Output in detail.
5. Segregate into meaningful sections.
6. Only extract the information of that specified sections.

HTML PAGE:
```
{html_page}
```

SECTIONS:
[{sections}]

Output format in JSON:
[
   {{
       "section_name": ... ,
       "paragraph": []
   }},
 ...
]

"""

EXTRACT_NODE_DESCRIPTION = """\
TASK:
You are working with a Bayesian Network focused on the "Metastasis Staging of TNM staging of laryngeal cancer".
Your task is to decode a specific node in this Bayesian Network and then gather detailed information of the node 
for clinical data mining purposes.
NodeID: identifier of the node in the Bayesian Network.
States: states of the node in the Bayesian Network.

NODE INFORMATION:
NodeID: "{node_id}"
States: "{states}"

INSTRUCTIONS: 
Please provide the following information for the node with ID "{node_id}":
Label: Provide a clinically relevant label that describes the node.
Description: Describe the clinical meaning and significance of the node, focusing on how it relates to the context of Metastasis Staging of TNM Staging of laryngeal cancer in details. Describe the methods used to determine the node.
Entity Information: 
For this node, retrieve the following entity information:
1. MeSH label and description
2. SNOMED-CT label and description
3. Wikidata label and description

IMPORTANT NOTES:
1. For each entity (MeSH, SNOMED-CT, Wikidata), retrieve only the label and description.
2. Do not retrieve the Entity ID of the terms.
3. If there is no corresponding entity information, output "None" for that particular field.
4. Output in JSON format.
5. The description of node should also display each states of the node and what it represents.

This information will be used for clinical data mining, so make sure the labels and descriptions are accurate and relevant to the medical domain.

DESIRED OUTPUT FORMAT: 
Provide the information in the following JSON structure:
{{"id":"{node_id}","label":"...","description":"...","entity_information":[{{"ontology_name":"MeSH","label":"...","description":"..."}},{{"ontology_name":"SNOMED-CT","label":"...","description":"..."}},{{"ontology_name":"Wikidata","label":"...","description":"..."}}]}}

If any entity information is not found, replace that field with "None".
"""

EDGE_RATIONALITY = """\
Verify whether the relationship between Node1 and Node2 nodes is a valid edge in the "Metastasis Staging of TNM Staging of Laryngeal Cancer" Bayesian Network. Use the provided details of Node1 and Node2 nodes and cross-reference with the NCCN Clinical Practitioner’s Guidelines. Then, assess the probable causal relationship between the nodes Node1 and Node2.

Input:
Node1:
id: {source_node_id}
label: {source_node_label}
description: {source_node_description}
Node2:
id: {target_node_id}
label: {target_node_label}
description: {target_node_description}

Instructions:
1. Extract the relevant information for both Node1 and Node2 nodes based on the provided details in the above Input.
2. Determine if there is a valid relationship between Node1 and Node2 for Metastasis Staging of TNM Staging of Laryngeal Cancer and the NCCN Clinical Practitioner’s Guidelines.
3. State the evidences of the validity of the relationship between Node1 and Node2.
4. Analyze the causal direction between Node1 and Node2:
5. Evaluate the likelihood of the relationship flowing from Node1 to Node2.
6. Evaluate the likelihood of the relationship flowing from Node2 to Node1.
7. Assign a probability to each possible direction based on your analysis of clinical guidelines and known relationships in the staging framework.
8. The edge should follow Cause --> Effect direction.
9. Evaluations should be based on facts and not interpretations.
10. Explanation should be corresponding to the edge taken into consideration.
11. Explanation of E2 should follow the same context as E1.
12. Explanation should mention the corresponding nodes.
13. Use the following structure to present your response:

**Relationship Verification:**
Is the edge between (`{source_node_id}`) and (`{target_node_id}`) valid?

**Evidences from NCCN Clinical Practitioner's Guidelines:**
- ...
- ...
...

**Causal Direction Analysis:**
- **E1** - (`{source_node_id}`, `{target_node_id}`):
    - Causal Direction: ...
    - Probability of (`{source_node_id}`, `{target_node_id}`): ...
    - Explanation: ...
- **E2** - (`{target_node_id}`, `{source_node_id}`):
    - Causal Direction: ...
    - Probability of (`{target_node_id}`, `{source_node_id}`): ...
    - Explanation: ...

**More probable direction:** ...

Example:
Input:

Node1:
id: Smoking
label: Patient Smoking History
description: Whether or not the patient has ever smoked.
Node2:
id: Lung_Cancer
label: Lung Cancer Status
description: Whether or not the patient has lung cancer.
Output:

**Relationship Verification:**
Is the edge between (`Smoking`) and (`Lung_Cancer`) valid?.

**Evidences from Clinical Practitioner's Guidelines:**
- ...
- ...

**Causal Direction Analysis:**
- **E1** - (`Smoking`, `Lung_Cancer`):
    - Causal Direction: Cause --> Effect
    - Probability of (`Smoking`, `Lung_Cancer`): 90%
    - Explanation: ...
- **E2** - (`Lung_Cancer`, `Smoking`):
    - Causal Direction: Effect --> Cause
    - Probability of (`Lung_Cancer`, `Smoking`): 10%
    - Explanation: ...

**More probable direction:** "Tumor size increases the likelihood of lymph node involvement."
"""