package com.anthony.reperevocal.modules.core.vision

import com.anthony.reperevocal.modules.core.common.AccessibilityPriority

object HazardPrioritizer {
    fun priorityFor(label: String, distanceMeters: Float?): AccessibilityPriority {
        val lower = label.lowercase()
        return when {
            distanceMeters != null && distanceMeters < 1.5f -> AccessibilityPriority.CRITICAL
            lower.contains("vehicle") || lower.contains("stairs") || lower.contains("hole") -> AccessibilityPriority.HIGH
            lower.contains("door") || lower.contains("person") || lower.contains("crosswalk") -> AccessibilityPriority.MEDIUM
            else -> AccessibilityPriority.LOW
        }
    }
}
