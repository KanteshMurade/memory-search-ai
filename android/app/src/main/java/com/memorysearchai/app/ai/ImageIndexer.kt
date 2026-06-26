package com.memorysearchai.app.ai

import com.memorysearchai.app.data.PhotoEntity

class ImageIndexer(
    private val embeddingEngine: EmbeddingEngine = EmbeddingEngine()
) {
    fun index(photo: PhotoEntity): PhotoEntity {
        val generatedCaption = buildCaption(photo)
        val detectedObjects = detectObjectsFromName(photo.displayName)
        val searchableText = listOf(
            generatedCaption,
            detectedObjects.joinToString(" "),
            photo.city.orEmpty(),
            photo.country.orEmpty(),
            photo.cameraModel.orEmpty()
        ).joinToString(" ")

        return photo.copy(
            caption = generatedCaption,
            objects = detectedObjects.joinToString("|"),
            embedding = embeddingEngine.embedText(searchableText),
            indexedAtMillis = System.currentTimeMillis()
        )
    }

    private fun buildCaption(photo: PhotoEntity): String {
        val cleanName = photo.displayName
            .substringBeforeLast(".")
            .replace(Regex("[_\\-]+"), " ")
        return "Photo showing $cleanName"
    }

    private fun detectObjectsFromName(name: String): List<String> {
        val knownObjects = listOf(
            "car", "dog", "cat", "laptop", "chair", "bottle", "food",
            "mountain", "beach", "building", "tree", "bike", "camera", "table"
        )
        val lower = name.lowercase()
        return knownObjects.filter { lower.contains(it) }
    }
}
