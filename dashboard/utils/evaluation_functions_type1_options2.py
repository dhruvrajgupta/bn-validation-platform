from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

import json
import openai
import weave

import asyncio
import numpy as np
from math import exp

from utils.db import get_node_descriptions, get_causal_factors

import streamlit as st

############## PORTION WITHIN THIS SECTION IS COMMON FOR ALL EVALUATIONS ##############

# Example
# dataset = [
#     {"id": 1, "edge": (), "correct": "B", "incorrect": "A", "prompt": "..."}
# ]

def format_reasoning(evaluation_data):
    for id, evaluation_data_item in enumerate(evaluation_data):
        # print(json.dumps(evaluation_data, indent=2))
        list_reasoning = evaluation_data_item.get("reasoning")
        # st.write(list_reasoning)
        if list_reasoning:
            formatted_reasoning = ""
            for step, reason in enumerate(list_reasoning):
                formatted_reasoning += f"{step + 1}. {reason}\n"
            evaluation_data[id]["reasoning"] = formatted_reasoning

        evidences = evaluation_data_item.get("evidences")
        if evidences:
            formatted_evidences = ""
            for step, evidence in enumerate(evidences):
                formatted_evidences += f"{step + 1}. {evidence}\n"
            evaluation_data[id]["evidences"] = formatted_evidences

        list_critique_reasoning = evaluation_data_item.get("critique_reasoning")
        # print(list_critique_reasoning)
        if list_critique_reasoning:
            formatted_critique_reasoning = ""
            for step, reason in enumerate(list_critique_reasoning):
                formatted_critique_reasoning += f"{step + 1}. {reason}\n"
            evaluation_data[id]["critique_reasoning"] = formatted_critique_reasoning

    return evaluation_data

