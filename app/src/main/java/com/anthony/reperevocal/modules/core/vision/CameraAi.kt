package com.anthony.reperevocal.modules.core.vision

import kotlinx.coroutines.flow.Flow

interface CameraAi {
    val detections: Flow<List<DetectedObject>>
    fun startAnalysis()
    fun stopAnalysis()
    fun enableLowLightMode(enabled: Boolean)
}
