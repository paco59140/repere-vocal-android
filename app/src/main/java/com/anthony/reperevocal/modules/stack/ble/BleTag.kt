package com.anthony.reperevocal.modules.stack.ble

data class BleTag(
    val id: String,
    val name: String,
    val rssi: Int? = null,
    val lastSeenAt: Long = System.currentTimeMillis()
)
