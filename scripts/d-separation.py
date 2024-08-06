from pgmpy.models import BayesianNetwork

# Define the Bayesian Network structure
bn = BayesianNetwork([
    ('X', 'Y'),
    ('Y', 'Z'),
    ('X', 'Z')  # This is the potentially redundant edge
])

# Function to check for d-separation
def check_d_separation(model, X, Y, Z):
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
edge_to_check = ('X', 'Z')
X = 'X'
Y = 'Z'
Z = ['Y']

is_redundant = is_edge_redundant(bn, edge_to_check, X, Y, Z)
print(f"Is the edge {edge_to_check} redundant? {is_redundant}")
