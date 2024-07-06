question_text = "Question What is the name of the castle in the city where the performer of Never Too Loud was formed?"
answer = "Casa Loma"

supoorting_passages = [
    "Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. It was recorded at Studio 606 in Los Angeles, with the producer Nick Raskulinecz.",
    "Danko Jones is a Canadian hard rock trio from Toronto. The band consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums). The band’s music includes elements of hard rock and punk and they are known for their energetic live shows.",
    "Casa Loma (improper Spanish for 'Hill House') is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada, that is now a historic house museum and landmark. It was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt. The architect was E. J. Lennox, who designed several other city landmarks."
]

###########################################################
##              GRAPH CONSTRUCTION                       ##
###########################################################

gc_prompt = """
    You are now an intelligent assistant tasked with meticulously extracting both key elements and 
    atomic facts from a long text.
    1. Key Elements: The essential nouns (e.g., characters, times, events, places, numbers), verbs (e.g., 
    actions), and adjectives (e.g., states, feelings) that are pivotal to the text’s narrative.
    2. Atomic Facts: The smallest, indivisible facts, presented as concise sentences. These include 
    propositions, theories, existences, concepts, and implicit elements like logic, causality, event 
    sequences, interpersonal relationships, timelines, etc.

    Requirements: 
    #####
    1. Ensure that all identified key elements are reflected within the corresponding atomic facts. 
    2. You should extract key elements and atomic facts comprehensively, especially those that are 
    important and potentially query-worthy and do not leave out details. 
    3. Whenever applicable, replace pronouns with their specific noun counterparts (e.g., change I, He, 
    She to actual names). 
    4. Ensure that the key elements and atomic facts you extract are presented in the same language as 
    the original text (e.g., English or Chinese). 
    5. You should output a total of key elements and atomic facts that do not exceed 1024 tokens. 
    6. Your answer format for each line should be: [Serial Number], [Atomic Facts], [List of Key 
    Elements, separated with ‘|’]
    #####

    Example: 
    ##### 
    User: One day, a father and his little son ...... 
    
    Assistant: 
    1. One day, a father and his little son were going home. | father | little son | going home 
    2. ...... 
    ##### 
    
    Please strictly follow the above format. Let’s begin.
"""

gc_prompt_result = """
    1. Never Too Loud is the fourth studio album by Canadian hard rock band Danko Jones. | Never Too Loud | fourth studio album | Canadian hard rock band | Danko Jones
    2. Never Too Loud was recorded at Studio 606 in Los Angeles. | Never Too Loud | recorded | Studio 606 | Los Angeles
    3. Nick Raskulinecz was the producer of Never Too Loud. | Nick Raskulinecz | producer | Never Too Loud
    4. Danko Jones is a Canadian hard rock trio from Toronto. | Danko Jones | Canadian | hard rock trio | Toronto
    5. The band Danko Jones consists of Danko Jones (vocals/guitar), John 'JC' Calabrese (bass), and Rich Knox (drums). | Danko Jones | Danko Jones (vocals/guitar) | John 'JC' Calabrese (bass) | Rich Knox (drums)
    6. Danko Jones' music includes elements of hard rock and punk. | Danko Jones | music | elements | hard rock | punk
    7. Danko Jones is known for their energetic live shows. | Danko Jones | known | energetic live shows
    8. Casa Loma is a Gothic Revival castle-style mansion and garden in midtown Toronto, Ontario, Canada. | Casa Loma | Gothic Revival | castle-style mansion | garden | midtown Toronto | Ontario | Canada
    9. Casa Loma is now a historic house museum and landmark. | Casa Loma | historic house museum | landmark
    10. Casa Loma was constructed from 1911 to 1914 as a residence for financier Sir Henry Pellatt. | Casa Loma | constructed | 1911 | 1914 | residence | financier | Sir Henry Pellatt
    11. The architect of Casa Loma was E. J. Lennox. | architect | Casa Loma | E. J. Lennox
    12. E. J. Lennox designed several other city landmarks. | E. J. Lennox | designed | several other city landmarks
"""

###
# Extract atomic facts and key elements
###
gc_prompt_result_list = [x.strip() for x in gc_prompt_result.splitlines()]
list_key_elements = []
for af_and_ke in gc_prompt_result_list:
    if len(af_and_ke):
        # print(af_and_ke)
        atomic_fact = af_and_ke.split("|")[0].strip()[af_and_ke.find(".")+1:].strip()
        print(atomic_fact)
        key_elements = [x.strip() for x in af_and_ke.split("|")[1:]]
        print(key_elements)
        for ke in key_elements:
            list_key_elements.append(ke)
        print("\n")