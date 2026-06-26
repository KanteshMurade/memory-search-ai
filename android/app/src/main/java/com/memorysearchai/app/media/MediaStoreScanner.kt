package com.memorysearchai.app.media

import android.content.ContentUris
import android.content.Context
import android.provider.MediaStore
import com.memorysearchai.app.data.PhotoEntity

class MediaStoreScanner(private val context: Context) {
    fun scanImages(): List<PhotoEntity> {
        val collection = MediaStore.Images.Media.EXTERNAL_CONTENT_URI
        val projection = arrayOf(
            MediaStore.Images.Media._ID,
            MediaStore.Images.Media.DISPLAY_NAME,
            MediaStore.Images.Media.DATE_TAKEN,
            MediaStore.Images.Media.DATE_ADDED,
            MediaStore.Images.Media.WIDTH,
            MediaStore.Images.Media.HEIGHT,
            MediaStore.Images.Media.SIZE
        )

        val photos = mutableListOf<PhotoEntity>()
        context.contentResolver.query(
            collection,
            projection,
            null,
            null,
            "${MediaStore.Images.Media.DATE_ADDED} DESC"
        )?.use { cursor ->
            val idColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media._ID)
            val nameColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DISPLAY_NAME)
            val dateTakenColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATE_TAKEN)
            val dateAddedColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATE_ADDED)
            val widthColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.WIDTH)
            val heightColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.HEIGHT)
            val sizeColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.SIZE)

            while (cursor.moveToNext()) {
                val id = cursor.getLong(idColumn)
                val uri = ContentUris.withAppendedId(collection, id).toString()
                val dateAddedMillis = cursor.getLong(dateAddedColumn) * 1000
                photos += PhotoEntity(
                    uri = uri,
                    displayName = cursor.getString(nameColumn) ?: "Photo $id",
                    dateTakenMillis = cursor.getLongOrNull(dateTakenColumn),
                    dateAddedMillis = dateAddedMillis,
                    width = cursor.getIntOrNull(widthColumn),
                    height = cursor.getIntOrNull(heightColumn),
                    sizeBytes = cursor.getLongOrNull(sizeColumn),
                    latitude = null,
                    longitude = null,
                    city = null,
                    country = null,
                    cameraModel = null,
                    caption = "",
                    objects = "",
                    people = "",
                    ocrText = "",
                    emotion = null,
                    embedding = null,
                    isFavorite = false,
                    albumIds = "",
                    indexedAtMillis = 0
                )
            }
        }
        return photos
    }
}

private fun android.database.Cursor.getLongOrNull(index: Int): Long? =
    if (isNull(index)) null else getLong(index)

private fun android.database.Cursor.getIntOrNull(index: Int): Int? =
    if (isNull(index)) null else getInt(index)
