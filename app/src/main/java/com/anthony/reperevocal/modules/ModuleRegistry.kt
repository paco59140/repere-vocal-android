
package com.anthony.reperevocal.modules

data class SourceModule(
    val name: String,
    val path: String,
    val type: String,
    val description: String
)

object ModuleRegistry {
    val modules = listOf(
        SourceModule("core_common", "modules/core/common", "module", "Résultats applicatifs, priorités d’accessibilité et messages parlés."),
        SourceModule("voice_core", "modules/core/voice", "module", "File de messages vocaux, réglages voix et contrat du moteur vocal."),
        SourceModule("gps_core", "modules/core/navigation", "module", "Contrats GPS, formatage de guidage piéton et détection hors itinéraire."),
        SourceModule("camera_ai", "modules/core/vision", "module", "Détections caméra, priorisation des dangers et contrat d’analyse vidéo."),
        SourceModule("ocr_reader", "modules/core/ocr", "module", "Lecture OCR, cadrage de document et résultat de lecture."),
        SourceModule("sos_core", "modules/core/safety", "module", "Contact d’urgence, message SOS et déclenchement d’alerte."),
        SourceModule("object_memory", "modules/core/memory", "module", "Mémoire d’objets, requêtes naturelles, Room et BLE."),
        SourceModule("transport_assist", "modules/feature/transport", "module", "Aide transports, retour maison et alertes avant descente."),
        SourceModule("smart_home", "modules/feature/smarthome", "module", "Commandes domotiques et retours vocaux."),
        SourceModule("background_work", "modules/stack/work", "module", "Politique de tâches différées WorkManager."),
        SourceModule("jetpack_compose", "modules/ui", "stack", "Composants Compose accessibles et espacement global."),
        SourceModule("camerax", "modules/stack/camera", "stack", "Configuration et contrôleur CameraX."),
        SourceModule("mlkit", "modules/stack/ml", "stack", "Configuration de pipeline ML Kit."),
        SourceModule("google_maps_sdk", "modules/stack/maps", "stack", "Configuration de navigation cartographique."),
        SourceModule("text_to_speech", "modules/stack/tts", "stack", "Gestionnaire TTS Android."),
        SourceModule("speech_recognizer", "modules/stack/speech", "stack", "Gestionnaire de reconnaissance vocale Android."),
        SourceModule("room_database", "modules/stack/database", "stack", "Base Room pour mémoire d’objets."),
        SourceModule("ble", "modules/stack/ble", "stack", "Structures BLE pour retrouver des objets."),
        SourceModule("foreground_gps_service", "modules/stack/service", "stack", "Service GPS de premier plan."),
    )
}
