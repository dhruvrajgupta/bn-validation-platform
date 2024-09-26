import streamlit as st
import streamlit_antd_components as sac

from utils.db import get_page_info
from utils.prompts import DATA_EXTRACTOR, ListSectionData
from utils.cpg import ask_llm, ask_llm_response_schema
import json

st.set_page_config(layout="wide")

if "page_data" not in st.session_state:
    st.session_state.page_data = None

def get_page_info_db(selected_page_no):
    page_data_info = get_page_info(selected_page_no)
    if page_data_info:
        st.session_state.data_source = "Database"
        st.session_state.page_data = page_data_info
    else:
        st.session_state.data_source = None
        st.session_state.page_data = {
            "page_no": selected_page_no,
            "sections_data": None
        }

guideline_map = {
    "NCCN": {
        "name":  "NCCN Guidelines Head and Neck Cancers v4.2024",
        "no_of_pages": 6,
        "dir_name": "NCCN_TNMLC",
    },
    "S3": {
        "name": "S3 guideline - Diagnosis, therapy and aftercare of laryngeal carcinoma",
        "no_of_pages": 147,
        "dir_name": "S3LC",
    }
}

def code_to_name(guideline_code):
    return guideline_map[guideline_code]["name"]

@st.dialog("View Prompt", width="large")
def show_prompt():
    from utils.prompts import DATA_EXTRACTOR
    st.code(DATA_EXTRACTOR, wrap_lines=True, line_numbers=True)

@st.fragment
def display_section():
    section_names = [section['section_name'] for section in st.session_state.page_data['sections_data']]
    selected_section_placeholder = st.empty()
    selected_section = selected_section_placeholder.radio("Select Section:", section_names, label_visibility="collapsed", horizontal=True)
    st.markdown(f"**Section Name:** {selected_section}")
    paragraph_content = ""
    for section in st.session_state.page_data['sections_data']:
        if section['section_name'] == selected_section:
            paragraph_content = ""
            for idx, para in enumerate(section['paragraph']):
                paragraph_content += f"{idx + 1}. {para}\n"
    st.info(paragraph_content)
    st.markdown(f"**Data Source:** {st.session_state.data_source}")

def save_to_db_callback():
    status = save_page_sections_data(selected_page_no, st.session_state.page_data["sections_data"])
    if status == "Same":
        st.toast("Same Data already present in the Database. Not Added !!", icon="🚫")
    elif status == "Replaced":
        st.toast(f"Page: {selected_page_no} replaced in the Database", icon="⚓")
    elif status == "Added":
        st.toast(f"Page: {selected_page_no} added to the Database", icon="✅")

with st.sidebar:
    selected_guideline = st.selectbox(
        "Select Guideline",
        ("NCCN", "S3"),
        format_func=lambda x: guideline_map[x]["name"],
        index=0,
        placeholder="Select guideline...",
    )

    items = [sac.TreeItem(f"Page - {i+1}") for i in range(guideline_map[selected_guideline]['no_of_pages'])]
    selected_page = sac.tree(items=items, label=f"**{guideline_map[selected_guideline]['name']}**", index=0, checkbox_strict=False, open_all=True)
    selected_page_no = selected_page.split("-")[-1].strip()
    get_page_info_db(selected_page_no)

guideline_page, data_extractions = st.tabs(["Guideline Page", "Data Extractions"])

with guideline_page:
    with st.container(border=True):
        st.markdown(f"<iframe src='http://localhost:3000/{guideline_map[selected_guideline]['dir_name']}/{selected_page_no}.html' style='width:1280px;height:960px; overflow:auto'></iframe>", unsafe_allow_html=True)

with data_extractions:
    html_page, data_extractions = st.columns(2)

    with html_page:
        with st.container(border=True):
            st.markdown(f"<iframe src='http://localhost:3000/{guideline_map[selected_guideline]['dir_name']}/{selected_page_no}.html' style='width:calc(100%);height:960px; overflow:auto'></iframe>", unsafe_allow_html=True)
    with data_extractions:
        with st.container(border=True):
            col1, col2 = st.columns([0.8, 0.2])

            with col1:
                sections = st.text_input("Sections to be extracted (separated by comma)", placeholder="Primary Tumor (N), Supraglottis, Glottis. Subglottis", value="Glottis")
            with col2:
                if st.button("View Prompt"):
                    show_prompt()

            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.markdown(f"**Extracted Data:**")
            with col2:
                eb = st.button("Extract Data")


            if eb:
                with st.spinner(f"Extracting data of sections.....{sections}"):
                    HtmlFile = open(
                        f"./dashboard/guidelines/{guideline_map[selected_guideline]['dir_name']}/{selected_page_no}.html",
                        'r', encoding='utf-8')
                    source_code = HtmlFile.read()
                    prompt = DATA_EXTRACTOR.format(html_page=source_code, sections=sections)
                    extracted_data = json.loads(ask_llm_response_schema(prompt, response_format=ListSectionData))["result"]
                    st.session_state.page_data = {"page_no": selected_page_no, "sections_data": extracted_data}
                    st.session_state.data_source = "GPT-4o-mini"

            if st.session_state.page_data["sections_data"]:
                display_section()
            else:
                st.markdown(f"**No Information Present in the Database for Page - {selected_page_no}**")

            from utils.db import save_page_sections_data
            if st.session_state.page_data["sections_data"]:
                st.button("Save to Database", type="primary", on_click=save_to_db_callback)


with st.expander("Session State"):
    st.write(st.session_state)