package com.anthony.reperevocal.modules.core.safety

data class EmergencyContact(
    val name: String,
    val phoneNumber: String,
    val canReceiveSms: Boolean = true,
    val canReceiveCall: Boolean = true
)
