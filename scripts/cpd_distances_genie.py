from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
import numpy as np

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



def euclidean_distance(p, q):
    print("P values:")
    print(p.get_values())
    print("Q values:")
    print(q.get_values())
    print()

    p_vals = p.get_values().transpose()
    q_vals = q.get_values().transpose()

    print("P Transpose:")
    print(p_vals)
    print("Q Transpose:")
    print(q_vals)

    no_of_states_parent_p = cpd_p.get_values().shape[1]
    print(f"No. of states of P parent: {no_of_states_parent_p}\n")

    print("After Tiling Q with P parent (no.) states:")
    q_vals = np.tile(q_vals, (no_of_states_parent_p, 1))
    print(q_vals)

    q_row = 0
    p_q_diff_square_sum = 0
    for p_par_state_id in range(p_vals.shape[0]):
        for p_state_id in range(p_vals.shape[1]):
            current_p_val = p_vals[p_par_state_id][p_state_id]
            print(current_p_val)
            print(q_vals[q_row])
            for q in q_vals[q_row]:
                p = current_p_val
                print(f"p : {p}")
                print(f"q: {q}")
                p_q_diff_square_sum += (p - q) ** 2
                print(f"p_q_diff_square_sum: {p_q_diff_square_sum}")
            q_row += 1
        print()

    print(np.sqrt(p_q_diff_square_sum))
    return np.sqrt(p_q_diff_square_sum)
    # return np.sqrt(np.sum((p - q) ** 2))

euclidean_distance(cpd_p, cpd_q)

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
euclidean_distance(p_cpd, q_cpd)
# Ans: 0.5477225575051662