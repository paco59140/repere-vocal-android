package com.anthony.reperevocal.modules.stack.maps

data class MapsNavigationConfig(
    val voiceFirstNavigation: Boolean = true,
    val announceNearbyStreets: Boolean = true,
    val offRouteThresholdMeters: Float = 15f
)
