import streamlit as st
import streamlit_antd_components as sac
from pathlib import Path
from utils.cpg import split_sequence, format_annotated_text
import json
from annotated_text import annotated_text

if "extracted_info_current_pagination_page" not in st.session_state:
    st.session_state["extracted_info_current_pagination_page"] = 1

page_mappings = {
    "ST-8": 126,
    "ST-9": 127,
    "ST-10": 128,
}

def get_page_info(selected_page):
    topic = selected_page.split(", ")[0].strip()
    guideline_page_number = selected_page.split(", ")[-1].strip()
    pdf_page_number = page_mappings[guideline_page_number]

    return topic, guideline_page_number, pdf_page_number

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

def extracted_information_from_page(pdf_page_number):
    with open("./../dashboard/cpg_pages/filtered-propositions_duplicate_removed.json", 'r') as f:
        all_extracted_information = json.load(f)

    page_info = [info["content"] for info in all_extracted_information if info['page'] == pdf_page_number]
    return page_info

with st.sidebar:
    st.markdown("**Guideline Information:**")

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


page, extracted_info, feedback_logs = st.tabs(["Guideline Page", "Extracted Informations", "Feedback Logs"])

with page:
    topic, guideline_page_number, pdf_page_number = get_page_info(selected_page)
    with st.container(border=True):
        topic_col, guideline_page_number_col, pdf_page_number_col = st.columns(3)
        with topic_col:
            st.markdown(f"**Topic:** {topic}")
        with guideline_page_number_col:
            st.markdown(f"**Guideline Page Number:** {guideline_page_number}")
        with pdf_page_number_col:
            st.markdown(f"**PDF Page Number:** {pdf_page_number}")

    with st.container(border=True):
        HtmlFile = open(html_page, 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        # st.components.v1.html(source_code, height = 920, width=1280, scrolling=True)
        st.html(source_code)

with extracted_info:
    topic, guideline_page_number, pdf_page_number = get_page_info(selected_page)

    with st.container(border=True):
        topic_col, guideline_page_number_col, pdf_page_number_col = st.columns(3)
        with topic_col:
            st.markdown(f"**Topic:** {topic}")
        with guideline_page_number_col:
            st.markdown(f"**Guideline Page Number:** {guideline_page_number}")
        with pdf_page_number_col:
            st.markdown(f"**PDF Page Number:** {pdf_page_number}")

    side_by_side_view = st.toggle("View side by side [Guideline <--> Extracted Information]", value=False)

    if side_by_side_view:
        # Guideline <--> Extracted Information side by side view
        guideline, extracted_information = st.columns(2)
        with guideline:
            with st.container(border=True):
                HtmlFile = open(html_page, 'r', encoding='utf-8')
                source_code = HtmlFile.read()
                # st.components.v1.html(source_code, height = 920, width=1280, scrolling=True)
                st.html(source_code)

        with extracted_information:
            info_list = extracted_information_from_page(pdf_page_number)
            split_info_list = split_sequence(info_list, 10)

            with st.container(border=True):
                st.markdown("**Extracted Information:** Dense retrieval method by Salim")
                # for id, info in enumerate(info_list):
                #     st.info(f"#{id+1}. {info}")

                # pagination_page = st.session_state['extracted_info_current_pagination_page']
                pagination_page = sac.pagination(
                    total=len(info_list),
                    page_size=10,
                    align='center', jump=True, show_total=True,
                    variant='filled',
                    key='extracted_info_current_pagination_page'
                )
                for idx, info in enumerate(split_info_list[pagination_page]):
                    st.info(f"#{(pagination_page-1)*10 + idx+1}. {info}")

    else:
        info_list = extracted_information_from_page(pdf_page_number)
        split_info_list = split_sequence(info_list, 10)
        with open("./../causality_extraction/laryngeal_cancer_predictions.json", 'r') as f:
            annotated_information = json.load(f)

        with st.container(border=True):
            st.markdown("**Extracted Information:** Dense retrieval method by Salim")
            # for id, info in enumerate(info_list):
            #     st.info(f"#{id+1}. {info}")

            # pagination_page = st.session_state['extracted_info_current_pagination_page']
            pagination_page = sac.pagination(
                total=len(info_list),
                page_size=10,
                align='center', jump=True, show_total=True,
                variant='filled',
                key='extracted_info_current_pagination_page'
            )
            for idx, info in enumerate(split_info_list[pagination_page]):
                with st.expander(f"#{(pagination_page-1)*10 + idx+1}. {info}"):
                    st.info(info)
                    annotated_text(format_annotated_text(annotated_information[(pagination_page-1)*10 + idx]))


with feedback_logs:
    topic, guideline_page_number, pdf_page_number = get_page_info(selected_page)
    with st.container(border=True):
        topic_col, guideline_page_number_col, pdf_page_number_col = st.columns(3)
        with topic_col:
            st.markdown(f"**Topic:** {topic}")
        with guideline_page_number_col:
            st.markdown(f"**Guideline Page Number:** {guideline_page_number}")
        with pdf_page_number_col:
            st.markdown(f"**PDF Page Number:** {pdf_page_number}")

    page_feedback = read_feedback(selected_page)

    st.write(page_feedback)

    with st.container(border=True):
        user = st.text_input("User", placeholder="Enter your name")
        feedback = st.text_area("Feedback", placeholder="Enter your feedback")
        if st.button("Submit"):
            page_feedback.append({"user": user, "feedback": feedback})
            write_feedback(selected_page, page_feedback)

with st.expander(f"Session Info"):
    st.write(st.session_state)