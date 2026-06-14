import os
import json
from PIL import Image
from ultralytics import YOLO
from transformers import BlipProcessor
from transformers import BlipForConditionalGeneration

PHOTO_FOLDER = "photos"

yolo = YOLO("yolov8n.pt")

processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

results_data = []

for file in os.listdir(PHOTO_FOLDER):

    if not file.lower().endswith(
        (".jpg",".jpeg",".png",".webp")
    ):
        continue

    path = os.path.join(
        PHOTO_FOLDER,
        file
    )

    image = Image.open(path).convert("RGB")

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    output = model.generate(
        **inputs,
        max_new_tokens=30
    )

    caption = processor.decode(
        output[0],
        skip_special_tokens=True
    )

    detections = yolo(path)

    objects = []

    for r in detections:
        for box in r.boxes:
            cls = int(box.cls)
            objects.append(
                yolo.names[cls]
            )

    objects = list(set(objects))

    results_data.append({
        "photo": file,
        "caption": caption,
        "objects": objects
    })

with open(
    "advanced_data.json",
    "w"
) as f:
    json.dump(
        results_data,
        f,
        indent=4
    )

print("Done")