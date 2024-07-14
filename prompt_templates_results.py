


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

def get_initial_nodes(corpus: str):
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

    result = """
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

    return result