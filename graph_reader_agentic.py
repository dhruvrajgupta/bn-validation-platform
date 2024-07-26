import os
import json
from corpus2 import corpus_map_small, corpus
from prompt_templates_results import get_rational_plan
from prompt_templates_results import get_initial_nodes
from typing import TypedDict, Annotated, Sequence, List, Any
from langgraph.graph import END, StateGraph, START
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.agents import AgentExecutor, create_openai_tools_agent
import functools
import operator
from agent_template import EXPLORING_ATOMIC_FACTS_PROMPT, EXPLORING_CHUNKS_PROMPT, \
EXPLORING_NEIGHBOURS_PROMPT
from utils import extract_notebook_rationale_next_steps_chosen_action
import re

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Graph Reader Agent - Small"

corpus_map = corpus_map_small

gr_state = {
    "question": "What is the name of the castle in the city where the performer of Never Too Loud was formed?",
    "rational_plan": get_rational_plan(),
    "previous_actions": [],
    "notebook": "",
    "chunk_queue": [],
    "node_stack": []
}

nodes_grouped_chunks_afs = {}

def print_state():
    global state
    print("======================================")
    print("CURRENT STATE:")
    print("======================================")
    print(f"QUESTION: {gr_state['question']}\n")
    print("RATIONAL PLAN:")
    print(f"{gr_state['rational_plan']}\n")
    print("PREVIOUS ACTIONS:")
    print(json.dumps(gr_state['previous_actions'], indent=2))
    print("\nNOTEBOOK:")
    print(f"{gr_state['notebook']}\n")
    print("CHUNK QUEUE:")
    print(gr_state['chunk_queue'])
    print(f"\nNODE STACK: {gr_state['node_stack']}\n")
    print("======================================\n")

def get_state():
    global gr_state
    result = f"""======================================
CURRENT STATE:
======================================
QUESTION: {gr_state["question"]}

RATIONAL PLAN:
{gr_state["rational_plan"]}

PREVIOUS ACTIONS:
{gr_state["previous_actions"]}

NOTEBOOK:
{gr_state["notebook"]}

CHUNK QUEUE:
{gr_state["chunk_queue"]}

NODE STACK:
{gr_state["node_stack"]}
"""
    
    return result

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

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

class NotebookRationaleChosenAction(BaseModel):
    notebook: str = Field(description="value of the *Updated Notebook*")
    rationale: str = Field(description="value of the *Rationale for Next Action*")
    chosen_action: str = Field(description="value of the *Chosen Action*")
    # setup: str = Field(description="question to set up a joke")
    # punchline: str = Field(description="answer to resolve the joke")

class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Sequence[BaseMessage]
    # The 'next' field indicates where to route to next
    next: str

########### TOOLS USED BY AGENT ##############

from langchain.tools import BaseTool, StructuredTool, Tool, tool
import random

def calculate_two_plus_two() -> None:
    pass

calculate_two_plus_two = StructuredTool.from_function(
    func=calculate_two_plus_two,
    name="calculate_two_plus_two",
    description="Calculate two plus two",)

tools = [calculate_two_plus_two]

##############################################


def preprocess_explore_atomic_facts():
    current_node = gr_state["node_stack"][-1]
    node_content = nodes_grouped_chunks_afs[current_node]

    more_info = f"""Current Node:
{current_node}

Current Node Chunks and Atomic Facts are of the following format:
"CHUNK_ID#": [{{
"ATOMIC_FACT_ID#": "ATOMIC_FACT_TEXT"}},
....
],
....

Current Node Chunks and Atomic Facts:
{json.dumps(node_content, indent=2)}
"""
    gr_state["previous_actions"].append(f"Exploring Atomic Facts of Node: {current_node}")

    return more_info

def preprocess_read_chunks():
    global gr_state
    current_chunk_id = gr_state["chunk_queue"].pop(0)
    # print(current_chunk_id)
    chunk_content = corpus_map[current_chunk_id]["text"]
    # print(chunk_content)
    more_info = f"""Question:
{gr_state["question"]}

Rational Plan:
{gr_state["rational_plan"]}

Previous Actions:
{gr_state["previous_actions"]}

Notebook:
{gr_state["notebook"]}

Current Text Chunk:
{chunk_content}"""
    
    gr_state["previous_actions"].append(f"Exploring Chunk: {current_chunk_id}")

    return more_info

