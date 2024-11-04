def get_nodes_by_type(node_type, nodes_contents):
    nodes_list = []
    for node, node_content in nodes_contents.items():
        if node_content['node_type'] == node_type:
            nodes_list.append(node)
    return nodes_list

def get_distinct_entities(ontology_name, nodes_having_entity):
    print(ontology_name)
    distinct_entity_list = []
    for node_desc in nodes_having_entity:
        for node_entity_list in node_desc['entity_information']:
            if node_entity_list['ontology_name'] == ontology_name:
                distinct_entity_list.append(node_entity_list['label'])

    # Return only the distinct entities
    print(list(set(distinct_entity_list)))
    return list(set(distinct_entity_list))

def get_nodes_by_entity(entity_name, nodes_having_entity):
    print(entity_name)
    nodes_list = []
    for node_desc in nodes_having_entity:
        for node_entity_list in node_desc['entity_information']:
            if node_entity_list['label'] == entity_name:
                nodes_list.append(node_desc['node_id'])

    print(nodes_list)
    return nodes_list