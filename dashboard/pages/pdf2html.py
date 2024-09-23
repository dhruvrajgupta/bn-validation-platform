import streamlit as st

st.set_page_config(layout="wide")

st.sidebar.markdown("Temperature calculator")

if not "page_sections_info" in st.session_state:
    st.session_state.page_sections_info = {}

@st.dialog("View Prompt")
def show_prompt():
    from utils.prompts import DATA_EXTRACTOR
    st.code(DATA_EXTRACTOR, wrap_lines=True)

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
        st.components.v1.iframe("http://localhost:3000/NCCN_TNMLC/1.html", height = 920, width=1210, scrolling=True)

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
            st.components.v1.iframe("http://localhost:3000/NCCN_TNMLC/1.html", height = 650, width=580, scrolling=True)

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
                    for section in extracted_data:
                        paragraph_content = ""
                        for idx, para in enumerate(section['paragraph']):
                            paragraph_content += f"{idx+1}. {para}\n"
                        st.session_state.page_sections_info[section["section_name"]] = paragraph_content

            if st.session_state.page_sections_info:
                selected_section = st.radio("Select Section:", list(st.session_state.page_sections_info.keys()), label_visibility="collapsed", horizontal=True)
                display_section(selected_section)

with st.expander("Session State"):
    st.write(st.session_state)