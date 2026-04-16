package com.anthony.reperevocal.modules.core.navigation

data class UserLocation(
    val latitude: Double,
    val longitude: Double,
    val accuracyMeters: Float,
    val speedMetersPerSecond: Float? = null,
    val bearing: Float? = null
)
