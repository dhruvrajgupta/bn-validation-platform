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