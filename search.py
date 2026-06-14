import json

query = input("Search: ").lower()

with open("photo_data.json", "r") as f:
    data = json.load(f)

print("\nResults:\n")

for item in data:
    if query in item["caption"].lower():
        print(item["photo"])
        print(item["caption"])
        print()