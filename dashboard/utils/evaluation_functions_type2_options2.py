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


#### EVALUATION WITH NODE ID ####
# (C) The is no direct relation between {n1} and {n2}
ONLY_NODE_ID = """\
Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

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
def baseline_only_node_id(incorrect_edges, eval_name, llm_model_name, bn_model):

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
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
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, ONLY_NODE_ID)

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



#### EVALUATION WITH NODE ID AND THEIR STATE NAMES ####
NODE_ID_STATE_NAMES = """\
`NODE1`:
id: {n1}
state_names: {n1_state_names}

`NODE2`:
id: {n2}
state_names: {n2_state_names}

Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

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
def node_id_state_names(incorrect_edges, eval_name, llm_model_name, bn_model):

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
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
                # "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_state_names=nodes_data["NODE1"]["states_names"],
                    n2_state_names=nodes_data["NODE2"]["states_names"],
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_STATE_NAMES)

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




#### EVALUATION WITH NODE ID AND THEIR STATE NAMES, CONNECTED NODES ####
NODE_ID_STATE_NAMES_CONNECTED_NODES = """\
`NODE1`:
id: {n1}
state_names: {n1_state_names}
direct_connected_nodes: {n1_connected_nodes}

`NODE2`:
id: {n2}
state_names: {n2_state_names}
direct_connected_nodes: {n2_connected_nodes}

Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

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
def node_id_state_names_connected_nodes(incorrect_edges, eval_name, llm_model_name, bn_model):

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
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
                # "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_state_names=nodes_data["NODE1"]["states_names"],
                    n2_state_names=nodes_data["NODE2"]["states_names"],
                    n1_connected_nodes=nodes_data["NODE1"]["connected_nodes"],
                    n2_connected_nodes=nodes_data["NODE2"]["connected_nodes"],
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_STATE_NAMES_CONNECTED_NODES)

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




#### EVALUATION WITH NODE ID AND THEIR STATE NAMES, NODE TYPE ####
NODE_ID_STATE_NAMES_NODE_TYPE = """\
`NODE1`:
id: {n1}
type: {n1_type}
state_names: {n1_state_names}

`NODE2`:
id: {n2}
type: {n2_type}
state_names: {n2_state_names}

Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

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

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
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
                    "states_names": f"{bn_model.states[n1]}"
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
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_state_names=nodes_data["NODE1"]["states_names"],
                    n2_state_names=nodes_data["NODE2"]["states_names"],
                    n1_type=nodes_data["NODE1"]["type"], n2_type=nodes_data["NODE2"]["type"],
                    id=id
                )
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_STATE_NAMES_NODE_TYPE)

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



#### EVALUATION WITH NODE ID AND THEIR STATE NAMES, NODE TYPE,OBSERVABILITY ####
NODE_ID_STATE_NAMES_NODE_TYPE_OBSERVABILITY = """\
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

Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

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
def node_id_state_names_node_type_observability(incorrect_edges, eval_name, llm_model_name, bn_model):

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
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
                    "states_names": f"{bn_model.states[n1]}"
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
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_state_names=nodes_data["NODE1"]["states_names"],
                    n2_state_names=nodes_data["NODE2"]["states_names"],
                    n1_type=nodes_data["NODE1"]["type"], n2_type=nodes_data["NODE2"]["type"],
                    n1_observability=nodes_data["NODE1"]["observability"],
                    n2_observability=nodes_data["NODE2"]["observability"],
                    id=id
                )
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_STATE_NAMES_NODE_TYPE_OBSERVABILITY)

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




#### EVALUATION WITH NODE ID AND THEIR STATE NAMES, NODE TYPE,OBSERVABILITY AND LABeLS ####
NODE_ID_STATE_NAMES_NODE_TYPE_OBSERVABILITY_LABEL = """\
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

Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

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
def node_id_state_names_node_type_observability_label(incorrect_edges, eval_name, llm_model_name, bn_model):

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
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
                    "states_names": f"{bn_model.states[n1]}"
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
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_state_names=nodes_data["NODE1"]["states_names"],
                    n2_state_names=nodes_data["NODE2"]["states_names"],
                    n1_type=nodes_data["NODE1"]["type"], n2_type=nodes_data["NODE2"]["type"],
                    n1_observability=nodes_data["NODE1"]["observability"],
                    n2_observability=nodes_data["NODE2"]["observability"],
                    n1_label=nodes_data["NODE1"]["label"], n2_label=nodes_data["NODE2"]["label"],
                    id=id
                )
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_STATE_NAMES_NODE_TYPE_OBSERVABILITY_LABEL)

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



