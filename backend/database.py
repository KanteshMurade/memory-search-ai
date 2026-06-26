from __future__ import annotations

from datetime import datetime
from typing import Iterable

import numpy as np
from sqlalchemy import DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

from backend.config import DATABASE_URL, ensure_directories


ensure_directories()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[str] = mapped_column(Text, default="")
    objects: Mapped[str] = mapped_column(Text, default="")
    people: Mapped[str] = mapped_column(Text, default="")
    date: Mapped[str | None] = mapped_column(String(80), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    indexed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    faces: Mapped[list["FaceEncoding"]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
    )


class FaceEncoding(Base):
    __tablename__ = "face_encodings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    encoding: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    distance_threshold: Mapped[float] = mapped_column(Float, default=0.58)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    person: Mapped[Person] = relationship(back_populates="faces")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def pack_vector(vector: Iterable[float] | np.ndarray | None) -> bytes | None:
    if vector is None:
        return None
    return np.asarray(vector, dtype=np.float32).tobytes()


def unpack_vector(blob: bytes | None) -> np.ndarray | None:
    if not blob:
        return None
    return np.frombuffer(blob, dtype=np.float32)


def list_to_text(values: Iterable[str] | None) -> str:
    return "\n".join(sorted({value.strip() for value in values or [] if value and value.strip()}))


def text_to_list(value: str | None) -> list[str]:
    return [item for item in (value or "").splitlines() if item]


def photo_to_view(photo: Photo, score: float | None = None) -> dict:
    return {
        "id": photo.id,
        "filename": photo.filename,
        "photo": photo.filename,
        "caption": photo.caption,
        "objects": text_to_list(photo.objects),
        "people": text_to_list(photo.people),
        "date": photo.date,
        "location": photo.location,
        "score": score,
    }


def find_photo(db: Session, filename: str) -> Photo | None:
    return db.query(Photo).filter(Photo.filename == filename).first()
