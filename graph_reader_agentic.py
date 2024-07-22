import os
import json
from corpus2 import corpus_map_small, corpus
from prompt_templates_results import get_rational_plan
from prompt_templates_results import get_initial_nodes
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import END, StateGraph, START
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.agents import AgentExecutor, create_openai_tools_agent
import functools
import operator

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Graph Reader Agent - Small"

corpus_map = corpus_map_small
question = "What is the name of the castle in the city where the performer of Never Too Loud was formed?"
rational_plan = get_rational_plan()
previous_actions = []
notebook = ""
chunk_queue = []
node_queue = []

nodes_grouped_chunks_afs = {}

class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

########### TOOLS USED BY AGENT ##############

from langchain.tools import BaseTool, StructuredTool, Tool, tool
import random

def make_uppercase(text: str) -> str:
    return "what is magic"

explore_atomic_facts = StructuredTool.from_function(
    func=make_uppercase,
    name="make_uppercase",
    description="Takes an input and convert into uppercase.",)

tools = [explore_atomic_facts]

##############################################

def print_state():
    print("======================================")
    print("CURRENT STATE:")
    print("======================================")
    print(f"QUESTION: {question}\n")
    print("RATIONAL PLAN:")
    print(f"{rational_plan}\n")
    print("PREVIOUS ACTIONS:")
    print(json.dumps(previous_actions, indent=2))
    print("\nNOTEBOOK:")
    print(f"{notebook}\n")
    print("CHUNK QUEUE:")
    print(chunk_queue)
    print(f"\nNODE QUEUE: {node_queue}\n")
    print("======================================\n")

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
    executor = AgentExecutor(agent=agent, tools=tools, return_intermediate_steps=True, verbose=True)
    return executor

def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}


def main():

    # print(f"\nCORPUS: \n{'='*50}\n{corpus}\n")
    # map_nodes_chunks_afs()

    # print(f"\n\nEXPLORATION \n{'='*50}\n")

    # # Initial Node and Score
    # current_node, score = get_initial_nodes()[0]
    # node_queue.append(current_node)
    # print_state()



    ##################################################################################

    members = ["UpperCaseMaker"]

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

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

    supervisor_chain = (
        prompt
        | llm.bind_functions(functions=[function_def], function_call="route")
        | JsonOutputFunctionsParser()
    )

    # Create Agents
    uppercase_agent = create_agent(llm, tools, "You are a language analyzer.")
    uppercase_node = functools.partial(agent_node, agent=uppercase_agent, name="UpperCaseMaker")

    workflow = StateGraph(AgentState)
    workflow.add_node("UpperCaseMaker", uppercase_node)
    workflow.add_node("supervisor", supervisor_chain)

    for member in members:
        # We want our workers to ALWAYS "report back" to the supervisor when done
        workflow.add_edge(member, "supervisor")
    # The supervisor populates the "next" field in the graph state
    # which routes to a node or finishes
    conditional_map = {k: k for k in members}
    conditional_map["FINISH"] = END
    workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
    # Finally, add entrypoint
    workflow.add_edge(START, "supervisor")

    graph = workflow.compile()



    for s in graph.stream(
        {"messages": [HumanMessage(content="make the text 'its magic' in capital letters")]},
        {"recursion_limit": 5},debug=True
    ):
        if "__end__" not in s:
            print(s)
            print("----")

    # print(f"INITIAL NODE: {current_node}, Score: {score}\n")
    # call_function("explore_atomic_facts()")
    # # search_more()
    # # current_node = "fourth studio album"
    # # call_function("read_neighbor_node('fourth studio album')")
    # # read_subsequent_chunk('C1')

    # # print_state(question, rational_plan, previous_actions, notebook, chunk_queue, current_node)


if __name__ == '__main__':
    main()