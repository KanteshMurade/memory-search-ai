package com.memorysearchai.app.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Album
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.GridView
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Timeline
import androidx.compose.material.icons.filled.Upload
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.memorysearchai.app.ai.SearchEngine
import com.memorysearchai.app.data.AppDatabase
import com.memorysearchai.app.data.PhotoEntity
import com.memorysearchai.app.data.RecentSearchEntity
import kotlinx.coroutines.launch

private enum class Section(
    val label: String,
    val icon: ImageVector
) {
    Home("Home", Icons.Default.Home),
    Gallery("Gallery", Icons.Default.GridView),
    People("People", Icons.Default.Person),
    Albums("Albums", Icons.Default.Album),
    Memories("Memories", Icons.Default.Timeline),
    Favorites("Favorites", Icons.Default.Favorite),
    Upload("Upload", Icons.Default.Upload),
    Profile("Profile", Icons.Default.CameraAlt),
    Settings("Settings", Icons.Default.Settings)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MemorySearchApp(
    database: AppDatabase,
    onIndexNow: () -> Unit
) {
    var selectedSection by remember { mutableStateOf(Section.Home) }
    var query by remember { mutableStateOf("") }
    val photos by database.photoDao().observeRecentPhotos().collectAsState(initial = emptyList())
    val favorites by database.photoDao().observeFavorites().collectAsState(initial = emptyList())
    val people by database.personDao().observePeople().collectAsState(initial = emptyList())
    val albums by database.albumDao().observeAlbums().collectAsState(initial = emptyList())
    val recentSearches by database.searchDao().observeRecentSearches().collectAsState(initial = emptyList())
    val scope = rememberCoroutineScope()
    val searchEngine = remember { SearchEngine() }
    val searchResults = remember(query, photos) {
        searchEngine.search(query, photos).map { it.photo }
    }

    LaunchedEffect(Unit) {
        onIndexNow()
    }

    MaterialTheme(colorScheme = darkColorScheme()) {
        Surface(modifier = Modifier.fillMaxSize()) {
            Scaffold(
                topBar = {
                    TopAppBar(
                        title = { Text("Memory Search AI", fontWeight = FontWeight.Bold) },
                        actions = {
                            Button(onClick = onIndexNow) {
                                Text("Scan")
                            }
                        }
                    )
                },
                bottomBar = {
                    NavigationBar {
                        Section.entries.take(5).forEach { section ->
                            NavigationBarItem(
                                selected = selectedSection == section,
                                onClick = { selectedSection = section },
                                icon = { Icon(section.icon, contentDescription = section.label) },
                                label = { Text(section.label) }
                            )
                        }
                    }
                }
            ) { padding ->
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding)
                        .padding(16.dp)
                ) {
                    SearchBar(
                        query = query,
                        onQueryChange = { query = it },
                        onSearch = {
                            if (query.isNotBlank()) {
                                scope.launch {
                                    database.searchDao().remember(
                                        RecentSearchEntity(query, System.currentTimeMillis())
                                    )
                                }
                            }
                            selectedSection = Section.Gallery
                        }
                    )
                    Spacer(Modifier.height(14.dp))
                    when (selectedSection) {
                        Section.Home -> HomeScreen(
                            photos = photos,
                            recentSearches = recentSearches.map { it.query },
                            suggestions = listOf(
                                "Me with Rahul",
                                "Sunset beach",
                                "Birthday party",
                                "White car",
                                "Camera on table"
                            ),
                            onSuggestionClick = {
                                query = it
                                selectedSection = Section.Gallery
                            }
                        )
                        Section.Gallery -> GalleryScreen(searchResults)
                        Section.People -> SimpleListScreen(
                            title = "People",
                            empty = "Known and unknown faces will appear here.",
                            rows = people.map { "${it.name} - ${it.photoCount} photos" }
                        )
                        Section.Albums -> SimpleListScreen(
                            title = "Albums",
                            empty = "Create albums or let AI suggest Family, College, Vacation and Birthday.",
                            rows = albums.map { it.name }
                        )
                        Section.Memories -> SimpleListScreen(
                            title = "Memories",
                            empty = "Daily highlights and on-this-day memories will appear here.",
                            rows = listOf("Today", "Yesterday", "This week", "Last month", "Last year")
                        )
                        Section.Favorites -> GalleryScreen(favorites)
                        Section.Upload -> SimpleListScreen(
                            title = "Upload",
                            empty = "Use Gallery import, Camera capture, multi-photo selection and auto-indexing here.",
                            rows = listOf("Upload from Gallery", "Take Photo", "Multi-photo Upload")
                        )
                        Section.Profile -> SimpleListScreen(
                            title = "Profile",
                            empty = "Profile, cloud sync, storage usage and backup status.",
                            rows = listOf("Storage usage", "Backup status", "Cloud sync")
                        )
                        Section.Settings -> SimpleListScreen(
                            title = "Settings",
                            empty = "AI models, privacy, theme, language, backup and notifications.",
                            rows = listOf("AI model settings", "Face recognition", "Privacy", "Theme", "Notifications")
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    onSearch: () -> Unit
) {
    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
        OutlinedTextField(
            value = query,
            onValueChange = onQueryChange,
            modifier = Modifier.weight(1f),
            placeholder = { Text("Describe a memory: sunset beach, mom cooking...") },
            leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
            singleLine = true
        )
        Button(
            onClick = onSearch,
            modifier = Modifier.align(Alignment.CenterVertically)
        ) {
            Text("Search")
        }
    }
}

@Composable
private fun HomeScreen(
    photos: List<PhotoEntity>,
    recentSearches: List<String>,
    suggestions: List<String>,
    onSuggestionClick: (String) -> Unit
) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        item {
            SectionTitle("Quick filters")
            ChipRow(listOf("Today", "This week", "Favorites", "People", "Beach", "Car"), onSuggestionClick)
        }
        item {
            SectionTitle("Search suggestions")
            ChipRow(suggestions, onSuggestionClick)
        }
        item {
            SectionTitle("Recently searched memories")
            ChipRow(recentSearches.ifEmpty { listOf("No recent searches yet") }, onSuggestionClick)
        }
        item {
            SectionTitle("Recent photos")
        }
        item {
            GalleryPreview(photos.take(12))
        }
        item {
            SectionTitle("AI recommendations")
            Text("Suggested albums, travel memories, people groups and similar photos will appear after indexing.")
        }
    }
}

@Composable
private fun GalleryScreen(photos: List<PhotoEntity>) {
    if (photos.isEmpty()) {
        EmptyState("No photos found. Grant photo access and tap Scan.")
        return
    }
    LazyVerticalGrid(
        columns = GridCells.Adaptive(130.dp),
        contentPadding = PaddingValues(bottom = 96.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(photos, key = { it.uri }) { photo ->
            PhotoTile(photo)
        }
    }
}

@Composable
private fun GalleryPreview(photos: List<PhotoEntity>) {
    if (photos.isEmpty()) {
        EmptyState("Your phone gallery will appear here.")
        return
    }
    LazyVerticalGrid(
        columns = GridCells.Adaptive(110.dp),
        modifier = Modifier.height(360.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(photos, key = { it.uri }) { photo -> PhotoTile(photo) }
    }
}

@Composable
private fun PhotoTile(photo: PhotoEntity, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .aspectRatio(1f),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Box {
            AsyncImage(
                model = photo.uri,
                contentDescription = photo.caption.ifBlank { photo.displayName },
                modifier = Modifier
                    .fillMaxSize()
                    .clip(RoundedCornerShape(12.dp)),
                contentScale = ContentScale.Crop
            )
        }
    }
}

@Composable
private fun SimpleListScreen(title: String, empty: String, rows: List<String>) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        item { SectionTitle(title) }
        if (rows.isEmpty()) {
            item { EmptyState(empty) }
        } else {
            items(rows) { row ->
                Card(Modifier.fillMaxWidth()) {
                    Text(row, Modifier.padding(16.dp))
                }
            }
        }
    }
}

@Composable
private fun SectionTitle(text: String) {
    Text(text, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
}

@Composable
private fun ChipRow(values: List<String>, onClick: (String) -> Unit) {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
        values.take(4).forEach { value ->
            Card(
                modifier = Modifier.clickable { onClick(value) },
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer)
            ) {
                Text(value, Modifier.padding(horizontal = 12.dp, vertical = 8.dp))
            }
        }
    }
}

@Composable
private fun EmptyState(message: String) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(180.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(message)
    }
}
