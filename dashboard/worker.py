from celery import Celery
from utils.file import build_network
from utils.edges import find_redundant_edges_d_separation, edge_strength_stats

app = Celery("worker", broker="pyamqp://bnv_rabbitmq", backend="mongodb://root:example@bnv_db/bn-validation")

@app.task
def task_edge_strength_stats(nodes_contents):
    bn_model = build_network(nodes_contents)
    edge_strength = edge_strength_stats(bn_model)
    return edge_strength.to_json(orient="split")

@app.task
def task_compute_redundant_edges_d_separation(nodes_contents):
    bn_model = build_network(nodes_contents)
    redundant_edges = find_redundant_edges_d_separation(bn_model, debug=True)
    return redundant_edges