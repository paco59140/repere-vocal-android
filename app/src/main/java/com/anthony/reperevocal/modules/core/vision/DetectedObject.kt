package com.anthony.reperevocal.modules.core.vision

import com.anthony.reperevocal.modules.core.common.AccessibilityPriority

data class DetectedObject(
    val label: String,
    val confidence: Float,
    val distanceEstimateMeters: Float? = null,
    val isMoving: Boolean = false,
    val priority: AccessibilityPriority = AccessibilityPriority.MEDIUM
)