#### EVALUATION WITH NODE ID AND THEIR STATE NAMES, NODE TYPE,OBSERVABILITY AND LABeLS ####
NODE_ID_STATE_NAMES_NODE_TYPE_OBSERVABILITY_LABEL_DESCRIPTION = """\
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

Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

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
def node_id_state_names_node_type_observability_label_description(incorrect_edges, eval_name, llm_model_name, bn_model):

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
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
                    "states_names": f"{bn_model.states[n1]}"
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
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_state_names=nodes_data["NODE1"]["states_names"],
                    n2_state_names=nodes_data["NODE2"]["states_names"],
                    n1_type=nodes_data["NODE1"]["type"], n2_type=nodes_data["NODE2"]["type"],
                    n1_observability=nodes_data["NODE1"]["observability"],
                    n2_observability=nodes_data["NODE2"]["observability"],
                    n1_label=nodes_data["NODE1"]["label"], n2_label=nodes_data["NODE2"]["label"],
                    n1_description=nodes_data["NODE1"]["description"],
                    n2_description=nodes_data["NODE2"]["description"],
                    id=id
                )
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_STATE_NAMES_NODE_TYPE_OBSERVABILITY_LABEL_DESCRIPTION)

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




#### EVALUATION WITH NODE ID AND THEIR STATE NAMES, NODE TYPE,OBSERVABILITY AND LABeLS ####
NODE_ID_NODE_TYPE_OBSERVABILITY_LABEL_DESCRIPTION_STATES_DESCRIPTIONS = """\
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

Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

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
def node_id_node_type_observability_label_description_states_descriptions(incorrect_edges, eval_name, llm_model_name, bn_model):

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
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
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_states=nodes_data["NODE1"]["states"], n2_states=nodes_data["NODE2"]["states"],
                    n1_type=nodes_data["NODE1"]["type"], n2_type=nodes_data["NODE2"]["type"],
                    n1_observability=nodes_data["NODE1"]["observability"],
                    n2_observability=nodes_data["NODE2"]["observability"],
                    n1_label=nodes_data["NODE1"]["label"], n2_label=nodes_data["NODE2"]["label"],
                    n1_description=nodes_data["NODE1"]["description"],
                    n2_description=nodes_data["NODE2"]["description"],
                    id=id
                )
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_NODE_TYPE_OBSERVABILITY_LABEL_DESCRIPTION_STATES_DESCRIPTIONS)

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




#### EVALUATION WITH NODE ID AND THEIR STATE NAMES, NODE TYPE,OBSERVABILITY AND LABeLS ####
NODE_ID_NODE_TYPE_OBSERVABILITY_LABEL_DESCRIPTION_STATES_DESCRIPTIONS_CAUSAL_FACTORS = """\
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

Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

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
def node_id_node_type_observability_label_description_states_descriptions_causal_factors(incorrect_edges, eval_name, llm_model_name, bn_model):

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
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
                "EDGE1": get_causal_factors((n1, n2)),
                "EDGE2": get_causal_factors((n2, n1))
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(context_input_data, indent=2),
                "schema_dep_validity": schema_dep_valid,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_states=context_input_data["NODE1"]["states"], n2_states=context_input_data["NODE2"]["states"],
                    n1_type=context_input_data["NODE1"]["type"], n2_type=context_input_data["NODE2"]["type"],
                    n1_observability=context_input_data["NODE1"]["observability"],
                    n2_observability=context_input_data["NODE2"]["observability"],
                    n1_label=context_input_data["NODE1"]["label"], n2_label=context_input_data["NODE2"]["label"],
                    n1_description=context_input_data["NODE1"]["description"],
                    n2_description=context_input_data["NODE2"]["description"],
                    e1=context_input_data["EDGE1"], e2=context_input_data["EDGE2"],
                    id=id
                )
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_NODE_TYPE_OBSERVABILITY_LABEL_DESCRIPTION_STATES_DESCRIPTIONS_CAUSAL_FACTORS)

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



#### EVALUATION WITH NODE ID AND THEIR STATE NAMES, NODE TYPE,OBSERVABILITY AND LABeLS ... EVIDENCES ####
NODE_ID_NODE_TYPE_OBSERVABILITY_LABEL_DESCRIPTION_STATES_DESCRIPTIONS_CAUSAL_FACTORS_EVIDENCES = """\
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

Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

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
def node_id_node_type_observability_label_description_states_descriptions_causal_factors_evidences(incorrect_edges, eval_name, llm_model_name, bn_model):

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
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
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
                "EDGE1": get_causal_factors((n1, n2)),
                "EDGE2": get_causal_factors((n2, n1))
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(str(context_input_data), indent=2),
                "schema_dep_validity": schema_dep_valid,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_states=context_input_data["NODE1"]["states"], n2_states=context_input_data["NODE2"]["states"],
                    n1_type=context_input_data["NODE1"]["type"], n2_type=context_input_data["NODE2"]["type"],
                    n1_observability=context_input_data["NODE1"]["observability"],
                    n2_observability=context_input_data["NODE2"]["observability"],
                    n1_label=context_input_data["NODE1"]["label"], n2_label=context_input_data["NODE2"]["label"],
                    n1_description=context_input_data["NODE1"]["description"],
                    n2_description=context_input_data["NODE2"]["description"],
                    e1=context_input_data["EDGE1"], e2=context_input_data["EDGE2"],
                    id=id
                )
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_NODE_TYPE_OBSERVABILITY_LABEL_DESCRIPTION_STATES_DESCRIPTIONS_CAUSAL_FACTORS_EVIDENCES)

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



