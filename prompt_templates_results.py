import json

def get_corpus():
    supoorting_passages = [
        "Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. It was recorded at Studio 606 in Los Angeles, with the producer Nick Raskulinecz.",
        "Danko Jones is a Canadian hard rock trio from Toronto. The band consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums). The band’s music includes elements of hard rock and punk and they are known for their energetic live shows.",
        "Casa Loma (improper Spanish for 'Hill House') is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada, that is now a historic house museum and landmark. It was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt. The architect was E. J. Lennox, who designed several other city landmarks."
    ]

    return supoorting_passages

def get_atomic_facts_and_key_elements(corpus: str):
    # CORPUS to ATOMIC FACTS AND KEY ELEMENTS
    gc_prompt = """
        You are now an intelligent assistant tasked with meticulously extracting both key elements and 
        atomic facts from a long text.
        1. Key Elements: The essential nouns (e.g., characters, times, events, places, numbers), verbs (e.g., 
        actions), and adjectives (e.g., states, feelings) that are pivotal to the text’s narrative.
        2. Atomic Facts: The smallest, indivisible facts, presented as concise sentences. These include 
        propositions, theories, existences, concepts, and implicit elements like logic, causality, event 
        sequences, interpersonal relationships, timelines, etc.

        Requirements: 
        #####
        1. Ensure that all identified key elements are reflected within the corresponding atomic facts. 
        2. You should extract key elements and atomic facts comprehensively, especially those that are 
        important and potentially query-worthy and do not leave out details. 
        3. Whenever applicable, replace pronouns with their specific noun counterparts (e.g., change I, He, 
        She to actual names). 
        4. Ensure that the key elements and atomic facts you extract are presented in the same language as 
        the original text (e.g., English or Chinese). 
        5. You should output a total of key elements and atomic facts that do not exceed 1024 tokens. 
        6. Your answer format for each line should be: [Serial Number], [Atomic Facts], [List of Key 
        Elements, separated with ‘|’]
        #####

        Example: 
        ##### 
        User: One day, a father and his little son ...... 
        
        Assistant: 
        1. One day, a father and his little son were going home. | father | little son | going home 
        2. ...... 
        ##### 
        
        Please strictly follow the above format. Let’s begin.
    """

    result = """
        1. Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. | Never Too Loud | fourth studio album | Canadian hard rock band | Danko Jones
        2. Never Too Loud was recorded at Studio 606 in Los Angeles. | Never Too Loud | recorded | Studio 606 | Los Angeles
        3. Nick Raskulinecz was the producer of Never Too Loud. | Nick Raskulinecz | producer | Never Too Loud
        4. Danko Jones is a Canadian hard rock trio from Toronto. | Danko Jones | Canadian | hard rock trio | Toronto
        5. The band Danko Jones consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums). | Danko Jones | Danko Jones (vocals/guitar) | John 'JC' Calabrese (bass) | Rich Knox (drums)
        6. Danko Jones' music includes elements of hard rock and punk. | Danko Jones | music | elements | hard rock | punk
        7. Danko Jones is known for their energetic live shows. | Danko Jones | known | energetic live shows
        8. Casa Loma is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada. | Casa Loma | Gothic Revival | castle-style mansion | garden | midtown Toronto | Ontario | Canada
        9. Casa Loma is now a historic house museum and landmark. | Casa Loma | historic house museum | landmark
        10. Casa Loma was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt. | Casa Loma | constructed | 1911 | 1914 | residence | financier | Sir Henry Pellatt
        11. The architect of Casa Loma was E. J. Lennox. | architect | Casa Loma | E. J. Lennox
        12. E. J. Lennox designed several other city landmarks. | E. J. Lennox | designed | several other city landmarks
    """

    result = """
        1. Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. | Never Too Loud | fourth studio album | Canadian hard rock band | Danko Jones
        4. Danko Jones is a Canadian hard rock trio from Toronto. | Danko Jones | Canadian | hard rock trio | Toronto
        8. Casa Loma is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada. | Casa Loma | Gothic Revival | castle-style mansion | garden | midtown Toronto | Ontario | Canada
    """

    return result


