package com.anthony.reperevocal.modules.core.voice

import com.anthony.reperevocal.modules.core.common.AccessibilityPriority
import com.anthony.reperevocal.modules.core.common.SpokenMessage
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.util.PriorityQueue

class VoiceQueueManager {
    private val queue = PriorityQueue<SpokenMessage>(compareByDescending { it.priority.ordinal })
    private val _isSpeaking = MutableStateFlow(false)
    val isSpeaking: StateFlow<Boolean> = _isSpeaking
    private var lastMessage: SpokenMessage? = null

    fun enqueue(message: SpokenMessage) {
        if (message.canInterrupt && message.priority >= AccessibilityPriority.HIGH) {
            queue.clear()
        }
        queue.add(message)
        lastMessage = message
    }

    fun nextOrNull(): SpokenMessage? = queue.poll()
    fun repeatLast(): SpokenMessage? = lastMessage
    fun setSpeaking(value: Boolean) { _isSpeaking.value = value }
    fun clear() { queue.clear() }
}
