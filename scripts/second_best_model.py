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
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from causalnex.structure.notears import from_pandas
from sklearn.preprocessing import MinMaxScaler
import bnlearn

warnings.filterwarnings("ignore")  # silence warnings


def sl_second_best_model():
    sm = StructureModel()

    # Learning structure from the best model to get the second best model

    # reader = BIFReader("/Users/dhruv/Desktop/abcd/bn-validation-platform/scripts/best_model/best_model_M_stage.bif")
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

    data = pd.read_csv("/home/dhruv/Desktop/bn-validation-platform/datasets/100percent.csv")
    # data = pd.read_csv("/Users/dhruv/Desktop/abcd/bn-validation-platform/datasets/100percent.csv")

    # print(data.head())
    data = data[:2000]
    data = data[[c for c in data.columns if c in model.nodes()]]
    # print(data.head())

    # non_numeric_columns = list(data.select_dtypes(exclude=[np.number]).columns)
    # print(len(non_numeric_columns))

    le = LabelEncoder()
    categorical_mappings = {}

    for col in data:
        data[col] = le.fit_transform(data[col])
        label_to_integer = dict(zip(le.classes_, range(len(le.classes_))))
        integer_to_label = dict(enumerate(le.classes_))
        categorical_mappings[col] = integer_to_label

    # print(data.head(5))
    # print(le.classes_)
    # print(le.inverse_transform(data.loc[0]))
    # print(categorical_mappings)

    sm = from_pandas(data, w_threshold=0.5)
    edge_attributes = {}

    # Create a dataframe of weights
    edges_weights = {
        "edges": [],
        "weight": []
    }
    for edge in sm.edges(data=True):
        print(edge)
        edge_tuple = (edge[0], edge[1])
        weight = edge[2]["weight"]
        edges_weights["edges"].append(edge_tuple)
        edges_weights["weight"].append(weight)
        # if weight > 0.8:
        edge_attributes[edge_tuple] = {"width": 5 * weight}

    edges_weights = pd.DataFrame.from_dict(edges_weights)
    # Normalize weights using MinMaxScaler
    scaler = MinMaxScaler()
    edges_weights['normalized_weight'] = scaler.fit_transform(edges_weights[['weight']])
    print(edges_weights)

    viz = plot_structure(
        sm,
        all_node_attributes=NODE_STYLE.WEAK,
        all_edge_attributes=EDGE_STYLE.WEAK,
        edge_attributes=edge_attributes,
        plot_options={
            "width": "100%",
            "height": "600px",
        }
    )

    viz.toggle_physics(False)
    viz.show_buttons(filter_=['physics'])
    viz.show("SL_M_State_BN.html")

    # Strength of arrow or edges using data statistics

    # Converting the DAG to bnlearn model
    edges_list = [edge for edge in sm.edges]
    sm = bnlearn.make_DAG(DAG=edges_list)
    # This can have cycles hence saving the original model
    bnlearn.save(model=model, filepath="second_best_model/2ndbest.pkl")
    print(sm.keys())


def edge_strenght_stats_ds():
    model = bnlearn.load(filepath="/home/dhruv/Desktop/bn-validation-platform/scripts/second_best_model/2ndbest.pkl")
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
    model = bnlearn.make_DAG(DAG=model)
    print(model.keys())
    df = pd.read_csv(dataset_paths[3])

    model = bnlearn.independence_test(model, df, test="g_sq")
    # The G-test is often preferred over the Chi-square test when dealing with smaller sample sizes or when the data involves counts.

    print(model.keys())
    print(model['independence_test'])

    # Normalize weights using MinMaxScaler
    edges_weights_df = model['independence_test']
    scaler = MinMaxScaler()
    edges_weights_df['normalized_weight'] = scaler.fit_transform(edges_weights_df[['g_sq']])
    print(edges_weights_df)

def learn_cpds():
    model = bnlearn.load(filepath="/home/dhruv/Desktop/bn-validation-platform/scripts/second_best_model/2ndbest.pkl")
    model = bnlearn.make_DAG(DAG=model)

    dataset_paths = [
        "/home/dhruv/Desktop/bn-validation-platform/datasets/40percent.csv",
        "/home/dhruv/Desktop/bn-validation-platform/datasets/60percent.csv",
        "/home/dhruv/Desktop/bn-validation-platform/datasets/80percent.csv",
        "/home/dhruv/Desktop/bn-validation-platform/datasets/100percent.csv",
    ]

    pgmpy_model = model["model"]


    df = pd.read_csv(dataset_paths[3])
    df = df[[c for c in df.columns if c in pgmpy_model.nodes()]]
    print(model.keys())

    model = bnlearn.parameter_learning.fit(model, df)
    # [Uses only 1000 as sample size]
    bnlearn.save(model, filepath="second_best_model/2ndbest_cpds.pkl")

