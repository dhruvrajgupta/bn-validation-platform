def get_nodes_by_type(node_type, nodes_contents):
    nodes_list = []
    for node, node_content in nodes_contents.items():
        if node_content['node_type'] == node_type:
            nodes_list.append(node)
    return nodes_list