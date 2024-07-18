import nltk
# from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
import re
import string
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from typing import List, Dict
from difflib import SequenceMatcher
from nltk.tokenize import sent_tokenize
from ollama import chat
import json

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

def cluster_key_elements(key_elements: List[str])-> Dict[int, List[str]]:
    """
    Clusters the given list of key elements using DBSCAN algorithm.

    Args:
        key_elements (List[str]): A list of key elements to be clustered.

    Returns:
        Dict[int, List[str]]: A dictionary mapping cluster labels to lists of key elements belonging to each cluster.

    Description:
        This function clusters the given list of key elements using the DBSCAN algorithm. It follows the following steps:
        1. Converts the corpus (list of key elements) to embeddings using the SentenceTransformer model.
        2. Performs clustering using the DBSCAN algorithm with eps=0.4, min_samples=2, and cosine metric.
        3. Organizes and displays the clusters.
        4. Returns a dictionary mapping cluster labels to lists of key elements belonging to each cluster.

        Note: The function currently does not display the clusters.

    Example:
        >>> key_elements = ['apple', 'banana', 'orange', 'grape', 'kiwi']
        >>> cluster_key_elements(key_elements)
        {0: ['apple', 'banana'], 1: ['orange', 'grape'], 2: ['kiwi']}
    """
    # Step 3: Convert Corpus to Embeddings
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeddings = model.encode(key_elements)

    # Step 4: Perform Clustering with DBSCAN
    clustering = DBSCAN(eps=0.4, min_samples=2, metric='cosine').fit(embeddings)
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

def similarity(a, b):
    """
    Calculate the similarity between two strings using the SequenceMatcher module.

    Parameters:
        a (str): The first string to compare.
        b (str): The second string to compare.

    Returns:
        float: The similarity ratio between the two strings. The value ranges from 0 to 1, where 1 indicates perfect similarity.
    """
    return SequenceMatcher(None, a, b).ratio()

def get_item_with_max_score(items):
    """
    A function that returns the item with the maximum score from a list of items.

    Parameters:
        items (list): A list of dictionaries where each dictionary represents an item with a score.

    Returns:
        dict or None: The item with the maximum score. Returns None if the list is empty.
    """
    if not items:
        return None  # Return None if the list is empty
    return max(items, key=lambda x: list(x.values())[0])

def paragraph_chunking(text, sentences_per_chunk=3):
        # Tokenize the text into sentences
        sentences = sent_tokenize(text)
        # Chunk sentences into the specified size
        chunks = [' '.join(sentences[i:i + sentences_per_chunk]) for i in range(0, len(sentences), sentences_per_chunk)]
        return chunks

def chunk_corpus(corpus):
    # Chunking the corpus
    print(f"Chunking the corpus...\n{'='*50}\n")
    chunked_corpus = paragraph_chunking(corpus, sentences_per_chunk=2)
    for i, chunk in enumerate(chunked_corpus):
        print(f"Chunk {i+1}:\n{chunk}\n")


def extract_notebook_rationale_next_steps_chosen_action(resposne: str):
    notebook_pattern = r"\*Updated Notebook\*:(.*?)(?=\*Rationale for Next Action\*:|\Z)"
    rationale_next_action_pattern = r"\*Rationale for Next Action\*:(.*?)(?=\*Chosen Action\*:|\Z)"
    chosen_action_pattern = r"\*Chosen Action\*:\s*(.*)"

    notebook = re.search(notebook_pattern, resposne, re.DOTALL)
    if notebook is not None:
        notebook = notebook.group(1).strip()
        notebook = notebook.replace("Notebook:", "").strip()
    rationale_next_action = re.search(rationale_next_action_pattern, resposne, re.DOTALL).group(1).strip()
    chosen_action = re.search(chosen_action_pattern, resposne, re.DOTALL).group(1).strip()

    return notebook, rationale_next_action, chosen_action


def print_state(question: str, rational_plan: str, previous_actions: List[str], notebook: str, chunk_queue: List[str], current_node: str):
    print("===================")
    print("CURRENT STATE:")
    print("===================")
    print(f"QUESTION: {question}\n")
    print("RATIONAL PLAN:")
    print(f"{rational_plan}\n")
    print("PREVIOUS ACTIONS:")
    print(json.dumps(previous_actions, indent=2))
    print("\nNOTEBOOK:")
    print(f"{notebook}\n")
    print("Chunk Queue:")
    print(chunk_queue)
    print(f"\nCURRENT NODE: {current_node}")
    print("===================\n")


def ask_llm(prompt: str):
    # Figure out to clear the context

    print(f"\nPROMPT RESPONSE: \n{'-'*20}\n")

    messages = [
    {
        'role': 'user',
        'content': prompt,
        'options': {
            "seed": 1,
            "temperature": 0.0001
        }
    },
    ]

    llm_response = ""
    model = 'xlama'

    for part in chat(model, messages=messages, stream=True):
        llm_response += part['message']['content']
        print(part['message']['content'], end='', flush=True)

    # end with a newline
    print("\n")
    print(f"END OF LLM RESPONSE\n{'-'*50}\n")

    messages = [
    {
        'role': 'user',
        'content': 'Why is the sky blue?',
        'options': {
            "seed": 1
        }
    },
    ]
    for part in chat(model, messages=messages, stream=True):
        # print(part['message']['content'], end='', flush=True)
        pass

    return llm_response