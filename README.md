# Memory Search AI

<<<<<<< HEAD
AI-powered photo search engine.

## Features

- AI image captioning
- Object detection (YOLOv8)
- Face recognition
- Semantic photo search
- FastAPI web interface
- Photo thumbnails

## Tech Stack

- Python
- FastAPI
- Transformers
- YOLOv8
- Face Recognition
- Jinja2

## Future Features

- Natural language memory search
- Android app
- Voice search
- Automatic indexing
- Location and date search
=======
AI-powered photo gallery for searching photos the way people remember them.

## What It Does

- Automatically indexes images from `photos/`
- Generates captions with BLIP
- Detects objects with YOLOv8
- Recognizes known people from enrolled face samples
- Stores photos, metadata, face encodings, and embeddings in SQLite
- Searches semantically with sentence-transformers and cosine similarity
- Filters search results by date, location, person, and detected object
- Provides a FastAPI/Jinja2 gallery with upload, search, detail, and people pages

## Project Structure

```text
backend/
    app.py
    config.py
    database.py
ai/
    caption.py
    detector.py
    embeddings.py
    faces.py
    indexing.py
    search.py
models/
data/
photos/
templates/
static/
    css/
    js/
    images/
```

## Run

```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload
```

Open `http://127.0.0.1:8000`.

The app indexes new images in `photos/` on startup. You can also upload photos from the gallery page or trigger indexing from the top-right refresh button.

## Android App

A native Android scaffold now lives in:

```text
android/
```

Open that folder in Android Studio to build the phone app. It uses Kotlin, Jetpack Compose, MediaStore, Room, and WorkManager. The Android app is the correct path for the final product because it can read phone gallery photos directly instead of asking users to upload photos into a website.

## Face Recognition

1. Open `/people`.
2. Add a person name.
3. Upload a clear face photo for that person.
4. The app stores the face encoding in SQLite and re-indexes existing photos.

## Storage

The application no longer uses JSON as the data store. SQLite lives at:

```text
data/memory_search.db
```

Embeddings and face encodings are stored as compact `float32` binary blobs.
>>>>>>> 1a0f748 (Added AI gallery UI, upload, reindex and search improvements)
