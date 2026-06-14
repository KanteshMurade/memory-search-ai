import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

with open("photo_data.json", "r") as f:
    data = json.load(f)

for item in data:
    item["embedding"] = model.encode(
        item["caption"]
    ).tolist()

with open("photo_vectors.json", "w") as f:
    json.dump(data, f)

print("Vectors created!")