#### EVALUATION WITH NODE ID AND THEIR STATE NAMES, NODE TYPE,OBSERVABILITY AND LABeLS ... EVIDENCES, ENTITIES AND RELATIONSHIPS ####
NODE_ID_NODE_TYPE_OBSERVABILITY_LABEL_DESCRIPTION_STATES_DESCRIPTIONS_CAUSAL_FACTORS_EVIDENCES_ENT_REL = """\
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

`INFORMATION FROM KNOWLEDGE BASE`:
{guideline_pages_info}

Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

The answer is: ...

1. State the evidences in detail of the validity of option (A) or (B) by cross referencing 
NCCN Clinical Practitioner’s Guidelines for Head and Neck Cancer.
2. If the evidences are obtained from `INFORMATION FROM KNOWLEDGE BASE`,
mention their corresponding Page Numbers, entities and relationships.

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
def node_id_node_type_observability_label_description_states_descriptions_causal_factors_evidences_ent_rel(incorrect_edges, eval_name, llm_model_name, bn_model):

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
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    def make_entities_dict(page_no):
        ent_desc_dict = {}
        from utils.db import get_page_info
        page_er_info = get_page_info(page_no)["er_info"]
        for section_er_info in page_er_info:
            for entity in section_er_info["entity_information"]:
                entity_label_upper = entity["label"].upper()
                # print(entity_label_upper)
                # print(entity["description"])
                if ent_desc_dict.get(entity_label_upper, None):
                    if len(ent_desc_dict[entity_label_upper]) < len(entity["description"]):
                        ent_desc_dict[entity_label_upper] = entity["description"]
                else:
                    ent_desc_dict[entity_label_upper] = entity["description"]
        # print(json.dumps(ent_desc_dict, indent=2))

        return ent_desc_dict

    def format_relationships(page_no):
        from utils.db import get_page_info
        page_er_info = get_page_info(page_no)["er_info"]
        # print(json.dumps(page_er_info, indent=2))
        out = ""
        count = 0
        for section_er_info in page_er_info:
            relationships_info = section_er_info["relationships_information"]
            for relationship in relationships_info:
                # print(json.dumps(relationship, indent=2))
                count += 1
                rel = f"{count}. Entity1: \"{relationship['entity1']}\", Entity2: \"{relationship['entity2']}\", Relationship: \"{relationship['relationship']}\"\n"
                out += rel

        return out

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]

            nodes_entities = []
            n1_entities = get_node_descriptions(n1)["entity_information"]
            n2_entities = get_node_descriptions(n2)["entity_information"]
            nodes_entities.extend(n1_entities)
            nodes_entities.extend(n2_entities)

            from utils.entities_match_guideline import get_top_10_pages_most_matching_entities

            top_10_guideline_pages = get_top_10_pages_most_matching_entities(nodes_entities)
            # print(json.dumps(top_10_guideline_pages))

            # count = 0
            out = ""
            for page_no, ent_info in top_10_guideline_pages.items():
                out += "-" * 50 + "\n"
                # print(page_ent_info)
                out += f"Page Number: {page_no}\n\n"
                out += f"All entities present in this page: \n"
                page_entities = make_entities_dict(page_no)
                # print(json.dumps(page_entities, indent=2))
                for idx, (entity_label, entity_description) in enumerate(page_entities.items()):
                    ent = f"{idx + 1}. {entity_label.title()} : {entity_description}\n"
                    out += ent

                out += f"\nAll Relationships present in this page: \n"
                out += format_relationships(page_no)

                out += "-" * 50 + "\n"
                # print(out)

                # count += 1
                # if count == 2:
                #     break

            guideline_info = out

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
                "EDGE1": get_causal_factors((n1, n2)),
                "EDGE2": get_causal_factors((n2, n1)),
                "ENTITIES_MATCHING_PAGES_INFO": top_10_guideline_pages,
                "GUIDELINE_PAGES_INFO": guideline_info,
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(str(context_input_data), indent=2),
                "schema_dep_validity": schema_dep_valid,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_states=context_input_data["NODE1"]["states"], n2_states=context_input_data["NODE2"]["states"],
                    n1_type=context_input_data["NODE1"]["type"], n2_type=context_input_data["NODE2"]["type"],
                    n1_observability=context_input_data["NODE1"]["observability"],
                    n2_observability=context_input_data["NODE2"]["observability"],
                    n1_label=context_input_data["NODE1"]["label"], n2_label=context_input_data["NODE2"]["label"],
                    n1_description=context_input_data["NODE1"]["description"],
                    n2_description=context_input_data["NODE2"]["description"],
                    e1=context_input_data["EDGE1"], e2=context_input_data["EDGE2"],
                    guideline_pages_info=context_input_data["GUIDELINE_PAGES_INFO"],
                    id=id
                )
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_NODE_TYPE_OBSERVABILITY_LABEL_DESCRIPTION_STATES_DESCRIPTIONS_CAUSAL_FACTORS_EVIDENCES_ENT_REL)

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




#### EVALUATION WITH NODE ID AND THEIR STATE NAMES, NODE TYPE,OBSERVABILITY AND LABeLS ... EVIDENCES, ENTITIES AND RELATIONSHIPS CAUSALITIES####
NODE_ID_NODE_TYPE_OBSERVABILITY_LABEL_DESCRIPTION_STATES_DESCRIPTIONS_CAUSAL_FACTORS_EVIDENCES_ENT_REL_CAUSALITIES = """\
edge - The edge which needs to be verified.
explanation - Explanation of what the edge represents and its validity.
causal_direction - Either Positive or Negative or Unknown. A positive influence direction indicates that both factors change in the same direction (e.g. an increase causes an increase effect). A negative influence direction indicates the opposite changes (e.g. an increase causes a decrease effect).
causal_factor - Is necessary or sufficient condition for an effect to occur. Exposure is a term commonly used in epidemiology to denote any condition that is considered as a possible cause of disease. Exposure is considered necessary when it always precedes the effects (e.g. symptoms) and always presents when the effects occur. A sufficient cause is a causal factor whose presence or occurrence guarantees the occurrence of symptom.
causal_distance - Either Distal or Proximal or Unknown. The distal factors lie towards the beginning of causal chain (i.e. indirect causal factors). The the proximal factors lie towards the end of the chain (i.e. cause directly or almost directly the effect).

