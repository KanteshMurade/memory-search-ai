package com.memorysearchai.app

import android.Manifest
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.LaunchedEffect
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import com.memorysearchai.app.ui.MemorySearchApp
import com.memorysearchai.app.worker.PhotoIndexWorker

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val database = (application as MemorySearchApplication).database

        setContent {
            val permissionLauncher = rememberLauncherForActivityResult(
                ActivityResultContracts.RequestMultiplePermissions()
            ) {
                enqueuePhotoIndexing()
            }

            LaunchedEffect(Unit) {
                permissionLauncher.launch(requiredMediaPermissions())
            }

            MemorySearchApp(
                database = database,
                onIndexNow = ::enqueuePhotoIndexing
            )
        }
    }

    private fun requiredMediaPermissions(): Array<String> {
        return when {
            Build.VERSION.SDK_INT >= 34 -> arrayOf(
                Manifest.permission.READ_MEDIA_IMAGES,
                Manifest.permission.READ_MEDIA_VIDEO,
                Manifest.permission.READ_MEDIA_VISUAL_USER_SELECTED
            )
            Build.VERSION.SDK_INT >= 33 -> arrayOf(
                Manifest.permission.READ_MEDIA_IMAGES,
                Manifest.permission.READ_MEDIA_VIDEO
            )
            else -> arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE)
        }
    }

    private fun enqueuePhotoIndexing() {
        val request = OneTimeWorkRequestBuilder<PhotoIndexWorker>().build()
        WorkManager.getInstance(this).enqueueUniqueWork(
            "photo-indexing",
            ExistingWorkPolicy.REPLACE,
            request
        )
    }
}
