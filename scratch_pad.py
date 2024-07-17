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


def max_substring():
    from difflib import SequenceMatcher

    def get_maximum_substring(s1, s2):
        # Create a SequenceMatcher object
        seq_matcher = SequenceMatcher(None, s1, s2)
        # Find the longest match
        match = seq_matcher.find_longest_match(0, len(s1), 0, len(s2))
        # Extract the longest matching substring
        if match.size != 0:
            substring = s1[match.a: match.a + match.size]
            return substring
        return ""

    # Example usage
    s1 = "midtown Toronto"
    s2 = "Toronto is a city"

    max_substring = get_maximum_substring(s1, s2)
    print(f"The longest matching substring is: '{max_substring}'")


# max_substring()

def fp_growth_association():

    from mlxtend.frequent_patterns import fpgrowth, association_rules
    import pandas as pd

    def preprocess_tags(tags_list):
        # Function to preprocess tags for standardization
        # e.g., converting to lowercase, removing punctuation, etc.
        return [tag.lower().strip() for tag in tags_list]

    def merge_associated_tags(tags_list, min_support=0.5, min_threshold=0.5):
        # Preprocess the input tags
        tags_list = preprocess_tags(tags_list)
        
        # Create a DataFrame with dummy variables
        df = pd.DataFrame([[tag in tags for tag in tags_list] for tags in [tags_list]], columns=tags_list)
        
        # Apply FP-Growth algorithm
        frequent_itemsets = fpgrowth(df, min_support=min_support, use_colnames=True)
        
        # Generate association rules
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_threshold)
        
        # Create a dictionary to store merged tags
        merged_tags = set(tags_list)
        
        for index, row in rules.iterrows():
            antecedents = set(row['antecedents'])
            consequents = set(row['consequents'])
            
            if len(antecedents) == 1 and len(consequents) == 1:
                tag_to_merge = next(iter(antecedents))
                tag_merged_into = next(iter(consequents))
                
                if tag_to_merge in merged_tags:
                    merged_tags.remove(tag_to_merge)
                merged_tags.add(tag_merged_into)
        
        return list(merged_tags)

    # Example usage
    input_tags_1 = ['Canadian', 'midtown Toronto', 'Toronto', 'Canada', 'Ontario']
    input_tags_2 = ['hard rock trio', 'Canadian hard rock band', 'hard rock']

    output_tags_1 = merge_associated_tags(input_tags_1)
    output_tags_2 = merge_associated_tags(input_tags_2)

    print("Output for input 1:", output_tags_1)
    print("Output for input 2:", output_tags_2)


def max_score_item():
    def get_item_with_max_score(items):
        if not items:
            return None  # Return None if the list is empty
        return max(items, key=lambda x: list(x.values())[0])

    # Example usage
    items = [{'landmark': 0.4444444444444444}, {'land': 0.7}]

    output = get_item_with_max_score(items)

    print(f"Input: {items}\nOutput: {output}")

def paragraph_chunking_main():
    import nltk
    from nltk.tokenize import sent_tokenize

    # Ensure you have the necessary resources downloaded
    nltk.download('punkt')

    def paragraph_chunking(text, sentences_per_chunk=3):
        # Tokenize the text into sentences
        sentences = sent_tokenize(text)
        # Chunk sentences into the specified size
        chunks = [' '.join(sentences[i:i + sentences_per_chunk]) for i in range(0, len(sentences), sentences_per_chunk)]
        return chunks

    # Example usage
    paragraph = (
        "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. "
        "Leading AI textbooks define the field as the study of 'intelligent agents': any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. "
        "Colloquially, the term 'artificial intelligence' is often used to describe machines (or computers) that mimic 'cognitive' functions that humans associate with the human mind, such as 'learning' and 'problem-solving'. "
        "As machines become increasingly capable, tasks considered to require 'intelligence' are often removed from the definition of AI, a phenomenon known as the AI effect. "
        "A quip in Tesler's Theorem says 'AI is whatever hasn't been done yet.' For instance, optical character recognition is frequently excluded from things considered to be AI, having become a routine technology. "
        "Modern machine capabilities generally classified as AI include successfully understanding human speech, competing at the highest level in strategic game systems (such as chess and Go), autonomously operating cars, intelligent routing in content delivery networks, and military simulations."
    )

    paragraph = (
    "Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. It was recorded at Studio 606 in Los Angeles, with the producer Nick Raskulinecz. "
    "Danko Jones is a Canadian hard rock trio from Toronto. The band consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums). The band’s music includes elements of hard rock and punk and they are known for their energetic live shows. "
    "Casa Loma (improper Spanish for 'Hill House') is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada, that is now a historic house museum and landmark. It was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt. The architect was E. J. Lennox, who designed several other city landmarks. "
    )

    chunks = paragraph_chunking(paragraph, sentences_per_chunk=2)
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}:\n{chunk}\n")


def ask_llm():
    from ollama import chat


    messages = [
    {
        'role': 'user',
        'content': 'Why is the sky blue?',
        'options': {
            "seed": 1
        }
    },
    ]

    for part in chat('llama3', messages=messages, stream=True):
        print(part['message']['content'], end='', flush=True)

    # end with a newline
    print()
# TODO: chunk the paragraph
paragraph_chunking_main()