from graphreader.utils import paragraph_chunking
import json

corpus = (
    "Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. It was recorded at Studio 606 in Los Angeles, with the producer Nick Raskulinecz. "
    "Danko Jones is a Canadian hard rock trio from Toronto. The band consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums). The band’s music includes elements of hard rock and punk and they are known for their energetic live shows. "
    "Casa Loma (improper Spanish for 'Hill House') is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada, that is now a historic house museum and landmark. It was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt. The architect was E. J. Lennox, who designed several other city landmarks. "
)

chunked_corpus = None

corpus_map = {
    "C0": {
        "text": "Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. It was recorded at Studio 606 in Los Angeles, with the producer Nick Raskulinecz.",
        "atomic_facts": {
            "AF1":{
                "atomic_fact":"Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones.",
                "key_elements":[
                    "Never Too Loud",
                    "fourth studio album",
                    "Canadian hard rock band",
                    "Danko Jones"
                ],
                "nodes":{
                    "Canadian hard rock band":[
                        {
                        "hard rock":0.5625
                        },
                        {
                        "Canad":0.35714285714285715
                        }
                    ],
                    "Danko Jones":[
                        {
                        "Danko Jones":1.0
                        }
                    ],
                    "Never Too Loud":"Never Too Loud",
                    "fourth studio album":"fourth studio album"
                },
                "nodes_labels":{
                    "Canadian hard rock band":"hard rock",
                    "Danko Jones":"Danko Jones",
                    "Never Too Loud":"Never Too Loud",
                    "fourth studio album":"fourth studio album"
                }
            },
            "AF2":{
                "atomic_fact":"Never Too Loud was recorded at Studio 606 in Los Angeles.",
                "key_elements":[
                    "Never Too Loud",
                    "recorded",
                    "Studio 606",
                    "Los Angeles"
                ],
                "nodes":{
                    "Never Too Loud":"Never Too Loud",
                    "recorded":"recorded",
                    "Studio 606":"Studio 606",
                    "Los Angeles":"Los Angeles"
                },
                "nodes_labels":{
                    "Never Too Loud":"Never Too Loud",
                    "recorded":"recorded",
                    "Studio 606":"Studio 606",
                    "Los Angeles":"Los Angeles"
                }
            },
            "AF3":{
                "atomic_fact":"Nick Raskulinecz was the producer of Never Too Loud.",
                "key_elements":[
                    "Nick Raskulinecz",
                    "producer",
                    "Never Too Loud"
                ],
                "nodes":{
                    "Nick Raskulinecz":"Nick Raskulinecz",
                    "producer":"producer",
                    "Never Too Loud":"Never Too Loud"
                },
                "nodes_labels":{
                    "Nick Raskulinecz":"Nick Raskulinecz",
                    "producer":"producer",
                    "Never Too Loud":"Never Too Loud"
                }
            },
        }
    },
    "C1": {
        "text": "Danko Jones is a Canadian hard rock trio from Toronto. The band consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums).",
        "atomic_facts": {
            "AF4":{
                "atomic_fact":"Danko Jones is a Canadian hard rock trio from Toronto.",
                "key_elements":[
                    "Danko Jones",
                    "Canadian",
                    "hard rock trio",
                    "Toronto"
                ],
                "nodes":{
                    "hard rock trio":[
                        {
                        "hard rock":0.782608695652174
                        }
                    ],
                    "Danko Jones":[
                        {
                        "Danko Jones":1.0
                        }
                    ],
                    "Toronto":[
                        {
                        "Toronto":1.0
                        }
                    ],
                    "Canadian":[
                        {
                        "Canad":0.7692307692307693
                        }
                    ]
                },
                "nodes_labels":{
                    "hard rock trio":"hard rock",
                    "Danko Jones":"Danko Jones",
                    "Toronto":"Toronto",
                    "Canadian":"Canada"
                }
            },
            "AF5":{
                "atomic_fact":"The band Danko Jones consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums).",
                "key_elements":[
                    "Danko Jones",
                    "Danko Jones (vocals/guitar)",
                    "John 'JC' Calabrese (bass)",
                    "Rich Knox (drums)"
                ],
                "nodes":{
                    "Danko Jones":[
                        {
                        "Danko Jones":1.0
                        }
                    ],
                    "Danko Jones (vocals/guitar)":[
                        {
                        "Danko Jones":0.5789473684210527
                        }
                    ],
                    "John 'JC' Calabrese (bass)":"John 'JC' Calabrese (bass)",
                    "Rich Knox (drums)":"Rich Knox (drums)"
                },
                "nodes_labels":{
                    "Danko Jones":"Danko Jones",
                    "Danko Jones (vocals/guitar)":"Danko Jones",
                    "John 'JC' Calabrese (bass)":"John 'JC' Calabrese (bass)",
                    "Rich Knox (drums)":"Rich Knox (drums)"
                }
            },
        }
    },
    "C2": {
        "text": "The band\u2019s music includes elements of hard rock and punk and they are known for their energetic live shows. Casa Loma (improper Spanish for 'Hill House') is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada, that is now a historic house museum and landmark.",
        "atomic_facts": {
            "AF6":{
                "atomic_fact":"Danko Jones' music includes elements of hard rock and punk.",
                "key_elements":[
                    "Danko Jones",
                    "music",
                    "elements",
                    "hard rock",
                    "punk"
                ],
                "nodes":{
                    "hard rock":[
                        {
                        "hard rock":1.0
                        }
                    ],
                    "Danko Jones":[
                        {
                        "Danko Jones":1.0
                        }
                    ],
                    "music":"music",
                    "elements":"elements",
                    "punk":"punk"
                },
                "nodes_labels":{
                    "hard rock":"hard rock",
                    "Danko Jones":"Danko Jones",
                    "music":"music",
                    "elements":"elements",
                    "punk":"punk"
                }
            },
            "AF7":{
                "atomic_fact":"Danko Jones is known for their energetic live shows.",
                "key_elements":[
                    "Danko Jones",
                    "known",
                    "energetic live shows"
                ],
                "nodes":{
                    "Danko Jones":[
                        {
                        "Danko Jones":1.0
                        }
                    ],
                    "known":"known",
                    "energetic live shows":"energetic live shows"
                },
                "nodes_labels":{
                    "Danko Jones":"Danko Jones",
                    "known":"known",
                    "energetic live shows":"energetic live shows"
                }
            },
            "AF8":{
                "atomic_fact":"Casa Loma is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada.",
                "key_elements":[
                    "Casa Loma",
                    "Gothic Revival",
                    "castle-style mansion",
                    "garden",
                    "midtown Toronto",
                    "Ontario",
                    "Canada"
                ],
                "nodes":{
                    "midtown Toronto":[
                        {
                        "Toronto":0.6363636363636364
                        }
                    ],
                    "Canada":[
                        {
                        "Canad":0.9090909090909091
                        }
                    ],
                    "Casa Loma":"Casa Loma",
                    "Gothic Revival":"Gothic Revival",
                    "castle-style mansion":"castle-style mansion",
                    "garden":"garden",
                    "Ontario":"Ontario"
                },
                "nodes_labels":{
                    "midtown Toronto":"Toronto",
                    "Canada":"Canada",
                    "Casa Loma":"Casa Loma",
                    "Gothic Revival":"Gothic Revival",
                    "castle-style mansion":"castle-style mansion",
                    "garden":"garden",
                    "Ontario":"Ontario"
                }
            },
            "AF9":{
                "atomic_fact":"Casa Loma is now a historic house museum and landmark.",
                "key_elements":[
                    "Casa Loma",
                    "historic house museum",
                    "landmark"
                ],
                "nodes":{
                    "landmark":[
                        {
                        "landmark":1.0
                        }
                    ],
                    "Casa Loma":"Casa Loma",
                    "historic house museum":"historic house museum"
                },
                "nodes_labels":{
                    "landmark":"landmark",
                    "Casa Loma":"Casa Loma",
                    "historic house museum":"historic house museum"
                }
            },
        }
    },
    "C3": {
        "text": "It was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt. The architect was E. J. Lennox, who designed several other city landmarks.",
        "atomic_facts": {
            "AF10":{
                "atomic_fact":"Casa Loma was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt.",
                "key_elements":[
                    "Casa Loma",
                    "constructed",
                    "1911",
                    "1914",
                    "residence",
                    "financier",
                    "Sir Henry Pellatt"
                ],
                "nodes":{
                    "Casa Loma":"Casa Loma",
                    "constructed":"constructed",
                    "1911":"1911",
                    "1914":"1914",
                    "residence":"residence",
                    "financier":"financier",
                    "Sir Henry Pellatt":"Sir Henry Pellatt"
                },
                "nodes_labels":{
                    "Casa Loma":"Casa Loma",
                    "constructed":"constructed",
                    "1911":"1911",
                    "1914":"1914",
                    "residence":"residence",
                    "financier":"financier",
                    "Sir Henry Pellatt":"Sir Henry Pellatt"
                }
            },
            "AF11":{
                "atomic_fact":"The architect of Casa Loma was E. J. Lennox.",
                "key_elements":[
                    "architect",
                    "Casa Loma",
                    "E. J. Lennox"
                ],
                "nodes":{
                    "architect":"architect",
                    "Casa Loma":"Casa Loma",
                    "E. J. Lennox":"E. J. Lennox"
                },
                "nodes_labels":{
                    "architect":"architect",
                    "Casa Loma":"Casa Loma",
                    "E. J. Lennox":"E. J. Lennox"
                }
            },
            "AF12":{
                "atomic_fact":"E. J. Lennox designed several other city landmarks.",
                "key_elements":[
                    "E. J. Lennox",
                    "designed",
                    "several other city landmarks"
                ],
                "nodes":{
                    "several other city landmarks":[
                        {
                        "landmark":0.4444444444444444
                        }
                    ],
                    "E. J. Lennox":"E. J. Lennox",
                    "designed":"designed"
                },
                "nodes_labels":{
                    "several other city landmarks":"landmark",
                    "E. J. Lennox":"E. J. Lennox",
                    "designed":"designed"
                }
            }
        }
    }
}

