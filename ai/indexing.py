from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image, ExifTags
from sqlalchemy.orm import Session

from ai.caption import generate_caption
from ai.detector import detect_objects
from ai.embeddings import embed_text, photo_embedding_text
from ai.faces import recognize_people
from backend.config import IMAGE_EXTENSIONS, PHOTOS_DIR
from backend.database import Photo, find_photo, list_to_text, pack_vector


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def extract_metadata(image_path: Path) -> tuple[str | None, str | None]:
    date = None
    try:
        image = Image.open(image_path)
        exif = image.getexif()
        tags = {ExifTags.TAGS.get(key, key): value for key, value in exif.items()}
        date = tags.get("DateTimeOriginal") or tags.get("DateTime")
    except Exception:
        date = None

    if not date:
        timestamp = image_path.stat().st_mtime
        date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    return date, None


def index_photo(db: Session, image_path: str | Path, force: bool = False) -> Photo:
    path = Path(image_path)
    existing = find_photo(db, path.name)
    if existing and not force:
        return existing

    caption = generate_caption(path)
    objects = detect_objects(path)
    people = recognize_people(db, path)
    date, location = extract_metadata(path)
    embedding_text = photo_embedding_text(caption, objects, people, date, location)
    embedding = pack_vector(embed_text(embedding_text))

    photo = existing or Photo(filename=path.name, path=str(path))
    photo.path = str(path)
    photo.caption = caption
    photo.objects = list_to_text(objects)
    photo.people = list_to_text(people)
    photo.date = date
    photo.location = location
    photo.embedding = embedding
    photo.indexed_at = datetime.utcnow()

    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def index_all_photos(db: Session, force: bool = False) -> int:
    count = 0
    for path in sorted(PHOTOS_DIR.iterdir()):
        if is_image(path):
            index_photo(db, path, force=force)
            count += 1
    return count


def save_uploaded_photo(upload_file, destination_dir: Path = PHOTOS_DIR) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / Path(upload_file.filename).name
    stem = destination.stem
    suffix = destination.suffix
    counter = 1
    while destination.exists():
        destination = destination_dir / f"{stem}-{counter}{suffix}"
        counter += 1

    with destination.open("wb") as handle:
        shutil.copyfileobj(upload_file.file, handle)
    return destination