CRITIQUE_PROMPT = """\
Analyze the output from an AI assistant. 
Is the final answer ({ini_answer}) consistent with the reasoning provided by the assistant?  

Question: {prompt_from_before}  
AI assistant: {answer_from_before}

The answer is: ...

DESIRED OUTPUT FORMAT:
<critique_thinking>
...
</critique_thinking>
<critique_answer>
{{
   "critique_thinking": ["...", ...]
   "critique_answer": ...
}}
</critique_answer>

Before providing the answer in <critique_answer> tags, think step by step in detail in <critique_thinking> tags and analyze every part.
Output inside <critique_answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

class Option(str, Enum):
    A = "A"
    B = "B"
    # C = "C"

class EdgeOrientationJudgement(BaseModel):
    # id: int
    thinking: List[str]
    evidences: Optional[List[str]]
    answer: Option

class CritiqueOption(str, Enum):
    A = "A"
    B = "B"

class CritiqueResponse(BaseModel):
    critique_thinking: List[str]
    critique_answer: CritiqueOption

class EvaluationModel(weave.Model):
    model_name: str

    @weave.op()
    async def predict(self, prompt: str) -> dict:
        client = openai.AsyncClient()

        response = await client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format=EdgeOrientationJudgement,
            temperature=0,
            logprobs=True,
            # top_logprobs=3,
            seed=123
        )
        result = response.choices[0].message.content

        answer_choice_probablities = {
            "A": None,
            "B": None,
            # "C": None
        }

        # import numpy as np
        # from math import exp
        # for token in response.choices[0].logprobs.content[-2].top_logprobs:
        #     print("Token:", token.token)
        #     print("Log prob:", token.logprob)
        #     print("Linear prob:", np.round(exp(token.logprob) * 100, 2), "%")
        #     print("Bytes:", token.bytes, "\n")

            # if token.token == "A":
            #     answer_choice_probablities["A"] = np.round(exp(token.logprob) * 100, 2)
            # elif token.token == "B":
            #     answer_choice_probablities["B"] = np.round(exp(token.logprob) * 100, 2)
            # elif token.token == "C":
            #     answer_choice_probablities["C"] = np.round(exp(token.logprob) * 100, 2)
        # print(answer_choice_probablities)
        #
        answer_choice_token_log_prob_content = response.choices[0].logprobs.content[-2]
        if answer_choice_token_log_prob_content.token == "B":
            answer_choice_probablities["B"] = np.round(exp(answer_choice_token_log_prob_content.logprob) * 100, 2)
            answer_choice_probablities["A"] = np.round(100.0 - answer_choice_probablities["B"], 2)
        else:
            answer_choice_probablities["A"] = np.round(exp(answer_choice_token_log_prob_content.logprob) * 100, 2)
            answer_choice_probablities["B"] = np.round(100.0 - answer_choice_probablities["A"],2)

        if result is None:
            raise ValueError("No response from model")
        parsed = json.loads(result)
        ini_parsed = json.loads(result)
        parsed["answer_choice_probablities"] = answer_choice_probablities

        #### Critique ####

        # print(CRITIQUE_PROMPT.format(
        #     prompt_from_before=prompt,
        #     answer_from_before=ini_parsed,
        #     ini_answer=ini_parsed["answer"]
        # ))
        critique_response = await client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "user", "content": CRITIQUE_PROMPT.format(
                    prompt_from_before=prompt,
                    answer_from_before=ini_parsed,
                    ini_answer=ini_parsed["answer"]
                )}
            ],
            response_format=CritiqueResponse,
            temperature=0,
            logprobs=True,
            # top_logprobs=3,
            seed=123
        )
        critique_result = critique_response.choices[0].message.content
        # print(critique_result)
        if critique_result is None:
            raise ValueError("No response from model")
        critique_parsed = json.loads(critique_result)

        parsed["critique"] = critique_parsed

        return parsed

#######################################################################################


######## DIFFERENT EVALUATIONS START FROM HERE ########


# ######## USING NODE IDENTIFIERS AND THEIR STATE NAMES | CAUSAL VERB: causes ########
# NODE_ID_AND_STATE_NAMES = """\
# NODE 1:
# node_id: {n1}
# states: {n1_states}
#
# NODE 2:
# node_id: {n2}
# states: {n2_states}
#
# Among these three options which one is the most likely true:
#
# (A) {n1} {verbk} {n2}
# (B) {n2} {verbk} {n1}
# (C) The is no direct causal relation between {n1} and {n2}
#
# The answer is: ...
#
# DESIRED OUTPUT FORMAT:
# <thinking>
# ...
# </thinking>
# <answer>
# {{
#    "thinking": ["...", ...]
#    "answer": ...
# }}
# </answer>
#
# Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part.
# Output inside <answer> tag in JSON format. Only output valid JSON.
# DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
# """
#
# def baseline_only_node_id_state_names_causes(incorrect_edges, eval_name, llm_model_name, bn_model):
#     dataset = []
#     evaluation_data = []
#
#     @weave.op()
#     def edge_judgement_scorer(id, output):
#         evaluation_data[id] = dataset[id]
#         evaluation_data[id]["reasoning"] = output["thinking"]
#         evaluation_data[id]["answer"] = output["answer"]
#         evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
#         return output["answer"] == dataset[id]["correct"]
#
#     def create_dataset(incorrect_edges, prompt_template):
#         # We are reversing the edges for evaluation
#         for id, edge in enumerate(incorrect_edges):
#             n1 = edge[0]
#             n2 = edge[1]
#             n1_states = bn_model.states[n1]
#             n2_states = bn_model.states[n2]
#             data = {
#                 "id": id,
#                 "llm_model_name": llm_model_name,
#                 "edge": edge,
#                 "n1_states": n1_states,
#                 "n2_states": n2_states,
#                 "verb": "causes",
#                 "correct": "B",
#                 # "incorrect": "A",
#                 "prompt": prompt_template.format(
#                     n1=n1, n2=n2,
#                     n1_states=n1_states, n2_states=n2_states,
#                     verbk="causes",
#                     id=id)
#             }
#             dataset.append(data)
#             evaluation_data.append(data)
#
#     create_dataset(incorrect_edges, NODE_ID_AND_STATE_NAMES)
#
#     weave.init('bnv_N_staging')
#
#     model = EvaluationModel(model_name=llm_model_name)
#
#     evaluation = weave.Evaluation(
#         name=eval_name,
#         dataset=dataset,
#         scorers=[edge_judgement_scorer]
#     )
#
#     evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))
#
#     eval_res_dict = {
#         # "dataset": dataset,
#         "eval_scorer_summary": evaluation_scorer_summary,
#         "evaluation_data": format_reasoning(evaluation_data)
#     }
#
#     return eval_res_dict



