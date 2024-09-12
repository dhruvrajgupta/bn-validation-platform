import networkx as nx
from streamlit_agraph import agraph, Node, Edge, Config
from pgmpy.models import BayesianNetwork
import itertools
import bnlearn
import pandas as pd
import numpy as np

def find_redundant_edges_multiple_paths(graph):
    def is_redundant_edge(G, edge):
        # Checking if removal of edges still has connectivity
        G_prime = G.copy()
        G_prime.remove_edge(*edge)
        # Check if there is still a path between the nodes
        is_redundant = nx.has_path(G_prime, edge[0], edge[1])
        return is_redundant

    redundant_edges  = [edge for edge in graph.edges() if is_redundant_edge(graph, edge)]

    return redundant_edges

def print_multiple_paths(graph, redundant_edges):
    output = ""
    for index, edge in enumerate(redundant_edges):
        output += f"Edge #{index + 1}: {edge}\n"
        output += "-" * 100 + "\n"
        for index, path in enumerate(nx.all_simple_paths(graph, edge[0], edge[1])):
            output += f"Path #{index + 1}: {path}\n"
        output += "\n"

    return output

def redundant_edges_digraph(graph, redundant_edges):
    G = nx.DiGraph()
    for edge in redundant_edges:
        for path in nx.all_simple_paths(graph, edge[0], edge[1]):
            for i in range(len(path) - 1):
                G.add_edge(path[i], path[i + 1])

    nodes = []
    edges = []
    for node in G.nodes:
        nodes.append(Node(id=node, label=node))
    for edge in G.edges:
        edges.append(Edge(source=edge[0], target=edge[1]))

    config = Config(width=1000, height=600, directed=True, physics=True)
    return agraph(nodes=nodes, edges=edges, config=config)

def find_redundant_edges_d_separation(graph, debug=False):

    import time
    start = time.time()
    print(f"Start: {start}")

    # Function to check for d-separation
    def check_d_separation(model, X, Y, Z):
        # Returns True if X and Y are independent given Z (i.e., d-separated)
        return not model.is_dconnected(X, Y, Z)

    # Function to check if an edge is redundant
    def is_edge_redundant(model, edge, X, Y, Z):
        # Check conditional independence before removing the edge
        before_removal = check_d_separation(model, X, Y, Z)

        # Remove the edge
        model.remove_edge(*edge)

        # Check conditional independence after removing the edge
        after_removal = check_d_separation(model, X, Y, Z)

        # Add the edge back to the model
        model.add_edge(*edge)

        # If removing the edge does not affect d-separation, it is redundant
        return before_removal == after_removal

    # graph = BayesianNetwork([
    #     ('Burglary', 'Alarm'),
    #     ('Earthquake', 'Alarm'),
    #     ('Alarm', 'JohnCalls'),
    #     ('Alarm', 'MaryCalls'),
    #     ('Burglary', 'Earthquake'), # <-- Redundant Edge
    #     # Burglary and Earthquake were already independent in the original graph unless conditioned on Alarm.
    #     # The new edge does not change this independence, as the two variables are still blocked by the collider at the Alarm unless the Alarm is observed.
    #     # Therefore, this edge does not add new information or change the probabilistic relationships between variables. It’s redundant in terms of the conditional independencies in the graph.
    # ])

    # List of redundant edges
    redundant_edges = []

    # List of nodes in the graph
    nodes = [node for node in graph.nodes()]

    # Checking each edge in the graph
    for edge in graph.edges():
        X = edge[0]
        Y = edge[1]

        # Removing the nodes already in the edge
        nodes_cp = nodes.copy()
        nodes_cp.remove(edge[0])
        nodes_cp.remove(edge[1])

        # Accumulating list that aggregrates is edge redundant given a set of variables
        # Only When all is True the edge is truly redundant given all combination of variables
        is_edge_redundant_given_variables = []

        flag_combi_break = False
        for i in range(len(nodes_cp)):
            if flag_combi_break:
                break
            for combination in itertools.combinations(nodes_cp, i):
                Z = list(combination)
                if not Z:
                    continue

                # Check if the edge is redundant
                is_redundant = is_edge_redundant(graph.copy(), edge, X, Y, Z)
                if is_redundant == False:
                    flag_combi_break = True
                    is_edge_redundant_given_variables.append(is_redundant)
                    break
                # if debug:
                #     print(f"Is the edge {edge} redundant given {list(combination)}? {is_redundant}")
                is_edge_redundant_given_variables.append(is_redundant)

        if debug:
            print(f"Is the edge {edge} redundant? {all(is_edge_redundant_given_variables)}")
        if all(is_edge_redundant_given_variables):
            redundant_edges.append(edge)

    end = time.time()
    print(f"End: {end}")
    print(f"Time: {end - start}")

    return redundant_edges