def get_rational_plan(corpus: str):
    # In Order to get the proper Rational Plan, LLM should not have any idea of the article.
    rational_plan_prompt = """
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

    result = """
        In order to answer this question, we first need to identify the following key pieces of information:

        1. The performer of the song "Never Too Loud."
        2. The city where this performer was formed.
        3. The name of the castle in that city.
        We will then gather the necessary details to provide a comprehensive answer.
    """

    return result

def get_initial_nodes():
    initial_node_selection_prompt = """
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
        Question: {QUESTION} 
        Plan: {RATIONAL PLAN} 
        Nodes: {LIST OF KEY ELEMENTS} 
        
        Assistant:{LIST OF SELECTED NODES} 
        ##### 
        
        Finally, I emphasize again that you need to select the starting node from the given Nodes, and 
        it must be consistent with the words of the node you selected. Please strictly follow the above 
        format. Let’s begin.
    """

    im_result = """
        Node: 'Never Too Loud', Score: 100
        Node: 'Danko Jones', Score: 100
        Node: 'Canadian hard rock band', Score: 90
        Node: 'Toronto', Score: 90
        Node: 'Casa Loma', Score: 80
        Node: 'castle-style mansion', Score: 70
        Node: 'midtown Toronto', Score: 70
        Node: 'Canadian', Score: 60
        Node: 'Ontario', Score: 60
        Node: 'Canada', Score: 50
    """

    result = []

    im_result = [x.strip() for x in im_result.splitlines()]
    for x in im_result:
        if x == '':
            continue

        x = x.split(",")
        node = x[0].split(":")[1].strip().replace("'","")
        score = int(x[1].split(":")[1].strip())
        result.append((node, score))

    return result


def exploring_atomic_facts_prompt(question, rational_plan, previous_actions, notebook, current_node, node_content):
    from prompt_templates import EXPLORING_ATOMIC_FACTS_PROMPT
    exploring_atomic_facts_prompt = EXPLORING_ATOMIC_FACTS_PROMPT

    from langchain_core.prompts import PromptTemplate

    exploring_atomic_facts_prompt = PromptTemplate.from_template(exploring_atomic_facts_prompt) \
                                        .format(
                                            question=question,
                                            rational_plan=rational_plan,
                                            previous_actions=previous_actions,
                                            notebook=notebook,
                                            current_node=current_node,
                                            node_content=json.dumps(node_content, indent=2)
                                        )


    print(exploring_atomic_facts_prompt)

    results = {
        "Never Too Loud": """
Updated Notebook:

Notebook:

Performer of "Never Too Loud":
Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. (Source: AF1, Chunk C1)
Rationale for Next Action:

The atomic fact we have indicates that "Never Too Loud" is an album by the band Danko Jones. This partially answers the first part of our rational plan. We need more information on the city where this band was formed and the name of the castle in that city. Therefore, it is crucial to explore more text chunks to gather the remaining details.

Chosen Action: read_chunk(["C1"])

