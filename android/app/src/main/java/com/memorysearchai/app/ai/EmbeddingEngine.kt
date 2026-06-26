package com.memorysearchai.app.ai

import kotlin.math.sqrt

class EmbeddingEngine {
    fun embedText(text: String, dimension: Int = 384): FloatArray {
        val vector = FloatArray(dimension)
        text.lowercase()
            .split(Regex("\\s+"))
            .filter { it.isNotBlank() }
            .forEach { token ->
                val index = token.fold(0) { acc, char -> (acc * 31 + char.code) and Int.MAX_VALUE } % dimension
                vector[index] += 1f
            }
        return normalize(vector)
    }

    fun cosineSimilarity(left: FloatArray?, right: FloatArray?): Float {
        if (left == null || right == null || left.isEmpty() || right.isEmpty()) return 0f
        val size = minOf(left.size, right.size)
        var dot = 0f
        var leftNorm = 0f
        var rightNorm = 0f
        for (index in 0 until size) {
            dot += left[index] * right[index]
            leftNorm += left[index] * left[index]
            rightNorm += right[index] * right[index]
        }
        if (leftNorm == 0f || rightNorm == 0f) return 0f
        return dot / (sqrt(leftNorm) * sqrt(rightNorm))
    }

    private fun normalize(vector: FloatArray): FloatArray {
        val norm = sqrt(vector.sumOf { (it * it).toDouble() }).toFloat()
        if (norm == 0f) return vector
        return FloatArray(vector.size) { vector[it] / norm }
    }
}