def edge_strength_stats(model):
    cpds = model.get_cpds()
    model = bnlearn.make_DAG(DAG=model, CPD=cpds, verbose=0)

    dataset_paths = [
        "./../datasets/40percent.csv",
        "./../datasets/60percent.csv",
        "./../datasets/80percent.csv",
        "./../datasets/100percent.csv",
    ]

    df = pd.read_csv(dataset_paths[3])

    model = bnlearn.independence_test(model, df, test="g_sq")
    # # The G-test is often preferred over the Chi-square test when dealing with smaller sample sizes or when the data involves counts.

    # print(model.keys())
    return model['independence_test']

def edge_strength_cpds(model, distance_type):

    # TODO: Investigate the distance values

    source_list = []
    target_list = []
    distance_list = []

    for edge in model.edges():
        p = edge[0]
        q = edge[1]

        source_list.append(p)
        target_list.append(q)

        p = model.get_cpds(p)
        q = model.get_cpds(q)

        if distance_type == "Euclidean":
            distance = euclidean_distance(p, q)
        elif distance_type == "Hellinger":
            distance = hellinger_distance(p, q)
        elif distance_type == "J-Divergence":
            distance = j_divergence_distance(p, q)
        elif distance_type == "CDF":
            distance = cdf_distance(p, q)

        distance_list.append(distance)

    df = pd.DataFrame(data={"source": source_list, "target": target_list, "distance": distance_list})
    return df

def euclidean_distance(p, q):

    # Marginalization of P
    p_evidence = p.get_evidence()
    # print(f"P: {p.variable}")
    # print(f"P evidence: {p_evidence}")
    p = p.marginalize(variables=p_evidence, inplace=False)

    # print(p)

    q_evidence = q.get_evidence()
    # print(f"Q: {q.variable}")
    # print(f"Q evidence: {q_evidence}")
    q_evidence.remove(p.variable)
    q = q.marginalize(q_evidence, inplace=False)

    # print(q)

    p_vals = p.get_values().transpose()
    q_vals = q.get_values().transpose()

    # Num of Columns of Q
    p_repeat = q_vals.shape[1]
    p_flat = np.repeat(p_vals, p_repeat)
    # print(f"P Flat: {p_flat}")

    q_flat = q_vals.flatten()
    # print(f"Q Flat: {q_flat}")

    # print(f"Len P Flat: {len(p_flat)}")
    # print(f"Len Q Flat: {len(q_flat)}")

    if len(p_flat) != len(q_flat):
        raise Exception("The two distributions number of elements mismatch.")

    sub_square = np.subtract(p_flat, q_flat) ** 2
    # print(sub_square)
    num_rows = p_vals.shape[1]
    num_cols = len(sub_square)//num_rows
    sub_square = sub_square.reshape(num_rows, num_cols)
    # print(sub_square)
    x_sum = np.sum(sub_square, axis=1)
    # print(x_sum)
    distance = np.mean(x_sum)
    # print(mean)

    # distance = np.sqrt(np.sum((p_flat - q_flat) ** 2))
    # print(distance)

    # print("="*50)
    return distance/np.sqrt(2)

def hellinger_distance(p, q):
    # Marginalization of P
    p_evidence = p.get_evidence()
    # print(f"P: {p.variable}")
    # print(f"P evidence: {p_evidence}")
    p = p.marginalize(variables=p_evidence, inplace=False)

    # print(p)

    q_evidence = q.get_evidence()
    # print(f"Q: {q.variable}")
    # print(f"Q evidence: {q_evidence}")
    q_evidence.remove(p.variable)
    q = q.marginalize(q_evidence, inplace=False)

    # print(q)

    p_vals = p.get_values().transpose()
    q_vals = q.get_values().transpose()

    # Num of Columns of Q
    p_repeat = q_vals.shape[1]
    p_flat = np.repeat(p_vals, p_repeat)
    # print(f"P Flat: {p_flat}")

    q_flat = q_vals.flatten()
    # # print(f"Q Flat: {q_flat}")

    # print(f"Len P Flat: {len(p_flat)}")
    # print(f"Len Q Flat: {len(q_flat)}")

    if len(p_flat) != len(q_flat):
        raise Exception("The two distributions number of elements mismatch.")

    distance = np.sqrt(np.sum(np.subtract(np.sqrt(p_flat), np.sqrt(q_flat)) ** 2))
    return distance/np.sqrt(2)

