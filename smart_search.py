import json
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    'all-MiniLM-L6-v2'
)

query = input("Search: ")

query_vector = model.encode(query)

with open("photo_vectors.json", "r") as f:
    data = json.load(f)

results = []

for item in data:

    photo_vector = np.array(
        item["embedding"]
    )

    similarity = np.dot(
        query_vector,
        photo_vector
    ) / (
        np.linalg.norm(query_vector)
        * np.linalg.norm(photo_vector)
    )

    results.append(
        (
            similarity,
            item["photo"],
            item["caption"]
        )
    )

results.sort(reverse=True)

print("\nTop Matches:\n")

for score, photo, caption in results[:5]:
    print(f"{photo}")
    print(f"{caption}")
    print(f"Score: {score:.3f}")
    print()