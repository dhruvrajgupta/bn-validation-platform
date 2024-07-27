import gradio as gr
import xmltodict
import networkx as nx

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
        output = "Graph has cycles:\n"
        output += f"{cycles}\n\n"
        output += f"Edges of the cycle:\n"
        for edges in cycles:
            output += f"{edges}\n"
            yield output

    except nx.exception.NetworkXNoCycle:
        yield "No cycles detected in the graph."


# Create Gradio interface
read_file_button = gr.Interface(
    fn=parse_xdsl,
    inputs=gr.File(file_types=['.xdsl']),
    outputs=[gr.Textbox(label="Status Message"), gr.Textbox(label="XDSL File Content"), ],
    title="Read XDSL File",
    description="Upload an XDSL file to read and parse its content.",
    allow_flagging="never"
)

check_cycles_button = gr.Interface(
    fn=detect_cycles,
    inputs=None,
    outputs=gr.Textbox(),
    title="Check for Cycles",
    description="Check the parsed graph for cycles.",
    allow_flagging="never"
)

app = gr.TabbedInterface(
    interface_list=[read_file_button, check_cycles_button],
    tab_names=["Read File", "Check Cycles", "Run Pipeline"]
)

# Launch the interface
app.launch()
