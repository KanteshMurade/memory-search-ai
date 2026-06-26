from __future__ import annotations

import numpy as np
from sqlalchemy.orm import Session

from ai.embeddings import embed_text
from backend.database import Photo, photo_to_view, text_to_list, unpack_vector


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    left_norm = np.linalg.norm(left)
    right_norm = np.linalg.norm(right)
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return float(np.dot(left, right) / (left_norm * right_norm))


def _matches_filter(value: str | None, selected: str | None) -> bool:
    if not selected:
        return True
    return selected.lower() in (value or "").lower()


def _matches_list_filter(value: str | None, selected: str | None) -> bool:
    if not selected:
        return True
    selected_lower = selected.lower()
    return any(selected_lower == item.lower() for item in text_to_list(value))


def _filtered_photos(
    photos: list[Photo],
    date: str | None = None,
    location: str | None = None,
    person: str | None = None,
    object_name: str | None = None,
) -> list[Photo]:
    return [
        photo
        for photo in photos
        if _matches_filter(photo.date, date)
        and _matches_filter(photo.location, location)
        and _matches_list_filter(photo.people, person)
        and _matches_list_filter(photo.objects, object_name)
    ]


def semantic_search(
    db: Session,
    query: str,
    limit: int = 40,
    date: str | None = None,
    location: str | None = None,
    person: str | None = None,
    object_name: str | None = None,
) -> list[dict]:
    photos = db.query(Photo).all()
    photos = _filtered_photos(
        photos,
        date=date,
        location=location,
        person=person,
        object_name=object_name,
    )
    if not query.strip():
        return [photo_to_view(photo) for photo in photos]

    query_vector = embed_text(query)
    scored: list[tuple[float, Photo]] = []
    lowered = query.lower()

    for photo in photos:
        vector = unpack_vector(photo.embedding)
        semantic_score = cosine_similarity(query_vector, vector) if vector is not None else 0.0
        text = f"{photo.caption} {photo.objects} {photo.people} {photo.date or ''} {photo.location or ''}".lower()
        keyword_bonus = 0.08 if lowered in text else 0.0
        scored.append((semantic_score + keyword_bonus, photo))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [photo_to_view(photo, score=score) for score, photo in scored[:limit]]
