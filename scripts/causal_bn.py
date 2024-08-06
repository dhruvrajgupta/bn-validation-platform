from pgmpy.models.BayesianNetwork import BayesianNetwork
from pgmpy.inference.CausalInference import CausalInference
import daft
from daft import PGM
import matplotlib.pyplot as plt


def convert_pgm_to_pgmpy(pgm):
    """Takes a Daft PGM object and converts it to a pgmpy BayesianModel"""
    edges = [(edge.node1.name, edge.node2.name) for edge in pgm._edges]
    model = BayesianNetwork(edges)
    return model

# Game 1
pgm = PGM(shape=[4, 3])

pgm.add_node(daft.Node('X', r"X", 1, 2))
pgm.add_node(daft.Node('Y', r"Y", 3, 2))
pgm.add_node(daft.Node('A', r"A", 2, 2))
pgm.add_node(daft.Node('B', r"B", 2, 1))

pgm.add_edge('X', 'A')
pgm.add_edge('A', 'Y')
pgm.add_edge('A', 'B')

pgm.render()
plt.show()

game1 = convert_pgm_to_pgmpy(pgm)
inference1 = CausalInference(game1)
print(f"Are there are active backdoor paths? {inference1.is_valid_backdoor_adjustment_set('X', 'Y')}")