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

    # Create tabu edges to prevent self loops
    tabu_edges = []
    for node in model.nodes:
        tabu_edges.append((node, node))
    tabu_edges.append(('bm_M_CT_body__patient','bm_M_CR_body__patient'))
    tabu_edges.append(('bm_M_PET_body__patient','bm_M_CR_body__patient'))

    # print(tabu_edges)

    # return

    # sm = from_pandas(data, w_threshold=0.5)
    sm = from_pandas(data, tabu_edges=tabu_edges)
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
        edge_attributes[edge_tuple] = {"width": 10 * weight}

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
            "height": "800px",
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
    bnlearn.save(model=model, filepath="second_best_model/2ndbest.pkl", overwrite=True)
    print(sm.keys())