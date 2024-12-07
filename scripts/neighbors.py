from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD

# Create a simple Bayesian network
bn = BayesianNetwork()
bn.add_node('A')
bn.add_node('B')
bn.add_node('C')
bn.add_edge('A', 'B')
bn.add_edge('B', 'C')

# Get all connected nodes of node B
node = 'B'
connected_nodes = bn.neighbors(node)
cn_list = [cn for cn in connected_nodes]

print(f"All connected nodes of {cn_list}:")

# You can also get parents and children separately
parents = bn.get_parents(node)
children = bn.get_children(node)

print(f"\nParents of {node}: {parents}")
print(f"Children of {node}: {children}")