#### EVALUATION WITH NODE ID AND DIFFERENT CAUSAL VERBS
# (C) The is no direct relation between {n1} and {n2}
ONLY_NODE_ID_DIFF_CAUSAL_VERB = """\
Among these two options which one is the most likely true: 

(A) `{n1}` {verbk} `{n2}` 
(B) `{n2}` {verbk} `{n1}` 

The answer is: ...

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": ["...", ...]
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

def baseline_only_node_id_causal_verb(incorrect_edges, eval_name, llm_model_name, bn_model):
    causal_verb = eval_name.split("_")[-1]

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = (
            "yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "schema_dep_validity": schema_dep_valid,
                "verb": causal_verb,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    verbk=causal_verb,
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, ONLY_NODE_ID_DIFF_CAUSAL_VERB)

    weave.init('bnv_N_staging')

    model = EvaluationModel(model_name=llm_model_name)

    evaluation = weave.Evaluation(
        name=eval_name,
        dataset=dataset,
        scorers=[edge_judgement_scorer, edge_judgement_consistency_scorer]
    )

    evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))

    eval_res_dict = {
        # "dataset": dataset,
        "eval_scorer_summary": evaluation_scorer_summary,
        "evaluation_data": format_reasoning(evaluation_data)
    }

    return eval_res_dict


#### EVALUATION WITH NODE ID THEIR STATE NAMES ####
NODE_ID_STATE_NAMES_DIFF_CAUSAL_VERB = """\
`NODE1`:
id: {n1}
state_names: {n1_state_names}

`NODE2`:
id: {n2}
state_names: {n2_state_names}

Among these two options which one is the most likely true: 

(A) `{n1}` {verbk} `{n2}` 
(B) `{n2}` `{verbk} `{n1}`

The answer is: ...

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": ["...", ...]
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

def node_id_state_names_causal_verb(incorrect_edges, eval_name, llm_model_name, bn_model):
    causal_verb = eval_name.split("_")[-1]

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = (
            "yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]
            nodes_data = {
                "NODE1": {
                    "id": n1,
                    "states_names": bn_model.states[n1]
                },
                "NODE2": {
                    "id": n2,
                    "states_names": bn_model.states[n2]
                }
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(nodes_data, indent=2),
                "schema_dep_validity": schema_dep_valid,
                "verb": causal_verb,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_state_names=nodes_data["NODE1"]["states_names"], n2_state_names=nodes_data["NODE2"]["states_names"],
                    verbk=causal_verb,
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_STATE_NAMES_DIFF_CAUSAL_VERB)

    weave.init('bnv_N_staging')

    model = EvaluationModel(model_name=llm_model_name)

    evaluation = weave.Evaluation(
        name=eval_name,
        dataset=dataset,
        scorers=[edge_judgement_scorer, edge_judgement_consistency_scorer]
    )

    evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))

    eval_res_dict = {
        # "dataset": dataset,
        "eval_scorer_summary": evaluation_scorer_summary,
        "evaluation_data": format_reasoning(evaluation_data)
    }

    return eval_res_dict



#### EVALUATION WITH NODE ID THEIR STATE NAMES, CONNECTED NODES ####
NODE_ID_STATE_NAMES__CONNECTED_NODES_DIFF_CAUSAL_VERB = """\
`NODE1`:
id: {n1}
state_names: {n1_state_names}
direct_connected_nodes: {n1_connected_nodes}

`NODE2`:
id: {n2}
state_names: {n2_state_names}
direct_connected_nodes: {n2_connected_nodes}

Among these two options which one is the most likely true: 

(A) `{n1}` {verbk} `{n2}` 
(B) `{n2}` `{verbk} `{n1}`

The answer is: ...

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": ["...", ...]
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

def node_id_state_names_connected_nodes_causal_verb(incorrect_edges, eval_name, llm_model_name, bn_model):
    causal_verb = eval_name.split("_")[-1]

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = (
            "yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]
            nodes_data = {
                "NODE1": {
                    "id": n1,
                    "states_names": f"{bn_model.states[n1]}",
                    "connected_nodes": f"{[cn for cn in bn_model.neighbors(n1)]}"
                },
                "NODE2": {
                    "id": n2,
                    "states_names": f"{bn_model.states[n2]}",
                    "connected_nodes": f"{[cn for cn in bn_model.neighbors(n2)]}"
                }
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(nodes_data, indent=2),
                "schema_dep_validity": schema_dep_valid,
                "verb": causal_verb,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_state_names=nodes_data["NODE1"]["states_names"], n2_state_names=nodes_data["NODE2"]["states_names"],
                    n1_connected_nodes=nodes_data["NODE1"]["connected_nodes"], n2_connected_nodes=nodes_data["NODE2"]["connected_nodes"],
                    verbk=causal_verb,
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_STATE_NAMES_DIFF_CAUSAL_VERB)

    weave.init('bnv_N_staging')

    model = EvaluationModel(model_name=llm_model_name)

    evaluation = weave.Evaluation(
        name=eval_name,
        dataset=dataset,
        scorers=[edge_judgement_scorer, edge_judgement_consistency_scorer]
    )

    evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))

    eval_res_dict = {
        # "dataset": dataset,
        "eval_scorer_summary": evaluation_scorer_summary,
        "evaluation_data": format_reasoning(evaluation_data)
    }

    return eval_res_dict



