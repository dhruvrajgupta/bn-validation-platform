import pandas as pd

df = pd.read_csv("/Users/dhruv/Desktop/abcd/bn-validation-platform/scripts/ASIA_DATA.csv")
x = df.loc[:, df.columns != 'dysp']
y = df['dysp']

from pgmpy.utils import get_example_model

asia_model = get_example_model("asia")
print("Nodes: ", asia_model.nodes())
print("Edges: ", asia_model.edges())

from pgmpy.inference import VariableElimination

asia_infer = VariableElimination(asia_model)

# pos, neg = 0, 0
# for index, row in x.head().iterrows():
#     evidence = row.to_dict()
#     # y_hat = asia_infer.query(variables=["dysp"], evidence=evidence)
#     # print(y_hat)
#     y_hat = asia_infer.map_query(variables=["dysp"], evidence=evidence, show_progress=False)
#     print(y_hat)
#     print(index)
#     if y_hat["dysp"] == y[index]:
#         pos += 1
#     else:
#         neg += 1

# print(f"Accuracy = {pos / (pos + neg)} ({pos}/{pos + neg})")
# print(asia_model.states["dysp"])

y_pred = asia_model.predict(x, stochastic=False)

comparison_df = pd.DataFrame({'y': y, 'y_pred': y_pred["dysp"]})
comparison_df['Equal'] = comparison_df['y'] == comparison_df['y_pred']
accuracy = comparison_df['Equal'].mean()
print("\nAccuracy:")
print(f"{accuracy * 100:.2f}%")
print(y_pred.value_counts().to_dict())
