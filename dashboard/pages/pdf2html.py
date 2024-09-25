import streamlit as st
import streamlit_antd_components as sac

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

st.set_page_config(layout="wide")

with st.sidebar:
    selected_guideline = st.selectbox(
        "Select Guideline",
        ("NCCN", "S3"),
        format_func=lambda x: guideline_map[x]["name"],
        index=0,
        placeholder="Select guideline...",
    )

    #### EXAMPLE OF WELL FORMATED TABLE OF CONTENTS ####
    # selected_page = sac.tree(items=[
    #     sac.TreeItem('TNM Staging System for the Larynx, ST-8', children=[
    #         sac.TreeItem('Primary Tumor(T), ST-8', children=[
    #             sac.TreeItem('Supraglottis, ST-8'),
    #             sac.TreeItem('Glottis, ST-8'),
    #             sac.TreeItem('Subglottis, ST-8')
    #         ]),
    #         sac.TreeItem('Regional Lymph Nodes(N), ST-9', children=[
    #             sac.TreeItem('Clinical N (cN), ST-9'),
    #             sac.TreeItem('Pathalogical N (pN), ST-10'),
    #         ]),
    #         sac.TreeItem('Distant Metastasis(M), ST-10'),
    #         sac.TreeItem('Histologic Grade(G), ST-10'),
    #         sac.TreeItem('Prognostic Stage Groups, ST-10'),
    #         sac.TreeItem('Discussion, MS-44', children=[
    #             sac.TreeItem('Cancer of the Larynx, MS-44', children=[
    #                 sac.TreeItem('Workup and Staging, MS-44'),
    #                 sac.TreeItem('Treatment, MS-44'),
    #                 sac.TreeItem('Treatment (contd.), MS-45'),
    #                 sac.TreeItem('Radiation Therapy Fractionation, MS-46'),
    #                 sac.TreeItem('Follow-up/Surveillance, MS-46')
    #             ])
    #         ])
    #     ])
    # ], label='NCCN Guidelines Head and Neck Cancers v4.2024', index=0, checkbox_strict=False, open_all=True)

    items = [sac.TreeItem(f"Page - {i+1}") for i in range(guideline_map[selected_guideline]['no_of_pages'])]
    selected_page = sac.tree(items=items, label=f"**{guideline_map[selected_guideline]['name']}**", index=0, checkbox_strict=False, open_all=True)
    selected_page_no = selected_page.split("-")[-1].strip()

if not "page_sections_info" in st.session_state:
    st.session_state.page_sections_info = {}

if not "data_source" in st.session_state:
    st.session_state.data_source = None

@st.dialog("View Prompt", width="large")
def show_prompt():
    from utils.prompts import DATA_EXTRACTOR
    st.code(DATA_EXTRACTOR, wrap_lines=True, line_numbers=True)

@st.fragment
def display_section(selected_section):
    st.markdown(f"**Section Name:** {selected_section}")
    st.info(st.session_state.page_sections_info[selected_section])

# st.markdown("Temperature calculator")
# temp_var = st.number_input('enter celcius')
# st.write(f'fahrenheit is: {temp_var*9/5+32}F')

guideline_page, data_extractions = st.tabs(["Guideline Page", "Data Extractions"])

with guideline_page:
    with st.container(border=True):
        st.markdown(f"<iframe src='http://localhost:3000/{guideline_map[selected_guideline]['dir_name']}/{selected_page_no}.html' style='width:1280px;height:960px; overflow:auto'></iframe>", unsafe_allow_html=True)

with data_extractions:
    html_page, data_extractions = st.columns(2)

    with html_page:
        with st.container(border=True):
        # HtmlFile = open("./dashboard/guidelines/NCCN_TNMLC/1.html", 'r', encoding='utf-8')
        # source_code = HtmlFile.read()
        # # st.components.v1.html(source_code, height = 920, width=1280, scrolling=True)
        # st.html(source_code)
        # st.write(f'<iframe src="http://localhost:3000/NCCN_TNMLC/1.html"></iframe>',
        #     unsafe_allow_html=True)
        # st.components.v1.html(f'<iframe src="http://localhost:3000/NCCN_TNMLC/1.html" height ="920" width="50%" style="border:0"></iframe>', height = 920, scrolling=True)
        # st.html(f'<iframe src="http://localhost:3000/NCCN_TNMLC/1.html" height ="920", width="1280",></iframe>')
        # st.markdown(f"**Guideline HTML:**")
            HtmlFile = open("./dashboard/guidelines/NCCN_TNMLC/1.html", 'r', encoding='utf-8')
            source_code = HtmlFile.read()
            # st.components.v1.html("<iframe src='http://localhost:3000/NCCN_TNMLC/1.html' style='width:calc(100%);height:calc(100%); overflow:auto'></iframe>", height=960)
            # st.components.v1.iframe("http://localhost:3000/NCCN_TNMLC/1.html", height = 920, width=calc(100%), scrolling=True)
            st.markdown(f"<iframe src='http://localhost:3000/{guideline_map[selected_guideline]['dir_name']}/{selected_page_no}.html' style='width:calc(100%);height:960px; overflow:auto'></iframe>", unsafe_allow_html=True)
    with data_extractions:
        with st.container(border=True):
            # st.markdown(f"**Data Extractions:**")

            col1, col2 = st.columns([0.8, 0.2])

            with col1:
                sections = st.text_input("Sections to be extracted (separated by comma)", placeholder="Primary Tumor (N), Supraglottis, Glottis. Subglottis")
                # if sections:
                #     st.info("Sections to be extracted: " + sections)
            with col2:
                if st.button("View Prompt"):
                    show_prompt()

            # with st.container(border=True):
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.markdown(f"**Extracted Data:**")
            with col2:
                eb = st.button("Extract Data")

            HtmlFile = open("./dashboard/guidelines/NCCN_TNMLC/1.html", 'r', encoding='utf-8')
            source_code = HtmlFile.read()

            from utils.prompts import DATA_EXTRACTOR, ListSectionData
            from utils.cpg import ask_llm, ask_llm_response_schema
            import json

            if eb:
                with st.spinner(f"Extracting data...{sections}"):
                    prompt = DATA_EXTRACTOR.format(html_page=source_code, sections=sections)
                    extracted_data = json.loads(ask_llm_response_schema(prompt, response_format=ListSectionData))["result"]
                    st.session_state.page_sections_info = {}
                    for section in extracted_data:
                        paragraph_content = ""
                        for idx, para in enumerate(section['paragraph']):
                            paragraph_content += f"{idx+1}. {para}\n"
                        st.session_state.page_sections_info[section["section_name"]] = paragraph_content
                        st.session_state.data_source = "GPT-4o-mini"

            if st.session_state.page_sections_info:
                selected_section = st.radio("Select Section:", list(st.session_state.page_sections_info.keys()), label_visibility="collapsed", horizontal=True)
                display_section(selected_section)
                st.markdown(f"**Data Source:** {st.session_state.data_source}")

with st.expander("Session State"):
    st.write(st.session_state)