#### EVALUATION WITH NODE ID THEIR STATE NAMES, NODE TYPE ####
NODE_ID_STATE_NAMES_NODE_TYPE_DIFF_CAUSAL_VERB = """\
`NODE1`:
id: {n1}
type: {n1_type}
state_names: {n1_state_names}

`NODE2`:
id: {n2}
type: {n2_type}
state_names: {n2_state_names}

Among these two options which one is the most likely true: 

(A) `{n1}` {verbk} `{n2}` 
(B) `{n2}` `{verbk} `{n1}`

The answer is: ...

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": ["...", ...]
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

def node_id_state_names_node_type(incorrect_edges, eval_name, llm_model_name, bn_model):
    causal_verb = eval_name.split("_")[-1]

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = (
            "yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]

            nodes_data = {
                "NODE1": {
                    "id": n1,
                    "type": get_node_descriptions(n1)["type"],
                    "states_names": f"{bn_model.states[n1]}",
                },
                "NODE2": {
                    "id": n2,
                    "type": get_node_descriptions(n2)["type"],
                    "states_names": f"{bn_model.states[n2]}",
                }
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(nodes_data, indent=2),
                "schema_dep_validity": schema_dep_valid,
                "verb": causal_verb,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_state_names=nodes_data["NODE1"]["states_names"], n2_state_names=nodes_data["NODE2"]["states_names"],
                    n1_type=nodes_data["NODE1"]["type"], n2_type=nodes_data["NODE2"]["type"],
                    verbk=causal_verb,
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_STATE_NAMES_NODE_TYPE_DIFF_CAUSAL_VERB)

    weave.init('bnv_N_staging')

    model = EvaluationModel(model_name=llm_model_name)

    evaluation = weave.Evaluation(
        name=eval_name,
        dataset=dataset,
        scorers=[edge_judgement_scorer, edge_judgement_consistency_scorer]
    )

    evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))

    eval_res_dict = {
        # "dataset": dataset,
        "eval_scorer_summary": evaluation_scorer_summary,
        "evaluation_data": format_reasoning(evaluation_data)
    }

    return eval_res_dict


#### EVALUATION WITH NODE ID THEIR STATE NAMES, NODE TYPE, OBSERVABILITY ####
NODE_ID_STATE_NAMES_NODE_TYPE_OBSERVABILITY_DIFF_CAUSAL_VERB = """\
`NODE1`:
id: {n1}
type: {n1_type}
observability: {n1_observability}
state_names: {n1_state_names}

`NODE2`:
id: {n2}
type: {n2_type}
observability: {n2_observability}
state_names: {n2_state_names}

Among these two options which one is the most likely true: 

(A) `{n1}` {verbk} `{n2}` 
(B) `{n2}` `{verbk} `{n1}`

The answer is: ...

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": ["...", ...]
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

def node_id_state_names_node_type_observablity(incorrect_edges, eval_name, llm_model_name, bn_model):
    causal_verb = eval_name.split("_")[-1]

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = (
            "yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]

            nodes_data = {
                "NODE1": {
                    "id": n1,
                    "type": get_node_descriptions(n1)["type"],
                    "observability": get_node_descriptions(n1)["observability"],
                    "states_names": f"{bn_model.states[n1]}",
                },
                "NODE2": {
                    "id": n2,
                    "type": get_node_descriptions(n2)["type"],
                    "observability": get_node_descriptions(n2)["observability"],
                    "states_names": f"{bn_model.states[n2]}",
                }
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(nodes_data, indent=2),
                "schema_dep_validity": schema_dep_valid,
                "verb": causal_verb,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_state_names=nodes_data["NODE1"]["states_names"], n2_state_names=nodes_data["NODE2"]["states_names"],
                    n1_type=nodes_data["NODE1"]["type"], n2_type=nodes_data["NODE2"]["type"],
                    n1_observability=nodes_data["NODE1"]["observability"], n2_observability=nodes_data["NODE2"]["observability"],
                    verbk=causal_verb,
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_STATE_NAMES_NODE_TYPE_OBSERVABILITY_DIFF_CAUSAL_VERB)

    weave.init('bnv_N_staging')

    model = EvaluationModel(model_name=llm_model_name)

    evaluation = weave.Evaluation(
        name=eval_name,
        dataset=dataset,
        scorers=[edge_judgement_scorer, edge_judgement_consistency_scorer]
    )

    evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))

    eval_res_dict = {
        # "dataset": dataset,
        "eval_scorer_summary": evaluation_scorer_summary,
        "evaluation_data": format_reasoning(evaluation_data)
    }

    return eval_res_dict



#### EVALUATION WITH NODE ID THEIR STATE NAMES, NODE TYPE, OBSERVABILITY, NODE LABELS ####
NODE_ID_STATE_NAMES_NODE_TYPE_OBSERVABILITY_NODE_LABELS_DIFF_CAUSAL_VERB = """\
`NODE1`:
id: {n1}
label: {n1_label}
type: {n1_type}
observability: {n1_observability}
state_names: {n1_state_names}

`NODE2`:
id: {n2}
label: {n2_label}
type: {n2_type}
observability: {n2_observability}
state_names: {n2_state_names}

Among these two options which one is the most likely true: 

(A) `{n1}` {verbk} `{n2}` 
(B) `{n2}` `{verbk} `{n1}`

