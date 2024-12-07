import streamlit as st

st.set_page_config(layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    with st.container(border=True):
        placeholder = st.empty()

        # Insert a form in the container
        with placeholder.form("login"):
            st.markdown("#### Enter your credentials")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

        from utils.db import get_user
        if submit and get_user(email) and password == get_user(email)["password"]:
            placeholder.empty()
            st.success("Login successful")
            st.session_state.logged_in = True
            user = get_user(email)
            st.session_state.user = user["username"]
            st.session_state.user_type = user["type"]
            st.rerun()
        elif submit and get_user(email) and password != get_user(email)["password"]:
            st.error("Login failed")
        elif submit and email == "" or password == "":
            st.error("Login failed")
        elif submit and get_user(email) is None:
            st.error("Login failed")
        else:
            pass

def logout():
    # if st.button("Log out"):
    st.session_state.logged_in = False
    st.rerun()

##### Pages

# Login
login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

## Instructions Manual
instructions_manual = st.Page("page_views/instructions_manual.py", title="Instructions Manual", default=True)

## Dashboard
ground_truth_model = st.Page("page_views/dashboard/ground_truth_model.py", title="Ground Truth Model")
work_in_progress_model = st.Page("page_views/dashboard/work_in_progress_model.py", title="Work In Progress Model")
comparison = st.Page("page_views/dashboard/comparison.py", title="Comparison")
guidelines = st.Page("page_views/dashboard/guidelines.py", title="Clinical Guidelines")

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
qualitative_analysis = st.Page("page_views/evaluations/qualitative_analysis.py", title="Qualitative Analysis")

## Previous
CPG = st.Page("page_views/previous/CPG.py", title="CPG")
dashboard = st.Page("page_views/previous/dashboard.py", title="Dashboard")
Edges_Rationality = st.Page("page_views/previous/Edges_Rationality.py", title="Edges Rationality")
Graphs = st.Page("page_views/previous/Graphs.py", title="Graphs")
Models = st.Page("page_views/previous/Models.py", title="Models")
Nodes_Descriptions = st.Page("page_views/previous/Nodes_Descriptions.py", title="Nodes Descriptions")
pdf2html = st.Page("page_views/previous/pdf2html.py", title="PDF2HTML")

if st.session_state.logged_in:
    if st.session_state.user_type == "admin":
        pg = st.navigation(
            {
                "Instructions Manual": [instructions_manual],
                "Dashboard": [ground_truth_model, work_in_progress_model, comparison, guidelines],
                "Models": [new_model, label_descriptions, file_contents, dataset],
                "Nodes Descriptions": [nodes_descriptions],
                "Edge Rationality": [edge_rationality],
                "Evaluations": [evaluations, qualitative_analysis],
                "Logout": [logout_page],
                "Previous": [CPG, dashboard, Edges_Rationality, Graphs, Models, Nodes_Descriptions, pdf2html],
            }
        )
    elif st.session_state.user_type == "clinician":
        pg = st.navigation(
            {
                "Evaluations": [qualitative_analysis],
                "Logout": [logout_page],
            }
        )
else:
    pg = st.navigation([login_page])

pg.run()