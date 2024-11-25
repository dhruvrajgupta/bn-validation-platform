import streamlit as st

st.set_page_config(layout="wide")

##### Pages

## Instructions Manual
instructions_manual = st.Page("page_views/instructions_manual.py", title="Instructions Manual", default=True)

## Dashboard
ground_truth_model = st.Page("page_views/dashboard/ground_truth_model.py", title="Ground Truth Model")
work_in_progress_model = st.Page("page_views/dashboard/work_in_progress_model.py", title="Work In Progress Model")
comparison = st.Page("page_views/dashboard/comparison.py", title="Comparison")

## Models
new_model = st.Page("page_views/models/new_model.py", title="New Model")
label_descriptions = st.Page("page_views/models/label_descriptions_nodes_contents.py", title="Label, Descriptions and Nodes Contents")
file_contents = st.Page("page_views/models/file_contents.py", title="XDSL File Contents")
dataset = st.Page("page_views/models/dataset.py", title="Dataset")

## Nodes
nodes_descriptions = st.Page("page_views/nodes_descriptions.py", title="Nodes Descriptions")

## Edge Rationality
edge_rationality = st.Page("page_views/edge_rationality.py", title="Edge Rationality")

## Evaluations
evaluations = st.Page("page_views/evaluations/evaluation.py", title="Evaluations")

## Previous
CPG = st.Page("page_views/previous/CPG.py", title="CPG")
dashboard = st.Page("page_views/previous/dashboard.py", title="Dashboard")
Edges_Rationality = st.Page("page_views/previous/Edges_Rationality.py", title="Edges Rationality")
Graphs = st.Page("page_views/previous/Graphs.py", title="Graphs")
Models = st.Page("page_views/previous/Models.py", title="Models")
Nodes_Descriptions = st.Page("page_views/previous/Nodes_Descriptions.py", title="Nodes Descriptions")
pdf2html = st.Page("page_views/previous/pdf2html.py", title="PDF2HTML")

pg = st.navigation(
    {
        "Instructions Manual": [instructions_manual],
        "Dashboard": [ground_truth_model, work_in_progress_model, comparison],
        "Models": [new_model, label_descriptions, file_contents, dataset],
        "Nodes Descriptions": [nodes_descriptions],
        "Edge Rationality": [edge_rationality],
        "Evaluations": [evaluations],
        "Previous": [CPG, dashboard, Edges_Rationality, Graphs, Models, Nodes_Descriptions, pdf2html],
    }
)

pg.run()