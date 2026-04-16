package com.anthony.reperevocal.modules.feature.transport

data class TransportUpdate(
    val title: String,
    val details: String,
    val stopsRemaining: Int? = null,
    val alertBeforeExit: Boolean = true
)
