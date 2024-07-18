from corpus import corpus, corpus_map_small
from prompt_templates_results import get_initial_nodes, get_rational_plan
from prompt_templates import EXPLORING_ATOMIC_FACTS_PROMPT, EXPLORING_CHUNKS_PROMPT, EXPLORING_NEIGHBOURS_PROMPT
from langchain_core.prompts import PromptTemplate
from utils import ask_llm, extract_notebook_rationale_next_steps_chosen_action, print_state
import json
import re

corpus_map = corpus_map_small
question = "What is the name of the castle in the city where the performer of Never Too Loud was formed?"
rational_plan = get_rational_plan()
previous_actions = []
notebook = ""
chunk_queue = []
current_node = None

nodes_grouped_chunks_afs = {}


# EXPLORING ATOMIC FACTS
def explore_atomic_facts():

    global notebook

    print(f"NODE: {current_node}")
    print(f"EXPLORING ATOMIC FACTS OF NODE: {current_node}")

    exploring_atomic_facts_prompt = EXPLORING_ATOMIC_FACTS_PROMPT
    exploring_atomic_facts_prompt = PromptTemplate.from_template(exploring_atomic_facts_prompt) \
                                        .format(
                                            question=question,
                                            rational_plan=rational_plan,
                                            previous_actions=json.dumps(previous_actions, indent=2),
                                            notebook=notebook,
                                            current_node=current_node,
                                            node_content=json.dumps(nodes_grouped_chunks_afs[current_node], indent=2)
                                        )

    previous_actions.append(f"Exploring Atomic Facts of Node: {current_node}")

    llm_response =ask_llm(exploring_atomic_facts_prompt)

    notebook, rationale_next_action, chosen_action = extract_notebook_rationale_next_steps_chosen_action(llm_response)

    call_function(chosen_action)


def read_chunk (chunk_id: str):
    # if the agent identifies certain chunks as valuable for further reading,
    # it will complete the function parameters with the chunk IDs,
    # i.e., read_chunk(List[ID]), and append these IDs to a chunk queue
    global notebook

    chunk_queue.append(chunk_id)
    print(f"CHUNK QUEUE: {chunk_queue}")
    print(f"CHUNK_ID: {chunk_id}")
    print(f"EXPLORING CHUNK: {chunk_id}\n")
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

    previous_actions.append(f"Exploring Chunk: {chunk_id}")

    llm_response =ask_llm(exploring_chunks_prompt)

    notebook, rationale_next_action, chosen_action = extract_notebook_rationale_next_steps_chosen_action(llm_response)

    chunk_queue.remove(chunk_id)

    # call_function(chosen_action, current_chunk_id=chunk_id)
    call_function(chosen_action)


def read_previous_chunk(chunk_id: str):
    # due to truncation issues, adjacent chunks might contain relevant
    # and useful information, the agent may insert these IDs to the queue;

    # Temp Logic to get the previous_chunk_id
    import collections
    sorted_chunks = collections.OrderedDict(sorted(corpus_map.items()))
    sorted_chunks_ids = [chunk_id for chunk_id in sorted_chunks.keys()]
    previous_chunk_index = sorted_chunks_ids.index(chunk_id) - 1

    if previous_chunk_index < 0:
        print("There is no previous chunk, so re-reading the current chunk...\n")
        # TODO: What to do when there is no previous chunk
        # For now we will re-read the chunk
        previous_chunk_index = 0

    previous_chunk_id =  sorted_chunks_ids[previous_chunk_index]

    print(f"CURRENT CHUNK ID: {chunk_id}")
    print(f"PREVIOUS CHUNK ID: {previous_chunk_id}")

    previous_actions.append(f"Reading Previous Chunk of {chunk_id}: Previous Chunk - {previous_chunk_id}")

    chosen_action = f'read_chunk(["{previous_chunk_id}]")'
    call_function(chosen_action)


def read_subsequent_chunk(chunk_id: str):
    # due to truncation issues, adjacent chunks might contain relevant
    # and useful information, the agent may insert these IDs to the queue;

    # Temp Logic to get the previous_chunk_id
    import collections
    sorted_chunks = collections.OrderedDict(sorted(corpus_map.items()))
    sorted_chunks_ids = [chunk_id for chunk_id in sorted_chunks.keys()]
    subsequent_chunk_index = sorted_chunks_ids.index(chunk_id) + 1

    if subsequent_chunk_index >= len(sorted_chunks_ids):
        print("There is no subsequent chunk, so re-reading the current chunk...\n")
        # TODO: What to do when there is no previous chunk
        # For now we will re-read the chunk
        subsequent_chunk_index = len(sorted_chunks_ids) - 1

    subsequent_chunk_id =  sorted_chunks_ids[subsequent_chunk_index]

    print(f"CURRENT CHUNK ID: {chunk_id}")
    print(f"SUBSEQUENT CHUNK ID: {subsequent_chunk_id}")

    previous_actions.append(f"Reading Subsequent Chunk of {chunk_id}: Subsequent Chunk - {subsequent_chunk_id}")

    chosen_action = f'read_chunk(["{subsequent_chunk_id}]")'
    call_function(chosen_action)


