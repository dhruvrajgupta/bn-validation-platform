# from pgmpy.models import BayesianNetwork

# # Define the Bayesian Network structure
# bn = BayesianNetwork([
#     ('X', 'Y'),
#     ('Y', 'Z'),
#     ('X', 'Z')  # This is the potentially redundant edge
# ])

# # Function to check for d-separation
# def check_d_separation(model, X, Y, Z):
#     return not model.is_dconnected(X, Y, Z)

# # Function to check if an edge is redundant
# def is_edge_redundant(model, edge, X, Y, Z):
#     # Check conditional independence before removing the edge
#     before_removal = check_d_separation(model, X, Y, Z)

#     # Remove the edge
#     model.remove_edge(*edge)

#     # Check conditional independence after removing the edge
#     after_removal = check_d_separation(model, X, Y, Z)

#     # Add the edge back to the model
#     model.add_edge(*edge)

#     # If removing the edge does not affect d-separation, it is redundant
#     return before_removal == after_removal

# # Example usage
# edge_to_check = ('X', 'Z')
# X = 'X'
# Y = 'Z'
# Z = ['Y']

# is_redundant = is_edge_redundant(bn, edge_to_check, X, Y, Z)
# print(f"Is the edge {edge_to_check} redundant? {is_redundant}")

# from pgmpy.models import BayesianNetwork

# # Define the Bayesian Network structure
# bn = BayesianNetwork([
#     ('A', 'B'),
#     ('B', 'C'),
#     ('C', 'D'),
#     ('A', 'C')  # This is the potentially redundant edge
# ])

# # Function to check for d-separation
# def check_d_separation(model, X, Y, Z):
#     # Returns True if X and Y are independent given Z (i.e., d-separated)
#     return not model.is_dconnected(X, Y, Z)

# # Function to check if an edge is redundant
# def is_edge_redundant(model, edge, X, Y, Z):
#     # Check conditional independence before removing the edge
#     before_removal = check_d_separation(model, X, Y, Z)

#     # Remove the edge
#     model.remove_edge(*edge)

#     # Check conditional independence after removing the edge
#     after_removal = check_d_separation(model, X, Y, Z)

#     # Add the edge back to the model
#     model.add_edge(*edge)

#     # If removing the edge does not affect d-separation, it is redundant
#     return before_removal == after_removal

# # Example usage
# edge_to_check = ('A', 'C')
# X = 'A'
# Y = 'C'
# Z = ['D']  # Conditioning on C

# # Check if the edge ('A', 'C') is redundant
# is_redundant = is_edge_redundant(bn, edge_to_check, X, Y, Z)
# print(f"Is the edge {edge_to_check} redundant? {is_redundant}")


from pgmpy.models import BayesianNetwork

# Define the Bayesian Network structure
bn = BayesianNetwork([
    ('Burglary', 'Alarm'),
    ('Earthquake', 'Alarm'),
    ('Alarm', 'JohnCalls'),
    ('Alarm', 'MaryCalls'),
    ('Burglary', 'Earthquake'),
    # Burglary and Earthquake were already independent in the original graph unless conditioned on Alarm.
    # The new edge does not change this independence, as the two variables are still blocked by the collider at the Alarm unless the Alarm is observed.
    # Therefore, this edge does not add new information or change the probabilistic relationships between variables. It’s redundant in terms of the conditional independencies in the graph.
])

# Define the Bayesian Network structure
# bn = BayesianNetwork([
#     ('A', 'B'),
#     ('B', 'C'),
#     ('C', 'D'),
#     ('A', 'C')  # This is the potentially redundant edge
# ])

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

# Example usage
# edge_to_check = ('A', 'C')
# X = 'A'
# Y = 'C'
# Z = ['D']  # Conditioning on C

nodes = [node for node in bn.nodes()]
print(nodes)

import itertools

# for i in range(len(nodes)):
#     # print(itertools.combinations(nodes, i))
#     for combination in itertools.combinations(nodes, i):
#         print(combination)
#     print()

for edge in bn.edges():
    is_redundant_list_given_variables = []
    X = edge[0]
    Y = edge[1]
    print(f"Edge: {edge}")
    nodes_cp = nodes.copy()
    nodes_cp.remove(edge[0])
    nodes_cp.remove(edge[1])
    print(f"Remaining Nodes List: {nodes_cp}")

    for i in range(len(nodes_cp)):
        for combination in itertools.combinations(nodes_cp, i):
            print(list(combination))
            Z = list(combination)
            if not Z:
                continue

            # Check if the edge ('A', 'C') is redundant
            is_redundant = is_edge_redundant(bn.copy(), edge, X, Y, Z)
            print(f"Is the edge {edge} redundant given {list(combination)}? {is_redundant}")
            is_redundant_list_given_variables.append(is_redundant)
        print()
    
    print("FINALLY:")
    print(f"Is the edge {edge} redundant? {all(is_redundant_list_given_variables)}")
    print("="*50)

    # Get all combinations of nodes

# Check if the edge ('A', 'C') is redundant
# is_redundant = is_edge_redundant(bn, edge_to_check, X, Y, Z)
# print(f"Is the edge {edge_to_check} redundant? {is_redundant}")