The answer is: ...

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": ["...", ...]
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

def node_id_state_names_node_type_observablity_node_labels(incorrect_edges, eval_name, llm_model_name, bn_model):
    causal_verb = eval_name.split("_")[-1]

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = (
            "yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]

            nodes_data = {
                "NODE1": {
                    "id": n1,
                    "label": get_node_descriptions(n1)["label"],
                    "type": get_node_descriptions(n1)["type"],
                    "observability": get_node_descriptions(n1)["observability"],
                    "states_names": f"{bn_model.states[n1]}",
                },
                "NODE2": {
                    "id": n2,
                    "label": get_node_descriptions(n2)["label"],
                    "type": get_node_descriptions(n2)["type"],
                    "observability": get_node_descriptions(n2)["observability"],
                    "states_names": f"{bn_model.states[n2]}",
                }
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(nodes_data, indent=2),
                "schema_dep_validity": schema_dep_valid,
                "verb": causal_verb,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_state_names=nodes_data["NODE1"]["states_names"], n2_state_names=nodes_data["NODE2"]["states_names"],
                    n1_type=nodes_data["NODE1"]["type"], n2_type=nodes_data["NODE2"]["type"],
                    n1_observability=nodes_data["NODE1"]["observability"], n2_observability=nodes_data["NODE2"]["observability"],
                    n1_label=nodes_data["NODE1"]["label"], n2_label=nodes_data["NODE2"]["label"],
                    verbk=causal_verb,
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_STATE_NAMES_NODE_TYPE_OBSERVABILITY_NODE_LABELS_DIFF_CAUSAL_VERB)

    weave.init('bnv_N_staging')

    model = EvaluationModel(model_name=llm_model_name)

    evaluation = weave.Evaluation(
        name=eval_name,
        dataset=dataset,
        scorers=[edge_judgement_scorer, edge_judgement_consistency_scorer]
    )

    evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))

    eval_res_dict = {
        # "dataset": dataset,
        "eval_scorer_summary": evaluation_scorer_summary,
        "evaluation_data": format_reasoning(evaluation_data)
    }

    return eval_res_dict




