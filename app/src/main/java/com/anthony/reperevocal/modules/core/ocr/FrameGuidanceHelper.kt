package com.anthony.reperevocal.modules.core.ocr

object FrameGuidanceHelper {
    fun guidanceFor(isCentered: Boolean, hasEnoughLight: Boolean): String {
        return when {
            !hasEnoughLight -> "Lumière insuffisante, rapprochez-vous ou éclairez le document."
            !isCentered -> "Ajustez le téléphone pour centrer le texte."
            else -> "Texte bien cadré, lecture en cours."
        }
    }
}
