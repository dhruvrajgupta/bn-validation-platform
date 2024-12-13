template = """
---

**Edge ID**: {id}

**Edge**: {edge}

**Schema Dependency Validity**: {schema_dep_validity}

**Prompt**:

{prompt}

**Answer**: {answer}

**Answer Choice Probabilities**: {answer_choice_probabilities}

**Reasoning**:

{reasoning}

**Critique**:

| Critique Consistent | Critique Answer | Critique Reasoning |
|---------------------|----------------|-------------------|
| {critique_consistent} | {critique_answer} | {critique_reasoning} |

---
"""

import pandas as pd
cvs_file = pd.read_csv("/home/dhruv/Desktop/bn-validation-platform/evaluation_results/type1only_node_ids.csv", header=0)
# print(cvs_file)

output = ""

for index, row in cvs_file.iterrows():
    # print(row)
    # if index == 2:
    #     break

    edge = row["edge"].split(",")
    edge = f"`{edge[0]}`  &emsp; ----> &emsp;  `{edge[1]}`"

    # print(row["prompt"].encode("ascii"))
    prompt = row["prompt"].replace("\n", "<br>")
    prompt = prompt.replace("<thinking>", "\<thinking\>")
    prompt = prompt.replace("</thinking>", "\<\/thinking\>")
    prompt = prompt.replace("<answer>", "\<answer\>")
    prompt = prompt.replace("</answer>", "\<\/answer\>")
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


print(output)