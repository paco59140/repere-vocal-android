package com.anthony.reperevocal.ui.screens

import android.app.Activity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.KeyboardVoice
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExtendedFloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.anthony.reperevocal.models.FeatureCard
import com.anthony.reperevocal.services.SpeechInputManager
import com.anthony.reperevocal.services.VoiceAction
import com.anthony.reperevocal.services.VoiceCommandProcessor
import com.anthony.reperevocal.ui.state.AppViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScreenScaffold(
    title: String,
    appViewModel: AppViewModel,
    onBack: () -> Unit,
    onGoHome: () -> Unit = {},
    openGps: () -> Unit = {},
    openVision: () -> Unit = {},
    openDocuments: () -> Unit = {},
    openObjects: () -> Unit = {},
    openSos: () -> Unit = {},
    openSettings: () -> Unit = {},
    content: @Composable (PaddingValues) -> Unit
) {
    val context = LocalContext.current
    val activity = context as Activity
    val speechManager = SpeechInputManager(activity)

    val speechLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val spoken = result.data?.getStringArrayListExtra(android.speech.RecognizerIntent.EXTRA_RESULTS)
            ?.firstOrNull()
            ?.lowercase().orEmpty()

        val parsed = VoiceCommandProcessor.process(spoken)
        when (parsed.action) {
            VoiceAction.HOME -> onGoHome()
            VoiceAction.GPS -> openGps()
            VoiceAction.VISION -> openVision()
            VoiceAction.DOCUMENTS -> openDocuments()
            VoiceAction.OBJECTS -> openObjects()
            VoiceAction.SOS -> openSos()
            VoiceAction.SETTINGS -> openSettings()
            VoiceAction.BACK -> onBack()
            VoiceAction.REPEAT -> appViewModel.repeatLastMessage()
            VoiceAction.UNKNOWN -> Unit
        }
        appViewModel.speak(parsed.feedback, vibrate = parsed.action != VoiceAction.UNKNOWN)
    }

    DisposableEffect(title) {
        appViewModel.speak("Écran $title")
        onDispose { }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(title) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Retour")
                    }
                }
            )
        },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                onClick = {
                    if (speechManager.isAvailable()) {
                        appViewModel.speak("Dites une commande")
                        speechManager.startSpeechInput(speechLauncher)
                    } else {
                        appViewModel.speak("Reconnaissance vocale indisponible")
                    }
                },
                icon = { Icon(Icons.Default.KeyboardVoice, contentDescription = null) },
                text = { Text("Commande vocale") }
            )
        }
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize()) {
            content(padding)
        }
    }
}

@Composable
fun FeatureList(cards: List<FeatureCard>) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(12.dp),
        contentPadding = PaddingValues(16.dp)
    ) {
        items(cards) { card ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(card.icon, contentDescription = null)
                    Column {
                        Text(card.title, fontWeight = FontWeight.Bold)
                        Text(card.description)
                    }
                }
            }
        }
    }
}
