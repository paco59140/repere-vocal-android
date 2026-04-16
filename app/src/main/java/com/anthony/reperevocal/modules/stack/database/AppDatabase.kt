package com.anthony.reperevocal.modules.stack.database

import androidx.room.Database
import androidx.room.RoomDatabase
import com.anthony.reperevocal.modules.stack.database.dao.MemoryItemDao
import com.anthony.reperevocal.modules.stack.database.entities.MemoryItemEntity

@Database(
    entities = [MemoryItemEntity::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun memoryItemDao(): MemoryItemDao
}
