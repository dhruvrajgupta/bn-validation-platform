RATIONAL_PLAN_PROMPT = """
As an intelligent assistant, your primary objective is to answer the question by gathering
supporting facts from a given article. To facilitate this objective, the first step is to make
a rational plan based on the question. This plan should outline the step-by-step process to
resolve the question and specify the key information required to formulate a comprehensive answer.

Example:
#####
User: Who had a longer tennis career, Danny or Alice?

Assistant: In order to answer this question, we first need to find the length of Danny’s
and Alice’s tennis careers, such as the start and retirement of their careers, and then compare the
two.
#####

Please strictly follow the above format. Let’s begin.
"""




INITIAL_NODE_SELECTION_PROMPT = """
As an intelligent assistant, your primary objective is to answer questions based on information
contained within a text. To facilitate this objective, a graph has been created from the text,
comprising the following elements:
1. Text Chunks: Chunks of the original text.
2. Atomic Facts: Smallest, indivisible truths extracted from text chunks.
3. Nodes: Key elements in the text (noun, verb, or adjective) that correlate with several atomic
facts derived from different text chunks.

Your current task is to check a list of nodes, with the objective of selecting the most
relevant initial nodes from the graph to efficiently answer the question. You are given the question, the
rational plan, and a list of node key elements. These initial nodes are crucial because they are the
starting point for searching for relevant information.

Requirements:
#####
1. Once you have selected a starting node, assess its relevance to the potential answer by assigning
a score between 0 and 100. A score of 100 implies a high likelihood of relevance to the answer,
whereas a score of 0 suggests minimal relevance.
2. Present each chosen starting node in a separate line, accompanied by its relevance score. Format
each line as follows: Node: [Key Element of Node], Score: [Relevance Score].
3. Please select at least 10 starting nodes, ensuring they are non-repetitive and diverse.
4. In the user’s input, each line constitutes a node. When selecting the starting node, please make
your choice from those provided, and refrain from fabricating your own. The nodes you output
must correspond exactly to the nodes given by the user, with identical wording.
#####

Example:
#####
User:
Question: {question}
Plan: {rational_plan}
Nodes: {list_key_elements}

Assistant:{LIST OF SELECTED NODES}
#####

Finally, I emphasize again that you need to select the starting node from the given Nodes, and
it must be consistent with the words of the node you selected. Please strictly follow the above
format. Let’s begin.
"""




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
formal parameter in parentheses should be replaced with the actual parameter.). The Chunk List[ID]s
will be provied below in the place "Chunk Identifiers (List[ID]): [Chunk ID 1, Chunk ID 2, Chunk ID 3, Chunk ID #, ...]"
You can read only one chunk at a time
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

Chunk Identifiers (List[ID]):
{chunk_ids}

Current Node Chunks and Atomic Facts are of the following format:
"CHUNK_ID#": [
    "ATOMIC_FACT_ID#": "ATOMIC_FACT_TEXT",
    ....
],
....

Current Node Chunks and Atomic Facts:
{node_content}
"""




EXPLORING_CHUNKS_PROMPT = """
As an intelligent assistant, your primary objective is to answer questions based on information
within a text. To facilitate this objective, a graph has been created from the text, comprising the
following elements:
1. Text Chunks: Segments of the original text.
2. Atomic Facts: Smallest, indivisible truths extracted from text chunks.
3. Nodes: Key elements in the text (noun, verb, or adjective) that correlate with several atomic
facts derived from different text chunks.


Your current task is to assess a specific text chunk and determine whether the available information
suffices to answer the question. Given the question, rational plan, previous actions, notebook
content, and the current text chunk, you have the following Action Options:
#####
1. search_more(): Choose this action if you think that the essential information necessary to
answer the question is still lacking.
2. read_previous_chunk(): Choose this action if you feel that the previous text chunk contains
valuable information for answering the question.
3. read_subsequent_chunk(): Choose this action if you feel that the subsequent text chunk contains
valuable information for answering the question.
4. termination(): Choose this action if you believe that the information you have currently obtained
is enough to answer the question. This will allow you to summarize the gathered information and
provide a final answer.
#####

Strategy:
#####
1. Reflect on previous actions and prevent redundant revisiting of nodes or chunks.
2. You can only choose one action.
#####

Response format:
#####
*Updated Notebook*: First, combine your previous notes with new insights and findings about the
question from current text chunks, creating a more complete version of the notebook that contains
more valid information.
*Rationale for Next Action*: Based on the given question, rational plan, previous actions, and
notebook content, analyze how to choose the next action.
*Chosen Action*: search_more() or read_previous_chunk() or read_subsequent_chunk() or
termination(). (Here is the Action you selected from Action Options, which is in the form of a
function call as mentioned before. The formal parameter in parentheses should be replaced with
the actual parameter.)
#####

Please strictly follow the above format. Let’s begin.

Question:
{question}

Rational Plan:
{rational_plan}

Previous Actions:
{previous_actions}

Notebook:
{notebook}

Current Text Chunk:
{chunk_content}
"""




EXPLORING_NEIGHBOURS_PROMPT = """
As an intelligent assistant, your primary objective is to answer questions based on information
within a text. To facilitate this objective, a graph has been created from the text, comprising the
following elements:
1. Text Chunks: Segments of the original text.
2. Atomic Facts: Smallest, indivisible truths extracted from text chunks.
3. Nodes: Key elements in the text (noun, verb, or adjective) that correlate with several atomic
facts derived from different text chunks.

Your current task is to assess all neighbouring nodes of the current node, with the
objective of determining whether to proceed to the next neighboring node. Given the question, rational
plan, previous actions, notebook content, and the neighbors of the current node, you have the
following Action Options:
#####
1. read_neighbor_node(key element of node): Choose this action if you believe that any of the
neighboring nodes may contain information relevant to the question. Note that you should focus
on one neighbor node at a time.
2. termination(): Choose this action if you believe that none of the neighboring nodes possess
information that could answer the question.
#####

Strategy:
#####
1. Reflect on previous actions and prevent redundant revisiting of nodes or chunks.
2. You can only choose one action. This means that you can choose to read only one neighbour
node or choose to terminate.
#####

Response format:
#####
*Rationale for Next Action*: Based on the given question, rational plan, previous actions, and
notebook content, analyze how to choose the next action.
*Chosen Action*: read_neighbor_node(neighbor_node) or termination(). (Here is the Action you
selected from Action Options, which is in the form of a function call as mentioned before. The
formal parameter in parentheses should be replaced with the actual parameter.)
#####

Please strictly follow the above format. Let’s begin.

Question:
{question}

Rational Plan:
{rational_plan}

Previous Actions:
{previous_actions}

Notebook:
{notebook}

Neighbours of Current Node:
{neighbour_nodes}
"""