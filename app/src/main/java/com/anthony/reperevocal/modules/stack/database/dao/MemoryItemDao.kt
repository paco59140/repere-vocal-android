package com.anthony.reperevocal.modules.stack.database.dao

import androidx.room.*
import com.anthony.reperevocal.modules.stack.database.entities.MemoryItemEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface MemoryItemDao {
    @Query("SELECT * FROM memory_items ORDER BY createdAt DESC")
    fun observeAll(): Flow<List<MemoryItemEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: MemoryItemEntity)

    @Delete
    suspend fun delete(item: MemoryItemEntity)

    @Query("SELECT * FROM memory_items WHERE title LIKE '%' || :query || '%' OR description LIKE '%' || :query || '%'")
    suspend fun search(query: String): List<MemoryItemEntity>
}
