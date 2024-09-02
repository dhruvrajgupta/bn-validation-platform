import streamlit as st
import time
from utils.file import parse_xdsl, convert_to_vis

st.set_page_config(layout="wide")

super_model, wip_model, tab3 = st.tabs(["Super Model", "WIP Model", "Comparison"])

with super_model:
    st.header("A cat")
    st.image("https://static.streamlit.io/examples/cat.jpg", width=200)


with wip_model:

    uploaded_file = st.file_uploader("Choose a file", type=["xdsl"])

    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8")
        graph = parse_xdsl(file_content)
        st.write(graph)

        with st.expander(f"View Graph"):
            convert_to_vis(graph)
            HtmlFile = open("/home/dhruv/Desktop/bn-validation-platform/scripts/dashboard/current_model.html", 'r', encoding='utf-8')
            source_code = HtmlFile.read()
            st.components.v1.html(source_code, height = 1000,width=1000)


with st.sidebar:
    with st.echo():
        st.write("This code will be printed to the sidebar.")

    with st.spinner("Loading..."):
        time.sleep(5)
    st.success("Done!")