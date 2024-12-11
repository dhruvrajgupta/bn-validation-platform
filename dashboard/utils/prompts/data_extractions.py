from pydantic import BaseModel
from typing import List, Optional

class SectionData(BaseModel):
    section_name: str
    paragraph: str

class ListSectionData(BaseModel):
    thinking: str
    sections: List[SectionData]

# 9. Add another section for superscripts informations present within the page for their relevant sections.
DATA_EXTRACTOR = """\
You are an expert at Data Extraction and Merging.

Task Description: 
1. Extract the contents in meaningful sentences so that it can be used for clinical data mining.
2. Extract all the sections from "SOURCE1".
3. Extract all the text accurately from "SOURCE1".
4. Extract all the sections from "SOURCE2".
5. Extract all the text accurately from "SOURCE2".
6. Merge the text contents of the two data sources "SOURCE1" and "SOURCE2"
7. Ensure the extraction is accurate and in detail.
8. Do not summarize.
9. Output in detail.
10. Segregate into meaningful sections.
11. "paragraph" should be in markdown representation in ith Output JSON.
12. The output in "paragraph" should depict the exact meaning in the "SOURCE1" and "SOURCE2".
13. Do not output repeated content. If repeated content, then higher preference for output should be from `SOURCE2`.

SOURCE1:
```
{chunk_data_content}
```

SOURCE2:
```
{html_hr_content}
```

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
    "thinking": "...",
    "sections": [
       {{
           "section_name": "..." ,
           "paragraph": "..."
       }},
        ...
    ]
}}
</answer>

Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""


HTML_TO_READABLE_FORMAT = """\
You are an expert Data Extractor.
You will be given a NCCN Clinical Practitioner's Guidelines page which is converted in HTML5 format.
Your task is to convert this HTML format to markdown format which is human readable and understandable format.
Ensure the extraction is accurate and in detail.

HTML PAGE CONTENT:
```
{html_page}
```
"""

class RelationshipResult(BaseModel):
    relationship_thinking: str
    entity1: str
    entity2: str
    relationship: str

class EntityInformation(BaseModel):
    ontology_name: Optional[str]
    label: Optional[str]
    description: Optional[str]

class E_R_Results(BaseModel):
    thinking: List[str]
    entity_information: List[EntityInformation]
    relationships_information: List[RelationshipResult]

ENTITIES_AND_RELATIONSHIPS = """\
TASK:
You’re an expert in clinical informatics with extensive knowledge of Entity Linking.

TEXT DATA:
`{text}`

##########
INSTRUCTIONS:
1. Extract all the important entities in the TEXT DATA.
2. Extract only the important entities from the TEXT DATA and only if the entities exists.
3. For each entity (MeSH, SNOMED-CT, Wikidata), retrieve only the label and description.
4. Do not retrieve the Entity ID of the terms.
5. This information will be used for clinical data mining, so make sure the labels and descriptions are accurate and relevant to the medical domain.
6. Each Entity label should have their corresponding descriptions.

For each entity, retrieve the following entity information:
1. MeSH label and description
2. SNOMED-CT label and description
3. Wikidata label and description

Now, extract all the relationships between the entities from the TEXT DATA.

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": ["...", ...],
   "entity_information":[
      {{
         "ontology_name": "MeSH",
         "label": "...",
         "description": "..."
      }},
      ...
   ],
   "relationships_information": [
    {{
        "relationship_thinking": "...",
        "entity1": "...",
        "entity2": "...",
        "relationship": "..."
    }},
    ...
   ]
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in  <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

class CausalityExtraction(BaseModel):
    thinking: str
    answer: str

EXTRACT_CAUSALITY = """\
You are an advanced text processing assistant with expertise in clinical data mining, specifically designed to analyze oncology clinical practitioner guidelines. 
Your task is to meticulously extract and tag causes, effects, conditions, and actions from complex clinical texts.

PARAGRAPH:
```
{text}
```

INSTRUCTIONS:
#####
1. You will be provided with text delimited by triple quotes in PARAGRAPH. Extract the cause, effect, condition and action from the given sentence. 
2. Enclose the begnining and the end with tags as given in the examples below. Use <A> for action, <C> for cause, <CO> for condition and <E> for effect.
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
1. Patients with advanced-stage lung cancer have a higher risk of metastasis, particularly if they have a history of smoking. Regular screening and early intervention are recommended for high-risk individuals.
2. Pregnant persons with gestational diabetes  are at increased risk for maternal and fetal complications, including preeclampsia, fetal macrosomia (which can cause shoulder dystocia and birth injury), and neonatal hypoglycemia.
3. Gestational diabetes  has also been associated with an increased risk of several long-term health outcomes in pregnant persons and intermediate outcomes in their offspring.

Tagged Result:
1. <C> Patients with advanced-stage lung cancer </C> <E> have a higher risk of metastasis </E>, particularly <CO> if they have a history of smoking </CO>. <A> Regular screening and early intervention </A> are recommended for high-risk individuals.
2. <CO>Pregnant persons with gestational diabetes</CO> <E>are at increased risk for maternal and fetal complications, including preeclampsia, fetal macrosomia</E> <CO>(which can cause shoulder dystocia and birth injury)</CO>, <E>and neonatal hypoglycemia</E>.
3. <C>Gestational diabetes</C> <E>has also been associated with an increased risk of several long-term health outcomes in pregnant persons and intermediate outcomes in their offspring</E>.

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": "...",
   "answer": "..."
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in  <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""