def j_divergence_distance(p, q):
    # Marginalization of P
    p_evidence = p.get_evidence()
    # print(f"P: {p.variable}")
    # print(f"P evidence: {p_evidence}")
    p = p.marginalize(variables=p_evidence, inplace=False)

    # print(p)

    q_evidence = q.get_evidence()
    # print(f"Q: {q.variable}")
    # print(f"Q evidence: {q_evidence}")
    q_evidence.remove(p.variable)
    q = q.marginalize(q_evidence, inplace=False)

    # print(q)

    p_vals = p.get_values().transpose()
    q_vals = q.get_values().transpose()

    # Num of Columns of Q
    p_repeat = q_vals.shape[1]
    p_flat = np.repeat(p_vals, p_repeat)
    # print(f"P Flat: {p_flat}")

    q_flat = q_vals.flatten()
    # # print(f"Q Flat: {q_flat}")

    # print(f"Len P Flat: {len(p_flat)}")
    # print(f"Len Q Flat: {len(q_flat)}")

    if len(p_flat) != len(q_flat):
        raise Exception("The two distributions number of elements mismatch.")

    kl_distance_p_q = - np.sum(np.multiply(p_flat, np.log2(q_flat))) + np.sum(np.multiply(p_flat, np.log2(p_flat)))
    kl_distance_q_p = - np.sum(np.multiply(q_flat, np.log2(p_flat))) + np.sum(np.multiply(q_flat, np.log2(q_flat)))

    # Parameter to control smoothness
    alpha = 10

    if np.any(q_flat == 0):
        return 1
    else:
        j_divergence = (kl_distance_p_q + kl_distance_q_p)/2
        j_divergence_norm = j_divergence/np.sqrt((j_divergence ** 2) + alpha)
        return j_divergence_norm


def cdf_distance(p, q):

    # The CDF distance is a good choice when there are ordinal nodes, because it represents the shift of probability
    # according to the cumulative probability functions of the two distributions.
    # Ordinal: if the states are ordered from left to right, from less important to most important

    # p = np.array([0,0,1,0])
    # print(p)
    # p = np.cumsum(p)
    # print(p)
    # q = np.array([0.1, 0, 0, 0.9])
    # print(q)
    # q = np.cumsum(q)
    # print(q)
    # print(p.shape)
    # no_elements = p.shape[0]
    #
    # cum_diff = np.absolute(np.subtract(p, q))
    # print(cum_diff)
    # distance = np.sum(cum_diff)
    # multiplier = 1/(no_elements - 1)

    # Marginalization of P
    p_evidence = p.get_evidence()
    # print(f"P: {p.variable}")
    # print(f"P evidence: {p_evidence}")
    p = p.marginalize(variables=p_evidence, inplace=False)

    # print(p)

    q_evidence = q.get_evidence()
    # print(f"Q: {q.variable}")
    # print(f"Q evidence: {q_evidence}")
    q_evidence.remove(p.variable)
    q = q.marginalize(q_evidence, inplace=False)

    # print(q)

    p_vals = p.get_values().transpose()
    q_vals = q.get_values().transpose()

    # Num of Columns of Q
    p_repeat = q_vals.shape[1]
    p_flat = np.repeat(p_vals, p_repeat)
    # print(f"P Flat: {p_flat}")

    q_flat = q_vals.flatten()
    # # print(f"Q Flat: {q_flat}")

    # print(f"Len P Flat: {len(p_flat)}")
    # print(f"Len Q Flat: {len(q_flat)}")

    if len(p_flat) != len(q_flat):
        raise Exception("The two distributions number of elements mismatch.")

    p_flat = np.cumsum(p_flat)
    q_flat = np.cumsum(q_flat)

    no_elements = p_flat.shape[0]

    cum_diff = np.absolute(np.subtract(p_flat, q_flat))
    distance = np.sum(cum_diff)
    multiplier = 1 / (no_elements - 1)

    return multiplier * distance

def g_test_rank_edges(dataframe):
    df = dataframe.copy(deep=True)
    df = df.drop(['stat_test', 'p_value', 'dof'], axis=1)
    df = df.sort_values(by='g_sq', ascending=False)
    df['rank'] = range(1, df.shape[0] + 1)

    # Placing Rank as the first column
    rank = df['rank']
    df.drop(labels=['rank'], axis=1, inplace=True)
    df.insert(0, 'rank', rank)
    return df

def cpd_rank_edges(dataframe):
    df = dataframe.copy(deep=True)
    df = df.sort_values(by='distance', ascending=False)
    df['rank'] = range(1, df.shape[0] + 1)

    # Placing Rank as the first column
    rank = df['rank']
    df.drop(labels=['rank'], axis=1, inplace=True)
    df.insert(0, 'rank', rank)
    return df