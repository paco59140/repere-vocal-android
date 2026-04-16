package com.anthony.reperevocal.modules.core.safety

import com.anthony.reperevocal.modules.core.navigation.UserLocation

interface SosCore {
    suspend fun triggerSos(currentLocation: UserLocation?, audioNotePath: String? = null)
    fun cancelPendingSos()
}
