package com.anthony.reperevocal.services

import java.util.Locale

enum class VoiceAction {
    HOME, GPS, VISION, DOCUMENTS, OBJECTS, SOS, SETTINGS, BACK, REPEAT, UNKNOWN
}

data class VoiceCommandResult(
    val action: VoiceAction,
    val feedback: String
)

object VoiceCommandProcessor {
    fun process(input: String): VoiceCommandResult {
        val spoken = input.lowercase(Locale.ROOT).trim()

        return when {
            spoken.contains("accueil") || spoken.contains("menu principal") || spoken == "home" ->
                VoiceCommandResult(VoiceAction.HOME, "Retour à l'accueil")
            spoken.contains("gps") || spoken.contains("où suis") || spoken.contains("position") || spoken.contains("localisation") ->
                VoiceCommandResult(VoiceAction.GPS, "Ouverture du GPS")
            spoken.contains("vision") || spoken.contains("camera") || spoken.contains("caméra") || spoken.contains("voir") ->
                VoiceCommandResult(VoiceAction.VISION, "Ouverture du mode vision")
            spoken.contains("document") || spoken.contains("courrier") || spoken.contains("facture") || spoken.contains("ocr") || spoken.contains("scan") ->
                VoiceCommandResult(VoiceAction.DOCUMENTS, "Ouverture du lecteur de documents")
            spoken.contains("objet") || spoken.contains("cherche") || spoken.contains("clés") || spoken.contains("cles") || spoken.contains("lunettes") ->
                VoiceCommandResult(VoiceAction.OBJECTS, "Ouverture de la recherche d'objets")
            spoken.contains("sos") || spoken.contains("urgence") || spoken.contains("aide") || spoken.contains("secours") ->
                VoiceCommandResult(VoiceAction.SOS, "Ouverture du mode SOS")
            spoken.contains("réglage") || spoken.contains("reglage") || spoken.contains("paramètre") || spoken.contains("parametre") || spoken.contains("settings") ->
                VoiceCommandResult(VoiceAction.SETTINGS, "Ouverture des réglages")
            spoken.contains("retour") || spoken.contains("reviens") || spoken.contains("précédent") || spoken.contains("precedent") ->
                VoiceCommandResult(VoiceAction.BACK, "Retour à l'écran précédent")
            spoken.contains("répète") || spoken.contains("repete") || spoken.contains("redis") ->
                VoiceCommandResult(VoiceAction.REPEAT, "Je répète le dernier message")
            else ->
                VoiceCommandResult(VoiceAction.UNKNOWN, "Commande non reconnue")
        }
    }
}
