
package com.anthony.reperevocal.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.anthony.reperevocal.ui.screens.ArchitectureScreen
import com.anthony.reperevocal.ui.screens.DocumentsScreen
import com.anthony.reperevocal.ui.screens.GpsScreen
import com.anthony.reperevocal.ui.screens.HomeScreen
import com.anthony.reperevocal.ui.screens.ObjectsScreen
import com.anthony.reperevocal.ui.screens.SettingsScreen
import com.anthony.reperevocal.ui.screens.SosScreen
import com.anthony.reperevocal.ui.screens.VisionScreen
import com.anthony.reperevocal.ui.state.AppViewModel

@Composable
fun AppNavGraph(appViewModel: AppViewModel) {
    val navController = rememberNavController()

    val goHome = { navController.navigate(Routes.Home.route) { popUpTo(0) } }
    val goGps = { navController.navigate(Routes.Gps.route) }
    val goVision = { navController.navigate(Routes.Vision.route) }
    val goDocuments = { navController.navigate(Routes.Documents.route) }
    val goObjects = { navController.navigate(Routes.Objects.route) }
    val goSos = { navController.navigate(Routes.Sos.route) }
    val goSettings = { navController.navigate(Routes.Settings.route) }
    val goArchitecture = { navController.navigate(Routes.Architecture.route) }

    NavHost(navController = navController, startDestination = Routes.Home.route) {
        composable(Routes.Home.route) {
            HomeScreen(
                appViewModel = appViewModel,
                openGps = goGps,
                openVision = goVision,
                openDocuments = goDocuments,
                openObjects = goObjects,
                openSos = goSos,
                openSettings = goSettings,
                openArchitecture = goArchitecture
            )
        }
        composable(Routes.Gps.route) {
            GpsScreen(
                appViewModel = appViewModel,
                onBack = { navController.popBackStack() },
                onGoHome = goHome,
                openGps = goGps,
                openVision = goVision,
                openDocuments = goDocuments,
                openObjects = goObjects,
                openSos = goSos,
                openSettings = goSettings
            )
        }
        composable(Routes.Vision.route) {
            VisionScreen(
                appViewModel = appViewModel,
                onBack = { navController.popBackStack() },
                onGoHome = goHome,
                openGps = goGps,
                openVision = goVision,
                openDocuments = goDocuments,
                openObjects = goObjects,
                openSos = goSos,
                openSettings = goSettings
            )
        }
        composable(Routes.Documents.route) {
            DocumentsScreen(
                appViewModel = appViewModel,
                onBack = { navController.popBackStack() },
                onGoHome = goHome,
                openGps = goGps,
                openVision = goVision,
                openDocuments = goDocuments,
                openObjects = goObjects,
                openSos = goSos,
                openSettings = goSettings
            )
        }
        composable(Routes.Objects.route) {
            ObjectsScreen(
                appViewModel = appViewModel,
                onBack = { navController.popBackStack() },
                onGoHome = goHome,
                openGps = goGps,
                openVision = goVision,
                openDocuments = goDocuments,
                openObjects = goObjects,
                openSos = goSos,
                openSettings = goSettings
            )
        }
        composable(Routes.Sos.route) {
            SosScreen(
                appViewModel = appViewModel,
                onBack = { navController.popBackStack() },
                onGoHome = goHome,
                openGps = goGps,
                openVision = goVision,
                openDocuments = goDocuments,
                openObjects = goObjects,
                openSos = goSos,
                openSettings = goSettings
            )
        }
        composable(Routes.Settings.route) {
            SettingsScreen(
                appViewModel = appViewModel,
                onBack = { navController.popBackStack() },
                onGoHome = goHome,
                openGps = goGps,
                openVision = goVision,
                openDocuments = goDocuments,
                openObjects = goObjects,
                openSos = goSos,
                openSettings = goSettings
            )
        }
        composable(Routes.Architecture.route) {
            ArchitectureScreen(
                appViewModel = appViewModel,
                onBack = { navController.popBackStack() },
                onGoHome = goHome,
                openGps = goGps,
                openVision = goVision,
                openDocuments = goDocuments,
                openObjects = goObjects,
                openSos = goSos,
                openSettings = goSettings
            )
        }
    }
}
