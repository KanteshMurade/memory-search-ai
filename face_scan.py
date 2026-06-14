import os
import json
import face_recognition

KNOWN_FOLDER = "known_faces"
PHOTO_FOLDER = "photos"

known_encodings = []
known_names = []

print("Loading known faces...")

for file in os.listdir(KNOWN_FOLDER):

    image_path = os.path.join(
        KNOWN_FOLDER,
        file
    )

    image = face_recognition.load_image_file(
        image_path
    )

    encodings = face_recognition.face_encodings(
        image
    )

    if len(encodings) > 0:

        known_encodings.append(
            encodings[0]
        )

        known_names.append(
            os.path.splitext(file)[0]
        )

print("Known faces loaded")

results = []

for file in os.listdir(PHOTO_FOLDER):

    if not file.lower().endswith(
        (".jpg",".jpeg",".png")
    ):
        continue

    path = os.path.join(
        PHOTO_FOLDER,
        file
    )

    image = face_recognition.load_image_file(
        path
    )

    face_locations = (
        face_recognition.face_locations(
            image
        )
    )

    face_encodings = (
        face_recognition.face_encodings(
            image,
            face_locations
        )
    )

    people_found = []

    for face_encoding in face_encodings:

        matches = (
            face_recognition.compare_faces(
                known_encodings,
                face_encoding
            )
        )

        name = "Unknown"

        if True in matches:

            match_index = (
                matches.index(True)
            )

            name = known_names[
                match_index
            ]

        people_found.append(name)

    results.append({
        "photo": file,
        "people": people_found
    })

with open(
    "face_data.json",
    "w"
) as f:
    json.dump(
        results,
        f,
        indent=4
    )

print("Saved to face_data.json")