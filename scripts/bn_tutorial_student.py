from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD

# Defining the model structure. We can define the network by just passing a list of edges.
model = BayesianNetwork([('Difficulty', 'Grade'), ('Intelligence', 'Grade'), ('Grade', 'Letter'), ('Intelligence', 'S')])

# CPDs can also be defined using the state names of the variables. If the state names are not provided
# like in the previous example, pgmpy will automatically assign names as: 0, 1, 2, ....

cpd_d_sn = TabularCPD(variable='Difficulty', variable_card=2, values=[[0.6], [0.4]], state_names={'Difficulty': ['Easy', 'Hard']})
cpd_i_sn = TabularCPD(variable='Intelligence', variable_card=2, values=[[0.7], [0.3]], state_names={'Intelligence': ['Dumb', 'Intelligent']})
cpd_g_sn = TabularCPD(variable='Grade', variable_card=3,
                      values=[[0.3, 0.05, 0.9,  0.5],
                              [0.4, 0.25, 0.08, 0.3],
                              [0.3, 0.7,  0.02, 0.2]],
                      evidence=['Intelligence', 'Difficulty'],
                      evidence_card=[2, 2],
                      state_names={'Grade': ['A', 'B', 'C'],
                                   'Intelligence': ['Dumb', 'Intelligent'],
                                   'Difficulty': ['Easy', 'Hard']})

cpd_l_sn = TabularCPD(variable='Letter', variable_card=2,
                      values=[[0.1, 0.4, 0.99],
                              [0.9, 0.6, 0.01]],
                      evidence=['Grade'],
                      evidence_card=[3],
                      state_names={'Letter': ['Bad', 'Good'],
                                   'Grade': ['A', 'B', 'C']})

cpd_s_sn = TabularCPD(variable='S', variable_card=2,
                      values=[[0.95, 0.2],
                              [0.05, 0.8]],
                      evidence=['Intelligence'],
                      evidence_card=[2],
                      state_names={'S': ['Bad', 'Good'],
                                   'Intelligence': ['Dumb', 'Intelligent']})

# These defined CPDs can be added to the model. Since, the model already has CPDs associated to variables, it will
# show warning that pmgpy is now replacing those CPDs with the new ones.
model.add_cpds(cpd_d_sn, cpd_i_sn, cpd_g_sn, cpd_l_sn, cpd_s_sn)

print(model.check_model())
print(model.get_cpds())
print(print(cpd_g_sn))
cpd_g_sn.to_csv("cpd_grade_given_intelligence_difficulty.csv")