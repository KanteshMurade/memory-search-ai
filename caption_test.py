from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Change this to your image filename
IMAGE_PATH = "photos/photo1.jpeg"

print("Loading model... (first run may take a few minutes)")

processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

image = Image.open(IMAGE_PATH).convert("RGB")

inputs = processor(images=image, return_tensors="pt")

output = model.generate(**inputs)

caption = processor.decode(
    output[0],
    skip_special_tokens=True
)

print("\nCaption:")
print(caption)