#### EVALUATION WITH NODE ID THEIR STATE NAMES, NODE TYPE, OBSERVABILITY, NODE LABELS AND DESCRIPTIONS ####
NODE_ID_STATE_NAMES_NODE_TYPE_OBSERVABILITY_NODE_LABELS_DESCRIPTIONS_DIFF_CAUSAL_VERB = """\
`NODE1`:
id: {n1}
label: {n1_label}
description: {n1_description}
type: {n1_type}
observability: {n1_observability}
state_names: {n1_state_names}

`NODE2`:
id: {n2}
label: {n2_label}
description: {n2_description}
type: {n2_type}
observability: {n2_observability}
state_names: {n2_state_names}

Among these two options which one is the most likely true: 

(A) `{n1}` {verbk} `{n2}` 
(B) `{n2}` `{verbk} `{n1}`

The answer is: ...

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": ["...", ...]
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

def node_id_state_names_node_type_observablity_node_labels_descriptions(incorrect_edges, eval_name, llm_model_name, bn_model):
    causal_verb = eval_name.split("_")[-1]

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = (
            "yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]

            nodes_data = {
                "NODE1": {
                    "id": n1,
                    "label": get_node_descriptions(n1)["label"],
                    "description": get_node_descriptions(n1)["description"],
                    "type": get_node_descriptions(n1)["type"],
                    "observability": get_node_descriptions(n1)["observability"],
                    "states_names": f"{bn_model.states[n1]}",
                },
                "NODE2": {
                    "id": n2,
                    "label": get_node_descriptions(n2)["label"],
                    "description": get_node_descriptions(n2)["description"],
                    "type": get_node_descriptions(n2)["type"],
                    "observability": get_node_descriptions(n2)["observability"],
                    "states_names": f"{bn_model.states[n2]}",
                }
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(nodes_data, indent=2),
                "schema_dep_validity": schema_dep_valid,
                "verb": causal_verb,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_state_names=nodes_data["NODE1"]["states_names"], n2_state_names=nodes_data["NODE2"]["states_names"],
                    n1_type=nodes_data["NODE1"]["type"], n2_type=nodes_data["NODE2"]["type"],
                    n1_observability=nodes_data["NODE1"]["observability"], n2_observability=nodes_data["NODE2"]["observability"],
                    n1_label=nodes_data["NODE1"]["label"], n2_label=nodes_data["NODE2"]["label"],
                    n1_description=nodes_data["NODE1"]["description"], n2_description=nodes_data["NODE2"]["description"],
                    verbk=causal_verb,
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_STATE_NAMES_NODE_TYPE_OBSERVABILITY_NODE_LABELS_DESCRIPTIONS_DIFF_CAUSAL_VERB)

    weave.init('bnv_N_staging')

    model = EvaluationModel(model_name=llm_model_name)

    evaluation = weave.Evaluation(
        name=eval_name,
        dataset=dataset,
        scorers=[edge_judgement_scorer, edge_judgement_consistency_scorer]
    )

    evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))

    eval_res_dict = {
        # "dataset": dataset,
        "eval_scorer_summary": evaluation_scorer_summary,
        "evaluation_data": format_reasoning(evaluation_data)
    }

    return eval_res_dict





#### EVALUATION WITH NODE ID THEIR STATE NAMES, NODE TYPE, OBSERVABILITY, NODE LABELS AND DESCRIPTIONS ####
NODE_ID_NODE_TYPE_OBSERVABILITY_NODE_LABELS_DESCRIPTIONS_STATE_DESCRIPTIONS_DIFF_CAUSAL_VERB = """\
`NODE1`:
id: {n1}
label: {n1_label}
description: {n1_description}
type: {n1_type}
observability: {n1_observability}
states: {n1_states}

`NODE2`:
id: {n2}
label: {n2_label}
description: {n2_description}
type: {n2_type}
observability: {n2_observability}
states: {n2_states}

Among these two options which one is the most likely true: 

(A) `{n1}` {verbk} `{n2}` 
(B) `{n2}` `{verbk} `{n1}`

The answer is: ...

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": ["...", ...]
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

def node_id_node_type_observablity_node_labels_descriptions_states_descriptions(incorrect_edges, eval_name, llm_model_name, bn_model):
    causal_verb = eval_name.split("_")[-1]

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = (
            "yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]

            nodes_data = {
                "NODE1": {
                    "id": n1,
                    "label": get_node_descriptions(n1)["label"],
                    "description": get_node_descriptions(n1)["description"],
                    "type": get_node_descriptions(n1)["type"],
                    "observability": get_node_descriptions(n1)["observability"],
                    "states": get_node_descriptions(n1)["node_states_description"],
                },
                "NODE2": {
                    "id": n2,
                    "label": get_node_descriptions(n2)["label"],
                    "description": get_node_descriptions(n2)["description"],
                    "type": get_node_descriptions(n2)["type"],
                    "observability": get_node_descriptions(n2)["observability"],
                    "states": get_node_descriptions(n2)["node_states_description"],
                }
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(nodes_data, indent=2),
                "schema_dep_validity": schema_dep_valid,
                "verb": causal_verb,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_states=nodes_data["NODE1"]["states"], n2_states=nodes_data["NODE2"]["states"],
                    n1_type=nodes_data["NODE1"]["type"], n2_type=nodes_data["NODE2"]["type"],
                    n1_observability=nodes_data["NODE1"]["observability"], n2_observability=nodes_data["NODE2"]["observability"],
                    n1_label=nodes_data["NODE1"]["label"], n2_label=nodes_data["NODE2"]["label"],
                    n1_description=nodes_data["NODE1"]["description"], n2_description=nodes_data["NODE2"]["description"],
                    verbk=causal_verb,
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_NODE_TYPE_OBSERVABILITY_NODE_LABELS_DESCRIPTIONS_STATE_DESCRIPTIONS_DIFF_CAUSAL_VERB)

    weave.init('bnv_N_staging')

    model = EvaluationModel(model_name=llm_model_name)

    evaluation = weave.Evaluation(
        name=eval_name,
        dataset=dataset,
        scorers=[edge_judgement_scorer, edge_judgement_consistency_scorer]
    )

    evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))

    eval_res_dict = {
        # "dataset": dataset,
        "eval_scorer_summary": evaluation_scorer_summary,
        "evaluation_data": format_reasoning(evaluation_data)
    }

    return eval_res_dict




#### EVALUATION WITH NODE ID THEIR STATE NAMES, NODE TYPE, OBSERVABILITY, NODE LABELS AND DESCRIPTIONS ####
NODE_ID_NODE_TYPE_OBSERVABILITY_NODE_LABELS_DESCRIPTIONS_STATE_DESCRIPTIONS_CAUSAL_FACTORS_DIFF_CAUSAL_VERB = """\
edge - The edge which needs to be verified.
explanation - Explanation of what the edge represents and its validity.
causal_direction - Either Positive or Negative or Unknown. A positive influence direction indicates that both factors change in the same direction (e.g. an increase causes an increase effect). A negative influence direction indicates the opposite changes (e.g. an increase causes a decrease effect).
causal_factor - Is necessary or sufficient condition for an effect to occur. Exposure is a term commonly used in epidemiology to denote any condition that is considered as a possible cause of disease. Exposure is considered necessary when it always precedes the effects (e.g. symptoms) and always presents when the effects occur. A sufficient cause is a causal factor whose presence or occurrence guarantees the occurrence of symptom.
causal_distance - Either Distal or Proximal or Unknown. The distal factors lie towards the beginning of causal chain (i.e. indirect causal factors). The the proximal factors lie towards the end of the chain (i.e. cause directly or almost directly the effect).


`NODE1`:
id: {n1}
label: {n1_label}
description: {n1_description}
type: {n1_type}
observability: {n1_observability}
states: {n1_states}

`NODE2`:
id: {n2}
label: {n2_label}
description: {n2_description}
type: {n2_type}
observability: {n2_observability}
states: {n2_states}

`EDGE1`:
{e1}

`EDGE2`:
{e2}

Among these two options which one is the most likely true: 

(A) `{n1}` {verbk} `{n2}` 
(B) `{n2}` `{verbk} `{n1}`

