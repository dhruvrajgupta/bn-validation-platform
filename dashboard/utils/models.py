def get_horrible_model(threshold=0):

    # DiGraph 45 Nodes and 1980 edges (990 cycles)
    if threshold == 0:
        path = "/home/dhruv/Desktop/bn-validation-platform/scripts/horrible_model/sl_without_threshold.pkl"


    import pickle
    with open(path, 'rb') as inp:
        sm = pickle.load(inp)
    print(sm)

    return sm