Causality Tags:
<A> for action, <C> for cause, <CO> for condition and <E> for effect.
Cause (C): The reason or origin that leads to an effect. Causes often involve disease conditions, risk factors, or underlying mechanisms.
Effect (E): The outcome or result of a cause. Effects usually represent clinical outcomes, complications, or results of a specific cause.
Condition (CO): The circumstance or prerequisite required for an action or effect to occur. Conditions may include patient characteristics, clinical scenarios, or specific diagnostic criteria.
Action (A): The recommended or described response or activity to address a cause or condition. Actions typically involve clinical interventions, diagnostic procedures, or treatment recommendations.


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

`INFORMATION FROM KNOWLEDGE BASE`:
{guideline_pages_info}

Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

The answer is: ...

1. State the evidences in detail of the validity of option (A) or (B) by cross referencing 
NCCN Clinical Practitioner’s Guidelines for Head and Neck Cancer.
2. If the evidences are obtained from `INFORMATION FROM KNOWLEDGE BASE`,
mention their corresponding Page Numbers, Section Name, entities, relationships and causalities.

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
def node_id_node_type_observability_label_description_states_descriptions_causal_factors_evidences_ent_rel_causalities(incorrect_edges, eval_name, llm_model_name, bn_model):

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
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    def make_entities_dict(page_no):
        ent_desc_dict = {}
        from utils.db import get_page_info
        page_er_info = get_page_info(page_no)["er_info"]
        for section_er_info in page_er_info:
            for entity in section_er_info["entity_information"]:
                entity_label_upper = entity["label"].upper()
                # print(entity_label_upper)
                # print(entity["description"])
                if ent_desc_dict.get(entity_label_upper, None):
                    if len(ent_desc_dict[entity_label_upper]) < len(entity["description"]):
                        ent_desc_dict[entity_label_upper] = entity["description"]
                else:
                    ent_desc_dict[entity_label_upper] = entity["description"]
        # print(json.dumps(ent_desc_dict, indent=2))

        return ent_desc_dict

    def format_page_information(page_no):
        from utils.db import get_page_info
        entities_dict = make_entities_dict(page_no)
        # print(json.dumps(entities_dict, indent=2))

        page_info = get_page_info(page_no)
        sections_info = page_info["sections"]
        er_info = page_info["er_info"]
        causality_info = page_info["causality_info"]

        out = ""
        for idx, sections_info in enumerate(sections_info):
            out += f"\nSection Name: {sections_info['section_name']}\n"
            out += "=" * 20 + "\n"
            out += f"Entities:-\n"
            section_entities = er_info[idx]["entity_information"]
            section_entity_dict = {}
            for entity in section_entities:
                if entity["label"].upper() in entities_dict and entity["label"].upper() not in section_entity_dict:
                    out += f"{entity['label'].upper().title()} : {entities_dict[entity['label'].upper()]}\n"
                    section_entity_dict[entity['label'].upper()] = entities_dict[entity['label'].upper()]

            out += "\nRelationships:-\n"
            for count, relationship in enumerate(er_info[idx]["relationships_information"]):
                rel = f"{count + 1}. Entity1: \"{relationship['entity1']}\", Entity2: \"{relationship['entity2']}\", Relationship: \"{relationship['relationship']}\"\n"
                out += rel

            try:
                section_causality_info = json.loads(causality_info[idx]["answer"])
            except json.JSONDecodeError as e:
                out += "\nCausalities:-\n"
                out += f"{causality_info[idx]['answer']}\n"
            section_causality_info = causality_info[idx]["answer"]
            # out += f"{section_causality_info}\n"

        return out

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]

            nodes_entities = []
            n1_entities = get_node_descriptions(n1)["entity_information"]
            n2_entities = get_node_descriptions(n2)["entity_information"]
            nodes_entities.extend(n1_entities)
            nodes_entities.extend(n2_entities)

            from utils.entities_match_guideline import get_top_10_pages_most_matching_entities

            top_10_guideline_pages = get_top_10_pages_most_matching_entities(nodes_entities)
            # print(json.dumps(top_10_guideline_pages))

            # count = 0
            out = ""
            for page_no, ent_info in top_10_guideline_pages.items():
                out += "-" * 50 + "\n"
                # print(page_ent_info)
                out += f"Page Number: {page_no}\n"
                out += format_page_information(page_no)

            # print(out)
            guideline_info = out
            # break

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
                "EDGE1": get_causal_factors((n1, n2)),
                "EDGE2": get_causal_factors((n2, n1)),
                "ENTITIES_MATCHING_PAGES_INFO": top_10_guideline_pages,
                "GUIDELINE_PAGES_INFO": guideline_info,
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(str(context_input_data), indent=2),
                "schema_dep_validity": schema_dep_valid,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_states=context_input_data["NODE1"]["states"], n2_states=context_input_data["NODE2"]["states"],
                    n1_type=context_input_data["NODE1"]["type"], n2_type=context_input_data["NODE2"]["type"],
                    n1_observability=context_input_data["NODE1"]["observability"],
                    n2_observability=context_input_data["NODE2"]["observability"],
                    n1_label=context_input_data["NODE1"]["label"], n2_label=context_input_data["NODE2"]["label"],
                    n1_description=context_input_data["NODE1"]["description"],
                    n2_description=context_input_data["NODE2"]["description"],
                    e1=context_input_data["EDGE1"], e2=context_input_data["EDGE2"],
                    guideline_pages_info=context_input_data["GUIDELINE_PAGES_INFO"],
                    id=id
                )
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_NODE_TYPE_OBSERVABILITY_LABEL_DESCRIPTION_STATES_DESCRIPTIONS_CAUSAL_FACTORS_EVIDENCES_ENT_REL_CAUSALITIES)

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



