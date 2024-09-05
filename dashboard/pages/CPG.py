import streamlit as st
import streamlit_antd_components as sac

with st.sidebar:
    st.markdown("BMI calculator")
    tree_data = [
        {
        "value": "parent 1",
        "title": "Parent 1",
        "children": 
            [
                {"value": "child 1",
                "title": "Child 1"},
                {"value": "child 2",
                "title": "Child 2"},
            ]
        },
        {
        "value": "parent 2",
        "title": "Parent 2",
        }
    ]

    page_tree = {
        "Primary Tumor, ST-8": "./../dashboard/cpg_pages/st-8.html",
        "item2": "st-8.html",
    }

    selected_page = sac.tree(items=[
        sac.TreeItem('Primary Tumor, ST-8'),
        sac.TreeItem('item2', icon='apple', description='item description', children=[
            sac.TreeItem('tooltip', icon='github', tooltip='item tooltip'),
            sac.TreeItem('item2-2', children=[
                sac.TreeItem('item2-2-1'),
                sac.TreeItem('item2-2-2'),
                sac.TreeItem('item2-2-3'),
            ]),
        ]),
        sac.TreeItem('disabled', disabled=True),
        sac.TreeItem('item3', children=[
            sac.TreeItem('item3-1'),
            sac.TreeItem('item3-2'),
        ]),
    ], label='TNM Staging', index=0, checkbox_strict=True)
    # st.session_state['selected_page'] = selected_page

    html_page = "./../dashboard/cpg_pages/"+selected_page.split(',')[-1].strip()+".html"


with st.expander("Page: "+selected_page):
    HtmlFile = open(html_page, 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    st.components.v1.html(source_code, height = 1000, width=1000, scrolling=True)

# st.markdown("BMI calculator")
# st.write('your BMI is 9999')

with st.expander(f"Session Info"):
    st.write(st.session_state)