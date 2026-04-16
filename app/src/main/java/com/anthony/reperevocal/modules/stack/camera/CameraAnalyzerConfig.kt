package com.anthony.reperevocal.modules.stack.camera

data class CameraAnalyzerConfig(
    val lowLightMode: Boolean = false,
    val targetFrameRate: Int = 24,
    val detectHazardsOnly: Boolean = false
)
