def hierarchical_clustering_tf_idf():
    ## Cons: Uses TF-IDF vectorization does not capture sematical meaning
    import numpy as np
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
    import matplotlib.pyplot as plt

    # Define the corpus
    corpus = {
        'Never Too Loud', 'Danko Jones (vocals/guitar)', 'Nick Raskulinecz', 'constructed', 'music', 
        'Casa Loma', 'designed', 'Canadian', 'garden', 'hard rock trio', 'Danko Jones', 
        'Sir Henry Pellatt', 'midtown Toronto', "John 'JC' Calabrese (bass)", 'producer', 
        'Toronto', 'elements', 'Canada', 'E. J. Lennox', 'landmark', 'fourth studio album', 
        'residence', 'Studio 606', 'castle-style mansion', 'Ontario', 'financier', 'architect', 
        'Gothic Revival', 'recorded', '1914', 'Los Angeles', 'known', 'Canadian hard rock band', 
        'historic house museum', 'energetic live shows', 'hard rock', 'Rich Knox (drums)', 
        'several other city landmarks', 'punk', '1911'
    }

    # Convert the corpus to a list
    corpus_list = list(corpus)

    # Vectorize the corpus using TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus_list)

    # Perform hierarchical clustering
    Z = linkage(X.toarray(), method='ward')

    # Plot the dendrogram
    plt.figure(figsize=(15, 10))
    dendrogram(Z, labels=corpus_list, orientation='right')
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('Distance')
    plt.ylabel('Key Elements')
    plt.show()

    # Extract clusters (using a distance threshold to determine clusters)
    # You can adjust the threshold to get different number of clusters
    threshold = 1.5
    clusters = fcluster(Z, threshold, criterion='distance')

    # Create a DataFrame to show the key elements and their clusters
    df = pd.DataFrame({'Key Element': corpus_list, 'Cluster': clusters})
    df = df.sort_values(by='Cluster').reset_index(drop=True)

    # Display the DataFrame
    # import ace_tools as tools; tools.display_dataframe_to_user(name="Clustered Key Elements", dataframe=df)
    print(df.values.tolist())

def dbscan_tf_idf():
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import DBSCAN
    from sklearn.metrics.pairwise import cosine_distances

    # Corpus of key elements/sub-sentences
    corpus = [
        'Never Too Loud', 'Danko Jones (vocals/guitar)', 'Nick Raskulinecz', 'constructed', 
        'music', 'Casa Loma', 'designed', 'Canadian', 'garden', 'hard rock trio', 'Danko Jones', 
        'Sir Henry Pellatt', 'midtown Toronto', "John 'JC' Calabrese (bass)", 'producer', 
        'Toronto', 'elements', 'Canada', 'E. J. Lennox', 'landmark', 'fourth studio album', 
        'residence', 'Studio 606', 'castle-style mansion', 'Ontario', 'financier', 'architect', 
        'Gothic Revival', 'recorded', '1914', 'Los Angeles', 'known', 'Canadian hard rock band', 
        'historic house museum', 'energetic live shows', 'hard rock', 'Rich Knox (drums)', 
        'several other city landmarks', 'punk', '1911'
    ]

    # Vectorize the corpus using TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)

    # Calculate the distance matrix using cosine distances
    distance_matrix = cosine_distances(X)

    # Apply DBSCAN clustering
    dbscan = DBSCAN(metric='precomputed', eps=0.5, min_samples=2)
    labels = dbscan.fit_predict(distance_matrix)

    # Organize results
    clusters = {}
    for label, item in zip(labels, corpus):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(item)

    # Print clusters
    for cluster_id, elements in clusters.items():
        print(f"Cluster {cluster_id}: {elements}")


def dbscan_sentence_embeddings():
    # Step 1: Install Required Libraries
    # pip install sentence-transformers scikit-learn

    # Step 2: Import Libraries and Define Corpus
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import DBSCAN
    import numpy as np

    corpus = [
        'Never Too Loud', 'Danko Jones (vocals/guitar)', 'Nick Raskulinecz', 
        'constructed', 'music', 'Casa Loma', 'designed', 'Canadian', 
        'garden', 'hard rock trio', 'Danko Jones', 'Sir Henry Pellatt', 
        'midtown Toronto', "John 'JC' Calabrese (bass)", 'producer', 
        'Toronto', 'elements', 'Canada', 'E. J. Lennox', 'landmark', 
        'fourth studio album', 'residence', 'Studio 606', 'castle-style mansion', 
        'Ontario', 'financier', 'architect', 'Gothic Revival', 'recorded', 
        '1914', 'Los Angeles', 'known', 'Canadian hard rock band', 
        'historic house museum', 'energetic live shows', 'hard rock', 
        'Rich Knox (drums)', 'several other city landmarks', 'punk', '1911'
    ]
    # corpus = ['Canadian', 'midtown Toronto', 'Toronto', 'Canada', 'Ontario']

    # Step 3: Convert Corpus to Embeddings
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeddings = model.encode(corpus)

    # Step 4: Perform Clustering with DBSCAN
    clustering = DBSCAN(eps=0.4, min_samples=2, metric='cosine').fit(embeddings)
    # 0.4
    labels = clustering.labels_

    # Step 5: Organize and Display Clusters
    clustered_data = {}
    for idx, label in enumerate(labels):
        if label not in clustered_data:
            clustered_data[label] = []
        clustered_data[label].append(corpus[idx])

    # Display the clusters
    for label, elements in clustered_data.items():
        print(f"Cluster {label}: {elements}")


def aggregation():

    from collections import Counter
    from difflib import SequenceMatcher
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Function to calculate similarity score
    def similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()

    # Function to aggregate associations
    def aggregate_associations(inputs):
        # Frequency-based aggregation
        freq_counter = Counter(inputs)
        most_common = freq_counter.most_common(1)[0][0]

        # Format-based aggregation
        format_aggregation = max(inputs, key=len)

        # Semantic-based aggregation using TF-IDF and cosine similarity
        vectorizer = TfidfVectorizer().fit_transform(inputs)
        vectors = vectorizer.toarray()
        cosine_matrix = cosine_similarity(vectors)
        avg_cosine_scores = cosine_matrix.mean(axis=1)
        semantic_aggregation = inputs[avg_cosine_scores.argmax()]

        # Association-based aggregation using similarity score
        association_aggregation = max(inputs, key=lambda x: sum(similarity(x, other) for other in inputs))

        # Combining results
        results = [most_common, format_aggregation, semantic_aggregation, association_aggregation]
        combined_results = Counter(results)
        final_result = combined_results.most_common(1)[0][0]

        return final_result

    # Example usage
    inputs1 = ['Canadian', 'midtown Toronto', 'Toronto', 'Canada', 'Ontario']
    inputs2 = ['hard rock trio', 'Canadian hard rock band', 'hard rock']

    output1 = aggregate_associations(inputs1)
    output2 = aggregate_associations(inputs2)

    print(f"Input: {inputs1}\nOutput: {output1}")
    print(f"Input: {inputs2}\nOutput: {output2}")
