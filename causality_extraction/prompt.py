import openai

openai.api_key = "sk-**********************"


def get_completion(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

prompt_1 = f"""
Perform the following actions:
1 - You will be provided with text delimited by triple quotes. Extract the cause, effect,signal, condition and action from the given sentence. Enclose the begnining and the end with tags as given in the examples below. Use A for action, C for cause, CO for condition, E for effect and O for others.
Example 1: Pregnant persons with gestational diabetes  are at increased risk for maternal and fetal complications, including preeclampsia, fetal macrosomia (which can cause shoulder dystocia and birth injury), and neonatal hypoglycemia.
Example 2: Gestational diabetes  has also been associated with an increased risk of several long-term health outcomes in pregnant persons and intermediate outcomes in their offspring .
Example 3: EVIDENCE ASSESSMENT The USPSTF concludes with moderate certainty that there is a moderate net benefit  to screening for gestational diabetes at 24 weeks of gestation or after  to improve maternal and fetal outcomes .
Example 4: RECOMMENDATION The USPSTF recommends screening for gestational diabetes  in asymptomatic pregnant persons at 24 weeks of gestation or after .

2 - Output a table that contains the following columns \
keys: Sentence , prediction
Separate your answers with line breaks.

Text:
```
```
"""
response = get_completion(prompt_1)
print("Completion for prompt 1:")
print(response)
