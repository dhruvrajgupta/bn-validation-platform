# Edge Strength based on statistics with datasets using BNLearn python package

import bnlearn as bn
from utils import parse_xdsl, build_network


bif_file = "/home/dhruv/Desktop/bn-validation-platform/scripts/best_model/best_model_M_stage.bif"
model = bn.import_DAG(bif_file)

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

# So manually create the DAG reading the xdsl file
xdsl_file_path = "/Users/dhruv/Desktop/abcd/bn-validation-platform/scripts/Mstage.xdsl"

nodes = parse_xdsl(xdsl_file_path)
model = build_network(nodes)

if model.check_model():
    print("The model is valid.")
else:
    print("The model is invalid.")

print("\n")


# Conver to bnlearn model