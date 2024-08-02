from graphreader.utils import paragraph_chunking, extract_notebook_rationale_next_steps_chosen_action
from corpus import corpus, corpus_map_small
import json
from typing import List
from prompt_templates_results import get_rational_plan, get_corpus, \
    get_initial_nodes, exploring_atomic_facts_prompt, exploring_chunks_prompt, \
    exploring_neighbors_prompt
import re

chunk_queue = []
corpus = get_corpus()
question = "What is the name of the castle in the city where the performer of Never Too Loud was formed?"
rational_plan = get_rational_plan(corpus)
notebook = ""
previous_actions = []

corpus_map = corpus_map_small
node_grouped_chunks_afs = {}

# EXPLORING ATOMIC FACTS
def exploring_atomic_facts(node: str):

    global notebook

    print(f"NODE: {node}")
    print(f"EXPLORING ATOMIC FACTS OF NODE: {node}")
    res = exploring_atomic_facts_prompt(
        question=question,
        rational_plan=rational_plan,
        previous_actions=previous_actions,
        notebook=notebook,
        current_node=node,
        node_content=node_grouped_chunks_afs[node]
    )

    print(f"PROMPT RESPONSE: \n{'-'*20}\n{res}")

    previous_actions.append(f"Exploring Atomic Facts of Node: {node}")

    notebook, rationale_next_action, chosen_action = extract_notebook_rationale_next_steps_chosen_action(res)

    print(f"{'-'*50}")
    call_function(chosen_action, node=node)

def call_function(chosen_action: str, node:str):
    print(f"CALL FUNCTION: {chosen_action}\n")
    if "read_chunk" in chosen_action:
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, chosen_action)
        parameters = matches[0]
        chunk_ids = parameters.replace('"','').strip()
        func = globals()["read_chunk"]
        func(chunk_ids, node)
    elif "search_more" in chosen_action:
        func = globals()["search_more"]
        func(node)
    elif"read_neighbor_node" in chosen_action:
        pattern = r'\("([^"]+)"\)'
        matches = re.findall(pattern, chosen_action)
        parameters = matches[0]
        node = parameters.replace('"','').strip()
        func = globals()["read_neighbor_node"]
        func(node)

# EXPLORING CHUNKS
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
    res = exploring_chunks_prompt(
        question=question,
        rational_plan=rational_plan,
        previous_actions=previous_actions,
        notebook=notebook,
        chunk_content=chunk_content,
        chunk_id=chunk_id)

    print(f"PROMPT RESPONSE: \n{'-'*20}\n{res}")

    previous_actions.append(f"Exploring Chunk: {chunk_id}")

    notebook, rationale_next_actions, chosen_action = extract_notebook_rationale_next_steps_chosen_action(res)

    chunk_queue.remove(chunk_id)
    print(f"CHUNK QUEUE: {chunk_queue}")

    print(f"{'-'*50}")

    call_function(chosen_action, node=node)

def search_more(node: str):
    # if supporting fact is insufficient, the agent will continue
    # exploring chunks in the queue;
    if chunk_queue:
        pass
    else:
        previous_actions.append("Searching More on empty queue")
        stop_and_read_neighbor(node)

def read_previous_chunk():
    # due to truncation issues, adjacent chunks might contain relevant
    # and useful information, the agent may insert these IDs to the queue;
    pass

def read_subsequent_chunk():
    # due to truncation issues, adjacent chunks might contain relevant
    # and useful information, the agent may insert these IDs to the queue;
    pass


def stop_and_read_neighbor(node: str):
    # conversely, if the agent deems that none of the chunks are worth
    # further reading, it will finish reading this node and proceed
    # to explore neighboring nodes.

    neighbouring_nodes = get_neighbouring_nodes(node)
    print(f"CURRENT NODE: {node}")
    print(f"NEIGHBOURING NODES: {json.dumps(neighbouring_nodes, indent=2)}")
    previous_actions.append(f"Exploring Neighbouring Nodes of Node: {node}")
    res = exploring_neighbors_prompt(
        question=question,
        rational_plan=rational_plan,
        previous_actions=previous_actions,
        notebook=notebook,
        neighbour_nodes=neighbouring_nodes,
        current_node=node)

    print(f"PROMPT RESPONSE: \n{'-'*20}\n{res}")
    print(res)

    _, rationale_next_steps, chosen_action = extract_notebook_rationale_next_steps_chosen_action(res)

    print(f"{'-'*50}")

    call_function(chosen_action, None)
    # Check if the node has been visited
    # for neighbouring_node in neighbouring_nodes:
    #     print(neighbouring_node)
    #     if f"Exploring Atomic Facts of Node: {neighbouring_node}" in previous_actions:
    #         print(f"Node: {neighbouring_node} has already been visited")
    #         continue

    #     if neighbouring_node == "Danko Jones":
    #         chosen_action = f"read_neighbor_node({neighbouring_node})"
    #         call_function(chosen_action, neighbouring_node)
    #         break

    #     if neighbouring_node == "Toronto":
    #         chosen_action = f"read_neighbor_node({neighbouring_node})"
    #         call_function(chosen_action, neighbouring_node)
    #         break

def read_neighbor_node(node: str):
    # the agent selects a neighboring node that might be helpful in
    # answering the question and re-enters the process of exploring
    # atomic facts and chunks;
    print(f"EXPLORING THE NEIGHBOUR NODE: {node}")
    exploring_atomic_facts(node)

def termination():
    # the agent determines that none of the neighboring nodes contain
    # useful information, it finish the exploration.

    # Perform c) answer reasoning
    pass

def get_neighbouring_nodes(node: str):
    neighbouring_nodes = []
    for chunk_id, chunk_content in corpus_map.items():
        for af_id, af in chunk_content["atomic_facts"].items():
            if node in af["nodes_labels"].values():
                neighbouring_nodes.extend([x for x in af["nodes_labels"].values() if x != node])

    return list(set(neighbouring_nodes))


def map_nodes_af_chunks():
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

                if node_label not in node_grouped_chunks_afs:
                    node_grouped_chunks_afs[node_label] = {
                        chunk_id: [{af_id: atomic_fact}]
                    }
                else:
                    if chunk_id not in node_grouped_chunks_afs[node_label]:
                        node_grouped_chunks_afs[node_label][chunk_id] = [{af_id: atomic_fact}]
                    else:
                        node_grouped_chunks_afs[node_label][chunk_id].append({af_id: atomic_fact})

    print()
    print(json.dumps(node_grouped_chunks_afs, indent=2))


def main():

    print(f"\nCorpus: \n{corpus}\n")
    map_nodes_af_chunks()

    print(f"\nEXPLORATION \n{'='*50}\n")
    # Initial Node and Score
    node, score = get_initial_nodes()[0]
    exploring_atomic_facts(node)

if __name__ == '__main__':
    main()