def get_neighbouring_nodes(node: str):
    neighbouring_nodes = []
    for chunk_id, chunk_content in corpus_map.items():
        for af_id, af in chunk_content["atomic_facts"].items():
            if node in af["nodes_labels"].values():
                neighbouring_nodes.extend([x for x in af["nodes_labels"].values() if x != node])

    return list(set(neighbouring_nodes))

def preprocess_explore_neighbours():
    global gr_state
    current_node = gr_state["node_stack"][-1]
    neighbour_nodes = get_neighbouring_nodes(current_node)
    more_info = f"""Question:
{gr_state["question"]}

Rational Plan:
{gr_state["rational_plan"]}

Previous Actions:
{gr_state["previous_actions"]}

Notebook:
{gr_state["notebook"]}

Neighbours of Current Node:
{neighbour_nodes}
"""
    gr_state["previous_actions"].append(f"Exploring Neighbouring Nodes of Node: {current_node}")

    return more_info

def process_state(result):
    import re
    global gr_state
    print(result["messages"])
    rational_plan_pattern = r"RATIONAL PLAN:\n(.*?)\n\nPREVIOUS ACTIONS:"
    gr_state["rational_plan"] = re.search(rational_plan_pattern, result["messages"], re.DOTALL).group(1).strip()
    previous_actions_pattern = r"PREVIOUS ACTIONS:\n(.*?)\n\nNOTEBOOK:"
    gr_state["previous_actions"] = re.search(previous_actions_pattern, result["messages"], re.DOTALL).group(1).strip()
    notebook_pattern = r"NOTEBOOK:\n(.*?)\n\nCHUNK QUEUE:"
    gr_state["notebook"] = re.search(notebook_pattern, result["messages"], re.DOTALL).group(1).strip()
    chunk_queue_pattern = r"CHUNK QUEUE:\n(.*?)\n\nNODE STACK:"
    gr_state["chunk_queue"] = re.search(chunk_queue_pattern, result["messages"], re.DOTALL).group(1).strip()
    node_stack_pattern = r"NODE STACK:\n(.*?)\n"
    gr_state["node_stack"] = re.search(node_stack_pattern, result["messages"], re.DOTALL).group(1).strip()

    return gr_state


def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    # Each worker node will be given a name and some tools.
    # agent_scratchpad should be a sequence of messages that contains the 
    # previous agent tool invocations and the corresponding tool outputs.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, return_intermediate_steps=False, verbose=True)
    return executor

def agent_node(agent_state, agent, name):
    global gr_state
    print(json.dumps(gr_state, indent=4))
    if name == "ExploreAtomicFacts":
        more_info = preprocess_explore_atomic_facts()
        agent_state["messages"] = [HumanMessage(content=more_info)]

    if name == "ExploreChunks":
        more_info = preprocess_read_chunks()
        agent_state["messages"] = [HumanMessage(content=more_info)]

    if name == "SearchMore":
        if gr_state["chunk_queue"]:
            # Read the next chunk in the queue
            return {"messages": [HumanMessage("Explore Chunks in the Chunk Queue")]}
        else:
            current_node = gr_state["node_stack"][-1]
            # print(f"The chunk queue is empty, so exploring the other nodes related to Node: '{current_node}' ...\n")
            gr_state["previous_actions"].append(f"Empty Chunk Queue, so exploring connected nodes to Node: '{current_node}'")
            return {"messages": 
                [
                    HumanMessage(content=f"The chunk queue is empty, so exploring the other nodes related to Node: '{current_node}' ...\n"),
                    HumanMessage(content=f"Stop and Read Neighbour Nodes")
                ]
            }
    
    if name == "ExploreNeighbours":
        more_info = preprocess_explore_neighbours()
        agent_state["messages"] = [HumanMessage(content=more_info)]

    result = agent.invoke(agent_state)

    notebook, rationale_next_step, chosen_action = extract_notebook_rationale_next_steps_chosen_action(result["output"])
    
    # Extract the chunklist from chosen_action
    if "read_chunk" in chosen_action:
        pattern = r"read_chunk\((.*?)\)"
        matches = re.findall(pattern, chosen_action)
        chunk_ids = json.loads(matches[0])
        gr_state["chunk_queue"].extend(chunk_ids)

    if "read_neighbor_node" in chosen_action:
        pattern = r"read_neighbor_node\((.*?)\)"
        matches = re.findall(pattern, chosen_action)
        node_id = matches[0].strip("'")
        print(node_id)
        gr_state["node_stack"].append(node_id)
        current_node = gr_state["node_stack"][-1]
        return {"messages": 
            [
                HumanMessage(content=f"Explore the Atomic Facts related to Node: '{current_node}' ...\n"),
            ]
        }
    
    if notebook:
        gr_state["notebook"] = notebook
    gr_state["rationale_next_step"]= rationale_next_step
    gr_state["chosen_action"] = chosen_action
    # print("-"*50)
    print(json.dumps(gr_state, indent=4))
    # print(result)
    # print(agent_state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}

