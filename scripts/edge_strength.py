# Edge Strength based on statistics with datasets using BNLearn python package
import bnlearn
import bnlearn as bn
from utils import parse_xdsl, build_network
import pandas as pd


# bif_file = "/home/dhruv/Desktop/bn-validation-platform/scripts/best_model/best_model_M_stage.bif"
# model = bn.import_DAG(bif_file)

#################### ERROR ########################
# [bnlearn] >Import </home/dhruv/Desktop/bn-validation-platform/scripts/best_model/best_model_M_stage.bif>
# [bnlearn] >Loading bif file </home/dhruv/Desktop/bn-validation-platform/scripts/best_model/best_model_M_stage.bif>
# [bnlearn] >Check whether CPDs sum up to one.
# [bnlearn] >CPD [bm_M_Scinti__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [bone_M_Scinti__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [bone_M_fracture__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [brain_M_cMRT__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [distant_lymphnode_CR_thorax__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [distant_lymphnode_CT_thorax__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [distant_lymphnode_endosono__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [hep_M_CT_abdomen__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [others_M_CT_abdomen__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [others_M_Sono_abdomen__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [perit_M_CT_abdomen__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [pleu_M_CT_thorax__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [pul_M_CR_thorax__patient] does not add up to 1 but is: [1. 1.]
# [bnlearn] >CPD [pulmonary_M_CT_GuidedPunction__patient] does not add up to 1 but is: [1. 1.]
# These warnings due to floating point precision errors


# So manually create the DAG reading the xdsl file
# xdsl_file_path = "/Users/dhruv/Desktop/abcd/bn-validation-platform/scripts/Mstage.xdsl"
xdsl_file_path = "/home/dhruv/Desktop/bn-validation-platform/scripts/Mstage.xdsl"

nodes = parse_xdsl(xdsl_file_path)
model = build_network(nodes)

if model.check_model():
    print("The model is valid.")
else:
    print("The model is invalid.")

print("\n")


# Convert to bnlearn model
edges_list = [edge for edge in model.edges]
print(len(edges_list))
cpds = model.get_cpds()
# print(cpds)

x = model.get_cpds("bm_M_Scinti__patient")
print(x)
print(type(x))
model = bnlearn.make_DAG(DAG=model, CPD=cpds)
print(model.keys())

# dataset_paths = [
#     "/Users/dhruv/Desktop/abcd/bn-validation-platform/datasets/40percent.csv",
#     "/Users/dhruv/Desktop/abcd/bn-validation-platform/datasets/60percent.csv",
#     "/Users/dhruv/Desktop/abcd/bn-validation-platform/datasets/80percent.csv",
#     "/Users/dhruv/Desktop/abcd/bn-validation-platform/datasets/100percent.csv",
# ]

dataset_paths = [
    "/home/dhruv/Desktop/bn-validation-platform/datasets/40percent.csv",
    "/home/dhruv/Desktop/bn-validation-platform/datasets/60percent.csv",
    "/home/dhruv/Desktop/bn-validation-platform/datasets/80percent.csv",
    "/home/dhruv/Desktop/bn-validation-platform/datasets/100percent.csv",
]

df = pd.read_csv(dataset_paths[3])

model = bnlearn.independence_test(model, df, test="g_sq")
# The G-test is often preferred over the Chi-square test when dealing with smaller sample sizes or when the data involves counts.

print(model.keys())
print(model['independence_test'])