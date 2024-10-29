import streamlit as st

from utils.db import get_models, get_model_by_name, get_node_descriptions, get_edge_rationality
from utils.file import build_network

def save_to_db_callback(edge, edge_rationality_info):
    from utils.db import save_edge_rationality
    status = save_edge_rationality(edge, edge_rationality_info)
    if status == "Same":
        st.toast("Same Data already present in the Database. Not Added !!", icon="🚫")
    elif status == "Updated":
        st.toast(f"Edge Rationality: {edge} updated in the Database", icon="⚓")
    elif status == "Added":
        st.toast(f"Edge Rationality: {edge} added to the Database", icon="✅")

def display_node_information(node, source_target, edge):
    with st.container(border=True):
        st.markdown(f"**{source_target} :**  ")
        st.markdown(f"**ID :** `{node}`")
        node_desc = get_node_descriptions(node)
        if node_desc:
            st.markdown(f"**Type :** `{node_desc['type']}`")
            st.markdown(f"**Observability :** `{node_desc['observability']}`")
            st.markdown(f"**Label :** {node_desc['label']}")
            st.markdown(f"**Description :** {node_desc['description']}")
            st.data_editor(node_desc['entity_information'], use_container_width=True, disabled=True, key=f"DataEditor - Entity - {source_target} - {node} - of edge {edge}")
        else:
            st.markdown("**No information on the node is available in our database.**")

def get_edge_rationality_from_gpt(edge, model_label, model_description):
    from utils.cpg import ask_llm
    from utils.prompts.edge_rationality import EDGE_RATIONALITY

    er = {
        "first": None,
        "second": None,
        "third": None
    }

    source_node_info = get_node_descriptions(edge[0])
    target_node_info = get_node_descriptions(edge[1])

    # if setup_type == "first":

    prompt = EDGE_RATIONALITY.format(
        source_node_id = source_node_info['node_id'],
        source_node_type = source_node_info['type'],
        source_node_observability = source_node_info['observability'],
        source_node_label = source_node_info['label'],
        source_node_description = source_node_info['description'],
        target_node_id = target_node_info['node_id'],
        target_node_type = target_node_info['type'],
        target_node_observability = target_node_info['observability'],
        target_node_label = target_node_info['label'],
        target_node_description = target_node_info['description'],
        model_label = model_label,
        model_description = model_description
    )

    gpt_edge_rationality = ask_llm(prompt)
    er["first"] = gpt_edge_rationality

    # elif setup_type == "second":

    # Separated Prompts
    from utils.prompts.edge_rationality import EDGE_RATIONALITY2
    er["second"] = list()

    prompt = EDGE_RATIONALITY2.format(
        source_node_id = source_node_info['node_id'],
        source_node_type = source_node_info['type'],
        source_node_observability = source_node_info['observability'],
        source_node_label = source_node_info['label'],
        source_node_description = source_node_info['description'],
        target_node_id = target_node_info['node_id'],
        target_node_type = target_node_info['type'],
        target_node_observability = target_node_info['observability'],
        target_node_label = target_node_info['label'],
        target_node_description = target_node_info['description'],
        model_label = model_label,
        model_description = model_description
    )

    gpt_edge_rationality1 = ask_llm(prompt)
    er["second"].append(gpt_edge_rationality1)

    source_node_info = get_node_descriptions(edge[1])
    target_node_info = get_node_descriptions(edge[0])

    prompt = EDGE_RATIONALITY2.format(
        source_node_id=source_node_info['node_id'],
        source_node_type = source_node_info['type'],
        source_node_observability = source_node_info['observability'],
        source_node_label=source_node_info['label'],
        source_node_description=source_node_info['description'],
        target_node_id=target_node_info['node_id'],
        target_node_type=target_node_info['type'],
        target_node_observability=target_node_info['observability'],
        target_node_label=target_node_info['label'],
        target_node_description=target_node_info['description'],
        model_label = model_label,
        model_description = model_description
    )

    gpt_edge_rationality2 = ask_llm(prompt)
    er["second"].append(gpt_edge_rationality2)


    # elif setup_type == "third":
    source_node_info = get_node_descriptions(edge[0])
    target_node_info = get_node_descriptions(edge[1])

    ## Structured with Causality Decomposition
    from utils.cpg import ask_llm_response_schema
    from utils.prompts.edge_rationality import VERIFY_EDGE, EdgeVerification
    import json
    er["third"] = list()

    prompt = VERIFY_EDGE.format(
        source_id=source_node_info['node_id'],
        source_node_type = source_node_info['type'],
        source_node_observability = source_node_info['observability'],
        source_label=source_node_info['label'],
        source_description=source_node_info['description'],
        target_id=target_node_info['node_id'],
        target_node_type = target_node_info['type'],
        target_node_observability = target_node_info['observability'],
        target_label=target_node_info['label'],
        target_description=target_node_info['description'],
        model_label = model_label,
        model_description = model_description
    )

    gpt_edge_rationality1 = json.loads(ask_llm_response_schema(prompt, response_format=EdgeVerification))
    er["third"].append(gpt_edge_rationality1)

    # st.json(gpt_edge_rationality1, expanded=False)

    source_node_info = get_node_descriptions(edge[1])
    target_node_info = get_node_descriptions(edge[0])

    prompt = VERIFY_EDGE.format(
        source_id=source_node_info['node_id'],
        source_node_type = source_node_info['type'],
        source_node_observability = source_node_info['observability'],
        source_label=source_node_info['label'],
        source_description=source_node_info['description'],
        target_id=target_node_info['node_id'],
        target_node_type = target_node_info['type'],
        target_node_observability = target_node_info['observability'],
        target_label=target_node_info['label'],
        target_description=target_node_info['description'],
        # causal_relation_type="causes",
        model_label = model_label,
        model_description = model_description
    )

    gpt_edge_rationality2 = json.loads(ask_llm_response_schema(prompt, response_format=EdgeVerification))
    er["third"].append(gpt_edge_rationality2)

    # st.json(gpt_edge_rationality2, expanded=False)

    return er

