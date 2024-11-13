import streamlit as st

from utils.file import xdsl_to_digraph, convert_to_vis_super, build_network
from utils.db import get_models, get_model_by_name, update_model_label_description, \
    get_node_descriptions, get_entities_of_model, get_entity_by_id
from utils.components import frag_edge_cpd_rank
from utils.edges import edge_schema_validation_check
from utils.nodes import get_nodes_by_type

#### START OF PAGE

st.markdown("#### Ground Truth Model")

model_type = "Ground Truth"
available_models = get_models(type=model_type)

model_names = [model['name'] for model in available_models]

selected_model = st.selectbox("Select a ground truth model", model_names,
                                 key="Selected GT Model", index=None)
model = get_model_by_name(selected_model)

if not model:
    st.write("**Please select a Ground Truth Model.**")
else:
    selected_gt_model_graph = xdsl_to_digraph(model['file_content'])
    convert_to_vis_super(selected_gt_model_graph)

    # Building the BN for this super graph
    try:
        nodes_contents = model['nodes_content']
        bn_model = build_network(nodes_contents)
        st.info(bn_model)

    except Exception as e:
        st.error(f"ERROR: \n{str(e)}")

    with st.expander("View Graph"):
        path = "dashboard/pyvis_htmls/super_model.html"
        HtmlFile = open(path, 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        st.components.v1.html(source_code, height=1000, width=1000, scrolling=True)

    ##### EDGE RANKINGS #####
    st.markdown("#### Edge Rankings")
    with st.container(border=True):
        # 1. Using Dataset stats (G-Test)
        if st.checkbox("Compute Edge Strength (G-Test)"):
            # TODO: Link with appropriate Dataset
            # frag_g_test(nodes_contents, key="gt_g_test")
            pass

        # 2. Using CPDs of the Bayesian Network
        if st.checkbox("Compute Edge Strength (Using CPDs)", key="gt_cpd_rank"):
            frag_edge_cpd_rank(bn_model, key="Ground Truth Model")


    ##### EDGE SCHEMA VALIDATION CHECK #####
    st.markdown("#### Edge Schema Validation Check")
    with st.container(border=True):
        if st.checkbox("Check Schema Valid Edges"):
            schema_validation_result = edge_schema_validation_check(bn_model, nodes_contents)
            st.markdown("**Valid Edges:**")
            st.json(schema_validation_result["valid"], expanded=False)
            st.markdown("**Invalid Edges:**")
            st.json(schema_validation_result["invalid"], expanded=False)


    ##### NODE RANKINGS #####
    st.markdown("#### Node Rankings")
    with st.container(border=True):
        # 1. PageRank
        if st.checkbox("Compute Node Strength (PageRank)"):
            from utils.nodes import compute_page_rank
            st.dataframe(compute_page_rank(bn_model))


    ##### NODE TYPES #####
    st.markdown("#### Node Types")
    with st.container(border=True):
        if st.checkbox("Check Node Types"):
            node_type = st.radio("Select Node Type:", ["Patient Situation", "Examination Result", "Decision Node", "Unknown"], index=0, horizontal=True)

            nodes_by_type = get_nodes_by_type(node_type, nodes_contents)
            st.write(nodes_by_type)


    ##### NODE TO ENTITY MAPPINGS
    nodes_having_entity = []
    nodes_not_having_entity = []
    st.markdown("#### Node to Entity Mappings")
    with st.container(border=True):
        if st.checkbox("Check Entity to Node Mappings"):
            for node in bn_model.nodes():
                node_desc = get_node_descriptions(node)

                if node_desc is None:
                    nodes_not_having_entity.append(node)
                    continue

                if node_desc['entity_information']:
                    nodes_having_entity.append(node_desc)
                else:
                    nodes_not_having_entity.append(node)

            all_entities_of_model_df = get_entities_of_model(bn_model)
            # st.dataframe(all_entities_of_model_df)

            with st.container(border=True):
                st.markdown("**Nodes having entity information:**")
                ontology_name = st.radio("Select Ontology Name:", ["MeSH", "SNOMED-CT", "Wikidata"], index=0, horizontal=True)
                st.markdown("**Selected Ontology Name:** &emsp; " + ontology_name)

                nodes_with_selected_ontology = all_entities_of_model_df[all_entities_of_model_df["ontology_name"] == ontology_name]

                # st.write(nodes_with_selected_ontology)

                distinct_entity_ids = nodes_with_selected_ontology['entity_id'].unique()
                # distinct_entity_labels = nodes_with_selected_ontology['entity_label'].unique()

                for entity_id in distinct_entity_ids:
                    with st.container(border=True):
                        entity_info = get_entity_by_id(entity_id)
                        # st.write(entity_info)
                        st.markdown(f"**Entity Name :** &emsp; {entity_info['label']}")
                        st.markdown(f"**Entity Description :** &emsp; {entity_info['description']}")

                        nodes_with_current_entity = nodes_with_selected_ontology[nodes_with_selected_ontology['entity_id'] == entity_id]
                        st.write(list(nodes_with_current_entity['nodes_list']))

                # from utils.nodes import get_distinct_entities, get_nodes_by_entity
                # from utils.db import get_distinct_entities
                # distinct_entities = get_distinct_entities()


                # for entity in distinct_entities:
                #     with st.container(border=True):
                #         st.markdown(f"**Entity Name:** &emsp; {entity}")
                #         st.write(get_nodes_by_entity(entity, nodes_having_entity))

                # for node_desc in nodes_having_entity:
                #     st.markdown(f"**{node_desc['node_id']}**")
                #     for entity_info in node_desc['entity_information']:
                #         st.markdown(f"- **{entity_info['ontology_name']} :** {entity_info['label']}")

            with st.container(border=True):
                st.markdown("**Nodes not having entity information:**")
                st.json(nodes_not_having_entity, expanded=False)