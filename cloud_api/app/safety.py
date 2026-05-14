from __future__ import annotations

from .models import SensorEvent, SmartAlert


def analyze_sensor_event(event: SensorEvent) -> SmartAlert | None:
    value_text = str(event.value).lower()

    if event.kind == "smoke" and _truthy(event.value):
        return SmartAlert(
            severity="critical",
            title="Fumee detectee",
            message=f"Signal fumee depuis {event.source} dans {event.room}. Verification immediate recommandee.",
            source=event.source,
            kind=event.kind,
            recommended_routine="security",
        )

    if event.kind == "water" and _truthy(event.value):
        return SmartAlert(
            severity="critical",
            title="Fuite d'eau possible",
            message=f"Capteur eau actif dans {event.room}. Coupez l'eau si le signal se confirme.",
            source=event.source,
            kind=event.kind,
            recommended_routine="security",
        )

    if event.kind == "fall" and event.confidence >= 0.62:
        return SmartAlert(
            severity="critical",
            title="Chute possible",
            message=f"Chute detectee dans {event.room} avec {round(event.confidence * 100)}% de confiance.",
            source=event.source,
            kind=event.kind,
            recommended_routine="senior",
        )

    if event.kind == "door" and value_text in {"open", "ouverte", "ouvert", "true"}:
        hour = _hour_from_event(event)
        severity = "warning" if hour >= 22 or hour < 6 else "info"
        return SmartAlert(
            severity=severity,
            title="Porte ouverte",
            message=f"Porte ouverte detectee dans {event.room}.",
            source=event.source,
            kind=event.kind,
            recommended_routine="security" if severity == "warning" else None,
        )

    if event.kind == "sound" and any(word in value_text for word in ["glass", "verre", "cri", "alarme", "scream"]):
        return SmartAlert(
            severity="warning",
            title="Son inhabituel",
            message=f"Son suspect detecte par {event.source} : {event.value}.",
            source=event.source,
            kind=event.kind,
            recommended_routine="security",
        )

    if event.kind == "health" and any(word in value_text for word in ["fatigue", "stress", "anormal", "immobile"]):
        return SmartAlert(
            severity="warning",
            title="Bien-etre a verifier",
            message=f"Signal sante detecte : {event.value}.",
            source=event.source,
            kind=event.kind,
            recommended_routine="wellbeing",
        )

    if event.kind == "motion" and event.confidence >= 0.75:
        return SmartAlert(
            severity="info",
            title="Mouvement detecte",
            message=f"Mouvement dans {event.room}.",
            source=event.source,
            kind=event.kind,
        )

    return None


def _truthy(value: str | float | int | bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    return value.lower() in {"1", "true", "on", "oui", "yes", "detected", "detecte"}


def _hour_from_event(event: SensorEvent) -> int:
    if event.timestamp and len(event.timestamp) >= 13:
        try:
            return int(event.timestamp[11:13])
        except ValueError:
            return 12
    return 12