def display_third_er(data):
    with st.container(border=True):
        # Edge Information
        # st.markdown("##### Edge")
        st.markdown(f"**Edge Relationship:** {data['edge']}")
        st.markdown(f"**Is Valid:** {data['is_valid']}")

        # Explanations Section
        st.markdown("##### Explanations")
        for explanation in data['explanation']:
            st.markdown(f"- {explanation}")

        # Causal Info Section
        st.markdown("##### Causal Information")
        causal_info = data['causal_info']
        st.markdown(f"**Causal Direction:** {causal_info['causal_direction']}")
        st.markdown(f"**Causal Factor :**   ")
        st.markdown(f"- **Necessary -** {causal_info['causal_factor']['necessary']}")
        st.markdown(f"- **Sufficient -** {causal_info['causal_factor']['sufficient']}")
        st.markdown(f"**Causal Distance:** {causal_info['causal_distance']}")
        st.markdown(f"**Probability Type:** {causal_info['probability_type']}")

        # Evidence Source Section
        st.markdown("##### Evidences Source")
        evidence_source = causal_info['evidences_source']
        st.markdown(f"**Guideline Name:** {evidence_source['guideline_name']}")
        st.markdown("**Facts and Recommendations:**")
        for fact in evidence_source['facts_and_recommendations']:
            st.markdown(f"- {fact}")

def display_edge_rationality(bn_model, model_type, model_label, model_description):
    edges = bn_model.edges()
    for edge in edges:
        edge_rationality_info = get_edge_rationality(edge)
        # st.write(edge_rationality_info)

        if edge_rationality_info:
            status_icon ="✅"
        else:
            status_icon = "🚫"

        if st.checkbox(f"{status_icon} {edge[0]} --> {edge[1]}", key=f"{model_type} - Edge Rationality - ({edge[0]})-->({edge[1]})"):
            source = edge[0]
            target = edge[1]
            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    display_node_information(source, "SOURCE", edge)
                with col2:
                    display_node_information(target, "TARGET", edge)

                if edge_rationality_info:
                    edge_rationality_info = edge_rationality_info["edge_rationality_info"]

                btn_er_info_gpt = st.button("Get Edge Rationality using GPT", key=f"GPT - {model_type} - Edge Rationality - ({edge[0]})-->({edge[1]})")

                if btn_er_info_gpt:
                    with st.spinner(f"Extracting Node information for edge '{edge}' ..."):
                        edge_rationality_info = get_edge_rationality_from_gpt(edge, model_label, model_description)
                        # st.json(edge_rationality_info, expanded=False)



                if not edge_rationality_info:
                    st.markdown("**No information on the edge rationality is available in our database.**")
                else:
                    with st.container(border=True):
                        st.markdown("#### First")
                        st.markdown(edge_rationality_info["first"])
                    #
                    # edge_rationality_info2 = get_edge_rationality_from_gpt(edge, "second")
                    #
                    with st.container(border=True):
                        st.markdown("#### Second")
                        st.markdown(edge_rationality_info["second"][0])
                        st.markdown("---")
                        st.markdown(edge_rationality_info["second"][1])
                    #
                    # edge_rationality_info3 = get_edge_rationality_from_gpt(edge, "third")
                    #
                    with st.container(border=True):
                        st.markdown("#### Third")
                        col1, col2 = st.columns(2)
                        with col1:
                            data = edge_rationality_info["third"][0]
                            # st.json(data, expanded=True)
                            display_third_er(data)
                        with col2:
                            data = edge_rationality_info["third"][1]
                            display_third_er(data)
                            # st.json(edge_rationality_info["third"][1], expanded=True)
                        # st.json(edge_rationality_info, expanded=False)
                    st.button("Save to Database", type="primary", on_click=save_to_db_callback, args=[edge, edge_rationality_info], key=f"Save to DB - {model_type} - Edge Rationality - ({edge[0]}, {edge[1]})")



##### START OF PAGE #####

st.markdown("#### Edge Rationality")

model_selected_flag = False

model_type = st.radio("Type of Network *", ["Ground Truth", "Work In Progress"], index=0, horizontal=True)
available_models = get_models(type=model_type)

model_names = [model['name'] for model in available_models]

if model_type == "Ground Truth":
    selected_model = st.selectbox("Select a ground truth model", model_names,
                                     key="Selected GT Model", index=None)
    model = get_model_by_name(selected_model)
    if model:
        model_selected_flag = True

else:
    selected_model = st.selectbox("Select a work in progress model", model_names,
                                  key="Selected WIP Model", index=None)
    model = get_model_by_name(selected_model)
    if model:
        model_selected_flag = True


if not model_selected_flag:
    st.write("**Please select a Model.**")
else:
    try:
        nodes_contents = model['nodes_content']
        model_bn = build_network(nodes_contents)

        if model_type == "Work In Progress":
            from utils.models import reverse_bayesian_network
            model_bn = reverse_bayesian_network(model_bn)

        st.info(model_bn)
    except Exception as e:
        st.error(f"ERROR: \n{str(e)}")

    display_edge_rationality(model_bn, model_type, model['label'], model['description'])