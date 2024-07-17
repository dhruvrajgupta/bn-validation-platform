from corpus import corpus, corpus_map_small
from prompt_templates_results import get_initial_nodes, get_rational_plan
from prompt_templates import EXPLORING_ATOMIC_FACTS_PROMPT, EXPLORING_CHUNKS_PROMPT
from langchain_core.prompts import PromptTemplate
from utils import ask_llm, extract_notebook_rationale_next_steps_chosen_action
import json
import re

corpus_map = corpus_map_small
question = "What is the name of the castle in the city where the performer of Never Too Loud was formed?"
rational_plan = get_rational_plan()
previous_actions = []
notebook = ""
chunk_queue = []
insert = ""

nodes_grouped_chunks_afs = {}


# EXPLORING ATOMIC FACTS
def explore_atomic_facts(node: str):

    global notebook

    print(f"NODE: {node}")
    print(f"EXPLORING ATOMIC FACTS OF NODE: {node}")
    exploring_atomic_facts_prompt = EXPLORING_ATOMIC_FACTS_PROMPT
    exploring_atomic_facts_prompt = PromptTemplate.from_template(exploring_atomic_facts_prompt) \
                                        .format(
                                            question=question,
                                            rational_plan=rational_plan,
                                            previous_actions=json.dumps(previous_actions, indent=2),
                                            notebook=notebook,
                                            current_node=node,
                                            node_content=json.dumps(nodes_grouped_chunks_afs[node], indent=2)
                                        )

    print(f"\nPROMPT TO THE LLM:\n{'-'*20}")
    print(exploring_atomic_facts_prompt)

    previous_actions.append(f"Exploring Atomic Facts of Node: {node}")

    print(f"PROMPT RESPONSE: \n{'-'*20}\n")
    llm_response =ask_llm(exploring_atomic_facts_prompt)

    notebook, rationale_next_action, chosen_action = extract_notebook_rationale_next_steps_chosen_action(llm_response)

    call_function(chosen_action, node=node)


def read_chunk (chunk_id: str, node: str = None):
    # if the agent identifies certain chunks as valuable for further reading,
    # it will complete the function parameters with the chunk IDs,
    # i.e., read_chunk(List[ID]), and append these IDs to a chunk queue
    global notebook
    chunk_queue.append(chunk_id)
    print(f"CHUNK QUEUE: {chunk_queue}")
    print(f"CHUNK_ID: {chunk_id}")
    print(f"EXPLORING CHUNK: {chunk_id}")
    chunk_content = corpus_map[chunk_id]["text"]
    exploring_chunks_prompt = EXPLORING_CHUNKS_PROMPT
    exploring_chunks_prompt = PromptTemplate.from_template(exploring_chunks_prompt) \
                                .format(
                                    question=question,
                                    rational_plan=rational_plan,
                                    previous_actions=json.dumps(previous_actions, indent=2),
                                    notebook=notebook,
                                    chunk_content=chunk_content,
                                    chunk_id=chunk_id
                                )

    print(f"\nPROMPT TO THE LLM:\n{'-'*20}")
    print(exploring_chunks_prompt)

    previous_actions.append(f"Exploring Chunk: {chunk_id}")

    print(f"PROMPT RESPONSE: \n{'-'*20}\n")
    llm_response =ask_llm(exploring_chunks_prompt)

    notebook, rationale_next_action, chosen_action = extract_notebook_rationale_next_steps_chosen_action(llm_response)

    chunk_queue.remove(chunk_id)
    print(f"CHUNK QUEUE: {chunk_queue}")

    print(f"{'-'*50}")

    call_function(chosen_action)


# def read_previous_chunk(chunk_id, node):
#     # due to truncation issues, adjacent chunks might contain relevant
#     # and useful information, the agent may insert these IDs to the queue;

#     # Temp Logic to get the previous_chunk_id
#     import collections
#     sorted_chunks = collections.OrderedDict(sorted(corpus_map.items()))
#     sorted_chunks_ids = [chunk_id for chunk_id in sorted_chunks.keys()]
#     previous_chunk_index = sorted_chunks_ids.index(chunk_id) - 1

#     if previous_chunk_index < 0:
#         print("There is no previous chunk, so re-reading the current chunk...\n")
#         # TODO: What to do when there is no previous chunk
#         # For now we will re-read the chunk
#         previous_chunk_index = 0

#     previous_chunk_id =  sorted_chunks_ids[previous_chunk_index]

#     print(f"CURRENT CHUNK ID: {chunk_id}")
#     print(f"PREVIOUS CHUNK ID: {previous_chunk_id}")
#     # previous_chunk = corpus_map[previous_chunk_id]
#     # previous_chunk_text = previous_chunk["text"]
#     # print(previous_chunk_text)
#     chosen_action = f'read_chunk("{previous_chunk_id}")'
#     call_function(chosen_action, node=node)



def map_nodes_chunks_afs():
    #
    # all atomic facts associated with a node are grouped by their
    # corresponding chunks, labeled with the respective chunk IDs,
    # and fed to the agent.
    #

    print(f"Mapping nodes with their associated chunks and atomic facts...\n{'='*50}")
    print(f"Nodes and their disambiguated label mapping...\n{'-'*50}")
    for chunk_id, chunk in corpus_map.items():

        chunk_text = chunk["text"]
        chunk_atomic_facts = chunk["atomic_facts"]

        for af_id, af in chunk_atomic_facts.items():

            atomic_fact = af["atomic_fact"]
            atomic_fact_key_elements = af["key_elements"]
            atomic_fact_nodes = af["nodes"]
            atomic_fact_nodes_labels = af["nodes_labels"]

            for af_key_element, node_label in atomic_fact_nodes_labels.items():
                print(f"{af_key_element} -> {node_label}")

                if node_label not in nodes_grouped_chunks_afs:
                    nodes_grouped_chunks_afs[node_label] = {
                        chunk_id: [{af_id: atomic_fact}]
                    }
                else:
                    if chunk_id not in nodes_grouped_chunks_afs[node_label]:
                        nodes_grouped_chunks_afs[node_label][chunk_id] = [{af_id: atomic_fact}]
                    else:
                        nodes_grouped_chunks_afs[node_label][chunk_id].append({af_id: atomic_fact})

    print("\n")
    print(json.dumps(nodes_grouped_chunks_afs, indent=2))

def call_function(chosen_action: str, **kwargs):
    print(f"CALL FUNCTION: {chosen_action}\n")
    if "read_chunk" in chosen_action:
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, chosen_action)
        parameters = matches[0]
        chunk_ids = parameters.replace('"','').strip()
        func = globals()["read_chunk"]
    #     func(chunk_ids, node)

    # if "read_previous_chunk" in chosen_action:
    #     pattern = r'\[([^\]]+)\]'
    #     matches = re.findall(pattern, chosen_action)
    #     parameters = matches[0]
    #     chunk_ids = parameters.replace('"','').strip()
    #     func = globals()["read_previous_chunk"]
    #     func(chunk_ids, node)

def main():

    print(f"\nCORPUS: \n{'='*50}\n{corpus}\n")
    map_nodes_chunks_afs()

    print(f"\n\nEXPLORATION \n{'='*50}\n")

    # Initial Node and Score
    node, score = get_initial_nodes()[0]

    print(f"INITIAL NODE: {node}, Score: {score}\n")
    explore_atomic_facts(node)
    # read_chunk("C1")
    # read_previous_chunk("C1")


if __name__ == '__main__':
    main()