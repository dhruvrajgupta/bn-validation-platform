import streamlit as st
from streamlit import image

st.write("## Qualitative Analysis on Modified Bayesian Network")
st.write("**In this modified Bayesian Network, the edges are reversed, as in the `source` becomes the `target` and vice versa.**")

st.write(f"**Clinician Username: `{st.session_state.user}`**")

@st.dialog("Lymph Node Staging of the TNM Staging of Laryngeal Cancer", width="large")
def show_bn_image():
    st.image(image="/usr/src/app/dashboard/page_views/evaluations/large_image.jpg", width=11375)


if st.button("View Ground Truth Bayesian Network"):
    show_bn_image()
    # st.image(image="/usr/src/app/dashboard/page_views/evaluations/large_image.jpg", output_format="auto",
    #          use_container_width=False)


type = st.radio("**Select the type:** ", ["**Type 1 - `Node1 {causal_verb} Node2`**", "**Type 2 - `changing {Node1} causes a change in {Node2}`**"], horizontal=True)



# with st.expander("**Session State**"):
#     st.json(st.session_state, expanded=False)