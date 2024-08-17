from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD

## Euclidean Distance of two CPDs
model = BayesianNetwork(['P','Q'])

p_cpd = TabularCPD(variable='P', variable_card=2, values=[[0.6], [0.4]], state_names={'P': ['M0', 'M1']})
q_cpd = TabularCPD(variable='Q', variable_card=2, values=[[0.7], [0.3]], evidence=['P'], state_names={'Q': ['M0', 'M1'], 'P': ['M0', 'M1']})

print(p_cpd)
print(q_cpd)