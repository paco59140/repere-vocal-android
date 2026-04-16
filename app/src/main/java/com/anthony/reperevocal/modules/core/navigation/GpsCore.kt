package com.anthony.reperevocal.modules.core.navigation

import kotlinx.coroutines.flow.Flow

interface GpsCore {
    val locationUpdates: Flow<UserLocation>
    fun startTracking()
    fun stopTracking()
    fun setBatterySaving(enabled: Boolean)
    fun setPedestrianPrecisionMode(enabled: Boolean)
}
