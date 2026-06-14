import os
import json
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

PHOTO_FOLDER = "photos"

print("Loading AI model...")

processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

photo_data = []

for file in os.listdir(PHOTO_FOLDER):

    if file.lower().endswith(
        (".jpg", ".jpeg", ".png", ".webp")
    ):

        image_path = os.path.join(PHOTO_FOLDER, file)

        try:
            image = Image.open(image_path).convert("RGB")

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

            print(f"{file} -> {caption}")

            photo_data.append({
                "photo": file,
                "caption": caption
            })

        except Exception as e:
            print(f"Error: {file}")

with open("photo_data.json", "w") as f:
    json.dump(photo_data, f, indent=4)

print("\nSaved to photo_data.json")