package com.anthony.reperevocal.modules.core.ocr

data class OcrResult(
    val fullText: String,
    val lines: List<String> = emptyList(),
    val detectedLanguage: String? = null,
    val confidence: Float? = null
)
