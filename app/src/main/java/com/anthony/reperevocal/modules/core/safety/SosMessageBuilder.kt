package com.anthony.reperevocal.modules.core.safety

import com.anthony.reperevocal.modules.core.navigation.UserLocation

object SosMessageBuilder {
    fun build(contactName: String, location: UserLocation?): String {
        val locationText = if (location == null) {
            "Position indisponible"
        } else {
            "Position: ${location.latitude}, ${location.longitude}"
        }
        return "Alerte SOS envoyée à $contactName. $locationText"
    }
}
