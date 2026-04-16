package com.anthony.reperevocal.modules.feature.smarthome

sealed class SmartHomeCommand {
    data class TurnLightOn(val room: String) : SmartHomeCommand()
    data class TurnLightOff(val room: String) : SmartHomeCommand()
    data class RunRoutine(val routineName: String) : SmartHomeCommand()
    data class QueryStatus(val deviceName: String) : SmartHomeCommand()
}
