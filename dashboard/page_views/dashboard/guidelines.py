import json

import streamlit as st
import streamlit_antd_components as sac

from utils.db import get_page_info, save_page_sections_data
from utils.prompts.data_extractions import DATA_EXTRACTOR, ListSectionData
from utils.cpg import ask_llm_response_schema

web_path = "http://localhost:8089/guidelines"

guideline_map = {
    "NCCN": {
        "name": "NCCN Guidelines Head and Neck Cancers v4.2024",
        "no_of_pages": 6,
        "dir_name": "NCCN_TNMLC",
    },
    "S3": {
        "name": "S3 guideline - Diagnosis, therapy and aftercare of laryngeal carcinoma",
        "no_of_pages": 147,
        "dir_name": "S3LC",
    },
    "TEST": {
        "name": "testing",
        "no_of_pages": 10,
        "dir_name": "TEST",
    },
    "NCCN_HN_LC": {
        "name": "NCCN Guidelines Head and Neck Cancers v4.2024 only for Laryngeal Cancer",
        "no_of_pages": 255,
        "dir_name": "NCCN_HN_LC",
    }
}

def save_to_db_callback(selected_page_no, sections_info, chunk_data):
    if sections_info:
        status = save_page_sections_data(selected_page_no, sections_info, chunk_data)
        if status == "Same":
            st.toast("Same Data already present in the Database. Not Added !!", icon="🚫")
        elif status == "Updated":
            st.toast(f"Page: {selected_page_no} updated in the Database", icon="⚓")
        elif status == "Added":
            st.toast(f"Page: {selected_page_no} added to the Database", icon="✅")

def get_selected_page_chunk_data():
    # Get Salims extracted contents
    chunk_data = None
    with open(f"./dashboard/guidelines/extracted_data/{guideline_map[selected_guideline]['dir_name']}.json",
              'r') as file:
        all_extracted_chunks = json.load(file)
        for chunk_dict in all_extracted_chunks:
            # st.write(chunk_dict)
            if chunk_dict["page_number"] == int(st.session_state["page_data"]["page_no"]) - page_offset:
                chunk_data = chunk_dict["content"]

    return chunk_data

@st.dialog("View Prompt", width="large")
def show_prompt():
    st.code(DATA_EXTRACTOR, wrap_lines=True, line_numbers=True)


def get_page_info_db(selected_page_no):
    page_data_info = get_page_info(selected_page_no)
    return page_data_info


with st.sidebar:
    selected_guideline = st.selectbox(
        "Select Guideline",
        ("NCCN_HN_LC"),
        # ("NCCN_HN_LC", "NCCN", "S3", "TEST"),
        format_func=lambda x: guideline_map[x]["name"],
        index=0,
        placeholder="Select guideline...",
    )

    NCCN_FLOWCHART_TO_TEXT_PAGE_NUMBER = [7, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 65,
                                          66, 67, 68, 90, 107, 110, 111, 126, 127, 128, 138, 139, 197]
    NCCN_RELEVANT_TEXT_PAGE_NUMBER = [69, 70, 89, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 104, 105, 106, 114,
                                      115, 116, 117, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153,
                                      154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 180, 181, 182, 185, 186,
                                      187, 188]
    page_offset = 2

    relevant_pages = []
    relevant_pages.extend(NCCN_FLOWCHART_TO_TEXT_PAGE_NUMBER)
    relevant_pages.extend(NCCN_RELEVANT_TEXT_PAGE_NUMBER)
    relevant_pages.sort()

    # st.write(relevant_pages) # Offset of page +2

    items = [sac.TreeItem(f"Page - {page_no+page_offset}") for page_no in relevant_pages]
    # items = [sac.TreeItem(f"Page - {i + 1}") for i in range(guideline_map[selected_guideline]['no_of_pages'])]
    selected_page = sac.tree(items=items, label=f"**{guideline_map[selected_guideline]['name']}**", index=0,
                             checkbox_strict=False, open_all=True)
    selected_page_no = selected_page.split("-")[-1].strip()
    # get_page_info_db(selected_page_no)

st.markdown(f"**Selected Guideline: `{guideline_map[selected_guideline]['name']}`**")
selected_topic = st.radio("Topic:", ["Guideline Page", "Data Extractions", "Sections Extractions","Causality"], horizontal=True, label_visibility="collapsed")

if selected_topic == "Guideline Page":
    with st.container(border=True):
        st.markdown(
            f"<iframe src='{web_path}/{guideline_map[selected_guideline]['dir_name']}/{selected_page_no}.html' style='width:1280px;height:960px; overflow:auto'></iframe>",
            unsafe_allow_html=True)

