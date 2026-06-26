# Memory Search AI Android

Native Android version of Memory Search AI.

This app is designed to behave like a normal phone gallery, but with prompt-based memory search.

## Current Scaffold

Implemented foundation:

- Kotlin Android app
- Jetpack Compose UI
- MediaStore scanner for phone photos
- Runtime media permissions
- Room database
- WorkManager photo indexing job
- Local photo grid
- Home, Gallery, People, Albums, Memories, Favorites, Upload, Profile, Settings sections
- Recent searches
- Prompt search pipeline
- Placeholder AI indexing layer with clear swap points for real on-device models

## Intended Product Flow

```text
Splash
  -> Login or Skip
  -> Home
  -> Search Photos
  -> Results
  -> Photo Details
```

Main sections:

```text
Home
Gallery
People
Albums
Memories
Favorites
Upload
Profile
Settings
```

## How Photo Access Works

The app uses Android `MediaStore` to read images from the phone gallery after the user grants permission.

Permissions included:

- Android 13+: `READ_MEDIA_IMAGES`, `READ_MEDIA_VIDEO`
- Android 14+: `READ_MEDIA_VISUAL_USER_SELECTED`
- Older Android: `READ_EXTERNAL_STORAGE`
- Camera permission for capture flow

## AI Roadmap

The app currently has placeholder indexing so the gallery/search flow can be built and tested first.

Replace the placeholder classes with mobile models:

- `ai/ImageIndexer.kt`
  - caption model
  - object detector
  - OCR
  - face recognition
  - emotion detection
- `ai/EmbeddingEngine.kt`
  - CLIP / MobileCLIP / sentence embedding TFLite or ONNX model
- `ai/SearchEngine.kt`
  - cosine similarity vector search
  - filters
  - similar photo search

## Build

Open the `android/` folder in Android Studio.

Then run:

```bash
./gradlew assembleDebug
```

This environment does not include the Android SDK or Gradle wrapper, so build verification must happen in Android Studio.
