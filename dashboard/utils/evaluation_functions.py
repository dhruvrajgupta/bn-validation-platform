from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

import json
import openai
import weave

import asyncio
import numpy as np
from math import exp

import streamlit as st

# Example
# dataset = [
#     {"id": 1, "edge": (), "correct": "B", "incorrect": "A", "prompt": "..."}
# ]

dataset = []
evaluation_data = []

def format_reasoning(evaluation_data):
    for id, evaluation_data_item in enumerate(evaluation_data):
        list_reasoning = evaluation_data_item.get("reasoning")
        # st.write(list_reasoning)
        if list_reasoning:
            formatted_reasoning = ""
            for step, reason in enumerate(list_reasoning):
                formatted_reasoning += f"{step + 1}. {reason}\n"
            evaluation_data[id]["reasoning"] = formatted_reasoning

    return evaluation_data

class Option(str, Enum):
    A = "A"
    B = "B"
class EdgeOrientationJudgement(BaseModel):
    # id: int
    thinking: List[str]
    answer: Option

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
            logprobs=True
        )
        result = response.choices[0].message.content

        answer_choice_probablities = {
            "A": None,
            "B": None
        }
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
        parsed["answer_choice_probablities"] = answer_choice_probablities
        return parsed


ONLY_NODE_ID = """\
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
   "thinking": ["...", ...]
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

@weave.op()
def edge_judgement_scorer(id, output):
    evaluation_data[id] = dataset[id]
    evaluation_data[id]["reasoning"] = output["thinking"]
    evaluation_data[id]["answer"] = output["answer"]
    evaluation_data[id]["answer_choice_probablities"] = output["answer_choice_probablities"]
    return output["answer"] == dataset[id]["correct"]

def baseline_only_node_id_causes(incorrect_edges, eval_name, bn_model):

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge in enumerate(incorrect_edges):
            data = {
                "id": id,
                "edge": edge,
                "verb": "causes",
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(n1=edge[0], n2=edge[1], verbk="causes", id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, ONLY_NODE_ID)
    weave.init('bnv_N_staging')

    model = EvaluationModel(model_name='gpt-4o-mini')

    evaluation = weave.Evaluation(
        name=eval_name,
        dataset=dataset,
        scorers=[edge_judgement_scorer]
    )

    evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))

    eval_res_dict = {
        # "dataset": dataset,
        "eval_scorer_summary": evaluation_scorer_summary,
        "evaluation_data": format_reasoning(evaluation_data)
    }

    return eval_res_dict


NODE_ID_AND_STATE_NAMES = """\
NODE 1:
node_id: {n1}
states: {n1_states}

NODE 2:
node_id: {n2}
states: {n2_states}

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
   "thinking": ["...", ...]
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

def baseline_only_node_id_state_names_causes(incorrect_edges, eval_name, bn_model):

    def create_dataset(incorrect_edges, prompt_template):
        # We are reversing the edges for evaluation
        for id, edge in enumerate(incorrect_edges):
            n1 = edge[0]
            n2 = edge[1]
            n1_states = bn_model.states[n1]
            n2_states = bn_model.states[n2]
            data = {
                "id": id,
                "edge": edge,
                "n1_states": n1_states,
                "n2_states": n2_states,
                "verb": "causes",
                "correct": "B",
                # "incorrect": "A",
                "prompt": prompt_template.format(
                    n1=n1, n2=n2,
                    n1_states=n1_states, n2_states=n2_states,
                    verbk="causes",
                    id=id)
            }
            dataset.append(data)
            evaluation_data.append(data)

    create_dataset(incorrect_edges, NODE_ID_AND_STATE_NAMES)

    weave.init('bnv_N_staging')

    model = EvaluationModel(model_name='gpt-4o-mini')

    evaluation = weave.Evaluation(
        name=eval_name,
        dataset=dataset,
        scorers=[edge_judgement_scorer]
    )

    evaluation_scorer_summary = asyncio.run(evaluation.evaluate(model))

    eval_res_dict = {
        # "dataset": dataset,
        "eval_scorer_summary": evaluation_scorer_summary,
        "evaluation_data": format_reasoning(evaluation_data)
    }

    return eval_res_dict