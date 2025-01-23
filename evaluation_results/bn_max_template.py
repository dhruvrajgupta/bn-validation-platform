import json

def get_eval_prompt(input_string):
    # print(input_string)
    # Find the start and end indices
    or_str = "Among these two options which one is the most likely true:\n"
    start_index = input_string.find("Among these two options which one is the most likely true:") + len(
        "Among these two options which one is the most likely true:")
    end_index = input_string.find("The answer is: ...")

    # Extract the substring between the start and end indices
    extracted_text = input_string[start_index:end_index].strip()

    # Print the extracted text
    return or_str+extracted_text

def get_matched_pages(input_string):
    # Find the start and end indices
    start_index = input_string.find("'ENTITIES_MATCHING_PAGES_INFO':") + len("'ENTITIES_MATCHING_PAGES_INFO':")
    end_index = input_string.find(", 'GUIDELINE_PAGES_INFO':")

    # Extract the substring between 'ENTITIES_MATCHING_PAGES_INFO' and 'GUIDELINE_PAGES_INFO'
    extracted_text = input_string[start_index:end_index].strip()
    extracted_text = extracted_text.replace("'", '"')

    # Print the extracted text
    return json.loads(extracted_text).keys()

def extract_edge1_data(input_string):
    # Find the start and end indices
    start_index = input_string.find("`EDGE1`:") + len("`EDGE1`:")
    end_index = input_string.find("`EDGE2`:")

    # Extract the substring between `EDGE1` and `EDGE2`
    extracted_string = input_string[start_index:end_index].strip()
    extracted_string = extracted_string.replace("'", '"')
    extracted_string = extracted_string.replace("True", 'true')
    extracted_string = extracted_string.replace("False", 'false')

    # split = extracted_string.split("\"explanation\"")
    # second_part = split[1]
    # second_part = second_part.replace("\"(", "'(")
    # second_part = second_part.replace(")\"", ")'")
    # extracted_string = split[0] + "\"explanation\"" + second_part

    # print(extracted_string)
    edge1 = json.loads(extracted_string)

    out = """
EDGE1:
edge: {edge}
causal_direction: {causal_direction}
causal_distance: {causal_distance}
causal_factor: 
    "necessary": {necessary}
    "sufficient": {sufficient}
explanation: {explanation}
"""
    explanation = [f"{c+1}. {x}\n" for c, x in enumerate(edge1["explanation"])]
    out = out.format(edge=edge1["edge"], explanation="\n"+"".join(explanation),
                     causal_direction=edge1["causal_direction"],
                     causal_distance=edge1["causal_distance"],
                     necessary=edge1["causal_factor"]["necessary"],
                     sufficient=edge1["causal_factor"]["sufficient"])

    return out

def extract_edge2_data(input_string):
    # Find the start and end indices
    start_index = input_string.find("`EDGE2`:") + len("`EDGE2`:")
    end_index = input_string.find("`INFORMATION FROM KNOWLEDGE BASE`:")

    # Extract the substring between `EDGE1` and `EDGE2`
    extracted_string = input_string[start_index:end_index].strip()
    extracted_string = extracted_string.replace("'", '"')
    extracted_string = extracted_string.replace("True", 'true')
    extracted_string = extracted_string.replace("False", 'false')

    # split = extracted_string.split("\"explanation\"")
    # second_part = split[1]
    # second_part = second_part.replace("\"(", "'(")
    # second_part = second_part.replace(")\"", ")'")
    # extracted_string = split[0]+"\"explanation\""+second_part

    # print(extracted_string)
    edge2 = json.loads(extracted_string)

    out = """
EDGE2:
edge: {edge}
causal_direction: {causal_direction}
causal_distance: {causal_distance}
causal_factor: 
    "necessary": {necessary}
    "sufficient": {sufficient}
explanation: {explanation}
"""
    explanation = [f"{c+1}. {x}\n" for c, x in enumerate(edge2["explanation"])]
    out = out.format(edge=edge2["edge"], explanation="\n"+"".join(explanation),
                     causal_direction=edge2["causal_direction"],
                     causal_distance=edge2["causal_distance"],
                     necessary=edge2["causal_factor"]["necessary"],
                     sufficient=edge2["causal_factor"]["sufficient"])

    return out

definitions_str = """edge - The edge which needs to be verified.
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


"""

ad_str = """
The answer is: ...

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{
   "thinking": ["...", ...]
   "answer": ...
}
</answer>

Before providing the answer in <answer> tags, think step by step in detail in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

template = """
---

