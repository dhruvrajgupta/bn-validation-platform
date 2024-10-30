import streamlit as st
import streamlit_antd_components as sac
from annotated_text import annotated_text

from utils.db import get_page_info, save_page_sections_data
from utils.prompts2 import DATA_EXTRACTOR, ListSectionData, EXTRACT_ATOMIC_FACTS, EXTRACT_CAUSALITY, ListCauseEffect
from utils.cpg import ask_llm, ask_llm_response_schema, format_annotated_text
import json

# st.set_page_config(layout="wide")

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
    st.code(DATA_EXTRACTOR, wrap_lines=True, line_numbers=True)

# @st.fragment
def display_section(key=None):
    section_names = [section['section_name'] for section in st.session_state.page_data['sections_data']]
    selected_section_placeholder = st.empty()
    selected_section = selected_section_placeholder.radio("Select Section:", section_names, label_visibility="collapsed", horizontal=True, key=key)
    # st.session_state.selected_section = selected_section
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
    elif status == "Updated":
        st.toast(f"Page: {selected_page_no} updated in the Database", icon="⚓")
    elif status == "Added":
        st.toast(f"Page: {selected_page_no} added to the Database", icon="✅")

def update_section_data(section_to_update):
    sections_data = []
    for section in st.session_state.page_data["sections_data"]:
        if section["section_name"] == section_to_update["section_name"]:
            sections_data.append(section_to_update)
        else:
            sections_data.append(section)

    st.session_state.page_data["sections_data"] = sections_data

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

guideline_page, data_extractions, causality = st.tabs(["Guideline Page", "Data Extractions", "Causality"])

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

            if st.session_state.page_data["sections_data"]:
                st.button("Save to Database", type="primary", on_click=save_to_db_callback)

    with causality:
        with st.container(border=True):
            if not st.session_state.page_data["sections_data"]:
                st.markdown("**Please extract sections from the guideline first and save it to the Database.**")
            else:
                display_section(key="causality_section")
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.markdown("**Atomic Facts:**")
                with col2:
                    btn_eaf = st.button("Extract Atomic Facts")

                selected_section_data = None
                for section in st.session_state.page_data["sections_data"]:
                    if section["section_name"] == st.session_state.causality_section:
                        selected_section_data = section

                if btn_eaf:
                    with st.spinner(f"Splitting Paragraphs into Atomic Facts of the section.....{selected_section_data['section_name']}"):
                        prompt = EXTRACT_ATOMIC_FACTS.format(section_name=section['section_name'],
                                                                      section_content=selected_section_data["paragraph"])
                        selected_section_data["atomic_facts"] = ask_llm(prompt)
                        clean_af_list = [af[af.find(".")+1:].strip() for af in selected_section_data["atomic_facts"].splitlines()]
                        selected_section_data["atomic_facts"] = clean_af_list
                        update_section_data(selected_section_data)

                # DISPLAY OF ATOMIC FACTS
                if "atomic_facts" not in selected_section_data.keys():
                    st.info("Please extract the Atomic Facts and save it to the database.")
                else:
                    atomic_facts_display = ""
                    for i, atomic_fact in enumerate(selected_section_data["atomic_facts"]):
                        atomic_facts_display += f"{i+1}. {atomic_fact} \n"
                    st.info(atomic_facts_display)
                    st.button("Save to Database", type="primary", on_click=save_to_db_callback, key="sv_db_af")

                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.markdown("**Cause and Effects:**")
                with col2:
                    btn_ce = st.button("Extract Cause & Effects")

                if btn_ce:
                    with st.spinner(f"Extracting Cause and Effect of section: {selected_section_data['section_name']}"):
                        prompt = EXTRACT_CAUSALITY.format(section_name=selected_section_data['section_name'], text=selected_section_data["atomic_facts"])
                        cause_effect_sentences = json.loads(ask_llm_response_schema(prompt, response_format=ListCauseEffect))["result"]
                        selected_section_data["cause_effect"] = cause_effect_sentences
                        update_section_data(selected_section_data)

                # DISPLAY CAUSALITY
                if "atomic_facts" not in selected_section_data.keys():
                    st.info("Please extract the Atomic Facts first to Extract Causality.")
                else:
                    if "cause_effect" not in selected_section_data.keys():
                        st.info("Please extract Cause and Effect and save it to the database.")
                    else:
                        for idx, cause_effect_sentences in enumerate(selected_section_data["cause_effect"]):
                            cause_effect_sentences = f"{idx+1}. {cause_effect_sentences}"
                            annotated_text(format_annotated_text(cause_effect_sentences))
                        st.button("Save to Database", type="primary", on_click=save_to_db_callback, key="sv_db_ce")




with st.expander("Session State"):
    st.write(st.session_state)