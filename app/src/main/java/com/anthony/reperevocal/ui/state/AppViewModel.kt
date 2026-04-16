package com.anthony.reperevocal.ui.state

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.anthony.reperevocal.data.SettingsRepository
import com.anthony.reperevocal.services.HapticGuide
import com.anthony.reperevocal.services.VoiceGuide
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class SettingsState(
    val speechEnabled: Boolean = true,
    val vibrationEnabled: Boolean = true,
    val trustedContact: String = "0612345678"
)

data class AppUiState(
    val lastSpokenText: String = "",
    val extractedText: String = "Aucun document analysé.",
    val liveVisionText: String = "Aucun texte détecté en direct.",
    val settings: SettingsState = SettingsState(),
    val settingsLoaded: Boolean = false
)

class AppViewModel(application: Application) : AndroidViewModel(application) {
    private val voiceGuide = VoiceGuide(application.applicationContext)
    private val hapticGuide = HapticGuide(application.applicationContext)
    private val settingsRepository = SettingsRepository(application.applicationContext)

    private val _uiState = MutableStateFlow(AppUiState())
    val uiState: StateFlow<AppUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            settingsRepository.settingsFlow.collect { settings ->
                _uiState.value = _uiState.value.copy(
                    settings = settings,
                    settingsLoaded = true
                )
            }
        }
    }

    fun speak(text: String, vibrate: Boolean = false) {
        val settings = _uiState.value.settings
        if (settings.speechEnabled) voiceGuide.speak(text)
        if (settings.vibrationEnabled && vibrate) hapticGuide.shortPulse()
        _uiState.value = _uiState.value.copy(lastSpokenText = text)
    }

    fun repeatLastMessage() {
        val last = _uiState.value.lastSpokenText.ifBlank { "Aucun message à répéter." }
        if (_uiState.value.settings.speechEnabled) {
            voiceGuide.speak(last)
        }
    }

    fun dangerAlert(text: String) {
        val settings = _uiState.value.settings
        if (settings.speechEnabled) voiceGuide.speak(text)
        if (settings.vibrationEnabled) hapticGuide.dangerPulse()
        _uiState.value = _uiState.value.copy(lastSpokenText = text)
    }

    fun updateExtractedText(text: String) {
        _uiState.value = _uiState.value.copy(extractedText = text)
    }

    fun updateLiveVisionText(text: String) {
        if (text.isBlank()) return
        _uiState.value = _uiState.value.copy(liveVisionText = text)
    }

    fun speakLatestVisionText() {
        speak(_uiState.value.liveVisionText, vibrate = true)
    }

    fun updateTrustedContact(phone: String) {
        _uiState.value = _uiState.value.copy(
            settings = _uiState.value.settings.copy(trustedContact = phone)
        )
    }

    fun updateSettings(
        speechEnabled: Boolean,
        vibrationEnabled: Boolean,
        trustedContact: String
    ) {
        val newSettings = SettingsState(
            speechEnabled = speechEnabled,
            vibrationEnabled = vibrationEnabled,
            trustedContact = trustedContact
        )
        _uiState.value = _uiState.value.copy(settings = newSettings)
        viewModelScope.launch {
            settingsRepository.saveSettings(newSettings)
        }
    }

    fun persistCurrentSettings() {
        viewModelScope.launch {
            settingsRepository.saveSettings(_uiState.value.settings)
        }
    }

    override fun onCleared() {
        super.onCleared()
        voiceGuide.shutdown()
    }
}