**Edge ID**: {id}

**Edge**: {edge}

**Prompt**:
{prompt}

**LLM Answer**: {answer}

**LLM Answer Choice Probabilities**: {answer_choice_probabilities}

**Evidences**:
{evidences}

**Reasoning**:
{reasoning}

**Critique**:

| Critique Consistent | Critique Answer | Critique Reasoning |
|---------------------|----------------|-------------------|
| {critique_consistent} | {critique_answer} | {critique_reasoning} |

---
<div style="page-break-after: always;"></div>
"""
# **Schema Dependency Validity**: {schema_dep_validity}

template_prev = """
---

**Edge ID**: {id}

**Edge**: {edge}

**Prompt**:
{prompt}

**LLM Answer**: {answer}

**LLM Answer Choice Probabilities**: {answer_choice_probabilities}

**Evidences**:
{evidences}

**Reasoning**:
{reasoning}

**Critique**:

| Critique Consistent | Critique Answer | Critique Reasoning |
|---------------------|----------------|-------------------|
| {critique_consistent} | {critique_answer} | {critique_reasoning} |

---
<div style="page-break-after: always;"></div>
"""

prompt_str = """
{edge1}

{edge2}

Top 5 Corresponding Pages:
{matching_pages}

{eval_prompt}
"""

import pandas as pd
# cvs_file = pd.read_csv("/home/dhruv/Desktop/bn-validation-platform/evaluation_results/type1only_node_ids.csv", header=0)
# cvs_file = pd.read_csv("/home/dhruv/Desktop/descccc.csv", header=0)
# print(cvs_file)
csv_file = pd.read_csv("/home/dhruv/Desktop/bn-validation-platform/llm_created_bn/Converted N Stage Model/Max/evaluation.csv",header=0)

output = ""

matching_pages = []

for index, row in csv_file.iterrows():
    # print(row)
    if index == 3:
        break

    edge = row["edge"].split(",")
    edge = f"`{edge[1]}`  &emsp; ----> &emsp;  `{edge[0]}`"

    # print(row["prompt"].encode("ascii"))

    # prompt = prompt.replace("<thinking>", "\<thinking\>")
    # prompt = prompt.replace("</thinking>", "\<\/thinking\>")
    # prompt = prompt.replace("<answer>", "\<answer\>")
    # prompt = prompt.replace("</answer>", "\<\/answer\>")
    # print(row["prompt"])
    # prompt = row["prompt"].replace(ad_str, "").strip()
    # prompt = row["prompt"].replace(definitions_str,"").strip()
    # prompt = prompt.replace("\n", "<br>")
    # print(row["prompt"])
    edge1 = extract_edge1_data(row["prompt"]).strip()
    edge2 = extract_edge2_data(row["prompt"]).strip()
    context_input_data = json.loads(row["context_input_data"])
    matched_pages = get_matched_pages(context_input_data)
    # print(matched_pages)
    matching_pages.extend(matched_pages)

    eval_prompt = get_eval_prompt(row["prompt"])
    prompt = prompt_str.format(edge1=edge1.replace("\n", "<br>"),
                               edge2=edge2.replace("\n", "<br>"),
                               eval_prompt=eval_prompt.replace("\n", "<br>"),
                               matching_pages=list(matched_pages))


    critique_reasoning = row["critique_reasoning"].replace("\n", "<br>")


    output += template.format(
        id=row["id"],
        edge=edge,
        schema_dep_validity=row["schema_dep_validity"],
        prompt=prompt,
        answer=row["answer"],
        answer_choice_probabilities=row["answer_choice_probablities"],
        reasoning=row["reasoning"],
        critique_consistent=row["critique_consistent"],
        critique_answer=row["critique_answer"],
        critique_reasoning=critique_reasoning,
        evidences=row["evidences"]
    )

# print(set(matching_pages))

title = """
# Causal Reasoning of edges of BN constructed by Max.
**In addition to the PDF representing the N-Staging sub model,
these evaluations here present as chatbot-based reasoning about two pre-selected edge directions.
We ask you to read the following reasonings and evaluate whether the LLM reasonings are,**
1. **Correct/Incorrect recommendation (Yes/No)**
2. **Conflict/No Conlict (Reasons), and**
3. **Helpful/Not Helpful**

**Please feel free to**  
4. **provide additional feedback of thoughts related to the chatbased evaluation.**
---
---
---
"""
print(title+output)

# print(output)