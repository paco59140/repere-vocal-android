package com.anthony.reperevocal.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.anthony.reperevocal.ui.state.AppViewModel

@Composable
fun SettingsScreen(
    appViewModel: AppViewModel,
    onBack: () -> Unit,
    onGoHome: () -> Unit = {},
    openGps: () -> Unit = {},
    openVision: () -> Unit = {},
    openDocuments: () -> Unit = {},
    openObjects: () -> Unit = {},
    openSos: () -> Unit = {},
    openSettings: () -> Unit = {}
) {
    val uiState by appViewModel.uiState.collectAsState()
    var phone by rememberSaveable { mutableStateOf("0612345678") }
    var speechEnabled by rememberSaveable { mutableStateOf(true) }
    var vibrationEnabled by rememberSaveable { mutableStateOf(true) }

    LaunchedEffect(uiState.settingsLoaded, uiState.settings) {
        if (uiState.settingsLoaded) {
            phone = uiState.settings.trustedContact
            speechEnabled = uiState.settings.speechEnabled
            vibrationEnabled = uiState.settings.vibrationEnabled
        }
    }

    ScreenScaffold(
        title = "Réglages",
        appViewModel = appViewModel,
        onBack = onBack,
        onGoHome = onGoHome,
        openGps = openGps,
        openVision = openVision,
        openDocuments = openDocuments,
        openObjects = openObjects,
        openSos = openSos,
        openSettings = openSettings
    ) { padding ->
        Column(
            modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text("Les réglages sont maintenant sauvegardés même après fermeture de l'application.")
            Row(
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Voix activée")
                Switch(checked = speechEnabled, onCheckedChange = { speechEnabled = it })
            }
            Row(
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Vibration activée")
                Switch(checked = vibrationEnabled, onCheckedChange = { vibrationEnabled = it })
            }
            OutlinedTextField(
                value = phone,
                onValueChange = { phone = it },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Contact de confiance") }
            )
            Button(
                onClick = {
                    appViewModel.updateSettings(
                        speechEnabled = speechEnabled,
                        vibrationEnabled = vibrationEnabled,
                        trustedContact = phone
                    )
                    appViewModel.speak("Réglages enregistrés de façon permanente", vibrate = true)
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Enregistrer")
            }
        }
    }
}
