EXPLORING_ATOMIC_FACTS_PROMPT = """
As an intelligent assistant, your primary objective is to answer questions based on information 
contained within a text. To facilitate this objective, a graph has been created from the text, 
comprising the following elements: 
1. Text Chunks: Chunks of the original text. 
2. Atomic Facts: Smallest, indivisible truths extracted from text chunks. 
3. Nodes: Key elements in the text (noun, verb, or adjective) that correlate with several atomic 
facts derived from different text chunks. 

Your current task is to check a node and its associated atomic facts, with the objective of 
determining whether to proceed with reviewing the text chunk corresponding to these atomic facts. 
Given the question, the rational plan, previous actions, notebook content, and the current node’s 
atomic facts and their corresponding chunk IDs, you have the following Action Options: 
##### 
1. read_chunk(List[ID]): Choose this action if you believe that a text chunk linked to an atomic 
fact may hold the necessary information to answer the question. This will allow you to access 
more complete and detailed information. 
2. stop_and_read_neighbor(): Choose this action if you ascertain that all text chunks lack valuable 
information. 
##### 

Strategy: 
##### 
1. Reflect on previous actions and prevent redundant revisiting nodes or chunks. 
2. You can choose to read multiple text chunks at the same time. 
3. Atomic facts only cover part of the information in the text chunk, so even if you feel that the 
atomic facts are slightly relevant to the question, please try to read the text chunk to get more 
complete information. 
##### 

Response format: 
##### 
*Updated Notebook*: First, combine your current notebook with new insights and findings about 
the question from current atomic facts, creating a more complete version of the notebook that 
contains more valid information. 
*Rationale for Next Action*: Based on the given question, the rational plan, previous actions, and 
notebook content, analyze how to choose the next action. 
*Chosen Action*: read_chunk(List[ID]) or stop_and_read_neighbor(). (Here is the Action you 
selected from Action Options, which is in the form of a function call as mentioned before. The 
formal parameter in parentheses should be replaced with the actual parameter.) 
##### 

Finally, it is emphasized again that even if the atomic fact is only slightly relevant to the 
question, you should still look at the text chunk to avoid missing information. You should only 
choose stop_and_read_neighbor() when you are very sure that the given text chunk is irrelevant to 
the question. Please strictly follow the above format. Let’s begin.

Question:
{question}

Rational Plan:
{rational_plan}

Previous Actions:
{previous_actions}

Notebook:
{notebook}

Current Node:
{current_node}

Current Node Chunks and Atomic Facts are of the following format:
"CHUNK_ID#": [
    "ATOMIC_FACT_ID#": "ATOMIC_FACT_TEXT",
    ....
],
....

Current Node Chunks and Atomic Facts:
{node_content}
"""