from utils.edges import edge_strength_cpds
import networkx as nx
import pandas as pd

def get_nodes_by_type(node_type, nodes_contents):
    nodes_list = []
    for node, node_content in nodes_contents.items():
        if node_content['node_type'] == node_type:
            nodes_list.append(node)
    return nodes_list

def get_distinct_entities(ontology_name, nodes_having_entity):
    print(ontology_name)
    distinct_entity_list = []
    for node_desc in nodes_having_entity:
        for node_entity_list in node_desc['entity_information']:
            if node_entity_list['ontology_name'] == ontology_name:
                distinct_entity_list.append(node_entity_list['label'])

    # Return only the distinct entities
    print(list(set(distinct_entity_list)))
    return list(set(distinct_entity_list))

def get_nodes_by_entity(entity_name, nodes_having_entity):
    print(entity_name)
    nodes_list = []
    for node_desc in nodes_having_entity:
        for node_entity_list in node_desc['entity_information']:
            if node_entity_list['label'] == entity_name:
                nodes_list.append(node_desc['node_id'])

    print(nodes_list)
    return nodes_list

def compute_page_rank(bn_model):
    # Edge Weight is important, otherwise by default it is 1
    # and on computing pagerank will then raise Exception
    #raise nx.PowerIterationFailedConvergence(max_iter)
    # networkx.exception.PowerIterationFailedConvergence: (PowerIterationFailedConvergence(...), 'power iteration failed to converge within 100 iterations')

    # pagerank with J-Divergence does not converge even if max_iter is set to 10000000

    # So dont support J-Divergence

    G = nx.DiGraph()
    edge_strength = edge_strength_cpds(bn_model, "Euclidean")
    for index, row in edge_strength.iterrows():
        # print(row["source"])
        # print(row["target"])
        # print(row["distance"])
        G.add_edge(row["source"], row["target"], weight=row["distance"])

    pr = nx.pagerank(G, weight="weight")

    pagerank_df = pd.DataFrame(list(pr.items()), columns=["node_id", "pagerank"])
    pagerank_df = pagerank_df.sort_values("pagerank", ascending=False)
    pagerank_df["rank"] = range(1, len(pagerank_df) + 1)

    pagerank_df = pagerank_df[["rank", "node_id", "pagerank"]]

    # fig = show_pagerank_distribution(pagerank_df)

    return pagerank_df
    # return pagerank_df, fig

def show_pagerank_distribution(pagerank_df):
    # Plot the distribution of PageRank values
    import matplotlib.pyplot as plt
    import seaborn as sns
    fig = plt.figure(figsize=(12, 6))

    # Histogram
    plt.subplot(1, 2, 1)
    sns.histplot(pagerank_df['pagerank'], kde=True, color='blue')
    plt.title('Histogram of PageRank Values')
    plt.xlabel('PageRank Value')
    plt.ylabel('Frequency')

    # Box Plot
    plt.subplot(1, 2, 2)
    sns.boxplot(y=pagerank_df['pagerank'], color='orange')
    plt.title('Box Plot of PageRank Values')
    plt.ylabel('PageRank Value')

    plt.tight_layout()
    plt.show()

    print(fig)
    return fig

def source_connected_nodes(bn_model, node_id):
    nodes_list = []
    for edge in bn_model.edges():
        source_node = edge[0]
        if source_node == node_id:
            nodes_list.append(edge[1])

    if nodes_list:
        return nodes_list
    else:
        return None

def target_connected_nodes(bn_model, node_id):
    nodes_list = []
    for edge in bn_model.edges():
        source_node = edge[1]
        if source_node == node_id:
            nodes_list.append(edge[0])

    if nodes_list:
        return nodes_list
    else:
        return None