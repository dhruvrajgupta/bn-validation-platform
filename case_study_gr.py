from utils import cluster_key_elements, get_maximum_substring

question_text = "Question What is the name of the castle in the city where the performer of Never Too Loud was formed?"
answer = "Casa Loma"

supoorting_passages = [
    "Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. It was recorded at Studio 606 in Los Angeles, with the producer Nick Raskulinecz.",
    "Danko Jones is a Canadian hard rock trio from Toronto. The band consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums). The band’s music includes elements of hard rock and punk and they are known for their energetic live shows.",
    "Casa Loma (improper Spanish for 'Hill House') is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada, that is now a historic house museum and landmark. It was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt. The architect was E. J. Lennox, who designed several other city landmarks."
]

###########################################################
##              GRAPH CONSTRUCTION                       ##
###########################################################

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

gc_prompt_result = """
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

gc_prompt_result = """
    1. Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. | Never Too Loud | fourth studio album | Canadian hard rock band | Danko Jones
    4. Danko Jones is a Canadian hard rock trio from Toronto. | Danko Jones | Canadian | hard rock trio | Toronto
    8. Casa Loma is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada. | Casa Loma | Gothic Revival | castle-style mansion | garden | midtown Toronto | Ontario | Canada
    """

###
# Extract atomic facts and key elements
###
def extract_atomic_facts_key_elements():
    """
    Extracts atomic facts and their key elements from a given prompt result list.
    Returns a dictionary with atomic facts mapped to their key elements.
    """

    """
    {
        11: {
            "atomic_fact": "The architect of Casa Loma was E. J. Lennox.",
            "key_elements": ["architect", "Casa Loma", "E. J. Lennox"]
        }
    }
    """
    gc_construct_map = {}

    gc_prompt_result_list = [x.strip() for x in gc_prompt_result.splitlines()]
    for id_af_and_ke in gc_prompt_result_list:
        if not len(id_af_and_ke):
            continue

        id = id_af_and_ke.split(".")[0].strip()
        af_ke = ".".join(id_af_and_ke.split(".")[1:]).strip()
        atomic_fact = af_ke.split("|")[0].strip()
        key_elements = [x.strip() for x in af_ke.split("|")[1:]]
        gc_construct_map[id] = {
            "atomic_fact": atomic_fact,
            "key_elements": key_elements
        }

    return gc_construct_map

def list_all_key_elements():
    list_of_key_elements = []
    for _, atomic_facts_key_elements in gc_construct_map.items():
        list_of_key_elements.extend(atomic_facts_key_elements["key_elements"])
    
    return list_of_key_elements

def distinct_node_from_list(list_of_key_elements, list_of_distinct_nodes):

    # Processed all the elements in the original list
    if not list_of_key_elements: return list_of_distinct_nodes
    
    # Get the longest common substring
    max_substring = ""
    max_length = 0
    for a in list_of_key_elements:
        for b in list_of_key_elements:
            if a == b:
                continue

            current_substring = get_maximum_substring(a,b)
            if len(current_substring) > max_length:
                max_substring = current_substring
                max_length = len(current_substring)

    # print(max_substring, max_length)
    # Extract all the key elements that have the longest common substring
    elements_with_max_substring = []
    max_substring = max_substring.strip()
    for element in list_of_key_elements:
        if max_substring in element:
            # print(element)
            elements_with_max_substring.append(element)
            # Element removal here does not adhere to the logic
            # list_of_key_elements.remove(element)
    # print(elements_with_max_substring)

    # Remove all the elements that have the longest common substring
    for element in elements_with_max_substring:
        if element in list_of_key_elements:
            list_of_key_elements.remove(element)

    key_element_max_substring = min(elements_with_max_substring, key=len)
    list_of_distinct_nodes.append({
        "key_element": key_element_max_substring,
        "max_substring": max_substring
        })

    # print(list_of_key_elements)

    return distinct_node_from_list(list_of_key_elements, list_of_distinct_nodes)

def extract_distinct_nodes(gc_construct_map):
    all_key_elements = list_all_key_elements()
    distinct_nodes = []

    clustered_key_elements = cluster_key_elements(all_key_elements)

    # Display the clusters
    for label, elements in clustered_key_elements.items():
        # print(f"Cluster {label}: {elements}")
        if label == -1:
            continue
        distinct_nodes.extend(distinct_node_from_list(elements, []))

    gc_construct_map["distinct_nodes_substring"] = distinct_nodes

    return gc_construct_map

if __name__ == "__main__":
    gc_construct_map = extract_atomic_facts_key_elements()
    gc_construct_map = extract_distinct_nodes(gc_construct_map)

    for id, gc_construct in gc_construct_map.items():
        if id == "distinct_nodes_substring":
            continue
        print(f"ID: {id}")
        print(f"Atomic Fact: {gc_construct['atomic_fact']}")
        print(f"Key Elements: {gc_construct['key_elements']}")
        print()
    
    print(f"Distinct Nodes: {gc_construct_map['distinct_nodes_substring']}")
