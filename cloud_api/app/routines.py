from __future__ import annotations

from .models import CompanionDecision, ContextSignal, RoutineAction


def decide_from_context(context: ContextSignal) -> CompanionDecision:
    if context.location == "maison" and context.hour >= 21:
        return build_routine("sleep", context)
    if context.location == "maison" and context.fatigue == "elevee":
        return build_routine("comfort", context)
    if context.location == "maison" and context.weather in {"pluie", "orage"} and context.hour >= 18:
        return build_routine("return_rain", context)
    if context.hour < 9:
        return build_routine("morning", context)
    return CompanionDecision(
        intent="observe",
        answer="Maison stable. Je surveille les habitudes, la securite et les rappels utiles.",
        routine=None,
        confidence=0.66,
        actions=[],
    )


def decide_from_command(text: str, context: ContextSignal) -> CompanionDecision:
    normalized = text.lower().strip()
    if any(word in normalized for word in ["dormir", "nuit", "coucher"]):
        return build_routine("sleep", context)
    if any(word in normalized for word in ["je rentre", "retour maison", "j'arrive"]):
        return build_routine("return", context)
    if any(word in normalized for word in ["frigo", "courses", "recette", "cuisine"]):
        return build_routine("kitchen", context)
    if any(word in normalized for word in ["medicament", "hydratation", "sante"]):
        return build_routine("wellbeing", context)
    if any(word in normalized for word in ["securite", "intrusion", "fumee", "fuite", "sos"]):
        return build_routine("security", context)
    if any(word in normalized for word in ["voiture", "trajet", "carburant", "maintenance"]):
        return build_routine("car", context)
    if any(word in normalized for word in ["memorise", "souviens", "retiens"]):
        cleaned = normalized.replace("memorise", "").replace("souviens-toi", "").replace("retiens", "").strip(" :.")
        return CompanionDecision(
            intent="memory.store",
            answer="C'est memorise localement.",
            confidence=0.8,
            memory_to_store=cleaned or text,
        )
    return CompanionDecision(
        intent="conversation",
        answer="J'ai compris. Je garde le contexte et je propose une action si une habitude se confirme.",
        confidence=0.58,
    )


def build_routine(name: str, context: ContextSignal) -> CompanionDecision:
    routines: dict[str, CompanionDecision] = {
        "sleep": CompanionDecision(
            intent="routine.sleep",
            routine="sleep",
            answer="Routine nuit prete : lumieres coupees, volume reduit, reveil et meteo du matin prepares.",
            confidence=0.92,
            actions=[
                RoutineAction(id="lights_off", label="Couper les lumieres", target="home.lights"),
                RoutineAction(id="volume_low", label="Reduire le volume Nest Hub", target="nest.volume", payload={"level": 18}),
                RoutineAction(id="alarm_prepare", label="Preparer le reveil", target="calendar.alarm"),
            ],
        ),
        "comfort": CompanionDecision(
            intent="routine.comfort",
            routine="comfort",
            answer="Mode confort : lumiere chaude, rappel hydratation et ambiance calme.",
            confidence=0.84,
            actions=[
                RoutineAction(id="warm_light", label="Lumiere chaude", target="home.lights", payload={"temperature": "warm"}),
                RoutineAction(id="hydration", label="Rappel hydratation", target="health.reminder"),
            ],
        ),
        "return_rain": CompanionDecision(
            intent="routine.return_rain",
            routine="return_rain",
            answer="Retour pluie detecte : entree eclairee, chauffage confort et sol surveille.",
            confidence=0.8,
            actions=[
                RoutineAction(id="entry_light", label="Allumer entree", target="home.entry_light"),
                RoutineAction(id="heat_comfort", label="Chauffage confort", target="home.heating", payload={"temperature": 20.5}),
            ],
        ),
        "return": CompanionDecision(
            intent="routine.return",
            routine="return",
            answer="Retour maison active : lumiere d'entree, chauffage confort et musique douce.",
            confidence=0.88,
            actions=[
                RoutineAction(id="entry_light", label="Allumer entree", target="home.entry_light"),
                RoutineAction(id="music_soft", label="Musique douce", target="media.music"),
            ],
        ),
        "morning": CompanionDecision(
            intent="routine.morning",
            routine="morning",
            answer="Brief matin : meteo, agenda, trajet et cuisine sont prepares.",
            confidence=0.82,
            actions=[
                RoutineAction(id="weather_brief", label="Lire la meteo", target="weather"),
                RoutineAction(id="calendar_brief", label="Lire agenda", target="calendar"),
            ],
        ),
        "kitchen": CompanionDecision(
            intent="routine.kitchen",
            routine="kitchen",
            answer="Cuisine intelligente prete : scan frigo, recettes vocales et liste de courses.",
            confidence=0.86,
            actions=[RoutineAction(id="fridge_scan", label="Scanner le frigo", target="vision.fridge")],
        ),
        "wellbeing": CompanionDecision(
            intent="routine.wellbeing",
            routine="wellbeing",
            answer="Bien-etre active : medicaments, hydratation, sommeil et fatigue surveilles.",
            confidence=0.83,
            actions=[
                RoutineAction(id="medicine_reminder", label="Verifier medicaments", target="health.medicine"),
                RoutineAction(id="sleep_watch", label="Surveiller sommeil", target="health.sleep"),
            ],
        ),
        "security": CompanionDecision(
            intent="routine.security",
            routine="security",
            answer="Securite intelligente active : intrusion, fumee, fuite d'eau et sons suspects.",
            confidence=0.9,
            actions=[
                RoutineAction(id="camera_guard", label="Activer analyse camera", target="vision.security"),
                RoutineAction(id="sound_guard", label="Analyser sons", target="audio.security"),
            ],
        ),
        "car": CompanionDecision(
            intent="routine.car",
            routine="car",
            answer="Assistant voiture pret : trafic, meteo trajet, carburant et maintenance.",
            confidence=0.78,
            actions=[RoutineAction(id="car_brief", label="Preparer trajet voiture", target="car.assistant")],
        ),
    }
    return routines[name]

