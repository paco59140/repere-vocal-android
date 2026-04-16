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
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.anthony.reperevocal.ui.state.AppViewModel

@Composable
fun ObjectsScreen(
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
    var objectName by rememberSaveable { mutableStateOf("clés") }

    ScreenScaffold(
        title = "Recherche d'objets",
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
            Text("Base V1 : mode mémoire vocale. La détection caméra pourra être branchée ensuite.")
            OutlinedTextField(
                value = objectName,
                onValueChange = { objectName = it },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Objet à chercher") }
            )
            Button(
                onClick = {
                    appViewModel.speak("Je cherche $objectName. Dernière position mémorisée inconnue pour le moment.", vibrate = true)
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Chercher l'objet")
            }
        }
    }
}
