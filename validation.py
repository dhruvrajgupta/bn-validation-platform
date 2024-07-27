import gradio as gr

# Function to read and display XDSL file content
def read_xdsl(file):
    if file is None:
        return "No file uploaded."
    with open(file.name, 'r') as f:
        content = f.read()
    return content

# Create Gradio interface
iface = gr.Interface(
    fn=read_xdsl,
    inputs=gr.components.File(file_types=['.xdsl']),
    outputs=gr.components.Textbox(),
    title="XDSL File Reader",
    description="Upload an XDSL file to read and display its content."
)

# Launch the interface
iface.launch()