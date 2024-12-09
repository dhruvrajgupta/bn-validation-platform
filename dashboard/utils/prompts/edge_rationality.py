from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

EDGE_RATIONALITY = """\
You are an expert clinician on the "{model_label}" whose description is "{model_description}". 
Your task is to verify whether the edge Node1 causes Node2 nodes is a valid edge in the "{model_label}" Bayesian Network. 
Use the provided details of Node1 and Node2 nodes and cross-reference with the NCCN Clinical Practitioner’s Guidelines. 
Then, assess the probable causal relationship between the nodes Node1 and Node2.

Input:
Node1:
id: {source_node_id}
type: {source_node_type}
observability: {source_node_observability}
label: {source_node_label}
description: {source_node_description}
Node2:
id: {target_node_id}
type: {target_node_type}
observability: {target_node_observability}
label: {target_node_label}
description: {target_node_description}

Instructions:
1. Extract the relevant information for both Node1 and Node2 nodes based on the provided details in the above Input.
2. Determine if the edge Node1 causes Node2 is valid by cross referencing NCCN Clinical Practitioner’s Guidelines.
3. State the evidences of the validity of the edge Node1 causes Node2.
4. Analyze the causal direction between Node1 and Node2:
5. Evaluate the likelihood of edge Node1 causes Node2.
6. Evaluate the likelihood of edge Node2 causes Node1.
7. Assign a probability to each edge based on your analysis of clinical guidelines and its corresponding relationships.
8. The edge should follow Cause --> Effect direction.
9. Evaluations should be based on facts and not interpretations.
10. Explanation should be corresponding to the edge taken into consideration.
11. Explanation of E2 should follow the same scenario as E1.
12. Explanation should mention the corresponding nodes.
13. In place of Node1 mention {source_node_id}, and in place of Node2 mention {target_node_id}.
13. Use the following structure to present your response:

**Relationship Verification:**
Is the edge (`{source_node_id}`) causes (`{target_node_id}`) valid?

**Evidences from NCCN Clinical Practitioner's Guidelines:**
- ...
- ...
...

**Causal Direction Analysis:**
- **E1** - (`{source_node_id}`) causes (`{target_node_id}`):
    - Causal Direction: ...
    - Probability of (`{source_node_id}`) causes (`{target_node_id}`): ...
    - Explanation: ...
- **E2** - (`{target_node_id}`) causes (`{source_node_id}`):
    - Causal Direction: ...
    - Probability of (`{target_node_id}`) causes (`{source_node_id}`): ...
    - Explanation: ...

**More probable direction:** ...

Example:
Input:

Node1:
id: Smoking
type: Examination Result
observability: Observed
label: Patient Smoking History
description: Whether or not the patient has ever smoked.
Node2:
id: Lung_Cancer
type: Decision Node
observability: Needs to be Predicted
label: Lung Cancer Status
description: Whether or not the patient has lung cancer.
Output:

**Relationship Verification:**
Is the edge (`Smoking`) causes (`Lung_Cancer`) valid?.

**Evidences from Clinical Practitioner's Guidelines:**
- ...
- ...

**Causal Direction Analysis:**
- **E1** - (`Smoking`) causes (`Lung_Cancer`):
    - Causal Direction: Cause --> Effect
    - Probability of (`Smoking`) causes (`Lung_Cancer`): ... %
    - Explanation: ...
- **E2** - (`Lung_Cancer`) causes (`Smoking`):
    - Causal Direction: Effect --> Cause
    - Probability of (`Lung_Cancer`) causes (`Smoking`): ... %
    - Explanation: ...

**More probable direction:** "Tumor size increases the likelihood of lymph node involvement."

LET'S TAKE A DEEP BREATH.
LET'S THINK STEP BY STEP.
REFLECT ON YOUR ANSWER.
"""

# just leave percentage and send screenshot

# Focusing on verifying only only one edge, no flipping

