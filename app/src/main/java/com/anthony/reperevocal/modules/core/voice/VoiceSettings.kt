package com.anthony.reperevocal.modules.core.voice

data class VoiceSettings(
    val speechRate: Float = 1.0f,
    val detailedMode: Boolean = true,
    val confirmationsEnabled: Boolean = true,
    val criticalAlertsRepeatCount: Int = 2
)
