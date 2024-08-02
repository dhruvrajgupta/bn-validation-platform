from graphreader.utils import cluster_key_elements, get_maximum_substring, \
    similarity, get_item_with_max_score
import json
from prompt_templates_results import get_atomic_facts_and_key_elements

question_text = "What is the name of the castle in the city where the performer of Never Too Loud was formed?"
answer = "Casa Loma"

supoorting_passages = [
    "Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. It was recorded at Studio 606 in Los Angeles, with the producer Nick Raskulinecz.",
    "Danko Jones is a Canadian hard rock trio from Toronto. The band consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums). The band’s music includes elements of hard rock and punk and they are known for their energetic live shows.",
    "Casa Loma (improper Spanish for 'Hill House') is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada, that is now a historic house museum and landmark. It was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt. The architect was E. J. Lennox, who designed several other city landmarks."
]

supoorting_passages = [
    "Type 2 diabetes is characterized by high blood sugar levels due to the body's inability to use insulin effectively. When blood sugar levels remain elevated over time, it can lead to damage of the blood vessels and nerves.",
    "The mechanism by which high blood sugar levels cause cardiovascular disease involves the process of atherosclerosis. High glucose levels damage the inner lining of the blood vessels, leading to inflammation and the buildup of fatty deposits (plaques) on the artery walls. This condition, known as atherosclerosis, narrows and hardens the arteries, increasing the risk of heart attack and stroke.",
    "Lifestyle changes that can mitigate the risk of cardiovascular disease in individuals with type 2 diabetes include adopting a balanced diet rich in fruits, vegetables, whole grains, and lean proteins, engaging in regular physical activity, quitting smoking, and managing stress. Additionally, maintaining a healthy weight and monitoring blood sugar, blood pressure, and cholesterol levels are crucial."
]

###########################################################
##              GRAPH CONSTRUCTION                       ##
###########################################################

gc_prompt_result = get_atomic_facts_and_key_elements(supoorting_passages)

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

    if max_substring == "":
        list_of_distinct_nodes.append(key_element_max_substring)
    else:
        list_of_distinct_nodes.append({
            "key_element": key_element_max_substring,
            "max_substring": max_substring
        })

    # print(list_of_key_elements)

    return distinct_node_from_list(list_of_key_elements, list_of_distinct_nodes)

def extract_distinct_nodes(gc_construct_map):
    all_key_elements = list_all_key_elements()
    print(f"\n List of all key elements: \n{set(all_key_elements)}")
    
    distinct_nodes = []

    clustered_key_elements = cluster_key_elements(all_key_elements)

    print("\nClustering all nodes semantically:")
    print("-"*50+"\n")
    # Display the clusters
    for label, elements in clustered_key_elements.items():
        print(f"Cluster {label}: {elements}")

    # Extracting distinct nodes within aggregated cluster
    print("\n\nExtracting distinct nodes within cluster...")
    print("-"*50+"\n")
    for label, elements in clustered_key_elements.items():
        print(f"Cluster {label}: {elements}")
        if label == -1:
            print(f"Skipping [Cluster -1] as they are alldistinct within the cluster...\n")
            continue
        
        elements = list(set(elements))
        if len(elements) > 1:
            cluster_distinct_nodes = distinct_node_from_list(elements, [])
        else:
            cluster_distinct_nodes = elements
        print(f"{json.dumps(cluster_distinct_nodes, indent=2)}\n")

        # Only append distinct nodes with substring mapping
        for node in cluster_distinct_nodes:
            if type(node) is not dict:
                continue
            distinct_nodes.append(node)

    gc_construct_map["distinct_nodes_substring"] = distinct_nodes

    return gc_construct_map

