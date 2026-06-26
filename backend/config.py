from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PHOTOS_DIR = BASE_DIR / "photos"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
MODELS_DIR = BASE_DIR / "models"
KNOWN_FACES_DIR = DATA_DIR / "known_faces"

DATABASE_URL = f"sqlite:///{DATA_DIR / 'memory_search.db'}"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CAPTION_MODEL = "Salesforce/blip-image-captioning-base"
YOLO_MODEL = str(BASE_DIR / "yolov8n.pt")


def ensure_directories() -> None:
    for directory in (DATA_DIR, PHOTOS_DIR, STATIC_DIR, MODELS_DIR, KNOWN_FACES_DIR):
        directory.mkdir(parents=True, exist_ok=True)
