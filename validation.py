import gradio as gr
import xmltodict
import networkx as nx
import matplotlib.pyplot as plt

# Global variable to store the parsed graph
graph = None


# Function to parse XDSL file and build graph
def parse_xdsl(file):
    global graph
    try:
        with open(file.name, 'r') as f:
            xdsl_content = f.read()

        xdsl_dict = xmltodict.parse(xdsl_content)
        graph = nx.DiGraph()

        nodes = xdsl_dict['smile']['nodes']['cpt']
        # print(nodes)
        if isinstance(nodes, list):
            for node in nodes:
                node_id = node['@id']
                graph.add_node(node_id)
                if 'parents' in node:
                    parents = node['parents'].split()
                    # print(parents)
                    for parent in parents:
                        graph.add_edge(parent, node_id)
        else:
            node_id = nodes['@id']
            graph.add_node(node_id)
            if 'parents' in nodes:
                parents = nodes['parents'].split()
                for parent in parents:
                    graph.add_edge(parent, node_id)

        # Draw the directed graph
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(graph)  # Position nodes using Fruchterman-Reingold force-directed algorithm
        nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color='gray', font_size=15,
                font_weight='bold', arrowsize=20)
        plt.title('Directed Graph')
        plt.savefig("full_directed_graph.png")
        # plt.show()

        return "File read successfully. Graph has been parsed.", xdsl_content
    except Exception as e:
        return "", f"Error reading file: {str(e)}"


# Function to detect cycles in the graph
def detect_cycles():
    if graph is None:
        return "Graph has not been initialized. Please read the file first."

    def is_sublist(small, big):
        it = iter(big)
        x = all(item in it for item in small)
        return x

    def dfs(node, visited, stack):
        visited.add(node)
        stack.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor, visited, stack)
            elif neighbor in stack:
                cycle = stack[stack.index(neighbor):] + [neighbor]
                cycle_procesed = False
                # Check if the cycle has already been included before
                for collected_cycle in all_cycles:
                    if len(collected_cycle) >= len(cycle):
                        if is_sublist(cycle, collected_cycle):
                            cycle_procesed = True
                            break
                if not cycle_procesed:
                    all_cycles.append(cycle + stack[stack.index(neighbor) + 1:])
        stack.pop()

    all_cycles = []
    for start_node in graph.nodes:
        visited = set()
        stack = []
        dfs(start_node, visited, stack)

    cycles_image_save(all_cycles)

    return all_cycles


def cycles_image_save(cycles):
    # Create a directed graph
    G = nx.DiGraph()

    for cycle in cycles:
        path_stack = []
        node_from = cycle[0]
        path_stack.append(node_from)
        for node_to in cycle[1:]:
            if node_to in path_stack:
                G.add_edge(node_from, node_to)
                break

            G.add_edge(node_from, node_to)
            path_stack.append(node_to)
            node_from = node_to

    # # Draw the directed graph
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G)  # Position nodes using Fruchterman-Reingold force-directed algorithm
    options = {
        'with_labels': True,
        'node_color': 'skyblue',
        'node_size': 2000,
        'edge_color': 'gray',
        'font_size': 10,
        'font_weight': 'normal',
        'arrowsize': 20,
        'node_shape': 'o'  # To keep nodes as circles
    }
    nx.draw(G, pos, **options)
    plt.title('All Cycles')
    plt.savefig("all_cycles.png")


def find_redundant_edges():
    def is_redundant_edge(G, edge):
        # Checking if removal of edges still has connectivity
        G_prime = G.copy()
        G_prime.remove_edge(*edge)
        # Check if there is still a path between the nodes
        is_redundant = nx.has_path(G_prime, edge[0], edge[1])
        return is_redundant

    redundant_edges = [edge for edge in graph.edges() if is_redundant_edge(graph, edge)]

    return redundant_edges

