from pydantic import BaseModel
from typing import List

class ListCauseEffect(BaseModel):
    result: List[str]

# MODIFIED
# Causality extraction from medical text using Large Language Models (LLMs), Gopalkrishnan et al.
EXTRACT_CAUSALITY = """\
Perform the following actions:
1 - You will be provided with text delimited by triple quotes. Extract the cause, effect, signal, condition and action from the given sentence. Enclose the begnining and the end with tags as given in the examples below. Use A for action, C for cause, CO for condition and E for effect.
Example 1: Pregnant persons with gestational diabetes  are at increased risk for maternal and fetal complications, including preeclampsia, fetal macrosomia (which can cause shoulder dystocia and birth injury), and neonatal hypoglycemia.
Example 2: Gestational diabetes  has also been associated with an increased risk of several long-term health outcomes in pregnant persons and intermediate outcomes in their offspring .
Example 3: EVIDENCE ASSESSMENT The USPSTF concludes with moderate certainty that there is a moderate net benefit  to screening for gestational diabetes at 24 weeks of gestation or after  to improve maternal and fetal outcomes .
Example 4: RECOMMENDATION The USPSTF recommends screening for gestational diabetes  in asymptomatic pregnant persons at 24 weeks of gestation or after .

2 - Output should be in JSON format.
Example Output:
'result': [
    '<C> Pregnant persons with gestational diabetes </C> <E> are at increased risk for maternal and fetal complications, including preeclampsia, fetal macrosomia (which can cause shoulder dystocia and birth injury), and neonatal hypoglycemia </E>.',
    ...
]

Text:
SECTION_NAME: {section_name}

SECTION_CONTENT:
```
{text}
```
"""

# '<C> Pregnant persons with gestational diabetes </C> <E> are at increased risk for maternal and fetal complications, including preeclampsia, fetal macrosomia (which can cause shoulder dystocia and birth injury), and neonatal hypoglycemia </E>.',
# '<C> Gestational diabetes </C> has also been <A> associated </A> with <E> an increased risk of several long-term health outcomes in pregnant persons and intermediate outcomes in their offspring </E>.',
#         '<O> EVIDENCE ASSESSMENT The USPSTF concludes </O> <CO> with moderate certainty </CO> that there is <E> a moderate net benefit to screening for gestational diabetes at 24 weeks of gestation or after to improve maternal and fetal outcomes </E>.',
#         '<O> RECOMMENDATION The USPSTF recommends </O> <A> screening for gestational diabetes </A> <CO> in asymptomatic pregnant persons at 24 weeks of gestation or after </CO>.',



# ATOMIC_FACTS_AND_KEY_ELEMENTS = """\
# You are now an intelligent assistant tasked with meticulously extracting atomic facts from a long text.
# 1. Atomic Facts: The smallest, indivisible facts, presented as concise sentences. These include
# propositions, theories, existences, concepts, and implicit elements like logic, causality, event
# sequences, interpersonal relationships, timelines, etc.
# Requirements:
# #####
# 1. You should extract key atomic facts comprehensively, especially those that are
# important and potentially query-worthy and do not leave out details.
# 2. Whenever applicable, mention the specific explicit subject of the atomic fact in relation to the SECTION NAME and SUMMARY
# 3. Ensure that the atomic facts you extract are presented in the same language as
# the original text (e.g., English or Chinese).
# 4. You should output a total of atomic facts that do not exceed 1024 tokens.
# 5. You should output the atomic facts as a python list of strings.
# #####
# Example:
# #####
# User:

# SUMMARY:
# This page details the AJCC TNM staging system for laryngeal cancers (8th edition, 2017). It categorizes the primary tumor (T) stages
# for different regions of the larynx: supraglottis, glottis, and subglottis. Each section describes the progression of tumor
# invasion, from limited local spread to advanced disease involving surrounding tissues and structures. T1 represents localized
# tumors, while T4 is divided into T4a for moderately advanced and T4b for very advanced disease, indicating extensive invasion
# into critical areas such as the thyroid cartilage, prevertebral space, or carotid artery encasement. Non-epithelial tumors
# are excluded from this staging system.

# SECTION NAME: Primary Tumor - Glottis

# SECTION CONTENT:
# The tumor invades soft tissues ......


# Assistant:
# [
#     "The tumor in stage T4a of the Glottis invades soft tissues of the neck, including deep extrinsic muscle of the tongue."
#     ......
# ]
# #####
# Please strictly follow the above format. Let’s begin.

# LONG TEXT:
# ```
# SUMMARY:
# {summary}

# SECTION NAME: {section_name}

# SECTION CONTENT:
# {section_content}
# ```
# """

# Here Structured Output was not giving good results
EXTRACT_ATOMIC_FACTS = """\
You are now an intelligent assistant tasked with meticulously extracting atomic facts from a long text.
1. Atomic Facts: The smallest, indivisible facts, presented as concise sentences. These include
propositions, theories, existences, concepts, and implicit elements like logic, causality, event
sequences, interpersonal relationships, timelines, etc.
Requirements:
#####
1. You should extract key atomic facts comprehensively, especially those that are
important and potentially query-worthy and do not leave out details.
2. Whenever applicable, mention the specific explicit subject of the atomic fact in relation to the SECTION NAME and SUMMARY
3. Ensure that the atomic facts you extract are presented in the same language as
the original text (e.g., English or Chinese).
4. You should output a total of atomic facts that do not exceed 1024 tokens.
5. Your answer format for each line should be: [Serial Number], [Atomic Facts].
#####
Example:
#####
User:
SECTION NAME: Primary Tumor - Glottis

SECTION CONTENT:
The tumor invades soft tissues ......


Assistant:
1. The tumor in stage T4a of the Glottis invades soft tissues of the neck, including deep extrinsic muscle of the tongue.
......

#####
Please strictly follow the above format. Let’s begin.

LONG TEXT:
```
SECTION NAME: {section_name}

SECTION CONTENT:
{section_content}
```
"""

class SectionData(BaseModel):
    section_name: str
    paragraph: List[str]

class ListSectionData(BaseModel):
    result: List[SectionData]

DATA_EXTRACTOR = """\
INSTRUCTIONS:
1. Extract the important contents of this page.
2. Extract the contents in meaningful sentences so that it can be used for clinical data mining.
3. Do not summarize.
4. Output in detail.
5. Segregate into meaningful sections.
6. Only extract the information of that specified sections.

HTML PAGE:
```
{html_page}
```

SECTIONS:
[{sections}]

Output format in JSON:
[
   {{
       "section_name": ... ,
       "paragraph": []
   }},
 ...
]

"""