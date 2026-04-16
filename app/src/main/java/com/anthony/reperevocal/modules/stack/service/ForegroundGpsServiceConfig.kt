package com.anthony.reperevocal.modules.stack.service

data class ForegroundGpsServiceConfig(
    val useAdaptiveFrequency: Boolean = true,
    val updateIntervalMs: Long = 5_000L,
    val fastestIntervalMs: Long = 2_000L,
    val distanceFilterMeters: Float = 3f
)
