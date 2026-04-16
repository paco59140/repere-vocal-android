package com.anthony.reperevocal.modules.core.memory

data class MemoryItem(
    val id: Long = 0L,
    val title: String,
    val description: String,
    val room: String? = null,
    val category: String? = null,
    val voiceNotePath: String? = null,
    val bleTagId: String? = null,
    val createdAt: Long = System.currentTimeMillis()
)