#
# def check_nodes_affected_removal_reachability():
#     def affects_reachability(graph, node):
#         original_reachable = dict(nx.all_pairs_shortest_path_length(graph))
#         graph.remove_node(node)
#         new_reachable = dict(nx.all_pairs_shortest_path_length(graph))
#         graph.add_node(node)  # Add the node back
#         return original_reachable != new_reachable
#
#     # Identify redundant nodes based on reachability
#     redundant_nodes_reachability = []
#     for node in graph.nodes:
#         if not affects_reachability(graph.copy(), node):
#             redundant_nodes_reachability.append(node)
#
#     return redundant_nodes_reachability
#

def run_pipeline(file):
    output = ""
    output += "READING FILE:\n\n"
    msg, parse_xdsl_gen = parse_xdsl(file)
    output += msg
    for xdsl_content in parse_xdsl_gen:
        output += xdsl_content
    output += "\n\n"

    output += f"{'=' * 90}\n\n"

    output += "CHECKING CYCLES:\n\n"
    cycles = detect_cycles()
    if cycles:
        output += f"{len(cycles)} cycle/s were found:\n\n"
    for index, cycle in enumerate(cycles):
        output += f"Cycle #{index + 1}:\n"
        output += f"{cycle}\n\n"

    output += f"\n{'=' * 90}\n\n"

    # if cycles:
    #     return output

    ## FIND REDUNDANT EDGES
    output += "FINDING REDUNDANT EDGES:\n\n"
    redundant_edges = find_redundant_edges()
    if redundant_edges:
        output += f"{len(redundant_edges)} edge/s were found:\n\n"
    for index, edge in enumerate(redundant_edges):
        output += f"Edge #{index + 1}:\n"
        output += f"{edge}\n"
        output += f"Multiple Paths:\n"
        for path in nx.all_simple_paths(graph, edge[0], edge[1]):
            output += f"{path}\n"
        output += "\n\n"

    output += f"{'=' * 90}\n\n"

    ## FIND REDUNDANT NODES
    output += "FINDING REDUNDANT NODES:\n\n"
    output += "Fininding Isolated nodes...\n\n"

    # 1. Finding isolated nodes
    isolated_nodes = list(nx.isolates(graph))
    if isolated_nodes:
        output += f"{len(isolated_nodes)} isolated node/s were found:\n"
        output += f"{isolated_nodes}\n\n"

    # 2. Check if removing a node affects reachability
    # output += "Checking if removing nodes does not affect reachability...\n\n"
    # redundant_nodes_reachability = check_nodes_affected_removal_reachability()
    # output += f"{redundant_nodes_reachability}"

    # redundant_edges = find_redundant_edges()
    # if redundant_edges:
    #     output += f"{len(redundant_edges)} edge/s were found:\n\n"
    # for index, edge in enumerate(redundant_edges):
    #     output += f"Edge #{index + 1}:\n"
    #     output += f"{edge}\n"
    #     output += f"Multiple Paths:\n"
    #     for path in nx.all_simple_paths(graph, edge[0], edge[1]):
    #         output += f"{path}\n"
    #     output += "\n\n"
    #
    # output += f"{'=' * 90}\n\n"



    return output


with gr.Blocks() as demo:
    with gr.Tab("Read File"):
        gr.Interface(
            fn=parse_xdsl,
            inputs=gr.File(file_types=['.xdsl']),
            outputs=[gr.Textbox(label="Status Message"), gr.Textbox(label="XDSL File Content"), ],
            title="Read XDSL File",
            description="Upload an XDSL file to read and parse its content.",
            allow_flagging="never"
        )
    with gr.Tab("Check Cycles"):
        gr.Interface(
            fn=detect_cycles,
            inputs=None,
            outputs=[gr.TextArea()],
            title="Check for Cycles",
            description="Check the parsed graph for cycles.",
            allow_flagging="never",
        )
    with gr.Tab("Run Pipeline"):
        gr.Interface(
            fn=run_pipeline,
            inputs=gr.File(file_types=['.xdsl']),
            outputs=[gr.Textbox(label="XDSL File Content", elem_id="widened_textbox")],
            title="Run Pipeline",
            description="Upload an XDSL file to run the entire pipeline: read and check for cycles."
        )

# Launch the interface
demo.launch()
