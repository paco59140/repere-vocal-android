package com.anthony.reperevocal.modules.core.memory

import kotlinx.coroutines.flow.Flow

interface ObjectMemory {
    fun observeItems(): Flow<List<MemoryItem>>
    suspend fun save(item: MemoryItem)
    suspend fun delete(itemId: Long)
    suspend fun search(query: String): List<MemoryItem>
}
