import os
from PIL import Image

PHOTO_FOLDER = "photos"

for file in os.listdir(PHOTO_FOLDER):

    filepath = os.path.join(PHOTO_FOLDER, file)

    try:
        img = Image.open(filepath)

        print("\n-------------------")
        print("File Name:", file)
        print("Format:", img.format)
        print("Width:", img.width)
        print("Height:", img.height)

    except Exception as e:
        print(f"Cannot read {file}")