def stop_and_read_neighbor():
    # conversely, if the agent deems that none of the chunks are worth
    # further reading, it will finish reading this node and proceed
    # to explore neighboring nodes.

    global current_node

    neighbouring_nodes = get_neighbouring_nodes(current_node)
    print(f"CURRENT NODE: {current_node}")
    print(f"NEIGHBOURING NODES: {json.dumps(neighbouring_nodes, indent=2)}")
    previous_actions.append(f"Exploring Neighbouring Nodes of Node: {current_node}")

    exploring_neighbours_prompt = EXPLORING_NEIGHBOURS_PROMPT
    exploring_neighbours_prompt = PromptTemplate.from_template(exploring_neighbours_prompt) \
                                .format(
                                    question=question,
                                    rational_plan=rational_plan,
                                    previous_actions=json.dumps(previous_actions, indent=2),
                                    notebook=notebook,
                                    neighbour_nodes=neighbouring_nodes,
                                    current_node=current_node
                                )

    llm_response =ask_llm(exploring_neighbours_prompt)

    _, rationale_next_steps, chosen_action = extract_notebook_rationale_next_steps_chosen_action(llm_response)

    if "termintaion" in chosen_action:
        pass
    else:
        pattern = r"\('([^']+)'\)"
        matches = re.findall(pattern, chosen_action)
        new_node = matches[0]
        current_node = new_node

    call_function(chosen_action)


def search_more():
    # if supporting fact is insufficient, the agent will continue
    # exploring chunks in the queue;
    if chunk_queue:
        pass
    else:
        print(f"The chunk queue is empty, so exploring the other nodes related to Node: '{current_node}' ...\n")
        previous_actions.append(f"Empty Chunk Queue, so exploring connected nodes to Node: '{current_node}'")
        stop_and_read_neighbor()

def read_neighbor_node():
    # the agent selects a neighboring node that might be helpful in
    # answering the question and re-enters the process of exploring
    # atomic facts and chunks;

    # The node is being set during stop_and_read_neighbor
    print(f"EXPLORING THE NEIGHBOUR NODE: {current_node}")
    explore_atomic_facts()


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


def get_neighbouring_nodes(node: str):
    neighbouring_nodes = []
    for chunk_id, chunk_content in corpus_map.items():
        for af_id, af in chunk_content["atomic_facts"].items():
            if node in af["nodes_labels"].values():
                neighbouring_nodes.extend([x for x in af["nodes_labels"].values() if x != node])

    return list(set(neighbouring_nodes))


def call_function(chosen_action: str, **kwargs):

    print_state(question, rational_plan, previous_actions, notebook, chunk_queue, current_node)

    print(f"CALL FUNCTION: {chosen_action}\n")

    if "explore_atomic_facts" in chosen_action:
        func = globals()["explore_atomic_facts"]
        func()

    if "read_chunk" in chosen_action:
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, chosen_action)
        parameters = matches[0]
        chunk_ids = parameters.replace('"','').strip()
        func = globals()["read_chunk"]
        func(chunk_ids)

    if "read_previous_chunk" in chosen_action:
        if "current_chunk_id" in kwargs:
            current_chunk_id = kwargs["current_chunk_id"]
            func = globals()["read_previous_chunk"]
            func(current_chunk_id)

    if "read_subsequent_chunk" in chosen_action:
        if "current_chunk_id" in kwargs:
            current_chunk_id = kwargs["current_chunk_id"]
            func = globals()["read_subsequent_chunk"]
            func(current_chunk_id)


    if "search_more" in chosen_action:
        func = globals()["search_more"]
        func()

    if "read_neighbor_node" in chosen_action:
        func = globals()["read_neighbor_node"]
        func()

def main():

    global current_node

    print(f"\nCORPUS: \n{'='*50}\n{corpus}\n")
    map_nodes_chunks_afs()

    print(f"\n\nEXPLORATION \n{'='*50}\n")

    # Initial Node and Score
    current_node, score = get_initial_nodes()[0]

    print(f"INITIAL NODE: {current_node}, Score: {score}\n")
    call_function("explore_atomic_facts()")
    # search_more()
    # current_node = "fourth studio album"
    # call_function("read_neighbor_node('fourth studio album')")
    # read_subsequent_chunk('C1')

    # print_state(question, rational_plan, previous_actions, notebook, chunk_queue, current_node)


if __name__ == '__main__':
    main()