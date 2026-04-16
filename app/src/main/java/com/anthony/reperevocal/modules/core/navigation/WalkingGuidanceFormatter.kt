package com.anthony.reperevocal.modules.core.navigation

object WalkingGuidanceFormatter {
    fun formatTurnInstruction(direction: String, distanceMeters: Int): String {
        return "Dans $distanceMeters mètres, tournez $direction."
    }

    fun formatNearbyStreet(streetName: String): String {
        return "Rue proche : $streetName."
    }
}
