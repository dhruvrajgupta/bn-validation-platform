import json
from openai import OpenAI

import weave

@weave.op()
def extract_dinos(wmodel: weave.Model, sentence: str) -> dict:
    response = wmodel.client.chat.completions.create(
        model=wmodel.model_name,
        temperature=wmodel.temperature,
        messages=[
            {
                "role": "system",
                "content": wmodel.system_prompt
            },
            {
                "role": "user",
                "content": sentence
            }
            ],
            response_format={ "type": "json_object" }
        )
    return response.choices[0].message.content

# Sub-class with a weave.Model
class ExtractDinos(weave.Model):
    client: OpenAI = None
    model_name: str
    temperature: float
    system_prompt: str

    # Ensure your function is called `invoke` or `predict`
    @weave.op()
    def invoke(self, sentence: str) -> dict:
        dino_data  = extract_dinos(self, sentence)
        return json.loads(dino_data)


weave.init('jurassic-park')
client = OpenAI()

system_prompt = """Extract any dinosaur `name`, their `common_name`, \
names and whether its `diet` is a herbivore or carnivore, in JSON format."""

dinos = ExtractDinos(
    client=client,
    model_name='gpt-4o',
    temperature=0.4,
    system_prompt=system_prompt
)

sentence = """I watched as a Tyrannosaurus rex (T. rex) chased after a Triceratops (Trike), \
both carnivore and herbivore locked in an ancient dance. Meanwhile, a gentle giant \
Brachiosaurus (Brachi) calmly munched on treetops, blissfully unaware of the chaos below."""

result = dinos.invoke(sentence)
print(result)