EDGE_RATIONALITY2 = """\
You are an expert clinician on the {model_label} whose description is {model_description}. 
Your task is to verify whether the edge Node1 causes Node2 nodes is a valid edge in the "{model_label}" Bayesian Network. 
Use the provided details of Node1 and Node2 nodes and cross-reference with the NCCN Clinical Practitioner’s Guidelines. 
Then, assess the probable causal relationship between the nodes Node1 and Node2.

Input:
Node1:
id: {source_node_id}
type: {source_node_type}
observability: {source_node_observability}
label: {source_node_label}
description: {source_node_description}
Node2:
id: {target_node_id}
type: {target_node_type}
observability: {target_node_observability}
label: {target_node_label}
description: {target_node_description}

Instructions:
1. Extract the relevant information for both Node1 and Node2 nodes based on the provided details in the above Input.
2. Determine if the edge Node1 causes Node2 is valid by cross referencing NCCN Clinical Practitioner’s Guidelines.
3. State the evidences of the validity of the edge Node1 causes Node2.
4. Analyze the causal direction between Node1 and Node2:
5. Evaluate the likelihood of edge Node1 causes Node2.
6. The edge should follow Cause --> Effect direction.
7. Evaluations should be based on facts and not interpretations.
8. Explanation should be corresponding to the edge taken into consideration.
9. Explanation should mention the corresponding nodes.
10. Use the following structure to present your response:

**Relationship Verification:**
Is the edge (`{source_node_id}`) causes (`{target_node_id}`) valid?

**Evidences from NCCN Clinical Practitioner's Guidelines:**
- ...
- ...
...

**Causal Direction Analysis:**
- **Edge** - (`{source_node_id}`) causes (`{target_node_id}`):
    - Causal Direction: ...
    - Probability of (`{source_node_id}`) causes (`{target_node_id}`): ...
    - Explanation: ...

**More probable direction:** ...

Example:
Input:

Node1:
id: Smoking
type: Examination Result
observability: Observed
label: Patient Smoking History
description: Whether or not the patient has ever smoked.
Node2:
id: Lung_Cancer
type: Decision Node
observability: Needs to be Predicted
label: Lung Cancer Status
description: Whether or not the patient has lung cancer.
Output:

**Relationship Verification:**
Is the edge (`Smoking`) causes (`Lung_Cancer`) valid?.

**Evidences from Clinical Practitioner's Guidelines:**
- ...
- ...

**Causal Direction Analysis:**
- **Edge** - (`Smoking`) causes (`Lung_Cancer`):
    - Causal Direction: Cause --> Effect
    - Probability of (`Smoking`) causes (`Lung_Cancer`): ... %
    - Explanation: ...

**More probable direction:** "Tumor size increases the likelihood of lymph node involvement."

LET'S TAKE A DEEP BREATH.
LET'S THINK STEP BY STEP.
REFLECT ON YOUR ANSWER.
"""
# use just percent symbol

######
# Rahim et al. - 2019 - A Clinical Decision Support System based on Ontology
# Causal Relations: causes
# Inverse Causal Relation: is caused by
######


class CausalDirectionCategory(str, Enum):
    POSITIVE =  "positive"
    NEGATIVE =  "Negative"
    UNKNOWN =  "Unknown"

class CausalDistanceCategory(str, Enum):
    DISTAL = "Distal"
    PROXIMAL = "Proximal"
    UNKNOWN =  "Unknown"

class CausalFactor(BaseModel):
    necessary: bool
    sufficient: bool
# Better naming for the type
class ProbabilityType(str, Enum):
    VERY_LOW = "Very Low"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "Very High"

class EvidencesSource(BaseModel):
    guideline_name: str
    facts_and_recommendations: List[str]

class CausalInfo(BaseModel):
    causal_direction: CausalDirectionCategory
    causal_factor: CausalFactor
    causal_distance: CausalDistanceCategory
    probability_type: ProbabilityType
    evidences_source: EvidencesSource

class EdgeVerification(BaseModel):
    edge: str
    is_valid: bool
    explanation: List[str]
    causal_info: Optional[CausalInfo]

