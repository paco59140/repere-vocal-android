package com.anthony.reperevocal.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.anthony.reperevocal.services.EmergencyActions
import com.anthony.reperevocal.ui.state.AppViewModel

@Composable
fun SosScreen(
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
    val context = LocalContext.current
    val uiState by appViewModel.uiState.collectAsState()
    var phone by rememberSaveable { mutableStateOf(uiState.settings.trustedContact) }

    ScreenScaffold(
        title = "SOS",
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
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text("Cette version ouvre le composeur d'appel et de SMS.")
            OutlinedTextField(
                value = phone,
                onValueChange = { phone = it },
                label = { Text("Contact de confiance") },
                modifier = Modifier.fillMaxWidth()
            )
            Button(
                onClick = { EmergencyActions.callTrustedContact(context, phone) },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Appeler")
            }
            Button(
                onClick = { EmergencyActions.sendEmergencySms(context, phone, "SOS envoyé depuis Repère Vocal") },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Envoyer SMS")
            }
            Button(
                onClick = {
                    appViewModel.updateTrustedContact(phone)
                    appViewModel.persistCurrentSettings()
                    appViewModel.speak("Contact SOS enregistré définitivement", vibrate = true)
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Enregistrer")
            }
        }
    }
}