The answer is: ...

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": ["...", ...]
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

def node_id_node_type_observablity_node_labels_descriptions_states_descriptions_causal_factors(incorrect_edges, eval_name, llm_model_name, bn_model):
    causal_verb = eval_name.split("_")[-1]

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = (
            "yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]

            context_input_data = {
                "NODE1": {
                    "id": n1,
                    "label": get_node_descriptions(n1)["label"],
                    "description": get_node_descriptions(n1)["description"],
                    "type": get_node_descriptions(n1)["type"],
                    "observability": get_node_descriptions(n1)["observability"],
                    "states": get_node_descriptions(n1)["node_states_description"],
                },
                "NODE2": {
                    "id": n2,
                    "label": get_node_descriptions(n2)["label"],
                    "description": get_node_descriptions(n2)["description"],
                    "type": get_node_descriptions(n2)["type"],
                    "observability": get_node_descriptions(n2)["observability"],
                    "states": get_node_descriptions(n2)["node_states_description"],
                },
                "EDGE1": get_causal_factors((n1,n2)),
                "EDGE2": get_causal_factors((n2,n1))

            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "context_input_data": json.dumps(context_input_data, indent=2),
                "schema_dep_validity": schema_dep_valid,
                "verb": causal_verb,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_states=context_input_data["NODE1"]["states"], n2_states=context_input_data["NODE2"]["states"],
                    n1_type=context_input_data["NODE1"]["type"], n2_type=context_input_data["NODE2"]["type"],
                    n1_observability=context_input_data["NODE1"]["observability"], n2_observability=context_input_data["NODE2"]["observability"],
                    n1_label=context_input_data["NODE1"]["label"], n2_label=context_input_data["NODE2"]["label"],
                    n1_description=context_input_data["NODE1"]["description"], n2_description=context_input_data["NODE2"]["description"],
                    verbk=causal_verb,
                    e1=context_input_data["EDGE1"], e2=context_input_data["EDGE2"],
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_NODE_TYPE_OBSERVABILITY_NODE_LABELS_DESCRIPTIONS_STATE_DESCRIPTIONS_CAUSAL_FACTORS_DIFF_CAUSAL_VERB)

    weave.init('bnv_N_staging')

    model = EvaluationModel(model_name=llm_model_name)

    evaluation = weave.Evaluation(
        name=eval_name,
        dataset=dataset,
        scorers=[edge_judgement_scorer, edge_judgement_consistency_scorer]
    )

    evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))

    eval_res_dict = {
        # "dataset": dataset,
        "eval_scorer_summary": evaluation_scorer_summary,
        "evaluation_data": format_reasoning(evaluation_data)
    }

    return eval_res_dict