def map_key_elements_to_distinct_nodes(gc_construct_map):
    """
    Node mapping and their relative strengths
    {
        11: {
            "atomic_fact": "The architect of Casa Loma was E. J. Lennox.",
            "key_elements": ["architect", "Casa Loma", "E. J. Lennox"],
            "nodes": {
                "architect": [{"arch": 0.3}, {"architectural": 1.3}],
                "Casa Loma": "Casa Loma"
                ...
                }
        }
    }
    """
    # Make nodes dictionary for all atomic facts
    for id, gc_construct in gc_construct_map.items():
        if id == "distinct_nodes_substring":
            continue
        gc_construct_map[id]["nodes"] = {}
    
    distinct_nodes_substring_list = gc_construct_map["distinct_nodes_substring"]

    for distinct_node_substring in distinct_nodes_substring_list:
        max_substring = distinct_node_substring["max_substring"]
        distinct_node_id = distinct_node_substring["key_element"]

        if similarity(max_substring, distinct_node_id) < 0.4: 
            continue

        if len(max_substring)/len(distinct_node_id) < 0.4:
            # designed, ed similarity = 0.4 so lengtth check
            continue

        if max_substring.isdigit():
            continue

        print(f"\nMapping key elements having [\"{max_substring}\"] to [\"{distinct_node_id}\"]...")
        print("-"*50)

        for id, gc_construct in gc_construct_map.items():
            if id == "distinct_nodes_substring":
                continue
            print(f"ID: {id}")
            print(f"Atomic Fact: {gc_construct['atomic_fact']}")
            print(f"Key Elements: {gc_construct['key_elements']}")

            nodes = gc_construct["nodes"]

            for element in gc_construct['key_elements']:
                if max_substring in element and not element.isdigit():
                    if element in nodes:
                        nodes[element].append({max_substring: similarity(element, max_substring)})
                    else:
                        nodes[element] = [{max_substring: similarity(element, max_substring)}]

            print(f"Nodes: {gc_construct_map[id]['nodes']}\n")

        print(f"{'-'*50}\n")

    # Mapping remaining key elements to distinct nodes
    print(f"Mapping remaining key elements...\n{'-'*50}")
    for id, gc_construct in gc_construct_map.items():
        if id == "distinct_nodes_substring":
                continue
        print(f"ID: {id}")
        print(f"Atomic Fact: {gc_construct['atomic_fact']}")
        print(f"Key Elements: {gc_construct['key_elements']}")
        print(f"Nodes: {gc_construct_map[id]['nodes']}")

        nodes = gc_construct["nodes"]

        for element in gc_construct['key_elements']:
            if element not in gc_construct_map[id]['nodes']:
                nodes[element] = element
        print(f"Nodes: {gc_construct_map[id]['nodes']}\n")
    return gc_construct_map

def map_nodes_label(gc_construct_map):

    # Make nodes_labels dictionary for all atomic facts
    for id, gc_construct in gc_construct_map.items():
        if id == "distinct_nodes_substring":
            continue
        gc_construct_map[id]["node_label"] = {}
    
    # Dictionay of substring : Node representation (e.g, Canad: Canada)
    print(f"\nCreating Node Mappings dictionary...\n{'-'*50}")
    node_mappings = {}
    for mapping in gc_construct_map["distinct_nodes_substring"]:
        key_element = mapping["key_element"]
        max_substring = mapping["max_substring"]
        node_mappings[max_substring] = key_element
    
    print(json.dumps(node_mappings, indent=2))

    print(f"\nMapping final representation of nodes labels...\n{'-'*50}")
    for id, gc_construct in gc_construct_map.items():
        # print(id)
        # print(gc_construct)
        if id == "distinct_nodes_substring":
            continue
        print(f"ID: {id}")
        print(f"Atomic Fact: {gc_construct['atomic_fact']}")
        print(f"Key Elements: {gc_construct['key_elements']}")
        print(f"Nodes: {gc_construct['nodes']}\n")

        nodes = gc_construct['nodes']

        for node, value in nodes.items():
            if type(value) == list:
                # map with highest ratio
                node_key = next(iter(get_item_with_max_score(value)))
                value = node_mappings[node_key]
                print(f"Substring Mapping: [{node_key} -> {value}]")

            print(f"Key Element Mapping: [{node} -> {value}]\n")
            gc_construct['node_label'][node] = value
        print(f"Nodes Label: {gc_construct['node_label']}\n{'.'*50}\n")


    return gc_construct_map

if __name__ == "__main__":
    print(f"\nStarting...\n{'='*50}")
    print("Extracting Atomic Facts and Key Elements...")
    gc_construct_map = extract_atomic_facts_key_elements()
    print(f"Extracted Atomic Facts and Key Elements COMPLETED\n{'='*50}")
    print("Extracting Distinct Nodes of the Graph...")
    gc_construct_map = extract_distinct_nodes(gc_construct_map)
    print(f"Extracting Distinct Nodes of the Graph COMPLETED\n{'='*50}")
    print("Mapping Key Elements to Distinct Nodes of the Graph...")
    gc_construct_map = map_key_elements_to_distinct_nodes(gc_construct_map)
    print(f"Mapping Key Elements to Distinct Nodes of the Graph COMPLETED\n{'='*50}")
    print("Labelling of Nodes of the Graph...")
    gc_construct_map = map_nodes_label(gc_construct_map)
    print(f"Mapping Key Elements to Distinct Nodes of the Graph COMPLETED\n{'='*50}")

    print("\n\n")
    print("*"*50)
    print("GRAPH DATA")
    print("*"*50+"\n\n")
    for id, gc_construct in gc_construct_map.items():
        if id == "distinct_nodes_substring":
            continue
        print(f"ID: {id}")
        print(f"Atomic Fact: {gc_construct['atomic_fact']}")
        print(f"Key Elements: {gc_construct['key_elements']}")
        print(f"Nodes: {json.dumps(gc_construct['nodes'], indent=2)}")
        print(f"Nodes Label :{gc_construct['node_label']}")
        print("-"*50)
    
    print(f"\nDistinct Nodes from Aggregation: \n{json.dumps(gc_construct_map['distinct_nodes_substring'], indent=2)}")
    print("\n\n"+"*"*50+"\n\n")