#### EVALUATION WITH NODE ID AND THEIR STATE NAMES, NODE TYPE,OBSERVABILITY AND LABeLS ... EVIDENCES, ENTITIES AND RELATIONSHIPS CAUSALITIES####
NODE_LABELS_ONLY = """\
Which cause-and-effect relationship is more likely?

A. changing `{n1}` causes a change in `{n2}`. 
B. changing `{n2}` causes a change in `{n1}`.

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

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""
def node_labels_only(incorrect_edges, eval_name, llm_model_name, bn_model):

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        # if "evidences" in output.keys():
        #     evaluation_data[id]["evidences"] = output["evidences"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    # def make_entities_dict(page_no):
    #     ent_desc_dict = {}
    #     from utils.db import get_page_info
    #     page_er_info = get_page_info(page_no)["er_info"]
    #     for section_er_info in page_er_info:
    #         for entity in section_er_info["entity_information"]:
    #             entity_label_upper = entity["label"].upper()
    #             # print(entity_label_upper)
    #             # print(entity["description"])
    #             if ent_desc_dict.get(entity_label_upper, None):
    #                 if len(ent_desc_dict[entity_label_upper]) < len(entity["description"]):
    #                     ent_desc_dict[entity_label_upper] = entity["description"]
    #             else:
    #                 ent_desc_dict[entity_label_upper] = entity["description"]
    #     # print(json.dumps(ent_desc_dict, indent=2))
    #
    #     return ent_desc_dict
    #
    # def format_page_information(page_no):
    #     from utils.db import get_page_info
    #     entities_dict = make_entities_dict(page_no)
    #     # print(json.dumps(entities_dict, indent=2))
    #
    #     page_info = get_page_info(page_no)
    #     sections_info = page_info["sections"]
    #     er_info = page_info["er_info"]
    #     causality_info = page_info["causality_info"]
    #
    #     out = ""
    #     for idx, sections_info in enumerate(sections_info):
    #         out += f"\nSection Name: {sections_info['section_name']}\n"
    #         out += "=" * 20 + "\n"
    #         out += f"Entities:-\n"
    #         section_entities = er_info[idx]["entity_information"]
    #         section_entity_dict = {}
    #         for entity in section_entities:
    #             if entity["label"].upper() in entities_dict and entity["label"].upper() not in section_entity_dict:
    #                 out += f"{entity['label'].upper().title()} : {entities_dict[entity['label'].upper()]}\n"
    #                 section_entity_dict[entity['label'].upper()] = entities_dict[entity['label'].upper()]
    #
    #         out += "\nRelationships:-\n"
    #         for count, relationship in enumerate(er_info[idx]["relationships_information"]):
    #             rel = f"{count + 1}. Entity1: \"{relationship['entity1']}\", Entity2: \"{relationship['entity2']}\", Relationship: \"{relationship['relationship']}\"\n"
    #             out += rel
    #
    #         try:
    #             section_causality_info = json.loads(causality_info[idx]["answer"])
    #         except json.JSONDecodeError as e:
    #             out += "\nCausalities:-\n"
    #             out += f"{causality_info[idx]['answer']}\n"
    #         section_causality_info = causality_info[idx]["answer"]
    #         # out += f"{section_causality_info}\n"
    #
    #     return out

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]

            # nodes_entities = []
            # n1_entities = get_node_descriptions(n1)["entity_information"]
            # n2_entities = get_node_descriptions(n2)["entity_information"]
            # nodes_entities.extend(n1_entities)
            # nodes_entities.extend(n2_entities)
            #
            # from utils.entities_match_guideline import get_top_10_pages_most_matching_entities
            #
            # top_10_guideline_pages = get_top_10_pages_most_matching_entities(nodes_entities)
            # # print(json.dumps(top_10_guideline_pages))
            #
            # # count = 0
            # out = ""
            # for page_no, ent_info in top_10_guideline_pages.items():
            #     out += "-" * 50 + "\n"
            #     # print(page_ent_info)
            #     out += f"Page Number: {page_no}\n"
            #     out += format_page_information(page_no)
            #
            # # print(out)
            # guideline_info = out
            # # break

            context_input_data = {
                "NODE1": {
                    # "id": n1,
                    "label": get_node_descriptions(n1)["label"],
                    # "description": get_node_descriptions(n1)["description"],
                    # "type": get_node_descriptions(n1)["type"],
                    # "observability": get_node_descriptions(n1)["observability"],
                    # "states": get_node_descriptions(n1)["node_states_description"],
                },
                "NODE2": {
                    # "id": n2,
                    "label": get_node_descriptions(n2)["label"],
                    # "description": get_node_descriptions(n2)["description"],
                    # "type": get_node_descriptions(n2)["type"],
                    # "observability": get_node_descriptions(n2)["observability"],
                    # "states": get_node_descriptions(n2)["node_states_description"],
                },
                # "EDGE1": get_causal_factors((n1, n2)),
                # "EDGE2": get_causal_factors((n2, n1)),
                # "ENTITIES_MATCHING_PAGES_INFO": top_10_guideline_pages,
                # "GUIDELINE_PAGES_INFO": guideline_info,
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(str(context_input_data), indent=2),
                "schema_dep_validity": schema_dep_valid,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    # n1=n1, n2=n2,
                    # n1_states=context_input_data["NODE1"]["states"], n2_states=context_input_data["NODE2"]["states"],
                    # n1_type=context_input_data["NODE1"]["type"], n2_type=context_input_data["NODE2"]["type"],
                    # n1_observability=context_input_data["NODE1"]["observability"],
                    # n2_observability=context_input_data["NODE2"]["observability"],
                    n1=context_input_data["NODE1"]["label"], n2=context_input_data["NODE2"]["label"],
                    # n1_description=context_input_data["NODE1"]["description"],
                    # n2_description=context_input_data["NODE2"]["description"],
                    # e1=context_input_data["EDGE1"], e2=context_input_data["EDGE2"],
                    # guideline_pages_info=context_input_data["GUIDELINE_PAGES_INFO"],
                    id=id
                )
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_LABELS_ONLY)

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


#### EVALUATION WITH NODE ID AND THEIR STATE NAMES, NODE TYPE,OBSERVABILITY AND LABeLS ... EVIDENCES, ENTITIES AND RELATIONSHIPS CAUSALITIES####
NODE_LABEL_CAUSAL_FACTORS = """\
edge - The edge which needs to be verified.
explanation - Explanation of what the edge represents and its validity.
causal_direction - Either Positive or Negative or Unknown. A positive influence direction indicates that both factors change in the same direction (e.g. an increase causes an increase effect). A negative influence direction indicates the opposite changes (e.g. an increase causes a decrease effect).
causal_factor - Is necessary or sufficient condition for an effect to occur. Exposure is a term commonly used in epidemiology to denote any condition that is considered as a possible cause of disease. Exposure is considered necessary when it always precedes the effects (e.g. symptoms) and always presents when the effects occur. A sufficient cause is a causal factor whose presence or occurrence guarantees the occurrence of symptom.
causal_distance - Either Distal or Proximal or Unknown. The distal factors lie towards the beginning of causal chain (i.e. indirect causal factors). The the proximal factors lie towards the end of the chain (i.e. cause directly or almost directly the effect).