#### EVALUATION WITH NODE ID THEIR STATE NAMES, NODE TYPE, OBSERVABILITY, NODE LABELS AND DESCRIPTIONS ####
NODE_ID_NODE_TYPE_OBSERVABILITY_NODE_LABELS_DESCRIPTIONS_STATE_DESCRIPTIONS_CAUSAL_FACTORS_EVIDENCES_DIFF_CAUSAL_VERB = """\
edge - The edge which needs to be verified.
explanation - Explanation of what the edge represents and its validity.
causal_direction - Either Positive or Negative or Unknown. A positive influence direction indicates that both factors change in the same direction (e.g. an increase causes an increase effect). A negative influence direction indicates the opposite changes (e.g. an increase causes a decrease effect).
causal_factor - Is necessary or sufficient condition for an effect to occur. Exposure is a term commonly used in epidemiology to denote any condition that is considered as a possible cause of disease. Exposure is considered necessary when it always precedes the effects (e.g. symptoms) and always presents when the effects occur. A sufficient cause is a causal factor whose presence or occurrence guarantees the occurrence of symptom.
causal_distance - Either Distal or Proximal or Unknown. The distal factors lie towards the beginning of causal chain (i.e. indirect causal factors). The the proximal factors lie towards the end of the chain (i.e. cause directly or almost directly the effect).


`NODE1`:
id: {n1}
label: {n1_label}
description: {n1_description}
type: {n1_type}
observability: {n1_observability}
states: {n1_states}

`NODE2`:
id: {n2}
label: {n2_label}
description: {n2_description}
type: {n2_type}
observability: {n2_observability}
states: {n2_states}

`EDGE1`:
{e1}

`EDGE2`:
{e2}

Among these two options which one is the most likely true: 

(A) `{n1}` {verbk} `{n2}` 
(B) `{n2}` `{verbk} `{n1}`

The answer is: ...

State the evidences in detail of the validity of option (A) or (B) by cross referencing 
NCCN Clinical Practitioner’s Guidelines for Head and Neck Cancer.

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
   "thinking": ["...", ...],
   "evidences": ["...", ...],
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

def node_id_node_type_observablity_node_labels_descriptions_states_descriptions_causal_factors_evidences(incorrect_edges, eval_name, llm_model_name, bn_model):
    causal_verb = eval_name.split("_")[-1]

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        if "evidences" in output.keys():
            evaluation_data[id]["evidences"] = output["evidences"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = (
            "yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]

            context_input_data = {
                "NODE1": {
                    "id": n1,
                    "label": get_node_descriptions(n1)["label"],
                    "description": get_node_descriptions(n1)["description"],
                    "type": get_node_descriptions(n1)["type"],
                    "observability": get_node_descriptions(n1)["observability"],
                    "states": get_node_descriptions(n1)["node_states_description"],
                },
                "NODE2": {
                    "id": n2,
                    "label": get_node_descriptions(n2)["label"],
                    "description": get_node_descriptions(n2)["description"],
                    "type": get_node_descriptions(n2)["type"],
                    "observability": get_node_descriptions(n2)["observability"],
                    "states": get_node_descriptions(n2)["node_states_description"],
                },
                "EDGE1": get_causal_factors((n1,n2)),
                "EDGE2": get_causal_factors((n2,n1))

            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "context_input_data": json.dumps(context_input_data, indent=2),
                "schema_dep_validity": schema_dep_valid,
                "verb": causal_verb,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_states=context_input_data["NODE1"]["states"], n2_states=context_input_data["NODE2"]["states"],
                    n1_type=context_input_data["NODE1"]["type"], n2_type=context_input_data["NODE2"]["type"],
                    n1_observability=context_input_data["NODE1"]["observability"], n2_observability=context_input_data["NODE2"]["observability"],
                    n1_label=context_input_data["NODE1"]["label"], n2_label=context_input_data["NODE2"]["label"],
                    n1_description=context_input_data["NODE1"]["description"], n2_description=context_input_data["NODE2"]["description"],
                    verbk=causal_verb,
                    e1=context_input_data["EDGE1"], e2=context_input_data["EDGE2"],
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_NODE_TYPE_OBSERVABILITY_NODE_LABELS_DESCRIPTIONS_STATE_DESCRIPTIONS_CAUSAL_FACTORS_EVIDENCES_DIFF_CAUSAL_VERB)

    weave.init('bnv_N_staging')

    model = EvaluationModel(model_name=llm_model_name)

    evaluation = weave.Evaluation(
        name=eval_name,
        dataset=dataset,
        scorers=[edge_judgement_scorer, edge_judgement_consistency_scorer]
    )

    evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))

    eval_res_dict = {
        # "dataset": dataset,
        "eval_scorer_summary": evaluation_scorer_summary,
        "evaluation_data": format_reasoning(evaluation_data)
    }

    return eval_res_dict