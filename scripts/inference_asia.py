from pgmpy.utils import get_example_model
from pgmpy.factors.discrete import TabularCPD

asia_model = get_example_model("asia")

print("Nodes: ", asia_model.nodes())
print("Edges: ", asia_model.edges())
asia_model.get_cpds()

from pgmpy.inference import VariableElimination

asia_infer = VariableElimination(asia_model)

# Computing the probability of bronc given smoke=no.
q = asia_infer.query(variables=["bronc"], evidence={"smoke": "no"})
print(q)

# Computing the joint probability of bronc and asia given smoke=yes
q = asia_infer.query(variables=["bronc", "asia"], evidence={"smoke": "yes"})
print(q)

# Computing the probabilities (not joint) of bronc and asia given smoke=no
q = asia_infer.query(variables=["bronc", "asia"], evidence={"smoke": "no"}, joint=False)
for factor in q.values():
    print(factor)


# from pgmpy.inference import BeliefPropagation

# asia_infer = BeliefPropagation(asia_model)


# # Computing the probability of bronc given smoke=no.
# q = asia_infer.query(variables=["bronc"], evidence={"smoke": "no"})
# print(q)

# # Computing the joint probability of bronc and asia given smoke=yes
# q = asia_infer.query(variables=["bronc", "asia"], evidence={"smoke": "yes"})
# print(q)

# # Computing the probabilities (not joint) of bronc and asia given smoke=no
# q = asia_infer.query(variables=["bronc", "asia"], evidence={"smoke": "no"}, joint=False)
# for factor in q.values():
#     print(factor)



# Computing the MAP of bronc given smoke=no.
q = asia_infer.map_query(variables=["bronc"], evidence={"smoke": "no"})
print(q)

#  Computing the MAP of bronc and asia given smoke=yes
q = asia_infer.map_query(variables=["bronc", "asia"], evidence={"smoke": "yes"})
print(q)

print("Virtual evidence")
lung_virt_evidence = TabularCPD(variable="lung", variable_card=2, values=[[0.4], [0.6]], state_names={"lung": ["yes", "no"]})

# Query with hard evidence smoke = no and virtual evidence lung = [0.4, 0.6]
q = asia_infer.query(
    variables=["bronc"], evidence={"smoke": "no"}, virtual_evidence=[lung_virt_evidence],
)
print(q)

# Query with hard evidence smoke = no and virtual evidences lung = [0.4, 0.6] and bronc = [0.3, 0.7]
lung_virt_evidence = TabularCPD(variable="lung", variable_card=2, values=[[0.4], [0.7]], state_names={"lung": ["yes", "no"]})

print(asia_model.get_cpds("lung"))