corpus_map_small = {
    "C0": {
        "text": "Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. It was recorded at Studio 606 in Los Angeles, with the producer Nick Raskulinecz.",
        "atomic_facts": {
            "AF1":{
                "atomic_fact":"Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones.",
                "key_elements":[
                    "Never Too Loud",
                    "fourth studio album",
                    "Canadian hard rock band",
                    "Danko Jones"
                ],
                "nodes":{
                    "Canadian hard rock band":[
                        {
                        "hard rock":0.5625
                        },
                        {
                        "Canad":0.35714285714285715
                        }
                    ],
                    "Danko Jones":[
                        {
                        "Danko Jones":1.0
                        }
                    ],
                    "Never Too Loud":"Never Too Loud",
                    "fourth studio album":"fourth studio album"
                },
                "nodes_labels":{
                    "Canadian hard rock band":"hard rock",
                    "Danko Jones":"Danko Jones",
                    "Never Too Loud":"Never Too Loud",
                    "fourth studio album":"fourth studio album"
                }
            },
        }
    },
    "C1": {
        "text": "Danko Jones is a Canadian hard rock trio from Toronto. The band consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums).",
        "atomic_facts": {
            "AF4":{
                "atomic_fact":"Danko Jones is a Canadian hard rock trio from Toronto.",
                "key_elements":[
                    "Danko Jones",
                    "Canadian",
                    "hard rock trio",
                    "Toronto"
                ],
                "nodes":{
                    "hard rock trio":[
                        {
                        "hard rock":0.782608695652174
                        }
                    ],
                    "Danko Jones":[
                        {
                        "Danko Jones":1.0
                        }
                    ],
                    "Toronto":[
                        {
                        "Toronto":1.0
                        }
                    ],
                    "Canadian":[
                        {
                        "Canad":0.7692307692307693
                        }
                    ]
                },
                "nodes_labels":{
                    "hard rock trio":"hard rock",
                    "Danko Jones":"Danko Jones",
                    "Toronto":"Toronto",
                    "Canadian":"Canada"
                }
            },
        }
    },
    "C2": {
        "text": "The band\u2019s music includes elements of hard rock and punk and they are known for their energetic live shows. Casa Loma (improper Spanish for 'Hill House') is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada, that is now a historic house museum and landmark.",
        "atomic_facts": {
            "AF8":{
                "atomic_fact":"Casa Loma is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada.",
                "key_elements":[
                    "Casa Loma",
                    "Gothic Revival",
                    "castle-style mansion",
                    "garden",
                    "midtown Toronto",
                    "Ontario",
                    "Canada"
                ],
                "nodes":{
                    "midtown Toronto":[
                        {
                        "Toronto":0.6363636363636364
                        }
                    ],
                    "Canada":[
                        {
                        "Canad":0.9090909090909091
                        }
                    ],
                    "Casa Loma":"Casa Loma",
                    "Gothic Revival":"Gothic Revival",
                    "castle-style mansion":"castle-style mansion",
                    "garden":"garden",
                    "Ontario":"Ontario"
                },
                "nodes_labels":{
                    "midtown Toronto":"Toronto",
                    "Canada":"Canada",
                    "Casa Loma":"Casa Loma",
                    "Gothic Revival":"Gothic Revival",
                    "castle-style mansion":"castle-style mansion",
                    "garden":"garden",
                    "Ontario":"Ontario"
                }
            }
        }
    },
    "C3": {
        "text": "It was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt. The architect was E. J. Lennox, who designed several other city landmarks.",
        "atomic_facts": {
            "AF10":{
                "atomic_fact":"Casa Loma was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt.",
                "key_elements":[
                    "Casa Loma",
                    "constructed",
                    "1911",
                    "1914",
                    "residence",
                    "financier",
                    "Sir Henry Pellatt"
                ],
                "nodes":{
                    "Casa Loma":"Casa Loma",
                    "constructed":"constructed",
                    "1911":"1911",
                    "1914":"1914",
                    "residence":"residence",
                    "financier":"financier",
                    "Sir Henry Pellatt":"Sir Henry Pellatt"
                },
                "nodes_labels":{
                    "Casa Loma":"Casa Loma",
                    "constructed":"constructed",
                    "1911":"1911",
                    "1914":"1914",
                    "residence":"residence",
                    "financier":"financier",
                    "Sir Henry Pellatt":"Sir Henry Pellatt"
                }
            }
        }
    }
}

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

def main():
    chunked_corpus = paragraph_chunking(corpus, sentences_per_chunk=2)
    for index, chunk in enumerate(chunked_corpus):
        corpus_map[f"C{index}"] = {
            "text": chunk,
        }

    print(json.dumps(corpus_map, indent=4))

if __name__ == "__main__":
    main()