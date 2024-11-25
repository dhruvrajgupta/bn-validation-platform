from typing import Optional, List
from pydantic import BaseModel

NODE_TOKENS_AND_THEIR_MEANINGS = """\
Node tokens and their meanings:
hep - The liver(hepar)
M - Metastasis
diagnostic - concerned with the diagnosis examinations of illness or other problems
sono - concerned with Ultrasound/Sonography
peri - peritoneum
"""

NODE_COMPOSITION_GUIDANCE = """\
The NodeID is composed of node tokens. Node tokens are obtained by splitting the node ID using `_`.
"""

class StateDescription(BaseModel):
    state_name: str
    state_description: str

class NodeDescription(BaseModel):
    thinking: List[str]
    id: str
    label: str
    description: str
    node_states_description: List[StateDescription]

EXTRACT_NODE_DESCRIPTION = """\
TASK:
You’re an expert in clinical informatics with extensive knowledge of Bayesian Networks, particularly focused on "{model_label}" whose description is "{model_description}". 
Your specialty lies in decoding complex nodes within these networks to extract detailed and clinically relevant information for data mining purposes.
Your task is to gather detailed information for a specific node in the given Bayesian Network.

"""+NODE_TOKENS_AND_THEIR_MEANINGS+"""

NodeID: identifier of the node in the Bayesian Network.
States: states of the node in the Bayesian Network.

NODE INFORMATION:
NodeID: `{node_id}`
Node Type: `{node_type}`
Observability: `{node_observability}`
States: `{states}`

##########
INSTRUCTIONS: 
1. Please provide the following information for the node with ID "`{node_id}`":
label, description, node_states_description, state_name, state_description
2. """+NODE_COMPOSITION_GUIDANCE+"""
3. Node label should include all the node tokens meanings.
4. The Node label should provide concise information of all information present in the node description.
5. Do not include the states information in the label.

##########
OUTPUT VARIABLES DEFINITIONS:
label: Provide a clinically relevant label that describes the node.
description: Describe the clinical meaning and significance of the node. Describe the methods used to determine the node.
node_state_description: A List of states of the node along with its description.
state_name: Name of the state.
state_description: Description of the state of the node and what it represents.


DESIRED OUTPUT FORMAT: 
<thinking>
...
</thinking>
<answer>
Provide the information in the following JSON structure:
{{
   "thinking": ["...", ...],
   "id":"{node_id}",
   "label":"...",
   "description":"...",
   "node_states_description": [
        "state_name": ... ,
        "state_description": ... ,
   ]
}}
</answer>

Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

# Existing Entity labels:
# MeSH: `{mesh_entities}`
# SNOMED-CT: `{snomed_ct_entities}`
# Wikidata: `{wikidata_entities}`

class EntityInformation(BaseModel):
    ontology_name: Optional[str]
    label: Optional[str]
    description: Optional[str]

class EntityInformationResult(BaseModel):
    thinking: List[str]
    entity_information: List[EntityInformation]

# Node States: `{node_states}`

ENTITY_INFORMATION = """\
TASK:
You’re an expert in clinical informatics with extensive knowledge of Entity Linking.

Node Label: label of the node in the Bayesian Network.

NODE INFORMATION:
NodeID: `{node_id}`
Node Label: `{node_label}`
Node States: `{node_states}`

EXCLUDE THE FOLLOWING ENTITIES:
[M0, M1, MX]


##########
INSTRUCTIONS:
1. Please provide the following information for the node label "`{node_label}`".
2. Extract all the important fine grained specific entities in the node label.
3. Extract only the important entities from the node states and only if the entities exists.
4. For each entity (MeSH, SNOMED-CT, Wikidata), retrieve only the label and description.
5. Do not retrieve the Entity ID of the terms.
6. This information will be used for clinical data mining, so make sure the labels and descriptions are accurate and relevant to the medical domain.
7. Each Entity label should have their corresponding descriptions.
8. Do not output entity information for the Node token 'patient'.

For each entity, retrieve the following entity information:
1. MeSH label and description
2. SNOMED-CT label and description
3. Wikidata label and description


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
   ]
}}
</answer>

Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""