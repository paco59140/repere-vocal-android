package com.anthony.reperevocal.modules.feature.smarthome

interface SmartHomeController {
    suspend fun execute(command: SmartHomeCommand): SmartHomeResult
}
