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

**Reasoning**:

{reasoning}

**Critique**:

| Critique Consistent | Critique Answer | Critique Reasoning |
|---------------------|----------------|-------------------|
| {critique_consistent} | {critique_answer} | {critique_reasoning} |

---
"""
# **Schema Dependency Validity**: {schema_dep_validity}
import pandas as pd
cvs_file = pd.read_csv("/home/dhruv/Desktop/bn-validation-platform/evaluation_results/type2only_node_ids.csv", header=0)
# print(cvs_file)

output = ""

for index, row in cvs_file.iterrows():
    # print(row)
    # if index == 2:
    #     break

    edge = row["edge"].split(",")
    edge = f"`{edge[0]}`  &emsp; ----> &emsp;  `{edge[1]}`"

    # print(row["prompt"].encode("ascii"))
    # prompt = row["prompt"].replace("\n", "<br>")
    # prompt = prompt.replace("<thinking>", "\<thinking\>")
    # prompt = prompt.replace("</thinking>", "\<\/thinking\>")
    # prompt = prompt.replace("<answer>", "\<answer\>")
    # prompt = prompt.replace("</answer>", "\<\/answer\>")
    # print(prompt)
    prompt = row["prompt"].replace(ad_str, "").strip()
    prompt = prompt.replace("\n", "<br>")
    # print(prompt)

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
    )

# title = """# Causal Reasoning based on prompt of Type2 using only Node Identitfiers"""
title = """
# Causal Reasoning based on prompt of Type2 using only Node Identitfiers.
**In addition to the PDF representing the N-Staging sub model,
these evaluations here present as chatbot-based reasoning about two pre-selected edge directions.
We ask you to read the following reasonings and evaluate whether the LLM reasonings are,**
1. **Correct/Incorrect recommendation (Yes/No)**
2. **Conflict/No Conlict (Reasons), and**
3. **Helpful/Not Helpful**

**Please feel free to**  
4. **provide additional feedback of thoughts related to the chatbased evaluation.**

**Finally, we would like to ask you:**  
5. **Select a number of edges/causal relations from the N-Staging subnetwork that you would be interested in getting additional insights similar to those presented here.**
---
---
---
"""
print(title + output)