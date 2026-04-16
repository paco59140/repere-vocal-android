package com.anthony.reperevocal.modules.stack.ml

data class MlKitPipeline(
    val objectDetectionEnabled: Boolean = true,
    val ocrEnabled: Boolean = true,
    val filterLowConfidenceResults: Boolean = true
)