VERIFY_EDGE = """\
You are an expert clinician on the "{model_label}" whose description is "{model_description}". 
Your task is to verify edge {source_id} causes {target_id} nodes is a valid edge in the "{model_label}" Bayesian Network. 
Use the provided details of {source_id} and {target_id} nodes and cross-reference with the NCCN Clinical Practitioner’s Guidelines. 
Then, assess the probable causal relationship between the nodes {source_id} and {target_id}.

##########
INSTRUCTIONS:
1. Extract the relevant information for both {source_id} and {target_id} nodes based on the provided details in the INPUT.
2. Determine if the edge given in input is valid for Metastasis Staging of TNM Staging of Laryngeal Cancer and the NCCN Clinical Practitioner’s Guidelines.
3. State the evidences of the validity of the edge.
4. Analyze the causal direction of the edge.
5. Evaluate the likelihood of the edge based on your analysis of clinical guidelines and known relationships in the staging framework.
6. Evaluations should be based on facts and recommendations, not interpretations.
7. Explanations should be corresponding to the edge taken into consideration.
8. Explanations should mention the corresponding nodes.
9. Verify the evaluations and explanations from Clinical Practitioner's Guidelines.
10. Output in JSON format.

##########
OUTPUT VARIABLES DEFINITTIONS:
edge - The edge which needs to be verified.
is_valid - Whether the edge is valid based on the cross referencing Clinical Practitioner's Guidelines.
explanation - Explanation of what the edge represents and its validity.
causal_info - Contains other information related to edge causality.
causal_direction - Either Positive or Negative or Unknown. A positive influence direction indicates that both factors change in the same direction (e.g. an increase causes an increase effect). A negative influence direction indicates the opposite changes (e.g. an increase causes a decrease effect).
causal_factor - Is necessary or sufficient condition for an effect to occur. Exposure is a term commonly used in epidemiology to denote any condition that is considered as a possible cause of disease. Exposure is considered necessary when it always precedes the effects (e.g. symptoms) and always presents when the effects occur. A sufficient cause is a causal factor whose presence or occurrence guarantees the occurrence of symptom.
causal_distance - Either Distal or Proximal or Unknown. The distal factors lie towards the beginning of causal chain (i.e. indirect causal factors). The the proximal factors lie towards the end of the chain (i.e. cause directly or almost directly the effect).
probability_type - Either very low, low, moderate, high or very high. Determines the likelihood of the edge based on the guidelines.
evidences_source - Evidences, Facts and recommendations from corresponding guidelines that determine the validity of the causal relationship of edge.


##########
DESIRED OUTPUT FORMAT:
Provide the information in the following JSON structure:
{{
    "edge": `({source_id})` causes `(target_id)`,
    "is_valid": ... ,
    "explanation": [ ... ] ,
    "causal_info": {{
        "causal_direction": ... ,
        "causal_factor": {{
            "necessary": ... ,
            "sufficient": ... ,
        }},
        "causal_distance": ... ,
        "probability_type": ... ,
        "verification_source": [
            {{
                "guideline_name": ... ,
                "facts_and_recommendations": [ ... ]
            }}
        ]
    }}
}}

##########
INPUT:
Edge: `({source_id})` causes `({target_id})`

Node 1:
id: {source_id}
type: {source_node_type}
observability: {source_node_observability}
label: {source_label}
description: {source_description}

Node 2:
id: {target_id}
type: {target_node_type}
observability: {target_node_observability}
label: {target_label}
description: {target_description}

LET'S TAKE A DEEP BREATH.
LET'S THINK STEP BY STEP.
REFLECT ON YOUR ANSWER.
"""

# and reflect on your answer

# message_list = [
#     {
#         "role": 'user',
#         "content": [
#             {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": get_base64_encoded_image("../images/best_practices/nine_dogs.jpg")}},
#             {"type": "text", "text": "You have perfect vision and pay great attention to detail which makes you an expert at counting objects in images. How many dogs are in this picture? Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part of the image."}
#         ]
#     }
# ]
#
# response = client.messages.create(
#     model=MODEL_NAME,
#     max_tokens=2048,
#     messages=message_list
# )
# print(response.content[0].text)

class EdgeRepresentation(BaseModel):
    edge: str
    thinking: List[str]
    representation: str

# "Unobserved" nodes are evaluated from the results of nodes of type 'Examination Results' which are different diagnostic methods.
# Emphasis on 'observability' of the node. is very crucial, even tough observability is mentioned in the context
EDGE_REPRESENTATION_E1 = """\
You are an expert clinician on the "{model_label}" whose description is "{model_description}". 
Your task is to understand what the edge {source_id} causes {target_id} represents. 
Use the provided details of {source_id} and {target_id} nodes. 

Emphasis on 'observability' of both nodes.
Nodes of type `Examination Results` represent different types of diagnostic methods.
`Patient Situation` nodes are evaluated from the results of node type `Examination Results`.

NODE 1: 
id: `{source_id}`
type: `{source_type}`
observability: `{source_observability}`
label: `{source_label}`
description: `{source_description}`
node_states: 
`{source_states}`

NODE 2:
id: `{target_id}`
type: `{target_type}`
observability: `{target_observability}`
label: `{target_label}`
description: `{target_description}`
node_states: 
`{target_states}`

##########
OUTPUT VARIABLES DEFINITTIONS:
representation: meaning of the edge representation and its description.

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "edge": "`{source_id}` causes `{target_id}`",
   "thinking": ["...", ...],
   "representation":"..."
}}
</answer>

Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

# REVERSE OF E1
EDGE_REPRESENTATION_E2 = """\
You are an expert clinician on the "{model_label}" whose description is "{model_description}". 
Your task is to understand what the edge {target_id} causes {source_id} represents. 
Use the provided details of {target_id} and {source_id} nodes. 

