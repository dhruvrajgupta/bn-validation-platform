from utils import paragraph_chunking

def main():

    # Passage
    corpus = (
        "Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. It was recorded at Studio 606 in Los Angeles, with the producer Nick Raskulinecz. "
        "Danko Jones is a Canadian hard rock trio from Toronto. The band consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums). The band’s music includes elements of hard rock and punk and they are known for their energetic live shows. "
        "Casa Loma (improper Spanish for 'Hill House') is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada, that is now a historic house museum and landmark. It was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt. The architect was E. J. Lennox, who designed several other city landmarks. "
    )

    print(f"\nCorpus: \n{corpus}\n")


    """
    CORPUS_MAP SCHEMA:
    {
        "ChunkID#": {
            "text": "...",
            "atomic_facts": {
                "AtomicFactID#": {
                    "atomic_fact" : "...",
                    "key_elements": [...],
                    "nodes": {...},
                    "nodes_labels": {...}
                }
            }
        }
    }
    """
    corpus_map = {
        "C1": {
            "text": "Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. It was recorded at Studio 606 in Los Angeles, with the producer Nick Raskulinecz. Danko Jones is a Canadian hard rock trio from Toronto. ",
            "atomic_facts": {
                "AF1": {
                    "atomic_fact" : "Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones.",
                    "key_elements": ['Never Too Loud', 'fourth studio album', 'Canadian hard rock band', 'Danko Jones'],
                    "nodes": {
                        "Canadian hard rock band": [
                            {
                                "hard rock": 0.5625
                            },
                            {
                                "Canad": 0.35714285714285715
                            }
                        ],
                        "Danko Jones": [
                            {
                                "Danko Jones": 1.0
                            }
                        ],
                        "Never Too Loud": "Never Too Loud",
                        "fourth studio album": "fourth studio album"
                    },
                    "nodes_labels": {'Canadian hard rock band': 'hard rock', 'Danko Jones': 'Danko Jones', 'Never Too Loud': 'Never Too Loud', 'fourth studio album': 'fourth studio album'},
                },
                "AF2": {
                    "atomic_fact": "Danko Jones is a Canadian hard rock trio from Toronto.",
                    "key_elements": ['Danko Jones', 'Canadian', 'hard rock trio', 'Toronto'],
                    "nodes": {
                        "hard rock trio": [
                            {
                                "hard rock": 0.782608695652174
                            }
                        ],
                        "Danko Jones": [
                            {
                                "Danko Jones": 1.0
                            }
                        ],
                        "Toronto": [
                            {
                                "Toronto": 1.0
                            }
                        ],
                        "Canadian": [
                            {
                                "Canad": 0.7692307692307693
                            }
                        ]
                    },
                    "nodes_labels": {'hard rock trio': 'hard rock', 'Danko Jones': 'Danko Jones', 'Toronto': 'Toronto', 'Canadian': 'Canada'},
                }
            },
        },
        "C2": {
            "text": "The band consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums). The band’s music includes elements of hard rock and punk and they are known for their energetic live shows. Casa Loma (improper Spanish for 'Hill House') is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada, that is now a historic house museum and landmark.",
            "atomic_facts": {
                "AF8": {
                    "atomic_fact": "Casa Loma is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada.",
                    "key_elements": ['Casa Loma', 'Gothic Revival', 'castle-style mansion', 'garden', 'midtown Toronto', 'Ontario', 'Canada'],
                    "nodes": {
                        "midtown Toronto": [
                            {
                                "Toronto": 0.6363636363636364
                            }
                        ],
                        "Canada": [
                            {
                                "Canad": 0.9090909090909091
                            }
                        ],
                        "Casa Loma": "Casa Loma",
                        "Gothic Revival": "Gothic Revival",
                        "castle-style mansion": "castle-style mansion",
                        "garden": "garden",
                        "Ontario": "Ontario"
                    },
                    "nodes_labels": {'midtown Toronto': 'Toronto', 'Canada': 'Canada', 'Casa Loma': 'Casa Loma', 'Gothic Revival': 'Gothic Revival', 'castle-style mansion': 'castle-style mansion', 'garden': 'garden', 'Ontario': 'Ontario'},
                }
            }
        }
    }

    # Chunking the corpus
    # print(f"Chunking the corpus...\n{'='*50}\n")
    # chunked_corpus = paragraph_chunking(corpus, sentences_per_chunk=2)
    # for i, chunk in enumerate(chunked_corpus):
    #     print(f"Chunk {i+1}:\n{chunk}\n")

if __name__ == '__main__':
    main()