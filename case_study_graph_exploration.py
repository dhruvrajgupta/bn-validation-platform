from utils import paragraph_chunking
from corpus import corpus, corpus_map_small
import json

def main():

    chunk_queue = []

    print(f"\nCorpus: \n{corpus}\n")

    corpus_map = corpus_map_small

    #
    # all atomic facts associated with a node are grouped by their 
    # corresponding chunks, labeled with the respective chunk IDs, 
    # and fed to the agent.
    #
    node_grouped_chunks_afs = {}

    for chunk_id, chunk in corpus_map.items():
        
        chunk_text = chunk["text"]
        chunk_atomic_facts = chunk["atomic_facts"]

        for af_id, af in chunk_atomic_facts.items():

            atomic_fact = af["atomic_fact"]
            atomic_fact_key_elements = af["key_elements"]
            atomic_fact_nodes = af["nodes"]
            atomic_fact_nodes_labels = af["nodes_labels"]

            for af_key_element, node_label in atomic_fact_nodes_labels.items():
                print(f"{af_key_element} -> {node_label}")

                if node_label not in node_grouped_chunks_afs:
                    node_grouped_chunks_afs[node_label] = {
                        "chunk_ids": [chunk_id],
                        "atomic_facts": [{af_id: atomic_fact}]
                    }
                else:
                    node_grouped_chunks_afs[node_label]["chunk_ids"].append(chunk_id)
                    node_grouped_chunks_afs[node_label]["atomic_facts"].append({af_id: atomic_fact})

    print()
    print(json.dumps(node_grouped_chunks_afs, indent=2))

if __name__ == '__main__':
    main()