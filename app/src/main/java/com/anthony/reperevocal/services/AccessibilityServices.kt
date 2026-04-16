package com.anthony.reperevocal.services

import android.Manifest
import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.location.Geocoder
import android.net.Uri
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.provider.MediaStore
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import androidx.activity.result.ActivityResultLauncher
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import kotlinx.coroutines.suspendCancellableCoroutine
import java.util.Locale
import kotlin.coroutines.resume

class VoiceGuide(context: Context) {
    private var ready = false
    private val tts = TextToSpeech(context.applicationContext) { status ->
        ready = status == TextToSpeech.SUCCESS
        if (ready) tts.language = Locale.FRANCE
    }

    fun speak(text: String) {
        if (ready) tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "repere_vocal")
    }

    fun shutdown() {
        tts.stop()
        tts.shutdown()
    }
}

class HapticGuide(context: Context) {
    private val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
    fun shortPulse() = vibrate(120)
    fun longPulse() = vibrate(260)
    fun dangerPulse() {
        vibrator.vibrate(
            VibrationEffect.createWaveform(longArrayOf(0, 120, 60, 120, 60, 220), -1)
        )
    }
    private fun vibrate(duration: Long) {
        vibrator.vibrate(VibrationEffect.createOneShot(duration, VibrationEffect.DEFAULT_AMPLITUDE))
    }
}

class SpeechInputManager(private val activity: Activity) {
    fun startSpeechInput(launcher: ActivityResultLauncher<Intent>) {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.FRANCE)
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Parlez maintenant")
        }
        launcher.launch(intent)
    }

    fun isAvailable(): Boolean = SpeechRecognizer.isRecognitionAvailable(activity)
}

class LocationGuide(private val context: Context) {
    private val fusedClient: FusedLocationProviderClient = LocationServices.getFusedLocationProviderClient(context)

    fun hasLocationPermission(): Boolean {
        return ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED ||
            ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED
    }

    suspend fun currentLocationSummary(): String {
        if (!hasLocationPermission()) return "La permission de localisation est nécessaire."
        val location = suspendCancellableCoroutine<com.google.android.gms.location.Location?> { cont ->
            fusedClient.lastLocation
                .addOnSuccessListener { cont.resume(it) }
                .addOnFailureListener { cont.resume(null) }
        }
        if (location == null) return "Position introuvable pour le moment."

        return try {
            val geocoder = Geocoder(context, Locale.FRANCE)
            val addresses = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                val list = mutableListOf<android.location.Address>()
                val latch = java.util.concurrent.CountDownLatch(1)
                geocoder.getFromLocation(location.latitude, location.longitude, 1) {
                    list.addAll(it)
                    latch.countDown()
                }
                latch.await()
                list
            } else {
                @Suppress("DEPRECATION")
                geocoder.getFromLocation(location.latitude, location.longitude, 1) ?: emptyList()
            }
            val line = addresses.firstOrNull()?.getAddressLine(0)
            line ?: "Latitude ${'$'}{location.latitude}, longitude ${'$'}{location.longitude}"
        } catch (_: Exception) {
            "Latitude ${'$'}{location.latitude}, longitude ${'$'}{location.longitude}"
        }
    }
}

object EmergencyActions {
    fun openDialer(context: Context, phoneNumber: String) {
        val intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:${'$'}phoneNumber"))
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
    }

    fun openSms(context: Context, phoneNumber: String, message: String) {
        val intent = Intent(Intent.ACTION_SENDTO).apply {
            data = Uri.parse("smsto:${'$'}phoneNumber")
            putExtra("sms_body", message)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        context.startActivity(intent)
    }

    fun openImagePicker(launcher: ActivityResultLauncher<Intent>) {
        val intent = Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
        intent.type = "image/*"
        launcher.launch(intent)
    }
}
