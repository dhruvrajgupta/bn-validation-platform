import xmltodict
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
import numpy as np

def parse_xdsl(file_path):
    """
    This function parses an XDSL file and returns a dictionary of nodes.

    Parameters:
        file_path (str): The path to the XDSL file to be parsed.

    Returns:
        dict: A dictionary where each key is a node ID and each value is another dictionary
            containing the node's states, parents, and probabilities.
    """
    nodes = {}
    with open(file_path, 'r') as f:
        xdsl_content = f.read()
    # print(xdsl_content)
    xdsl_dict = xmltodict.parse(xdsl_content)
    nodes_contents = xdsl_dict['smile']['nodes']['cpt']

    if isinstance(nodes_contents, list):
        for node in nodes_contents:
            # print(node)
            node_id = node['@id']
            # print(node_id)

            states_content = node['state']
            states = []
            parents_contents = node.get('parents', [])
            parents = []
            probabilities = [float(x) for x in node['probabilities'].split(" ")]

            if isinstance(states_content, list):
                for state in states_content:
                    state = state['@id']
                    states.append(state)

            if parents_contents:
                parents.extend(parents_contents.split(" "))

            # print(probabilities)
            # print(parents)
            nodes[node_id] = {
                'states': states,
                'parents': parents,
                'probabilities': probabilities
            }
            # import json
            # print(json.dumps(nodes[node_id], indent=2))
    return nodes


def build_network(nodes):
    model = BayesianNetwork()

    # Add nodes and edges
    for node_id, details in nodes.items():
        model.add_node(node_id)
        for parent in details['parents']:
            model.add_edge(parent, node_id)

    # Add CPDs
    for node_id, details in nodes.items():
        node_states_card = len(details['states'])
        parents = details['parents']
        parent_states = [len(nodes[parent]['states']) for parent in parents]
        values = details['probabilities']

        state_names = {}

        if parents:
            num_of_cols = node_states_card
            # num_of_cols = int(len(values)/states)
            num_of_rows = int(len(values) / node_states_card)
            x = np.array(values)
            x = x.reshape(num_of_rows, num_of_cols)
            su = x.sum(axis=1)
            x = x.transpose()
            values = x
            # values = x.tolist()
            # values = [values[i:i + states] for i in range(0, len(values), states)]
        else:
            values = [[value] for value in values]
            values = np.array(values)
            su = values.sum(axis=0)

        state_names[node_id] = details['states']
        if parents:
            for parent in parents:
                state_names[parent] = nodes[parent]['states']

        # print(f"Node_ID: {node_id}")
        # print(f"Node States Cardinality: {node_states_card}")
        # print(f"Evidence / Parents: {parents}")
        # print(f"Evidence Cardinality: {parent_states}")
        # print(f"State Names: {json.dumps(state_names, indent=2)}")
        # print(f"CPD Values: \n{values}")
        # print("-" * 50)

        cpd = TabularCPD(variable=node_id, variable_card=node_states_card, values=values,
                         evidence=parents, evidence_card=parent_states, state_names=state_names)
        model.add_cpds(cpd)

    return model

def euclidean_distance(p, q):
    # print("P values:")
    # print(p.get_values())
    # print("Q values:")
    # print(q.get_values())
    # print()

    p_vals = p.get_values().transpose()
    q_vals = q.get_values().transpose()

    p_row_before = p_vals.shape[0]

    # print("P Transpose:")
    # print(p_vals)
    # print("Q Transpose:")
    # print(q_vals)

    # Match Col of P with Row of Q
    p_row, p_col = p_vals.shape
    q_row, q_col = q_vals.shape

    if q_row > p_col:
        # print("Tiling P to match Q")
        p_tile_repeat = q_row // p_col
        p_vals = np.tile(p_vals, (p_tile_repeat, 1))
    elif q_row < p_col:
        # Change P to Q
        euclidean_distance(q, p)

    # print(p_vals)
    # print(p_vals.shape)
    # print(q_vals)
    # print(q_vals.shape)

    # P Repeat = no. of columns of q or no of states of q
    p_repeat = q_vals.shape[1]
    # print(f"P repeat: {p_repeat}")
    p_flat = np.repeat(p_vals, p_repeat)
    # print(p_flat)
    # print(f"Lenght of P Flat: {len(p_flat)}")
    
    # Q repeat = no of rows of p
    q_repeat = p_row_before
    # print(f"Q repeat: {q_repeat}")
    q_tiled = np.tile(q_vals, (q_repeat, 1))
    # print("Q tiled shape: ",q_tiled.shape)
    q_flat = q_tiled.flatten()
    # print(q_flat)
    # print(f"Q Flat Length: {len(q_flat)}")

    if len(p_flat) != len(q_flat):
        raise Exception("The two distributions number of elements mismatch.")
    
    # print()
    # s = 0
    # for i in range(len(p_flat)):
    #     # print(p_flat[i], q_flat[i])
    #     diff = (p_flat[i] - q_flat[i]) ** 2
    #     # print(diff)
    #     s += diff
    # print(f"Sum: {s}")
    # print(f"SQRT: {np.sqrt(s)}")
    # Calculate the Euclidean distance
    distance = np.sqrt(np.sum((p_flat - q_flat) ** 2))
    # print(distance)
    # return distance
    # print("-"*50)
    return distance


