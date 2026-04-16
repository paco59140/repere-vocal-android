package com.anthony.reperevocal.modules.stack.tts

import android.content.Context
import android.speech.tts.TextToSpeech
import java.util.Locale

class AppTextToSpeechManager(
    context: Context,
    private val locale: Locale = Locale.FRANCE
) {
    private var tts: TextToSpeech? = null

    init {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = locale
                tts?.setSpeechRate(1.0f)
            }
        }
    }

    fun speak(text: String, flush: Boolean = true) {
        val queueMode = if (flush) TextToSpeech.QUEUE_FLUSH else TextToSpeech.QUEUE_ADD
        tts?.speak(text, queueMode, null, "vision_assist_tts")
    }

    fun stop() = tts?.stop()

    fun release() {
        tts?.stop()
        tts?.shutdown()
    }
}
