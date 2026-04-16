package com.anthony.reperevocal.navigation

sealed class Routes(val route: String) {
    data object Home : Routes("home")
    data object Gps : Routes("gps")
    data object Vision : Routes("vision")
    data object Documents : Routes("documents")
    data object Objects : Routes("objects")
    data object Sos : Routes("sos")
    data object Settings : Routes("settings")
    data object Architecture : Routes("architecture")
}
