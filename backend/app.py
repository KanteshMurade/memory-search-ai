from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ai.faces import add_face_encoding
from ai.indexing import index_all_photos, index_photo, save_uploaded_photo
from ai.search import semantic_search
from backend.config import KNOWN_FACES_DIR, PHOTOS_DIR, STATIC_DIR, TEMPLATES_DIR, ensure_directories
from backend.database import Person, Photo, get_db, init_db, photo_to_view, text_to_list


ensure_directories()
init_db()

app = FastAPI(title="Memory Search AI")
app.mount("/photos", StaticFiles(directory=PHOTOS_DIR), name="photos")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def gallery_context(db: Session, results: list[dict], query: str = "", filters: dict | None = None) -> dict:
    photos = db.query(Photo).all()
    dates = sorted({photo.date for photo in photos if photo.date}, reverse=True)
    locations = sorted({photo.location for photo in photos if photo.location})
    people = sorted({name for photo in photos for name in text_to_list(photo.people)})
    objects = sorted({name for photo in photos for name in text_to_list(photo.objects)})
    return {
        "results": results,
        "query": query,
        "indexed_count": len(results),
        "filters": filters or {},
        "filter_options": {
            "dates": dates,
            "locations": locations,
            "people": people,
            "objects": objects,
        },
    }


@app.on_event("startup")
def startup_index() -> None:
    db = next(get_db())
    try:
        index_all_photos(db)
    finally:
        db.close()


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    photos = db.query(Photo).order_by(Photo.indexed_at.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=gallery_context(db, [photo_to_view(photo) for photo in photos]),
    )


@app.get("/search")
async def search(
    request: Request,
    query: str = "",
    date: str = "",
    location: str = "",
    person: str = "",
    object_name: str = "",
    db: Session = Depends(get_db),
):
    filters = {
        "date": date,
        "location": location,
        "person": person,
        "object_name": object_name,
    }
    results = semantic_search(
        db,
        query,
        date=date,
        location=location,
        person=person,
        object_name=object_name,
    )
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=gallery_context(db, results, query=query, filters=filters),
    )


@app.get("/photo/{photo_id}")
async def photo_detail(photo_id: int, request: Request, score: float | None = None, db: Session = Depends(get_db)):
    photo = db.get(Photo, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return templates.TemplateResponse(
        request=request,
        name="detail.html",
        context={"item": photo_to_view(photo, score=score)},
    )


@app.post("/upload")
async def upload_photo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    destination = save_uploaded_photo(file)
    index_photo(db, destination, force=True)
    return RedirectResponse("/", status_code=303)


@app.post("/index")
async def rebuild_index(force: bool = Form(False), db: Session = Depends(get_db)):
    index_all_photos(db, force=force)
    return RedirectResponse("/", status_code=303)


@app.get("/people")
async def people_page(request: Request, db: Session = Depends(get_db)):
    people = db.query(Person).order_by(Person.name).all()
    return templates.TemplateResponse(
        request=request,
        name="people.html",
        context={"people": people},
    )


@app.post("/people")
async def add_person(name: str = Form(...), db: Session = Depends(get_db)):
    clean_name = name.strip()
    if clean_name:
        person = db.query(Person).filter(Person.name == clean_name).first()
        if not person:
            db.add(Person(name=clean_name))
            db.commit()
    return RedirectResponse("/people", status_code=303)


@app.post("/people/{person_id}/faces")
async def upload_person_face(person_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    person_dir = KNOWN_FACES_DIR / str(person.id)
    destination = save_uploaded_photo(file, person_dir)
    added = add_face_encoding(db, person, destination)
    if not added:
        Path(destination).unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="No face was detected in that upload")

    for photo in db.query(Photo).all():
        index_photo(db, photo.path, force=True)
    return RedirectResponse("/people", status_code=303)
