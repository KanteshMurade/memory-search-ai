package com.memorysearchai.app.ai

import com.memorysearchai.app.data.PhotoEntity

data class SearchFilters(
    val person: String = "",
    val location: String = "",
    val objectName: String = "",
    val year: String = "",
    val favoriteOnly: Boolean = false,
    val albumId: String = ""
)

data class PhotoSearchResult(
    val photo: PhotoEntity,
    val score: Float
)

class SearchEngine(
    private val embeddingEngine: EmbeddingEngine = EmbeddingEngine()
) {
    fun search(
        query: String,
        photos: List<PhotoEntity>,
        filters: SearchFilters = SearchFilters()
    ): List<PhotoSearchResult> {
        val filtered = photos.filter { photo ->
            (!filters.favoriteOnly || photo.isFavorite) &&
                filters.person.matchesTokenList(photo.people) &&
                filters.objectName.matchesTokenList(photo.objects) &&
                filters.location.matchesText("${photo.city.orEmpty()} ${photo.country.orEmpty()}") &&
                filters.albumId.matchesTokenList(photo.albumIds)
        }

        if (query.isBlank()) {
            return filtered.map { PhotoSearchResult(it, 1f) }
        }

        val queryEmbedding = embeddingEngine.embedText(query)
        return filtered.map { photo ->
            val semantic = embeddingEngine.cosineSimilarity(queryEmbedding, photo.embedding)
            val text = listOf(
                photo.displayName,
                photo.caption,
                photo.objects,
                photo.people,
                photo.ocrText,
                photo.city.orEmpty(),
                photo.country.orEmpty()
            ).joinToString(" ").lowercase()
            val keywordBonus = if (text.contains(query.lowercase())) 0.15f else 0f
            PhotoSearchResult(photo, semantic + keywordBonus)
        }.sortedByDescending { it.score }
    }
}

private fun String.matchesText(value: String): Boolean =
    isBlank() || value.lowercase().contains(lowercase())

private fun String.matchesTokenList(value: String): Boolean =
    isBlank() || value.split("|").any { it.equals(this, ignoreCase = true) }