def cpd_weigts():
    from utils import euclidean_distance, euclidean_distance_marginalization, euclidean_distance_marginalization_avg, \
        euclidean_distance_marginalization_avg_normalized, hellinger_distance, j_divergence_distance, cdf_distance
    # model = bnlearn.load(filepath="/Users/dhruv/Desktop/abcd/bn-validation-platform/scripts/second_best_model/2ndbest_cpds.pkl")
    model = bnlearn.load(filepath="/home/dhruv/Desktop/bn-validation-platform/scripts/second_best_model/2ndbest_cpds.pkl")
    model = bnlearn.make_DAG(DAG=model)

    print(model.keys())
    pgmpy_model = model["model"]
    # print(pgmpy_model.get_cpds())
    # print(model["model_edges"])
    # count = 0
    for edge in model["model_edges"]:
        # print(edge)
        # if count > 5:
        #     break
        p = edge[0]
        q = edge[1]
        p = pgmpy_model.get_cpds(p)
        q = pgmpy_model.get_cpds(q)
        weight = euclidean_distance(p,q)
        weignt_m = euclidean_distance_marginalization(p,q)
        weight_avg = euclidean_distance_marginalization_avg(p,q)
        weight_norm = euclidean_distance_marginalization_avg_normalized(p, q)
        hellinger_distance_weight = hellinger_distance(p, q)
        j_divergence_weight = j_divergence_distance(p, q)
        cdf_weight = cdf_distance(p, q)
        print("Edge: ", edge)
        print("mat manipulation:", weight)
        print("marginalization:", weignt_m)
        print("marginalization_avg:", weight_avg)
        print("marginalization_avg_norm:", weight_norm)
        print("hellinger:", hellinger_distance_weight)
        print("J divergence:", j_divergence_weight)
        print("CDF distance: ", cdf_weight)
        print()
        # count += 1

def run_evaluation_second_best():
    # Load the second best model with cpds
    model = bnlearn.load(
        filepath="/home/dhruv/Desktop/bn-validation-platform/scripts/second_best_model/2ndbest_cpds.pkl")
    model = bnlearn.make_DAG(DAG=model)
    print(model.keys())
    sl_model = model["model"]

    dataset_paths = [
        "/home/dhruv/Desktop/bn-validation-platform/datasets/40percent.csv",
        "/home/dhruv/Desktop/bn-validation-platform/datasets/60percent.csv",
        "/home/dhruv/Desktop/bn-validation-platform/datasets/80percent.csv",
        "/home/dhruv/Desktop/bn-validation-platform/datasets/100percent.csv"
    ]

    target = "M_state__patient"

    print(f"Target Node: {target}")
    print("Preforming model test in multiple datasets...\n")

    for dataset_path in dataset_paths:
        print(f"\nDataset: {dataset_path}\n")
        df = pd.read_csv(dataset_path)
        # print(df)
        df = df[[c for c in df.columns if c in sl_model.nodes()]]
        # print(df)
        df = df.replace(to_replace="*", value=np.nan)
        # # df = df[df[target].notna()]
        # # print(df)
        X = df.loc[:, df.columns != target]
        Y = df[target]
        # # print(Y)
        #

        from utils import predict

        y_pred = predict(sl_model, data=X, stochastic=False)
        comparison_df = pd.DataFrame({'Y': Y, 'y_pred': y_pred[target]})
        # print(comparison_df)
        # print(len(comparison_df))
        comparison_df = comparison_df.dropna(subset=['Y'])
        # print(comparison_df)
        # print(len(comparison_df))
        print(f"Number of rows dropped due to unknow NaN values of {target}: {len(Y) - len(comparison_df)}")
        comparison_df['Equal'] = comparison_df['Y'] == comparison_df['y_pred']
        # print(comparison_df)
        # print(len(comparison_df))
        accuracy = comparison_df['Equal'].mean()
        print("\nAccuracy:")
        print(f"{target} = {accuracy}")
        target_state_counts = Y.value_counts().to_dict()
        for state, actual_state_count in target_state_counts.items():
            state_correct_pred = comparison_df[(comparison_df['Equal'] == True) & (comparison_df['Y'] == state)]
            pred_count = len(state_correct_pred)
            # print(state)
            # print(pred_count)
            # print(actual_state_count)
            if actual_state_count:
                print(f"\t{state} = {pred_count / actual_state_count} ({pred_count}/{actual_state_count})")
            else:
                print(f"\t{state} = 0.0 ({pred_count}/{actual_state_count})")
        print()
        print("-" * 100)


def comparison_evaluation():
    pass


if __name__ == "__main__":
    # sl_second_best_model()
    # edge_strenght_stats_ds()
    # learn_cpds()
    # cpd_weigts()
    # run_evaluation_second_best()
    comparison_evaluation()