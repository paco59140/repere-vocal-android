package com.anthony.reperevocal.modules.core.ocr

import kotlinx.coroutines.flow.Flow

interface OcrReader {
    val textResults: Flow<OcrResult>
    suspend fun readCurrentFrame()
    fun setLineByLineMode(enabled: Boolean)
    fun setAutoLanguageDetection(enabled: Boolean)
}
