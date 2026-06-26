from __future__ import annotations

from pathlib import Path

import numpy as np
from sqlalchemy.orm import Session

from backend.database import FaceEncoding, Person, pack_vector, unpack_vector


def create_face_encoding(image_path: str | Path) -> np.ndarray | None:
    try:
        import face_recognition

        image = face_recognition.load_image_file(str(image_path))
        encodings = face_recognition.face_encodings(image)
        return np.asarray(encodings[0], dtype=np.float32) if encodings else None
    except Exception:
        return None


def recognize_people(db: Session, image_path: str | Path) -> list[str]:
    try:
        import face_recognition

        known_faces = db.query(FaceEncoding).join(Person).all()
        if not known_faces:
            return []

        image = face_recognition.load_image_file(str(image_path))
        locations = face_recognition.face_locations(image)
        unknown_encodings = face_recognition.face_encodings(image, locations)
        people: set[str] = set()

        for unknown in unknown_encodings:
            best_name = None
            best_distance = 1.0
            for known in known_faces:
                known_vector = unpack_vector(known.encoding)
                if known_vector is None:
                    continue
                distance = float(np.linalg.norm(known_vector - unknown))
                if distance < best_distance and distance <= known.distance_threshold:
                    best_distance = distance
                    best_name = known.person.name
            if best_name:
                people.add(best_name)

        return sorted(people)
    except Exception:
        return []


def add_face_encoding(db: Session, person: Person, image_path: str | Path) -> bool:
    encoding = create_face_encoding(image_path)
    if encoding is None:
        return False
    db.add(
        FaceEncoding(
            person_id=person.id,
            image_path=str(image_path),
            encoding=pack_vector(encoding),
        )
    )
    db.commit()
    return True