def create_supervisor(members: List[str], llm: ChatOpenAI):
    # Creating the Supervisor which handles the routing
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        " following workers:  {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
    )
    # Our team supervisor is an LLM node. It just picks the next agent to process
    # and decides when the work is completed
    options = ["FINISH"] + members
    # Using openai function calling can make output parsing easier for us
    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                }
            },
            "required": ["next"],
        },
    }
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next?"
                " Or should we FINISH? Select one of: {options}",
            ),
        ]
    ).partial(options=str(options), members=", ".join(members))

    supervisor_chain = (
        prompt
        | llm.bind_functions(functions=[function_def], function_call="route")
        # | process_messages
        | JsonOutputFunctionsParser()
    )
    return supervisor_chain

def main():
    global gr_state

    print(f"\nCORPUS: \n{'='*50}\n{corpus}\n")
    map_nodes_chunks_afs()

    print(f"\n\nEXPLORATION \n{'='*50}\n")

    # Initial Node and Score
    current_node, score = get_initial_nodes()[0]
    gr_state["node_stack"].append(current_node)
    print_state()



    ##################################################################################

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
    # from langchain_groq import ChatGroq
    # llm = ChatGroq(model="llama3-groq-8b-8192-tool-use-preview")

    members = ["ExploreAtomicFacts", "ExploreChunks", "SearchMore", "ExploreNeighbours"]

    # Create Agents
    # nodes_analyzer_agent = create_agent(llm, tools, "You are an expert in analyzing list of nodes.")
    # nodes_analyzer_node = functools.partial(agent_node, agent=nodes_analyzer_agent, name="NodesAnalyzer")
    explore_atomic_facts_agent = create_agent(llm, tools, EXPLORING_ATOMIC_FACTS_PROMPT)
    explore_atomic_facts_node = functools.partial(agent_node, agent=explore_atomic_facts_agent, name="ExploreAtomicFacts")

    exploring_chunk_agent = create_agent(llm, tools, EXPLORING_CHUNKS_PROMPT)
    exploring_chunk_node = functools.partial(agent_node, agent=exploring_chunk_agent, name="ExploreChunks")

    search_more_agent = create_agent(llm, tools, "If Chosen Action is search_more() then this agent is executed")
    search_more_agent_node = functools.partial(agent_node, agent=search_more_agent, name="SearchMore")

    exploring_neighbours_agent = create_agent(llm, tools, EXPLORING_NEIGHBOURS_PROMPT)
    exploring_neighbours_node = functools.partial(agent_node, agent=exploring_neighbours_agent, name="ExploreNeighbours")

    #### Create the Workflow Graph ####

    workflow = StateGraph(AgentState)
    workflow.add_node("ExploreAtomicFacts", explore_atomic_facts_node)
    workflow.add_node("ExploreChunks", exploring_chunk_node)
    workflow.add_node("SearchMore", search_more_agent_node)
    workflow.add_node("ExploreNeighbours", exploring_neighbours_node)
    workflow.add_node("supervisor", create_supervisor(members,llm))

    for member in members:
        # We want our workers to ALWAYS "report back" to the supervisor when done
        workflow.add_edge(member, "supervisor")
    # The supervisor populates the "next" field in the graph gr_state
    # which routes to a node or finishes
    conditional_map = {k: k for k in members}
    conditional_map["FINISH"] = END
    workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
    # Finally, add entrypoint
    workflow.add_edge(START, "supervisor")

    graph = workflow.compile()



    for s in graph.stream(
        {
            "messages": [
            HumanMessage(content=get_state()),
            ]
        },
        {"recursion_limit": 30},debug=True
    ):
        if "__end__" not in s:
            # print("========")
            # # print(s)
            # print("========")
            print("="*100)
            pass

    # print(f"INITIAL NODE: {current_node}, Score: {score}\n")
    # call_function("explore_atomic_facts()")
    # # search_more()
    # # current_node = "fourth studio album"
    # # call_function("read_neighbor_node('fourth studio album')")
    # # read_subsequent_chunk('C1')

    # # print_state(question, rational_plan, previous_actions, notebook, chunk_queue, current_node)


if __name__ == '__main__':
    main()