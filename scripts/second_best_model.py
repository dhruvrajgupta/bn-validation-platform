# Here we will use the dataset to perform Structure Learning
# so that it can be compared to the best model aka (LC/Mstage xdsl file)
# best model will be stored in the 'best_model' folder

# We will perform NOTEARS Structure Learning as it is the 
# current SOTA Structure Learning method
# CausalNex library already contains the method
# https://proceedings.neurips.cc/paper_files/paper/2018/file/e347c51419ffb23ca3fd5050202f9c3d-Paper.pdf


from causalnex.structure import StructureModel
import warnings
from pgmpy.readwrite import BIFReader

warnings.filterwarnings("ignore")  # silence warnings

sm = StructureModel()

# Learning structure from the best model to get the second best model

reader = BIFReader("/home/dhruv/Desktop/bn-validation-platform/scripts/best_model/best_model_M_stage.bif")
model = reader.get_model()
print(model)

# Create Network to be read by CausalNex
for edge in model.edges:
    sm.add_edge(*edge)

from causalnex.plots import plot_structure, NODE_STYLE, EDGE_STYLE

viz = plot_structure(
    sm,
    all_node_attributes=NODE_STYLE.WEAK,
    all_edge_attributes=EDGE_STYLE.WEAK,
)
viz.show("M_State_BN.html")
