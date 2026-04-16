package com.anthony.reperevocal.modules.core.voice

import com.anthony.reperevocal.modules.core.common.SpokenMessage
import kotlinx.coroutines.flow.StateFlow

interface VoiceCore {
    val isSpeaking: StateFlow<Boolean>
    fun speak(message: SpokenMessage)
    fun stop()
    fun repeatLastMessage()
    fun setSpeechRate(rate: Float)
    fun setDetailedMode(enabled: Boolean)
}
