package com.anthony.reperevocal.data

import android.content.Context
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.anthony.reperevocal.ui.state.SettingsState
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore(name = "repere_vocal_settings")

class SettingsRepository(private val context: Context) {

    private object Keys {
        val speechEnabled = booleanPreferencesKey("speech_enabled")
        val vibrationEnabled = booleanPreferencesKey("vibration_enabled")
        val trustedContact = stringPreferencesKey("trusted_contact")
    }

    val settingsFlow: Flow<SettingsState> = context.dataStore.data.map { prefs ->
        SettingsState(
            speechEnabled = prefs[Keys.speechEnabled] ?: true,
            vibrationEnabled = prefs[Keys.vibrationEnabled] ?: true,
            trustedContact = prefs[Keys.trustedContact] ?: "0612345678"
        )
    }

    suspend fun saveSettings(settings: SettingsState) {
        context.dataStore.edit { prefs: MutablePreferences ->
            prefs[Keys.speechEnabled] = settings.speechEnabled
            prefs[Keys.vibrationEnabled] = settings.vibrationEnabled
            prefs[Keys.trustedContact] = settings.trustedContact
        }
    }
}

typealias MutablePreferences = androidx.datastore.preferences.core.MutablePreferences
