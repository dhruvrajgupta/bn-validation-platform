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

Please strictly follow the above format. Let’s begin."""