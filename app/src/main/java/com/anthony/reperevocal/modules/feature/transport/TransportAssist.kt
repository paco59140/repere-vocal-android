package com.anthony.reperevocal.modules.feature.transport

import kotlinx.coroutines.flow.Flow

interface TransportAssist {
    val updates: Flow<TransportUpdate>
    suspend fun loadTrip(destination: String)
    fun enableStopAlerts(enabled: Boolean)
    fun markReturnHome(homeAddress: String)
}
