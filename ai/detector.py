from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from backend.config import YOLO_MODEL


@lru_cache(maxsize=1)
def _load_yolo():
    from ultralytics import YOLO

    return YOLO(YOLO_MODEL)


def detect_objects(image_path: str | Path) -> list[str]:
    try:
        yolo = _load_yolo()
        detections = yolo(str(image_path), verbose=False)
        objects: set[str] = set()
        for result in detections:
            for box in result.boxes:
                objects.add(yolo.names[int(box.cls)])
        return sorted(objects)
    except Exception:
        return []
