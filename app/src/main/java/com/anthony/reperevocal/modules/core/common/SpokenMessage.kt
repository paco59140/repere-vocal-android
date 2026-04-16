package com.anthony.reperevocal.modules.core.common

data class SpokenMessage(
    val text: String,
    val priority: AccessibilityPriority = AccessibilityPriority.MEDIUM,
    val canInterrupt: Boolean = false,
    val repeatCount: Int = 0
)