Emphasis on 'observability' of both nodes.
Nodes of type `Examination Results` represent different types of diagnostic methods.
`Patient Situation` nodes are evaluated from the results of node type `Examination Results`.

NODE 1: 
id: `{target_id}`
type: `{target_type}`
observability: `{target_observability}`
label: `{target_label}`
description: `{target_description}`
node_states: 
`{target_states}`

NODE 2:
id: `{source_id}`
type: `{source_type}`
observability: `{source_observability}`
label: `{source_label}`
description: `{source_description}`
node_states: 
`{source_states}`

##########
OUTPUT VARIABLES DEFINITTIONS:
representation: meaning of the edge representation and its description.

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "edge": "`{target_id}` causes `{source_id}`"
   "thinking": ["...", ...],
   "output":"..."
}}
</answer>

Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

class Option(str, Enum):
    A = "A"
    B = "B"
class EdgeOrientationJudgement(BaseModel):
    thinking: List[str]
    answer: Option

# During reasoning, a greater emphasis should be imposed on the 'observability' of the nodes.
# Paper: Causal Discovery with Language Models as Imperfect Experts (2023)
LLM_EDGE_ORIENTATION_JUDGEMENT = """\
E1: `{e1}`
E2: `{e2}`

Among these two options which one is the most likely true: 

(A) {n1} {verbk} {n2} 
(B) {n2} {verbk} {n1} 

The answer is: ...

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": ["...", ...],
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""


class CausalDirectionCategory(str, Enum):
    POSITIVE =  "positive"
    NEGATIVE =  "Negative"
    UNKNOWN =  "Unknown"

class CausalDistanceCategory(str, Enum):
    DISTAL = "Distal"
    PROXIMAL = "Proximal"
    UNKNOWN =  "Unknown"

class CausalFactor(BaseModel):
    necessary: bool
    sufficient: bool

class CausalInfo(BaseModel):
    causal_direction: CausalDirectionCategory
    causal_factor: CausalFactor
    causal_distance: CausalDistanceCategory

class CFResult(BaseModel):
    thinking: List[str]
    edge: str
    is_valid: bool
    explanation: List[str]
    causal_info: Optional[CausalInfo]

CAUSAL_FACTORS = """\
You are an expert clinician. 
Your task is to verify edge {n1} causes {n2} nodes is a valid edge in the Bayesian Network. 
Use the provided details of {n1} and {n2} nodes and then, assess the probable causal relationship between the nodes.

##########
INPUT:
Edge: `({n1})` causes `({n2})`

NODE1:
id: {n1}
type: {n1_type}
observability: {n1_observability}
label: {n1_label}
description: {n1_description}
states: {n1_states}

NODE2:
id: {n2}
type: {n2_type}
observability: {n2_observability}
label: {n2_label}
description: {n2_description}
states: {n2_states}

##########
INSTRUCTIONS:
1. Extract the relevant information for both {n1} and {n2} nodes based on the provided details in the INPUT.
2. Determine if the edge given in input is valid.
3. Analyze the causal direction of the edge.
4. Explanations should be corresponding to the edge taken into consideration.
5. Explanations should mention the corresponding nodes.
6. Output in JSON format.

##########
OUTPUT VARIABLES DEFINITTIONS:
edge - The edge which needs to be verified.
explanation - Explanation of what the edge represents and its validity.
causal_info - Contains other information related to edge causality.
causal_direction - Either Positive or Negative or Unknown. A positive influence direction indicates that both factors change in the same direction (e.g. an increase causes an increase effect). A negative influence direction indicates the opposite changes (e.g. an increase causes a decrease effect).
causal_factor - Is necessary or sufficient condition for an effect to occur. Exposure is a term commonly used in epidemiology to denote any condition that is considered as a possible cause of disease. Exposure is considered necessary when it always precedes the effects (e.g. symptoms) and always presents when the effects occur. A sufficient cause is a causal factor whose presence or occurrence guarantees the occurrence of symptom.
causal_distance - Either Distal or Proximal or Unknown. The distal factors lie towards the beginning of causal chain (i.e. indirect causal factors). The the proximal factors lie towards the end of the chain (i.e. cause directly or almost directly the effect).

##########
DESIRED OUTPUT FORMAT:
Provide the information in the following JSON structure:
<thinking>
...
</thinking>
<answer>
{{
    "thinking": ["...", ...],
    "edge": `({n1})` causes `({n2})`,
    "explanation": [ ... ] ,
    "causal_info": {{
        "causal_direction": ... ,
        "causal_factor": {{
            "necessary": ... ,
            "sufficient": ... ,
        }},
        "causal_distance": ... ,
    }}
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""