`NODE1`:
id: {n1}
label: {n1_label}

`NODE2`:
id: {n2}
label: {n2_label}

`EDGE1`:
{e1}

`EDGE2`:
{e2}

Which cause-and-effect relationship is more likely?

A. changing `{n1_label}` causes a change in `{n2_label}`. 
B. changing `{n2_label}` causes a change in `{n1_label}`.

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

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""
def node_label_causal_factors(incorrect_edges, eval_name, llm_model_name, bn_model):

    dataset = []
    evaluation_data = []

    @weave.op()
    def edge_judgement_scorer(id, output):
        # print(json.dumps(output, indent=4))
        evaluation_data[id] = dataset[id]
        evaluation_data[id]["reasoning"] = output["thinking"]
        # if "evidences" in output.keys():
        #     evaluation_data[id]["evidences"] = output["evidences"]
        evaluation_data[id]["answer"] = output["answer"]
        evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
        evaluation_data[id]["critique_consistent"] = ("yes" if output["critique"]["critique_answer"] == output["answer"] else "no")
        evaluation_data[id]["critique_answer"] = output["critique"]["critique_answer"]
        evaluation_data[id]["critique_reasoning"] = output["critique"]["critique_thinking"]
        return output["answer"] == dataset[id]["correct"]

    @weave.op()
    def edge_judgement_consistency_scorer(id, output):
        return output["answer"] == output["critique"]["critique_answer"]

    # def make_entities_dict(page_no):
    #     ent_desc_dict = {}
    #     from utils.db import get_page_info
    #     page_er_info = get_page_info(page_no)["er_info"]
    #     for section_er_info in page_er_info:
    #         for entity in section_er_info["entity_information"]:
    #             entity_label_upper = entity["label"].upper()
    #             # print(entity_label_upper)
    #             # print(entity["description"])
    #             if ent_desc_dict.get(entity_label_upper, None):
    #                 if len(ent_desc_dict[entity_label_upper]) < len(entity["description"]):
    #                     ent_desc_dict[entity_label_upper] = entity["description"]
    #             else:
    #                 ent_desc_dict[entity_label_upper] = entity["description"]
    #     # print(json.dumps(ent_desc_dict, indent=2))
    #
    #     return ent_desc_dict
    #
    # def format_page_information(page_no):
    #     from utils.db import get_page_info
    #     entities_dict = make_entities_dict(page_no)
    #     # print(json.dumps(entities_dict, indent=2))
    #
    #     page_info = get_page_info(page_no)
    #     sections_info = page_info["sections"]
    #     er_info = page_info["er_info"]
    #     causality_info = page_info["causality_info"]
    #
    #     out = ""
    #     for idx, sections_info in enumerate(sections_info):
    #         out += f"\nSection Name: {sections_info['section_name']}\n"
    #         out += "=" * 20 + "\n"
    #         out += f"Entities:-\n"
    #         section_entities = er_info[idx]["entity_information"]
    #         section_entity_dict = {}
    #         for entity in section_entities:
    #             if entity["label"].upper() in entities_dict and entity["label"].upper() not in section_entity_dict:
    #                 out += f"{entity['label'].upper().title()} : {entities_dict[entity['label'].upper()]}\n"
    #                 section_entity_dict[entity['label'].upper()] = entities_dict[entity['label'].upper()]
    #
    #         out += "\nRelationships:-\n"
    #         for count, relationship in enumerate(er_info[idx]["relationships_information"]):
    #             rel = f"{count + 1}. Entity1: \"{relationship['entity1']}\", Entity2: \"{relationship['entity2']}\", Relationship: \"{relationship['relationship']}\"\n"
    #             out += rel
    #
    #         try:
    #             section_causality_info = json.loads(causality_info[idx]["answer"])
    #         except json.JSONDecodeError as e:
    #             out += "\nCausalities:-\n"
    #             out += f"{causality_info[idx]['answer']}\n"
    #         section_causality_info = causality_info[idx]["answer"]
    #         # out += f"{section_causality_info}\n"
    #
    #     return out

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge_item in enumerate(incorrect_edges):
            schema_dep_valid = edge_item["schema_dep_validity"]
            edge = edge_item["edge"]
            n1 = edge[0]
            n2 = edge[1]

            # nodes_entities = []
            # n1_entities = get_node_descriptions(n1)["entity_information"]
            # n2_entities = get_node_descriptions(n2)["entity_information"]
            # nodes_entities.extend(n1_entities)
            # nodes_entities.extend(n2_entities)
            #
            # from utils.entities_match_guideline import get_top_10_pages_most_matching_entities
            #
            # top_10_guideline_pages = get_top_10_pages_most_matching_entities(nodes_entities)
            # # print(json.dumps(top_10_guideline_pages))
            #
            # # count = 0
            # out = ""
            # for page_no, ent_info in top_10_guideline_pages.items():
            #     out += "-" * 50 + "\n"
            #     # print(page_ent_info)
            #     out += f"Page Number: {page_no}\n"
            #     out += format_page_information(page_no)
            #
            # # print(out)
            # guideline_info = out
            # # break

            context_input_data = {
                "NODE1": {
                    "id": n1,
                    "label": get_node_descriptions(n1)["label"],
                    # "description": get_node_descriptions(n1)["description"],
                    # "type": get_node_descriptions(n1)["type"],
                    # "observability": get_node_descriptions(n1)["observability"],
                    # "states": get_node_descriptions(n1)["node_states_description"],
                },
                "NODE2": {
                    "id": n2,
                    "label": get_node_descriptions(n2)["label"],
                    # "description": get_node_descriptions(n2)["description"],
                    # "type": get_node_descriptions(n2)["type"],
                    # "observability": get_node_descriptions(n2)["observability"],
                    # "states": get_node_descriptions(n2)["node_states_description"],
                },
                "EDGE1": get_causal_factors((n1, n2)),
                "EDGE2": get_causal_factors((n2, n1)),
                # "ENTITIES_MATCHING_PAGES_INFO": top_10_guideline_pages,
                # "GUIDELINE_PAGES_INFO": guideline_info,
            }
            data = {
                "id": id,
                "llm_model_name": llm_model_name,
                "edge": edge,
                "nodes_data": json.dumps(str(context_input_data), indent=2),
                "schema_dep_validity": schema_dep_valid,
                "num_options": 2,
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    # n1_states=context_input_data["NODE1"]["states"], n2_states=context_input_data["NODE2"]["states"],
                    # n1_type=context_input_data["NODE1"]["type"], n2_type=context_input_data["NODE2"]["type"],
                    # n1_observability=context_input_data["NODE1"]["observability"],
                    # n2_observability=context_input_data["NODE2"]["observability"],
                    n1_label=context_input_data["NODE1"]["label"], n2_label=context_input_data["NODE2"]["label"],
                    # n1_description=context_input_data["NODE1"]["description"],
                    # n2_description=context_input_data["NODE2"]["description"],
                    e1=context_input_data["EDGE1"], e2=context_input_data["EDGE2"],
                    # guideline_pages_info=context_input_data["GUIDELINE_PAGES_INFO"],
                    id=id
                )
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_LABEL_CAUSAL_FACTORS)

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