from openai import OpenAI
from typing import List
from enum import Enum

OPENAI_API_KEY=""


from pydantic import BaseModel
def ask_llm_response_schema(prompt: str, response_format: BaseModel):
    """
    Ask the LLM a question and print the response.

    Parameters
    ----------
    prompt : str
        The question to ask the LLM.
    stream : bool, optional
        If True, stream the response from the LLM as it is generated. If False, wait for the
        entire response to be generated before printing it. Defaults to False.

    Returns
    -------
    str
        The response from the LLM.
    """

    # return

    model_name = "gpt-4o-mini"
    # model_name = "gpt-4o"
    # temperature = 0

    client = OpenAI(
        # Defaults to os.environ.get("OPENAI_API_KEY")
        api_key=OPENAI_API_KEY
    )

    print(f"PROMPT:\n\n{prompt}")

    response = client.beta.chat.completions.parse(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        # temperature=temperature,
        response_format=response_format,
        logprobs=True
    )

    # print(len(response.choices))

    # for choice in response.choices:
    #     print(f"ROLE: {choice.message.role}")
    #     print(f"CONTENT: {choice.message.content}")

    import numpy as np
    from math import exp
    for token in response.choices[0].logprobs.content:
        print("Token:", token.token)
        print("Log prob:", token.logprob)
        print("Linear prob:", np.round(exp(token.logprob) * 100, 2), "%")
        print("Bytes:", token.bytes, "\n")

    print(f"START OF LLM RESPONSE: \n{'-'*20}\n")

    llm_response = response.choices[0].message.content
    print(llm_response)

    print(f"\n\nEND OF LLM RESPONSE\n{'-'*50}\n")

    # print(response)

    # return llm_response


class Option(str, Enum):
    A = "A"
    B = "B"
class EdgeOrientationJudgement(BaseModel):
    thinking: List[str]
    answer: Option


PROMPT = """\
Among these two options which one is the most likely true:
(A) lung cancer causes cigarette smoking
(B) cigarette smoking causes lung cancer

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


ask_llm_response_schema(PROMPT, EdgeOrientationJudgement)