elif selected_topic == "Data Extractions":
    # with st.container(border=True):
    html_page, data_extractions = st.columns(2)

    with html_page:
        with st.container(border=True):
            st.markdown(
                f"<iframe src='{web_path}/{guideline_map[selected_guideline]['dir_name']}/{selected_page_no}.html' style='width:calc(100%);height:960px; overflow:auto'></iframe>",
                unsafe_allow_html=True)

    with data_extractions:
        with st.container(border=True):
            HtmlFile = open(
                f"./dashboard/guidelines/{guideline_map[selected_guideline]['dir_name']}/{selected_page_no}.html",
                'r', encoding='utf-8')
            source_code = HtmlFile.read()

            type = st.radio("Data Source:", ["Sections", "From JSON", "Sections extraction"], horizontal=True, label_visibility="collapsed")

            if type == "Sections":
                page_info = get_page_info_db(selected_page_no)
                section_names = [section_dict["section_name"] for section_dict in page_info["sections"]]
                selected_section = st.radio("**Section:**", section_names, horizontal=True)

                for section_dict in page_info["sections"]:
                    if selected_section == section_dict["section_name"]:
                        paragraph = ""
                        for idx, para in enumerate(section_dict["paragraph"]):
                            # paragraph += f"{idx+1}. {para}\n"
                            paragraph += f"{para}\n\n"
                        st.info(paragraph)
                        break

            if type == "From JSON":
                # with st.expander("Source code"):
                #     st.code(source_code)

                st.markdown("**Extracted Data:**")
                chunk_data = get_selected_page_chunk_data()
                st.info(chunk_data)

            elif type == "Sections extraction":
                # with st.expander("Source code"):
                #     st.code(source_code)

                chunk_data = get_selected_page_chunk_data()

                db_info = None
                if db_info:
                    pass
                else:
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.markdown(f"**Extracted Data:**")
                    with col2:
                        eb = st.button("Extract Data")

                    sections_data = None
                    if eb:
                        with st.spinner(f"Extracting sections ..."):
                            prompt = DATA_EXTRACTOR.format(text_content=chunk_data, html_page=source_code)
                            # st.write(prompt)
                            sections_data = json.loads(ask_llm_response_schema(prompt, response_format=ListSectionData))

                    st.json(sections_data, expanded=False)
                    # st.write(selected_page_no)
                    st.button("Save to Database", type="primary",
                              on_click=save_to_db_callback, args=[selected_page_no, sections_data, chunk_data])


                    # # Check if sections data present
                    # if st.session_state.page_data["sections_data"]:
                    #     # st.write(st.session_state.page_data["sections_data"])
                    #     sections_names = [section["section_name"] for section in st.session_state.page_data["sections_data"]["sections"]]
                    #     selected_section = st.radio("", sections_names, horizontal=True, label_visibility="collapsed")
                    #
                    #     # Show selected section paragraphs
                    #     for section_data in st.session_state.page_data["sections_data"]["sections"]:
                    #         if selected_section == section_data["section_name"]:
                    #             st.write(section_data["paragraph"])
                    #
                    #     st.write(extracted_data)



elif selected_topic == "Causality":
    # with st.container(border=True):
    data_extractions, causality_extractions = st.columns(2)

    # with html_page:
    #     with st.container(border=True):
    #         st.markdown(
    #             f"<iframe src='{web_path}/{guideline_map[selected_guideline]['dir_name']}/{selected_page_no}.html' style='width:calc(100%);height:960px; overflow:auto'></iframe>",
    #             unsafe_allow_html=True)

    with data_extractions:
        with st.container(border=True):
            HtmlFile = open(
                f"./dashboard/guidelines/{guideline_map[selected_guideline]['dir_name']}/{selected_page_no}.html",
                'r', encoding='utf-8')
            source_code = HtmlFile.read()

            # with st.expander("Source code"):
            #     st.code(source_code)
            st.markdown("**Extracted Data:**")

            # Get Salims extracted contents
            with open(f"./dashboard/guidelines/extracted_data/{guideline_map[selected_guideline]['dir_name']}.json",
                      'r') as file:
                all_extracted_chunks = json.load(file)
                for chunk_dict in all_extracted_chunks:
                    # st.write(chunk_dict)
                    if chunk_dict["page_number"] == int(st.session_state["page_data"]["page_no"]) - page_offset:
                        st.info(chunk_dict["content"])

        with causality_extractions:
            with st.container(border=True):
                st.markdown("**Causality Extractions:**")

with st.expander("Session State"):
    st.json(st.session_state, expanded=False)
