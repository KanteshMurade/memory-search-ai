import json

with open("advanced_data.json", "r") as f:
    advanced_data = json.load(f)

with open("face_data.json", "r") as f:
    face_data = json.load(f)

face_lookup = {}

for item in face_data:
    face_lookup[item["photo"]] = item["people"]

master_data = []

for item in advanced_data:

    photo = item["photo"]

    master_data.append({
        "photo": photo,
        "caption": item["caption"],
        "objects": item["objects"],
        "people": face_lookup.get(photo, [])
    })

with open("master_data.json", "w") as f:
    json.dump(master_data, f, indent=4)

print("master_data.json created")