def euclidean_distance_marginalization(p, q):
    # print("="*50)
    # print("MARGINALIZATION")
    #     p_evidence = cpd_p.get_evidence()
    # print(p_evidence)
    # cpd_p = cpd_p.marginalize(p_evidence, inplace=False)
    # print(cpd_p)
    # print(cpd_p.variable)

    # q_evidence = cpd_q.get_evidence()
    # q_evidence.remove(cpd_p.variable)
    # print(q_evidence)
    # if q_evidence:
    #     cpd_q = cpd_q.marginalize(q_evidence, inplace=False)
    # print(cpd_q)

    # p_flat = cpd_p.get_values().flatten()
    # print(p_flat)
    # q_flat = cpd_q.get_values().flatten()
    # print(q_flat)

    # if len(p_flat) < len(q_flat):
    #     p_flat = np.pad(p_flat, (0, len(q_flat) - len(p_flat)), 'constant')
    # else:
    #     q_flat = np.pad(q_flat, (0, len(p_flat) - len(q_flat)), 'constant')

    # print(p_flat)
    # print(q_flat)

    # distance = np.sqrt(np.sum(p_flat - q_flat) ** 2)
    # print(distance)


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

    distance = np.sqrt(np.sum((p_flat - q_flat) ** 2))
    # print(distance)

    # print("="*50)
    return distance

def euclidean_distance_marginalization_avg(p, q):
    ##### PROMPT #### DeepSeekCoder
    # i have two nodes 'P' and 'Q', node 'P' has 2 states where as node 'Q' has 3 states. 
    # P and Q are part of Directed Acyclic Graph where 'P' --> 'Q'. 'P' and 'Q' both have conditional probability tables. 
    # I want to find the euclidean distance between conditional probability distribution 'P' and conditional probability distribution 'Q'.
    ##################


    # print("="*50)
    # print("MARGINALIZATION")
    #     p_evidence = cpd_p.get_evidence()
    # print(p_evidence)
    # cpd_p = cpd_p.marginalize(p_evidence, inplace=False)
    # print(cpd_p)
    # print(cpd_p.variable)

    # q_evidence = cpd_q.get_evidence()
    # q_evidence.remove(cpd_p.variable)
    # print(q_evidence)
    # if q_evidence:
    #     cpd_q = cpd_q.marginalize(q_evidence, inplace=False)
    # print(cpd_q)

    # p_flat = cpd_p.get_values().flatten()
    # print(p_flat)
    # q_flat = cpd_q.get_values().flatten()
    # print(q_flat)

    # if len(p_flat) < len(q_flat):
    #     p_flat = np.pad(p_flat, (0, len(q_flat) - len(p_flat)), 'constant')
    # else:
    #     q_flat = np.pad(q_flat, (0, len(p_flat) - len(q_flat)), 'constant')

    # print(p_flat)
    # print(q_flat)

    # distance = np.sqrt(np.sum(p_flat - q_flat) ** 2)
    # print(distance)


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
    return distance

def euclidean_distance_marginalization_avg_normalized(p, q):
    distance = euclidean_distance_marginalization_avg(p, q)
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