package com.anthony.reperevocal.ui.screens

import android.Manifest
import android.app.Activity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.anthony.reperevocal.services.LocationGuide
import com.anthony.reperevocal.ui.state.AppViewModel
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@Composable
fun GpsScreen(
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
    val activity = context as Activity
    val locationGuide = remember { LocationGuide(context) }
    val uiState by appViewModel.uiState.collectAsState()

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        if (permissions.values.all { it }) {
            appViewModel.speak("Permissions GPS accordées")
        } else {
            appViewModel.speak("Le GPS a besoin des permissions de localisation")
        }
    }

    ScreenScaffold(
        title = "GPS",
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
            Text("Position actuelle : ${uiState.lastSpokenText}")
            Button(
                onClick = {
                    permissionLauncher.launch(arrayOf(
                        Manifest.permission.ACCESS_FINE_LOCATION,
                        Manifest.permission.ACCESS_COARSE_LOCATION
                    ))
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Demander permissions GPS")
            }
            Button(
                onClick = {
                    CoroutineScope(Dispatchers.Main).launch {
                        val result = locationGuide.currentLocationSummary()
                        appViewModel.speak(result, vibrate = true)
                    }
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Dire ma position")
            }
        }
    }
}