""",
    }

    if current_node in results:
        return results[current_node]
    else:
        return "Result Not Found!!!"

def exploring_chunks_prompt():
    exploring_chunks_prompt = """
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
    """


def exploring_neighbors_prompt():
    exploring_neighbors_prompt = """
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
    """


def answer_reasoning_prompt():
    answer_reasoning_prompt = """
    As an intelligent assistant, your primary objective is to answer questions based on information
    within a text. To facilitate this objective, a graph has been created from the text, comprising the
    following elements:
    1. Text Chunks: Segments of the original text.
    2. Atomic Facts: Smallest, indivisible truths extracted from text chunks.
    3. Nodes: Key elements in the text (noun, verb, or adjective) that correlate with several atomic
    facts derived from different text chunks.

    You have now explored multiple paths from various starting nodes on this graph,
    recording key information for each path in a notebook.
    Your task now is to analyze these memories and reason to answer the question.

    Strategy:
    #####
    1. You should first analyze each notebook content before providing a final answer.
    2. During the analysis, consider complementary information from other notes and employ a
    majority voting strategy to resolve any inconsistencies.
    3. When generating the final answer, ensure that you take into account all available information.
    #####

    Example:
    #####
    User: 
    Question: Who had a longer tennis career, Danny or Alice?
    Notebook of different exploration paths:
    1. We only know that Danny’s tennis career started in 1972 and ended in 1990, but we don’t know
    the length of Alice’s career.
    2. ......

    Assistant:
    Analyze:
    The summary of search path 1 points out that Danny’s tennis career is 1990-1972=18 years.
    Although it does not indicate the length of Alice’s career, the summary of search path 2 finds this
    information, that is, the length of Alice’s tennis career is 15 years. Then we can get the final
    answer, that is, Danny’s tennis career is longer than Alice’s.
    Final answer:
    Danny’s tennis career is longer than Alice’s.
    #####

    Please strictly follow the above format. Let’s begin.
    """


def llm_rating_one_prompt():
    llm_rating_one_prompt = """
        After reading some text, John was given the following question about the text: 
        {QUESTION TEXT} 
        John’s answer to the question was: 
        {MODEL RESPONSE TEXT} 
        The ground truth answer was: 
        {REFERENCE RESPONSE TEXT} 
        Does John’s answer agree with the ground truth answer? 
        Please answer "Yes" or "No".
    """

def llm_rating_two_prompt():
    llm_rating_two_prompt = """
        After reading some text, John was given the following question about the text: 
        {QUESTION TEXT} 
        John’s answer to the question was: 
        {MODEL RESPONSE TEXT} 
        The ground truth answer was: 
        {REFERENCE RESPONSE TEXT} 
        
        Does John’s answer agree with the ground truth answer? 
        Please answer “Yes”, “Yes, partially”, or “No”. If John’s response has any overlap with the ground 
        truth answer, answer “Yes, partially”. If John’s response contains the ground truth answer, answer 
        “Yes”. If John’s response is more specific than the ground truth answer, answer “Yes”.
    """


def full_text_read_prompt():
    full_text_read_prompt = """
        Please read the passage below and answer the question based on the passage. 
        Passage: 
        {PASSAGE TEXT} 
        Question: 
        {QUESTION TEXT} 

        Now please answer this question based on the passage content.
    """


def chunk_read_prompt():
    chunk_read_prompt = """
        Please read the text chunks below and answer the question. 
        Text chunks: 
        {CHUNKED PASSAGE TEXT} 
        Question: 
        {QUESTION TEXT} 
        
        If you think you can answer the question based on the above text chunks please output 
        [answerable] and then output your answer. 
        Otherwise, if there is not enough information to answer the question, please output: 
        [unanswerable]
    """


def chunk_read_note_prompt():
    chunk_read_note_prompt = """
        Please read the text chunk below and answer the questions based on your previous summary. 
        Text chunk: 
        {CHUNKED PASSAGE TEXT} 
        Your previous summary: 
        {SUMMARY TEXT} 
        Question: 
        {QUESTION TEXT} 
        
        If the above text chunk has information that can help answer the question, please extract 
        the effective information, output [summary], and then output the refined information. Please note 
        that it must be brief. 
        If you can answer the question based on the above information, please output [answerable] and 
        then output your answer. 
        Otherwise, if there is insufficient information to answer the question, please output [unanswerable].
    """


def rag_prompt():
    rag_prompt = """
        Please read the text chunk below and answer the question. 
        Text chunks: 
        {RETRIEVED PASSAGE TEXT} 
        Question: 
        {QUESTION TEXT} 
        
        Now please answer this question based on the text chunks.
    """


def evaluate_recall_prompt():
    evaluate_recall_prompt = """
        Now you are an intelligent assistant. Given a text, a question, and x supporting facts that can
        answer the question, please determine how many supporting facts the text covers.

        Requirements:
        #####
        1. It’s possible that not all supporting facts are needed to answer the question, so you’ll need to
        analyze the supporting facts to determine which supporting facts are actually needed, and then
        determine whether those supporting facts are covered. Supporting facts that are not really needed
        are discarded, and you do not need to judge whether they are covered. So the number of real
        supporting facts is t (0 < t <= x).
        2. A supporting fact has some valid information that helps answer the question. When the text
        provides this part of the valid information, it is considered to have covered the supporting fact,
        even if the text does not provide all the information supporting the fact.
        3. The number of covered items in your output should be between 0 and t (including 0 and t).
        4. Please analyze and reason first, and then output the final result.
        #####

        Example:
        #####
        {EXAMPLE}
        #####

        Please note that you should follow: 0 <= Number of recalls <= True number of
        supporting facts <= Number of supporting facts.
        Please output according to the example format. Now let’s start.
    """