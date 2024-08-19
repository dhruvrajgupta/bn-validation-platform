from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
import numpy as np
from utils import euclidean_distance, euclidean_distance_marginalization

# Define the structure of the DAG: O --> P --> Q
model = BayesianNetwork([('O', 'P'), ('P', 'Q')])

states = {
    'O': ['M0', 'M1'],
    'P': ['M0', 'M1', 'M2'],
    'Q': ['M0', 'M1', 'M2', 'M3']
}

# Define the CPDs

# CPD for O
cpd_o = TabularCPD(variable='O', variable_card=2, values=[[0.7], [0.3]],
                   state_names={'O': ['M0', 'M1']})

# CPD for P given O
cpd_p = TabularCPD(variable='P', variable_card=3,
                   values=[[0.5, 0.2],  # P = M0
                           [0.3, 0.4],  # P = M1
                           [0.2, 0.4]],  # P = M2
                   evidence=['O'], evidence_card=[2],
                   state_names={'P': ['M0', 'M1', 'M2'], 'O': ['M0', 'M1']})

# CPD for Q given P
cpd_q = TabularCPD(variable='Q', variable_card=4,
                   values=[[0.6, 0.3, 0.1],  # Q = M0
                           [0.2, 0.3, 0.2],  # Q = M1
                           [0.1, 0.3, 0.4],  # Q = M2
                           [0.1, 0.1, 0.3]],  # Q = M3
                   evidence=['P'], evidence_card=[3],
                   state_names={'Q': ['M0', 'M1', 'M2', 'M3'], 'P': ['M0', 'M1', 'M2']})

print(cpd_o)
print(cpd_p)
print(cpd_q)

# Add CPDs to the model
model.add_cpds(cpd_o, cpd_p, cpd_q)

# Validate the model structure and CPDs
# print(model.check_model())

# Perform inference
# inference = VariableElimination(model)

# # Query the probability distribution of Q given O = M0
# result = inference.query(variables=['Q'], evidence={'O': 0})
# print(result)



# def euclidean_distance(p, q):
#     print("P values:")
#     print(p.get_values())
#     print("Q values:")
#     print(q.get_values())
#     print()

#     p_vals = p.get_values().transpose()
#     q_vals = q.get_values().transpose()

#     print("P Transpose:")
#     print(p_vals)
#     # P Repeat = no. of columns of q
#     p_repeat = q_vals.shape[1]
#     p_flat = np.repeat(p_vals, p_repeat)
#     print(p_flat)
#     print(f"Lenght of P Flat: {len(p_flat)}")
#     print(f"P repeat: {p_repeat}")
#     print("Q Transpose:")
#     print(q_vals)
#     # Q repeat = no of rows of p
#     q_repeat = p_vals.shape[0]
#     print(f"Q repeat: {q_repeat}")
#     q_tiled = np.tile(q_vals, (q_repeat, 1))
#     print(q_tiled)
#     q_flat = q_tiled.flatten()
#     print(q_flat)
#     print(f"Q Flat Length: {len(q_flat)}")

#     # Calculate the Euclidean distance
#     distance = np.sqrt(np.sum((p_flat - q_flat) ** 2))
#     print(distance)
    # return np.sqrt(np.sum((p - q) ** 2))

# euclidean_distance(cpd_p, cpd_q)
# Ans: 0.9797958971132713
euclidean_distance_marginalization(cpd_p, cpd_q)

## Euclidean Distance of two CPDs
model = BayesianNetwork()
model.add_edge('P', 'Q')

p_cpd = TabularCPD(variable='P', variable_card=2, values=[[0.6], [0.4]], state_names={'P': ['M0', 'M1']})
q_cpd = TabularCPD(variable='Q', variable_card=2, values=[[0.7, 0.2], [0.3, 0.8]],
                   evidence=['P'], evidence_card=[2], state_names={'Q': ['M0', 'M1'], 'P': ['M0', 'M1']})

model.add_cpds(p_cpd, q_cpd)
# print(model.check_model())

print(p_cpd)
print(q_cpd)
# euclidean_distance(p_cpd, q_cpd)
# # Ans: 0.5477225575051662
euclidean_distance_marginalization(p_cpd, q_cpd)