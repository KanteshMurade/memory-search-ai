from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import Image

from backend.config import CAPTION_MODEL


@lru_cache(maxsize=1)
def _load_blip():
    from transformers import BlipForConditionalGeneration, BlipProcessor

    processor = BlipProcessor.from_pretrained(CAPTION_MODEL)
    model = BlipForConditionalGeneration.from_pretrained(CAPTION_MODEL)
    return processor, model


def generate_caption(image_path: str | Path) -> str:
    path = Path(image_path)
    try:
        processor, model = _load_blip()
        image = Image.open(path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        output = model.generate(**inputs, max_new_tokens=35)
        return processor.decode(output[0], skip_special_tokens=True)
    except Exception:
        return f"Photo named {path.stem.replace('_', ' ').replace('-', ' ')}"
