# Causality extraction from medical text using Large Language Models (LLMs), Gopalkrishnan et al.
EXTRACT_CAUSALITY = """\
Perform the following actions:
1 - You will be provided with text delimited by triple quotes. Extract the cause, effect,signal, condition and action from the given sentence. Enclose the begnining and the end with tags as given in the examples below. Use A for action, C for cause, CO for condition and E for effect.
Example 1: Pregnant persons with gestational diabetes  are at increased risk for maternal and fetal complications, including preeclampsia, fetal macrosomia (which can cause shoulder dystocia and birth injury), and neonatal hypoglycemia.
Example 2: Gestational diabetes  has also been associated with an increased risk of several long-term health outcomes in pregnant persons and intermediate outcomes in their offspring .
Example 3: EVIDENCE ASSESSMENT The USPSTF concludes with moderate certainty that there is a moderate net benefit  to screening for gestational diabetes at 24 weeks of gestation or after  to improve maternal and fetal outcomes .
Example 4: RECOMMENDATION The USPSTF recommends screening for gestational diabetes  in asymptomatic pregnant persons at 24 weeks of gestation or after .

2 - Output should be in JSON format.
Example Output:
'annotated_sentences': [
    '<C> Pregnant persons with gestational diabetes </C> <E> are at increased risk for maternal and fetal complications, including preeclampsia, fetal macrosomia (which can cause shoulder dystocia and birth injury), and neonatal hypoglycemia </E>.',
    ...
]

Text:
```
{text}
```
"""

# '<C> Pregnant persons with gestational diabetes </C> <E> are at increased risk for maternal and fetal complications, including preeclampsia, fetal macrosomia (which can cause shoulder dystocia and birth injury), and neonatal hypoglycemia </E>.',
# '<C> Gestational diabetes </C> has also been <A> associated </A> with <E> an increased risk of several long-term health outcomes in pregnant persons and intermediate outcomes in their offspring </E>.',
#         '<O> EVIDENCE ASSESSMENT The USPSTF concludes </O> <CO> with moderate certainty </CO> that there is <E> a moderate net benefit to screening for gestational diabetes at 24 weeks of gestation or after to improve maternal and fetal outcomes </E>.',
#         '<O> RECOMMENDATION The USPSTF recommends </O> <A> screening for gestational diabetes </A> <CO> in asymptomatic pregnant persons at 24 weeks of gestation or after </CO>.',