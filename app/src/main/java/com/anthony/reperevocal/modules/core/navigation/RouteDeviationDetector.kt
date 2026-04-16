package com.anthony.reperevocal.modules.core.navigation

class RouteDeviationDetector(
    private val allowedDistanceMeters: Float = 15f
) {
    fun isOffRoute(currentDistanceFromRouteMeters: Float): Boolean {
        return currentDistanceFromRouteMeters > allowedDistanceMeters
    }
}
