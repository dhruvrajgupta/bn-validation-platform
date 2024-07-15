from utils import paragraph_chunking, extract_notebook_rationale_next_steps_chosen_action
from corpus import corpus, corpus_map_small
import json
from typing import List
from prompt_templates_results import get_rational_plan, get_corpus, \
    get_initial_nodes, exploring_atomic_facts_prompt, exploring_chunks_prompt
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

    print("PROMPT RESPONSE: \n", res)

    previous_actions.append(f"Exploring Atomic Facts of Node: {node}")

    notebook, rationale_next_action, chosen_action = extract_notebook_rationale_next_steps_chosen_action(res)

    print(f"{'-'*50}")
    
    call_function(chosen_action)

def call_function(chosen_action: str):
    print(f"CALL FUNCTION: {chosen_action}\n")
    if "read_chunk" in chosen_action:
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, chosen_action)
        parameters = matches[0]
        chunk_ids = parameters.replace('"','').strip()
        func = globals()["read_chunk"]
        func(chunk_ids)

# EXPLORING CHUNKS
def read_chunk (chunk_id: str):
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
    
    print("PROMPT RESPONSE: \n", res)

    previous_actions.append(f"Exploring Chunk: {chunk_id}")

    notebook, rationale_next_actions, chosen_action = extract_notebook_rationale_next_steps_chosen_action(res)

    chunk_queue.remove(chunk_id)
    print(f"CHUNK QUEUE: {chunk_queue}")

    print(f"{'-'*50}")

    call_function(chosen_action)

def search_more():
    # if supporting fact is insufficient, the agent will continue 
    # exploring chunks in the queue;
    pass

def read_previous_chunk():
    # due to truncation issues, adjacent chunks might contain relevant 
    # and useful information, the agent may insert these IDs to the queue;
    pass

def read_subsequent_chunk():
    # due to truncation issues, adjacent chunks might contain relevant 
    # and useful information, the agent may insert these IDs to the queue;
    pass


    def termination():
        # if sufficient information has been gathered for answering the question, 
        # the agent will finish exploration.
        pass



def stop_and_read_neighbor():
    # conversely, if the agent deems that none of the chunks are worth 
    # further reading, it will finish reading this node and proceed 
    # to explore neighboring nodes.
    pass

def read_neighbor_node():
    # the agent selects a neighboring node that might be helpful in 
    # answering the question and re-enters the process of exploring 
    # atomic facts and chunks;
    pass

def termination():
    # the agent determines that none of the neighboring nodes contain 
    # useful information, it finish the exploration.
    pass


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