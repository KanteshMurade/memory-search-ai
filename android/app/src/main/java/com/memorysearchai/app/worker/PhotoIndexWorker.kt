package com.memorysearchai.app.worker

import android.content.Context
import androidx.room.Room
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.memorysearchai.app.ai.ImageIndexer
import com.memorysearchai.app.data.AppDatabase
import com.memorysearchai.app.media.MediaStoreScanner

class PhotoIndexWorker(
    appContext: Context,
    params: WorkerParameters
) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        val database = Room.databaseBuilder(
            applicationContext,
            AppDatabase::class.java,
            "memory-search-ai.db"
        ).build()

        return try {
            val scanner = MediaStoreScanner(applicationContext)
            val indexer = ImageIndexer()
            val photos = scanner.scanImages().map(indexer::index)
            database.photoDao().upsertAll(photos)
            Result.success()
        } catch (_: Exception) {
            Result.retry()
        } finally {
            database.close()
        }
    }
}
