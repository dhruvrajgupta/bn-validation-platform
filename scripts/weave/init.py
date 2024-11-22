import weave
import json
from openai import OpenAI

client = OpenAI()

@weave.op()
def extract_dinos(sentence: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """Extract any dinosaur `name`, their `common_name`, \
names and whether its `diet` is a herbivore or carnivore, in JSON format."""
            },
            {
                "role": "user",
                "content": sentence
            }
            ],
            response_format={ "type": "json_object" }
        )
    return response.choices[0].message.content

@weave.op()
def count_dinos(dino_data: dict) -> int:
    # count the number of items in the returned list
    k = list(dino_data.keys())[0]
    return len(dino_data[k])

@weave.op()
def dino_tracker(sentence: str) -> dict:
    # extract dinosaurs using a LLM
    dino_data = extract_dinos(sentence)

    # count the number of dinosaurs returned
    dino_data = json.loads(dino_data)
    n_dinos = count_dinos(dino_data)
    return {"n_dinosaurs": n_dinos, "dinosaurs": dino_data}

weave.init('jurassic-park')

sentence = """I watched as a Tyrannosaurus rex (T. rex) chased after a Triceratops (Trike), \
both carnivore and herbivore locked in an ancient dance. Meanwhile, a gentle giant \
Brachiosaurus (Brachi) calmly munched on treetops, blissfully unaware of the chaos below."""

result = dino_tracker(sentence)
print(result)