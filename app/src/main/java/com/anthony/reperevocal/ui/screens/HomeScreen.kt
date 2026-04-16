
package com.anthony.reperevocal.ui.screens

import android.app.Activity
import android.speech.RecognizerIntent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountTree
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.Emergency
import androidx.compose.material.icons.filled.KeyboardVoice
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.RemoveRedEye
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.anthony.reperevocal.models.FeatureCard
import com.anthony.reperevocal.services.SpeechInputManager
import com.anthony.reperevocal.ui.state.AppViewModel

@Composable
fun HomeScreen(
    appViewModel: AppViewModel,
    openGps: () -> Unit,
    openVision: () -> Unit,
    openDocuments: () -> Unit,
    openObjects: () -> Unit,
    openSos: () -> Unit,
    openSettings: () -> Unit,
    openArchitecture: () -> Unit = {}
) {
    val context = LocalContext.current
    val activity = context as Activity
    val uiState by appViewModel.uiState.collectAsState()
    val speechManager = SpeechInputManager(activity)

    fun runVoiceCommand(spoken: String) {
        when {
            spoken.contains("gps") || spoken.contains("où suis") || spoken.contains("position") -> {
                appViewModel.speak("Ouverture du GPS", vibrate = true)
                openGps()
            }
            spoken.contains("vision") || spoken.contains("camera") || spoken.contains("caméra") || spoken.contains("voir") -> {
                appViewModel.speak("Ouverture du mode vision", vibrate = true)
                openVision()
            }
            spoken.contains("document") || spoken.contains("lire") || spoken.contains("courrier") || spoken.contains("facture") -> {
                appViewModel.speak("Ouverture du lecteur de documents", vibrate = true)
                openDocuments()
            }
            spoken.contains("objet") || spoken.contains("clé") || spoken.contains("cle") || spoken.contains("lunette") -> {
                appViewModel.speak("Ouverture de la recherche d'objets", vibrate = true)
                openObjects()
            }
            spoken.contains("sos") || spoken.contains("urgence") || spoken.contains("aide") -> {
                appViewModel.speak("Ouverture du mode SOS", vibrate = true)
                openSos()
            }
            spoken.contains("réglage") || spoken.contains("reglage") || spoken.contains("param") || spoken.contains("option") -> {
                appViewModel.speak("Ouverture des réglages", vibrate = true)
                openSettings()
            }
            spoken.contains("architecture") || spoken.contains("modules") || spoken.contains("source") -> {
                appViewModel.speak("Ouverture de l'architecture", vibrate = true)
                openArchitecture()
            }
            spoken.contains("bonjour") || spoken.contains("salut") -> {
                appViewModel.speak("Bonjour Anthony. Je suis prête.", vibrate = true)
            }
            spoken.isNotBlank() -> appViewModel.speak("Commande non reconnue : $spoken")
            else -> appViewModel.speak("Aucune commande reconnue")
        }
    }

    val voiceLauncher = rememberLauncherForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        val spoken = result.data
            ?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            ?.firstOrNull()
            ?.lowercase()
            .orEmpty()
        runVoiceCommand(spoken)
    }

    LaunchedEffect(Unit) {
        appViewModel.speak(
            "Bienvenue sur Repère Vocal. Appuyez sur le bouton micro puis dites GPS, vision, documents, objets, SOS, réglages ou architecture.",
            vibrate = true
        )
    }

    val features = listOf(
        FeatureCard("GPS piéton", "Où suis-je et guidage simple", Icons.Default.LocationOn),
        FeatureCard("Vision IA", "Description assistée de l'environnement", Icons.Default.RemoveRedEye),
        FeatureCard("Documents", "Choisir une image et lire le texte", Icons.Default.Description),
        FeatureCard("Recherche d'objets", "Mode mémoire et guidage vocal", Icons.Default.Search),
        FeatureCard("SOS", "Appel et SMS d'urgence", Icons.Default.Emergency),
        FeatureCard("Réglages", "Voix, vibration et contact", Icons.Default.Settings),
        FeatureCard("Architecture", "Tous les nouveaux modules et stacks intégrés", Icons.Default.AccountTree)
    )

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Commande vocale", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                    Text(
                        "Dis par exemple : GPS, Vision, Lire document, Cherche mes clés, SOS, Réglages ou Architecture.",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Button(
                        onClick = {
                            if (speechManager.isAvailable()) {
                                appViewModel.speak("Je vous écoute")
                                speechManager.startSpeechInput(voiceLauncher)
                            } else {
                                appViewModel.speak("La reconnaissance vocale n'est pas disponible sur ce téléphone")
                            }
                        }
                    ) {
                        Icon(Icons.Default.KeyboardVoice, contentDescription = null)
                        Text("  Lancer la commande vocale")
                    }
                    if (uiState.lastSpokenText.isNotBlank()) {
                        Text(
                            "Dernier retour vocal : ${uiState.lastSpokenText}",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }
        }

        items(features) { item ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                onClick = {
                    when (item.title) {
                        "GPS piéton" -> openGps()
                        "Vision IA" -> openVision()
                        "Documents" -> openDocuments()
                        "Recherche d'objets" -> openObjects()
                        "SOS" -> openSos()
                        "Architecture" -> openArchitecture()
                        else -> openSettings()
                    }
                }
            ) {
                androidx.compose.foundation.layout.Row(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Icon(item.icon, contentDescription = null)
                    Column {
                        Text(item.title, fontWeight = FontWeight.Bold)
                        Text(item.description)
                    }
                }
            }
        }
    }
}
