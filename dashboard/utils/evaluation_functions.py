from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class Option(str, Enum):
    A = "A"
    B = "B"
class EdgeOrientationJudgement(BaseModel):
    thinking: List[str]
    answer: Option

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
   "thinking": ["...", ...],
   "answer": ...
}}
</answer>

Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""

import streamlit as st

def baseline_only_node_id_causes(incorrect_edges, correct_edges):
    for edge in incorrect_edges:
        st.write(edge)