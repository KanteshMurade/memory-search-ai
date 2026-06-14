import json

query = input("Search: ").lower()

with open("advanced_data.json", "r") as f:
    data = json.load(f)

print("\nResults:\n")

for item in data:

    caption = item["caption"].lower()

    objects = " ".join(
        item["objects"]
    ).lower()

    searchable_text = (
        caption + " " + objects
    )

    if query in searchable_text:

        print(
            f"Photo: {item['photo']}"
        )

        print(
            f"Caption: {item['caption']}"
        )

        print(
            f"Objects: {item['objects']}"
        )

        print()