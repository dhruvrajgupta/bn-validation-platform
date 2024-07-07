import nltk
# from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
import re
import string
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from typing import List, Dict

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

def clean_text(text):
    text = text.lower()  # Lowercase
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    text = re.sub(r'\W', ' ', text)  # Remove special characters
    return text

def lemmatize(element: str) -> str:
    english_stopwords = stopwords.words('english')
    element = [word for word in element.split(" ") if word not in english_stopwords]
    # stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    # stemmed_text = [stemmer.stem(word) for word in element.split(" ")]
    element = " ".join([lemmatizer.lemmatize(word) for word in element])
    # print(stemmed_text)
    # print(element)
    return element

def cluster_key_elements(key_elements: List[str])-> Dict[int, List[str]]:
    # Step 3: Convert Corpus to Embeddings
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeddings = model.encode(key_elements)

    # Step 4: Perform Clustering with DBSCAN
    clustering = DBSCAN(eps=0.5, min_samples=2, metric='cosine').fit(embeddings)
    labels = clustering.labels_

    # Step 5: Organize and Display Clusters
    clustered_data = {}
    for idx, label in enumerate(labels):
        if label not in clustered_data:
            clustered_data[label] = []
        clustered_data[label].append(key_elements[idx])

    # Display the clusters
    # for label, elements in clustered_data.items():
    #     print(f"Cluster {label}: {elements}")

    return clustered_data


