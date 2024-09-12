import streamlit as st
import streamlit_antd_components as sac
from pathlib import Path
import json

page_mappings = {
    "ST-8": 126
}

def read_feedback(page):
    feedback_path = Path("./../dashboard/cpg_pages/feedbacks/"+page.split(',')[-1].strip()+".json")
    if feedback_path.is_file():
        with open(feedback_path, 'r') as f:
            feedback = json.load(f)
            return feedback
    else:
        return []

def write_feedback(page, feedback):
    feedback_path = Path("./../dashboard/cpg_pages/feedbacks/"+page.split(',')[-1].strip()+".json")
    with open(feedback_path, 'w') as f:
        json.dump(feedback, f, indent=4)

with st.sidebar:
    st.markdown("BMI calculator")

    selected_page = sac.tree(items=[
        sac.TreeItem('TNM Staging System for the Larynx, ST-8', children=[
            sac.TreeItem('Primary Tumor(T), ST-8', children=[
                sac.TreeItem('Supraglottis, ST-8'),
                sac.TreeItem('Glottis, ST-8'),
                sac.TreeItem('Subglottis, ST-8')
            ]),
            sac.TreeItem('Regional Lymph Nodes(N), ST-9', children=[
            sac.TreeItem('Clinical N (cN), ST-9'),
                sac.TreeItem('Pathalogical N (pN), ST-10'),
            ]),
            sac.TreeItem('Distant Metastasis(M), ST-10'),
            sac.TreeItem('Histologic Grade(G), ST-10'),
            sac.TreeItem('Prognostic Stage Groups, ST-10'),
            sac.TreeItem('Discussion, MS-44', children=[
                sac.TreeItem('Cancer of the Larynx, MS-44', children=[
                    sac.TreeItem('Workup and Staging, MS-44'),
                    sac.TreeItem('Treatment, MS-44'),
                    sac.TreeItem('Treatment (contd.), MS-45'),
                    sac.TreeItem('Radiation Therapy Fractionation, MS-46'),
                    sac.TreeItem('Follow-up/Surveillance, MS-46')
                ])
            ])
        ])
    ], label='NCCN Guidelines Head and Neck Cancers v4.2024', index=0, checkbox_strict=False, open_all=True)
    st.session_state['selected_page'] = selected_page

    if type(selected_page) is list:
        selected_page = selected_page[0]

    html_page = "./../dashboard/cpg_pages/"+selected_page.split(',')[-1].strip()+".html"
    feedback_path = Path("./../dashboard/feedback_store/"+selected_page.split(',')[-1].strip()+".json")
    if feedback_path.is_file():
        with open(feedback_path, 'r') as f:
            feedback = json.load(f)
            st.write(feedback)
    else:
        feedback = {}



with st.expander("Page: "+selected_page, expanded=True):
    HtmlFile = open(html_page, 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    # st.components.v1.html(source_code, height = 920, width=1280, scrolling=True)
    st.html(source_code)


with st.expander("Feedback Log"):
    page_feedback = read_feedback(selected_page)

    user = st.text_input("User", placeholder="Enter your name")
    feedback = st.text_area("Feedback", placeholder="Enter your feedback")
    if st.button("Submit"):
        page_feedback.append({"user": user, "feedback": feedback})
        write_feedback(selected_page, page_feedback)

    st.write(page_feedback)

# st.markdown("BMI calculator")
# st.write('your BMI is 9999')

with st.expander(f"Session Info"):
    st.write(st.session_state)