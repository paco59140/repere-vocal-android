package com.anthony.reperevocal.ui.screens

import android.Manifest
import android.content.Context
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.anthony.reperevocal.services.LiveTextAnalyzer
import com.anthony.reperevocal.ui.state.AppViewModel
import java.util.concurrent.Executors

@Composable
fun VisionScreen(
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
    var hasCameraPermission by remember { mutableStateOf(false) }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        hasCameraPermission = granted
        appViewModel.speak(if (granted) "Caméra activée" else "Permission caméra refusée")
    }

    LaunchedEffect(Unit) {
        permissionLauncher.launch(Manifest.permission.CAMERA)
    }

    ScreenScaffold(
        title = "Vision IA",
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
            if (hasCameraPermission) {
                CameraPreview(
                    context = context,
                    onTextFound = { appViewModel.updateLiveVisionText(it) },
                    onError = { appViewModel.speak(it) }
                )
            } else {
                Text("La permission caméra est nécessaire.")
            }
            Button(
                onClick = { appViewModel.speak(uiState.liveVisionText, vibrate = true) },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Lire le dernier texte détecté")
            }
            Button(
                onClick = { appViewModel.dangerAlert("Obstacle possible devant vous") },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Tester alerte obstacle")
            }
            Text(uiState.liveVisionText)
        }
    }
}

@Composable
private fun CameraPreview(
    context: Context,
    onTextFound: (String) -> Unit,
    onError: (String) -> Unit
) {
    val previewView = remember { PreviewView(context) }
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    val executor = remember { Executors.newSingleThreadExecutor() }

    DisposableEffect(Unit) {
        val cameraProvider = cameraProviderFuture.get()
        val preview = Preview.Builder().build().also {
            it.surfaceProvider = previewView.surfaceProvider
        }

        val analysis = ImageAnalysis.Builder().build().also {
            it.setAnalyzer(executor, LiveTextAnalyzer(onTextFound, onError))
        }

        try {
            cameraProvider.unbindAll()
            cameraProvider.bindToLifecycle(
                context as androidx.lifecycle.LifecycleOwner,
                CameraSelector.DEFAULT_BACK_CAMERA,
                preview,
                analysis
            )
        } catch (e: Exception) {
            onError(e.localizedMessage ?: "Erreur caméra")
        }

        onDispose {
            cameraProvider.unbindAll()
            executor.shutdown()
        }
    }

    AndroidView(
        factory = { previewView },
        modifier = Modifier.fillMaxWidth().height(280.dp)
    )
}
