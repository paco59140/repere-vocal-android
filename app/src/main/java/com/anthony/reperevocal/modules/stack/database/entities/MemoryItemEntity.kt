package com.anthony.reperevocal.modules.stack.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "memory_items")
data class MemoryItemEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0L,
    val title: String,
    val description: String,
    val room: String?,
    val category: String?,
    val voiceNotePath: String?,
    val bleTagId: String?,
    val createdAt: Long
)
