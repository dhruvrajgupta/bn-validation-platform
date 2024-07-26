previous_actions = [
    "Exploring Atomic Facts of Node: Los Angeles",
    "Exploring Chunk: C0",
    "Empty Chunk Queue, so exploring connected nodes to Node: 'Los Angeles'",
    "Exploring Neighbouring Nodes of Node: Los Angeles",
    "Exploring Atomic Facts of Node: recorded",
    "Exploring Chunk: C0",
    "Empty Chunk Queue, so exploring connected nodes to Node: 'recorded'",
    "Exploring Neighbouring Nodes of Node: recorded",
    "Exploring Atomic Facts of Node: Studio 606",
    "Exploring Chunk: C0"
]

current_chunk = None

for item in reversed(previous_actions):
    if "Exploring Chunk" in item:
        current_chunk = item.split(":")[-1].strip()
        break

print(current_chunk)