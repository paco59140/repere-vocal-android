package com.anthony.reperevocal.modules.core.memory

object NaturalMemoryQuery {
    fun normalize(query: String): String {
        return query.lowercase()
            .replace("où sont", "")
            .replace("ou sont", "")
            .replace("mes", "")
            .trim()
    }
}
