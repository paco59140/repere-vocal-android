
package com.anthony.reperevocal.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.anthony.reperevocal.modules.ModuleRegistry
import com.anthony.reperevocal.modules.ui.components.VoiceStatusCard
import com.anthony.reperevocal.ui.state.AppViewModel

@Composable
fun ArchitectureScreen(
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
    ScreenScaffold(
        title = "Architecture",
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
        LazyColumn(
            modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            item {
                Text("Cette vue liste tous les nouveaux modules et stacks reconstruits dans l'application.")
            }
            items(ModuleRegistry.modules) { module ->
                VoiceStatusCard(
                    title = "${module.type.uppercase()} · ${module.name}",
                    subtitle = "${module.description}\nChemin source : ${module.path}"
                )
            }
        }
    }
}
