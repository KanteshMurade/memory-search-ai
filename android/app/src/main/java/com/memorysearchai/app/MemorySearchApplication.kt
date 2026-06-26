package com.memorysearchai.app

import android.app.Application
import androidx.room.Room
import com.memorysearchai.app.data.AppDatabase

class MemorySearchApplication : Application() {
    val database: AppDatabase by lazy {
        Room.databaseBuilder(
            this,
            AppDatabase::class.java,
            "memory-search-ai.db"
        ).build()
    }
}
