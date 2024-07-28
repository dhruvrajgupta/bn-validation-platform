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
        if isinstance(nodes, list):
            for node in nodes:
                node_id = node['@id']
                graph.add_node(node_id)
                if 'parents' in node:
                    parents = node['parents'].split()
                    for parent in parents:
                        graph.add_edge(parent, node_id)
        else:
            node_id = nodes['@id']
            graph.add_node(node_id)
            if 'parents' in nodes:
                parents = nodes['parents'].split()
                for parent in parents:
                    graph.add_edge(parent, node_id)

        return "File read successfully. Graph has been parsed.", xdsl_content
    except Exception as e:
        return "", f"Error reading file: {str(e)}"


# Function to detect cycles in the graph
def detect_cycles():
    if graph is None:
        return "Graph has not been initialized. Please read the file first."

    try:
        cycles = nx.find_cycle(graph, orientation='original')
        cycles_image_save(cycles)
        output = "Graph has cycles:\n"
        output += f"{cycles}\n\n"
        output += f"Edges of the cycle:\n"
        for edges in cycles:
            output += f"{edges}\n"
            yield output

    except nx.exception.NetworkXNoCycle:
        yield "No cycles detected in the graph."


def cycles_image_save(cycles):
    # Create a directed graph
    G = nx.DiGraph()

    # Get the nodes from the edges and formatted edges
    nodes = []
    edges = []
    for edge in cycles:
        node_from = edge[0]
        node_to = edge[1]

        nodes.append(node_from)
        nodes.append(node_to)
        edges.append((node_from, node_to))

    nodes = list(set(nodes))

    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # Draw the directed graph
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
    plt.title('Directed Graph')
    plt.savefig("directed_graph.png")


def run_pipeline(file):
    output = ""
    output += "READING FILE:\n\n"
    msg, parse_xdsl_gen = parse_xdsl(file)
    output += msg
    for xdsl_content in parse_xdsl_gen:
        output += xdsl_content

    output += f"{'=' * 90}\n\n"

    output += "CHECKING CYCLES:\n\n"
    cycle_message = detect_cycles()
    for msg in cycle_message:
        output += msg

    output += f"\n{'=' * 90}\n\n"

    yield output


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
