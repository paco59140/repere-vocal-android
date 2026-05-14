from __future__ import annotations

import json
import ipaddress
import os
from pathlib import Path
from datetime import date

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse

from .ai_router import AIConfigStore, AIRouter
from .integrations import ActionExecutor, IntegrationStore
from .memory import MemoryStore
from .models import (
    ActionExecutionResult,
    AIConfig,
    AutomationProposal,
    BehaviorAnomaly,
    CalendarEvent,
    CarReminder,
    ChatRequest,
    ChatResponse,
    CommandRequest,
    CompanionDecision,
    CompanionNotification,
    ContextInsight,
    ContextSignal,
    CustomRoutine,
    DailyBrief,
    DeviceCommand,
    EmergencyContact,
    EnergyReading,
    EnvironmentalSnapshot,
    EscalationResult,
    ExecuteActionsRequest,
    FamilyAlbum,
    FamilyMoment,
    HealthReminder,
    HubState,
    GoogleHomeStatus,
    IntegrationConfig,
    KitchenItem,
    LearnedAutomation,
    MemoryItem,
    NestHubState,
    NestHubUpdate,
    PresenceSignal,
    RoutineAction,
    SensorEvent,
    SmartAlert,
    SmartDevice,
    SystemDiagnostic,
    UserProfile,
    VisionObservation,
    WellbeingCheckIn,
)
from .nest_hub import NestHubStore, render_display
from .routines import build_routine, decide_from_command, decide_from_context
from .safety import analyze_sensor_event

DATA_DIR = Path(os.environ.get("COMPANION_DATA_DIR", Path(__file__).resolve().parents[1] / "data"))
store = MemoryStore(DATA_DIR / "companion_memory.sqlite3")
store.ensure_default_devices()
integrations = IntegrationStore(DATA_DIR / "integrations.json")
nest_hub = NestHubStore(DATA_DIR / "nest_hub.json")
ai_config = AIConfigStore(DATA_DIR / "ai_config.json")

app = FastAPI(title="Companion Hub AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def protect_remote_access(request: Request, call_next):
    config = integrations.load()
    if should_require_remote_token(request, config):
        token = request.headers.get("x-companion-token") or request.headers.get("authorization", "").removeprefix("Bearer ").strip()
        if not token or token != config.remote_access_token:
            return JSONResponse({"detail": "Cle d'acces distant Companion invalide."}, status_code=401)
    return await call_next(request)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "cloud-first"}


@app.get("/remote/status")
def remote_status() -> dict[str, object]:
    config = integrations.load()
    return {
        "enabled": config.remote_access_enabled,
        "public_url": config.remote_public_url,
        "token_configured": bool(config.remote_access_token),
        "secured": bool(config.remote_access_enabled and config.remote_access_token),
        "google_home_ready": build_google_home_status(config).ready,
        "message": remote_access_message(config),
    }


@app.post("/context", response_model=HubState)
def update_context(context: ContextSignal) -> HubState:
    insight = build_context_insight(context)
    decision = evaluate_learned_automations(context) or decision_from_insight(insight, context) or decide_from_context(context)
    store.add_event(decision.answer)
    return HubState(
        status="online",
        context=context,
        suggestion=decision,
        context_insight=insight,
        memories=store.list_memories(),
        user_profiles=store.list_user_profiles(),
        presence_signals=store.list_presence_signals(),
        family_moments=store.list_family_moments(),
        family_albums=store.list_family_albums(),
        health_reminders=store.list_health_reminders(),
        wellbeing_checkins=store.list_wellbeing_checkins(),
        behavior_anomalies=store.list_behavior_anomalies(),
        calendar_events=store.list_calendar_events(),
        environmental_snapshots=store.list_environmental_snapshots(),
        energy_readings=store.list_energy_readings(),
        kitchen_items=store.list_kitchen_items(),
        smart_devices=store.list_smart_devices(),
        car_reminders=store.list_car_reminders(),
        custom_routines=store.list_custom_routines(),
        learned_automations=store.list_learned_automations(),
        automation_proposals=store.list_automation_proposals(),
        vision_observations=store.list_vision_observations(),
        alerts=store.list_alerts(),
        notifications=store.list_notifications(),
        emergency_contacts=store.list_emergency_contacts(),
        nest_hub=nest_hub.load(),
        events=store.list_events(),
    )


@app.post("/command")
def command(request: CommandRequest) -> dict[str, object]:
    decision = decide_from_command(request.text, request.context)
    if decision.intent == "conversation":
        chat_response = AIRouter(ai_config.load()).chat(
            ChatRequest(
                text=request.text,
                context=request.context,
                memories=[item.text for item in store.list_memories(8)],
            )
        )
        decision.answer = chat_response.answer
        decision.confidence = 0.72 if chat_response.provider != "local" else decision.confidence
    if decision.memory_to_store:
        store.add_memory(decision.memory_to_store, "conversation")
    if decision.actions:
        decision.execution_results = ActionExecutor(integrations.load()).execute_many(decision.actions)
    store.add_event(f"{request.text} -> {decision.answer}")
    return decision.model_dump()


@app.get("/ai/config", response_model=AIConfig)
def get_ai_config() -> AIConfig:
    config = ai_config.load()
    if config.api_key:
        config = config.model_copy(update={"api_key": "***"})
    return config


@app.post("/ai/config", response_model=AIConfig)
def save_ai_config(config: AIConfig) -> AIConfig:
    saved = ai_config.save(config)
    store.add_event(f"Configuration IA mise a jour : {saved.provider}")
    if saved.api_key:
        saved = saved.model_copy(update={"api_key": "***"})
    return saved


@app.post("/ai/chat", response_model=ChatResponse)
def ai_chat(request: ChatRequest) -> ChatResponse:
    if not request.memories:
        request.memories = [item.text for item in store.list_memories(8)]
    response = AIRouter(ai_config.load()).chat(request)
    store.add_event(f"Chat IA ({response.provider}) -> {response.answer[:90]}")
    return response


@app.get("/family/moments", response_model=list[FamilyMoment])
def family_moments() -> list[FamilyMoment]:
    return store.list_family_moments()


@app.post("/family/moments", response_model=FamilyMoment)
def add_family_moment(moment: FamilyMoment) -> FamilyMoment:
    saved = store.add_family_moment(moment)
    store.add_memory(saved.summary or saved.description, "family")
    store.add_event(f"Souvenir familial ajoute : {saved.title}")
    nest_hub.update(
        NestHubUpdate(
            screen="family",
            title=saved.title,
            message=saved.summary or saved.description,
        )
    )
    return saved


@app.get("/family/journal")
def family_journal() -> dict[str, object]:
    moments = store.list_family_moments(12)
    albums = store.list_family_albums(6)
    if not moments:
        return {
            "title": "Journal familial",
            "summary": "Aucun souvenir familial enregistre pour le moment.",
            "moments": [],
            "albums": [album.model_dump() for album in albums],
        }
    lines = [moment.summary or moment.description for moment in moments[:5]]
    return {
        "title": "Journal familial",
        "summary": " ".join(lines),
        "moments": [moment.model_dump() for moment in moments],
        "albums": [album.model_dump() for album in albums],
    }


@app.get("/family/albums", response_model=list[FamilyAlbum])
def family_albums() -> list[FamilyAlbum]:
    return store.list_family_albums()


@app.post("/family/albums", response_model=FamilyAlbum)
def add_family_album(album: FamilyAlbum) -> FamilyAlbum:
    saved = store.add_family_album(album)
    store.add_memory(saved.narration, "family_album")
    store.add_event(f"Album familial ajoute : {saved.title}")
    nest_hub.update(
        NestHubUpdate(
            screen="family",
            title=saved.title,
            message=saved.narration,
        )
    )
    return saved


@app.post("/family/albums/auto", response_model=FamilyAlbum)
def auto_family_album(theme: str = "semaine") -> FamilyAlbum:
    saved = store.auto_family_album(theme)
    store.add_memory(saved.narration, "family_album")
    store.add_event(f"Album familial automatique : {saved.title}")
    nest_hub.update(
        NestHubUpdate(
            screen="family",
            title=saved.title,
            message=saved.narration,
        )
    )
    return saved


@app.get("/users/profiles", response_model=list[UserProfile])
def user_profiles() -> list[UserProfile]:
    return store.list_user_profiles()


@app.post("/users/profiles", response_model=UserProfile)
def add_user_profile(profile: UserProfile) -> UserProfile:
    saved = store.add_user_profile(profile)
    store.add_memory(
        f"{saved.name} prefere une lumiere {saved.preferred_light} et le calme apres {saved.quiet_hours_start}.",
        "user",
    )
    store.add_event(f"Profil utilisateur ajoute : {saved.name}")
    nest_hub.update(
        NestHubUpdate(
            screen="family",
            title=f"Bienvenue {saved.name}",
            message=f"Preference lumiere {saved.preferred_light}, role {saved.role}.",
        )
    )
    return saved


@app.post("/users/profiles/{profile_id}/seen", response_model=UserProfile | None)
def mark_user_profile_seen(profile_id: int) -> UserProfile | None:
    saved = store.mark_user_seen(profile_id)
    if saved is not None:
        signal = store.add_presence_signal(
            PresenceSignal(
                user_profile_id=saved.id,
                user_name=saved.name,
                room="maison",
                proximity="near",
                source="manual",
                confidence=0.88,
            )
        )
        store.add_event(f"Presence detectee : {saved.name}")
        nest_hub.update(
            NestHubUpdate(
                screen="home",
                title=f"Bonjour {saved.name}",
                message=build_presence_message(signal, saved),
            )
        )
    return saved


@app.get("/presence/events", response_model=list[PresenceSignal])
def presence_events() -> list[PresenceSignal]:
    return store.list_presence_signals()


@app.post("/presence/events", response_model=PresenceSignal)
def add_presence_event(signal: PresenceSignal) -> PresenceSignal:
    saved = store.add_presence_signal(signal)
    if saved.user_profile_id is not None:
        store.mark_user_seen(saved.user_profile_id)
    store.add_event(f"Presence {saved.user_name} : {saved.room} ({saved.proximity})")
    profile = next((item for item in store.list_user_profiles() if item.id == saved.user_profile_id), None)
    nest_hub.update(
        NestHubUpdate(
            screen="home",
            title=f"Presence : {saved.user_name}",
            message=build_presence_message(saved, profile),
        )
    )
    return saved


@app.get("/presence/summary")
def presence_summary() -> dict[str, object]:
    signals = store.list_presence_signals(12)
    active = [item for item in signals if item.proximity != "away"]
    names = []
    for signal in active:
        if signal.user_name not in names:
            names.append(signal.user_name)
    return {
        "active_count": len(names),
        "message": build_presence_summary(signals),
        "present_users": names[:8],
        "signals": [item.model_dump() for item in signals],
    }


@app.get("/health/reminders", response_model=list[HealthReminder])
def health_reminders(active_only: bool = False) -> list[HealthReminder]:
    return store.list_health_reminders(active_only=active_only)


@app.post("/health/reminders", response_model=HealthReminder)
def add_health_reminder(reminder: HealthReminder) -> HealthReminder:
    saved = store.add_health_reminder(reminder)
    store.add_event(f"Rappel sante ajoute : {saved.title} a {saved.schedule_time}")
    nest_hub.update(
        NestHubUpdate(
            screen="health",
            title="Rappel sante",
            message=f"{saved.title} a {saved.schedule_time}",
        )
    )
    return saved


@app.post("/health/reminders/{reminder_id}/done", response_model=HealthReminder | None)
def mark_health_reminder_done(reminder_id: int) -> HealthReminder | None:
    saved = store.mark_health_reminder_done(reminder_id)
    if saved is not None:
        store.add_event(f"Rappel sante termine : {saved.title}")
    return saved


@app.get("/health/checkins", response_model=list[WellbeingCheckIn])
def wellbeing_checkins() -> list[WellbeingCheckIn]:
    return store.list_wellbeing_checkins()


@app.post("/health/checkins", response_model=WellbeingCheckIn)
def add_wellbeing_checkin(checkin: WellbeingCheckIn) -> WellbeingCheckIn:
    saved = store.add_wellbeing_checkin(checkin)
    store.add_event(f"Check-in bien-etre : {saved.user} risque {saved.risk_level}")
    if saved.risk_level == "high":
        alert = store.add_alert(
            SmartAlert(
                severity="warning",
                title="Fatigue ou stress eleve",
                message=saved.recommendation,
                source="wellbeing",
                kind="health",
                recommended_routine="wellbeing",
            )
        )
        nest_hub.alert(alert)
    else:
        nest_hub.update(
            NestHubUpdate(
                screen="health",
                title=f"Bien-etre {saved.user}",
                message=saved.recommendation,
            )
        )
    return saved


@app.get("/health/summary")
def health_summary() -> dict[str, object]:
    reminders = store.list_health_reminders(active_only=True)
    pending = [item for item in reminders if item.last_done_at is None]
    checkins = store.list_wellbeing_checkins(10)
    return {
        "active_count": len(reminders),
        "pending_count": len(pending),
        "message": build_health_summary(reminders, checkins),
        "reminders": [item.model_dump() for item in reminders],
        "checkins": [item.model_dump() for item in checkins],
        "anomalies": [item.model_dump() for item in store.list_behavior_anomalies(10)],
    }


@app.get("/health/anomalies", response_model=list[BehaviorAnomaly])
def behavior_anomalies(include_acknowledged: bool = False) -> list[BehaviorAnomaly]:
    return store.list_behavior_anomalies(include_acknowledged=include_acknowledged)


@app.post("/health/anomalies/analyze", response_model=BehaviorAnomaly)
def analyze_behavior_anomalies() -> BehaviorAnomaly:
    anomaly = build_behavior_anomaly()
    saved = store.add_behavior_anomaly(anomaly)
    store.add_event(f"Analyse comportement : {saved.risk_level} ({saved.risk_score})")
    if saved.risk_level in {"medium", "high"}:
        store.add_notification(
            CompanionNotification(
                title="Comportement inhabituel",
                message=saved.summary,
                priority="urgent" if saved.risk_level == "high" else "high",
                source="health.anomaly",
                action_hint="wellbeing",
            )
        )
        nest_hub.update(
            NestHubUpdate(
                screen="health",
                title="Comportement a surveiller",
                message=saved.recommendation,
            )
        )
    return saved


@app.post("/health/anomalies/{anomaly_id}/ack")
def acknowledge_behavior_anomaly(anomaly_id: int) -> dict[str, bool]:
    acknowledged = store.acknowledge_behavior_anomaly(anomaly_id)
    if acknowledged:
        store.add_event(f"Anomalie comportement {anomaly_id} acquittee.")
    return {"acknowledged": acknowledged}


@app.get("/calendar/events", response_model=list[CalendarEvent])
def calendar_events(include_done: bool = False) -> list[CalendarEvent]:
    return store.list_calendar_events(include_done=include_done)


@app.post("/calendar/events", response_model=CalendarEvent)
def add_calendar_event(event: CalendarEvent) -> CalendarEvent:
    saved = store.add_calendar_event(event)
    store.add_event(f"Agenda ajoute : {saved.title} a {saved.starts_at}")
    nest_hub.update(
        NestHubUpdate(
            screen="home",
            title="Agenda familial",
            message=calendar_event_line(saved),
        )
    )
    return saved


@app.post("/calendar/events/{event_id}/done", response_model=CalendarEvent | None)
def mark_calendar_event_done(event_id: int) -> CalendarEvent | None:
    saved = store.mark_calendar_event_done(event_id)
    if saved is not None:
        store.add_event(f"Agenda termine : {saved.title}")
    return saved


@app.get("/environment/snapshots", response_model=list[EnvironmentalSnapshot])
def environmental_snapshots() -> list[EnvironmentalSnapshot]:
    return store.list_environmental_snapshots()


@app.post("/environment/snapshots", response_model=EnvironmentalSnapshot)
def add_environmental_snapshot(snapshot: EnvironmentalSnapshot) -> EnvironmentalSnapshot:
    saved = store.add_environmental_snapshot(snapshot)
    store.add_event(f"Ambiance {saved.room}: {saved.recommendation}")
    nest_hub.update(
        NestHubUpdate(
            screen="home",
            title=f"Ambiance {saved.room}",
            message=saved.recommendation,
        )
    )
    return saved


@app.get("/environment/comfort")
def environment_comfort() -> dict[str, object]:
    snapshots = store.list_environmental_snapshots(12)
    return {
        "message": build_environment_summary(snapshots),
        "snapshots": [item.model_dump() for item in snapshots],
    }


@app.get("/energy/readings", response_model=list[EnergyReading])
def energy_readings() -> list[EnergyReading]:
    return store.list_energy_readings()


@app.post("/energy/readings", response_model=EnergyReading)
def add_energy_reading(reading: EnergyReading) -> EnergyReading:
    saved = store.add_energy_reading(reading)
    store.add_event(f"Energie {saved.zone}: {saved.kwh:g} kWh. {saved.recommendation}")
    return saved


@app.get("/energy/summary")
def energy_summary() -> dict[str, object]:
    readings = store.list_energy_readings(12)
    return {
        "message": build_energy_summary(readings),
        "readings": [item.model_dump() for item in readings],
    }


@app.get("/brief/daily", response_model=DailyBrief)
def daily_brief_get() -> DailyBrief:
    return build_daily_brief(ContextSignal())


@app.post("/brief/daily", response_model=DailyBrief)
def daily_brief(context: ContextSignal) -> DailyBrief:
    brief = build_daily_brief(context)
    store.add_event("Brief quotidien genere.")
    nest_hub.update(
        NestHubUpdate(
            screen="home",
            title=brief.title,
            message=brief.summary,
        )
    )
    return brief


@app.get("/kitchen/items", response_model=list[KitchenItem])
def kitchen_items() -> list[KitchenItem]:
    return store.list_kitchen_items()


@app.post("/kitchen/items", response_model=KitchenItem)
def add_kitchen_item(item: KitchenItem) -> KitchenItem:
    saved = store.add_kitchen_item(item)
    store.add_event(f"Aliment ajoute : {saved.name} ({saved.quantity})")
    nest_hub.update(
        NestHubUpdate(
            screen="kitchen",
            title="Cuisine intelligente",
            message=f"{saved.name} ajoute au frigo.",
        )
    )
    return saved


@app.delete("/kitchen/items/{item_id}")
def remove_kitchen_item(item_id: int) -> dict[str, bool]:
    removed = store.remove_kitchen_item(item_id)
    if removed:
        store.add_event(f"Aliment retire : {item_id}")
    return {"removed": removed}


@app.get("/kitchen/summary")
def kitchen_summary() -> dict[str, object]:
    items = store.list_kitchen_items()
    expiring = [item for item in items if item.expires_at and days_until(item.expires_at) <= 3]
    missing = build_shopping_list(items)
    return {
        "message": build_kitchen_summary(items, expiring, missing),
        "items": [item.model_dump() for item in items],
        "expiring": [item.model_dump() for item in expiring],
        "shopping_list": missing,
        "recipe": suggest_recipe(items),
    }


@app.get("/kitchen/shopping-list")
def kitchen_shopping_list() -> dict[str, object]:
    items = store.list_kitchen_items()
    return {"items": build_shopping_list(items)}


@app.get("/devices", response_model=list[SmartDevice])
def smart_devices() -> list[SmartDevice]:
    return store.list_smart_devices()


@app.post("/devices", response_model=SmartDevice)
def add_smart_device(device: SmartDevice) -> SmartDevice:
    saved = store.add_smart_device(device)
    store.add_event(f"Appareil ajoute : {saved.name} ({saved.room})")
    return saved


@app.post("/devices/{device_id}/command", response_model=SmartDevice | None)
def command_smart_device(device_id: int, command: DeviceCommand) -> SmartDevice | None:
    saved = store.command_smart_device(device_id, command)
    if saved is not None:
        action = RoutineAction(
            id=f"device_{device_id}_{command.command}",
            label=f"{saved.name} {command.command}",
            target=device_target(saved),
            payload=device_payload(saved, command),
        )
        result = ActionExecutor(integrations.load()).execute(action)
        store.add_event(f"Appareil {saved.name} -> {saved.state} ({result.status})")
    return saved


@app.get("/car/reminders", response_model=list[CarReminder])
def car_reminders(include_done: bool = False) -> list[CarReminder]:
    return store.list_car_reminders(include_done=include_done)


@app.post("/car/reminders", response_model=CarReminder)
def add_car_reminder(reminder: CarReminder) -> CarReminder:
    saved = store.add_car_reminder(reminder)
    store.add_event(f"Rappel voiture ajoute : {saved.title}")
    nest_hub.update(
        NestHubUpdate(
            screen="car",
            title="Assistant voiture",
            message=build_car_line(saved),
        )
    )
    return saved


@app.post("/car/reminders/{reminder_id}/done", response_model=CarReminder | None)
def mark_car_reminder_done(reminder_id: int) -> CarReminder | None:
    saved = store.mark_car_reminder_done(reminder_id)
    if saved is not None:
        store.add_event(f"Rappel voiture termine : {saved.title}")
    return saved


@app.get("/car/summary")
def car_summary() -> dict[str, object]:
    reminders = store.list_car_reminders()
    priority = sorted(reminders, key=car_priority)
    return {
        "message": build_car_summary(priority),
        "reminders": [item.model_dump() for item in priority],
        "trip": build_trip_advice(ContextSignal(location="voiture")),
    }


@app.post("/car/trip")
def car_trip(context: ContextSignal) -> dict[str, str]:
    advice = build_trip_advice(context)
    store.add_event(f"Trajet voiture prepare : {advice}")
    return {"advice": advice}


@app.get("/routines/custom", response_model=list[CustomRoutine])
def custom_routines(enabled_only: bool = False) -> list[CustomRoutine]:
    return store.list_custom_routines(enabled_only=enabled_only)


@app.post("/routines/custom", response_model=CustomRoutine)
def add_custom_routine(routine: CustomRoutine) -> CustomRoutine:
    saved = store.add_custom_routine(routine)
    store.add_event(f"Scenario personnalise ajoute : {saved.name}")
    return saved


@app.post("/routines/custom/{routine_id}/enabled", response_model=CustomRoutine | None)
def set_custom_routine_enabled(routine_id: int, enabled: bool = True) -> CustomRoutine | None:
    saved = store.set_custom_routine_enabled(routine_id, enabled)
    if saved is not None:
        store.add_event(f"Scenario {saved.name} {'active' if saved.enabled else 'desactive'}")
    return saved


@app.post("/routines/custom/{routine_id_or_name}/execute", response_model=list[ActionExecutionResult])
def execute_custom_routine(routine_id_or_name: str) -> list[ActionExecutionResult]:
    routine = store.find_custom_routine(routine_id_or_name)
    if routine is None or not routine.enabled:
        return []
    results = ActionExecutor(integrations.load()).execute_many(routine.actions)
    store.update_devices_for_actions(routine.actions)
    store.add_event(f"Scenario personnalise execute : {routine.name} ({len(results)} action(s))")
    return results


@app.get("/automations/learned", response_model=list[LearnedAutomation])
def learned_automations(enabled_only: bool = False) -> list[LearnedAutomation]:
    return store.list_learned_automations(enabled_only=enabled_only)


@app.get("/automations/proposals", response_model=list[AutomationProposal])
def automation_proposals(status: str = "proposed") -> list[AutomationProposal]:
    return store.list_automation_proposals(status=status)


@app.post("/automations/propose", response_model=list[AutomationProposal])
def propose_automations(context: ContextSignal) -> list[AutomationProposal]:
    proposals = build_automation_proposals(context)
    saved = [store.add_automation_proposal(proposal) for proposal in proposals]
    if saved:
        store.add_event(f"{len(saved)} proposition(s) automation creee(s)")
    return saved


@app.post("/automations/proposals/{proposal_id}/accept", response_model=LearnedAutomation | None)
def accept_automation_proposal(proposal_id: int) -> LearnedAutomation | None:
    saved = store.accept_automation_proposal(proposal_id)
    if saved is not None:
        store.add_memory(
            f"Automatisation acceptee : {saved.name} quand {saved.trigger}={saved.trigger_value}.",
            "automation",
        )
        store.add_event(f"Proposition automation acceptee : {saved.name}")
    return saved


@app.post("/automations/proposals/{proposal_id}/dismiss")
def dismiss_automation_proposal(proposal_id: int) -> dict[str, bool]:
    dismissed = store.dismiss_automation_proposal(proposal_id)
    if dismissed:
        store.add_event(f"Proposition automation ignoree : {proposal_id}")
    return {"dismissed": dismissed}


@app.post("/automations/learned", response_model=LearnedAutomation)
def add_learned_automation(automation: LearnedAutomation) -> LearnedAutomation:
    saved = store.add_learned_automation(automation)
    store.add_memory(
        f"Automatisation apprise : {saved.name} quand {saved.trigger}={saved.trigger_value}.",
        "automation",
    )
    store.add_event(f"Automatisation apprise ajoutee : {saved.name}")
    return saved


@app.post("/automations/evaluate", response_model=CompanionDecision)
def evaluate_automations(context: ContextSignal) -> CompanionDecision:
    proposed = build_automation_proposals(context)
    for proposal in proposed:
        store.add_automation_proposal(proposal)
    return evaluate_learned_automations(context) or decision_from_insight(build_context_insight(context), context) or decide_from_context(context)


@app.post("/context/insight", response_model=ContextInsight)
def context_insight(context: ContextSignal) -> ContextInsight:
    insight = build_context_insight(context)
    store.add_event(f"Insight contexte : {insight.priority} ({insight.score})")
    return insight


@app.post("/routines/{routine_name}/execute", response_model=list[ActionExecutionResult])
def execute_routine(routine_name: str, context: ContextSignal | None = None) -> list[ActionExecutionResult]:
    aliases = {
        "evening": "comfort",
        "fridge": "kitchen",
        "medicine": "wellbeing",
        "hydration": "wellbeing",
        "away": "security",
        "senior": "security",
    }
    resolved_name = aliases.get(routine_name, routine_name)
    custom = store.find_custom_routine(resolved_name)
    if custom is not None:
        return execute_custom_routine(str(custom.id or custom.name))
    decision = build_routine(resolved_name, context or ContextSignal())
    results = ActionExecutor(integrations.load()).execute_many(decision.actions)
    store.update_devices_for_actions(decision.actions)
    store.add_event(f"Routine {routine_name} executee : {len(results)} action(s)")
    return results


@app.post("/actions/execute", response_model=list[ActionExecutionResult])
def execute_actions(request: ExecuteActionsRequest) -> list[ActionExecutionResult]:
    config = request.config or integrations.load()
    results = ActionExecutor(config).execute_many(request.actions)
    store.update_devices_for_actions(request.actions)
    store.add_event(f"Actions executees : {len(results)}")
    return results


@app.post("/sensors/events", response_model=SmartAlert | None)
def ingest_sensor_event(event: SensorEvent) -> SmartAlert | None:
    alert = analyze_sensor_event(event)
    store.add_event(f"Capteur {event.kind} depuis {event.source}: {event.value}")
    if alert is None:
        return None
    saved = store.add_alert(alert)
    nest_hub.alert(saved)
    if saved.severity == "critical":
        escalate_alert(saved)
    if saved.recommended_routine and saved.severity in {"warning", "critical"}:
        try:
            results = execute_routine(saved.recommended_routine)
            store.add_event(f"Alerte {saved.title}: routine {saved.recommended_routine} preparee ({len(results)} action(s))")
        except (KeyError, ValueError):
            store.add_event(f"Alerte {saved.title}: routine indisponible")
    return saved


@app.get("/vision/observations", response_model=list[VisionObservation])
def vision_observations() -> list[VisionObservation]:
    return store.list_vision_observations()


@app.post("/vision/observations", response_model=VisionObservation)
def add_vision_observation(observation: VisionObservation) -> VisionObservation:
    saved = store.add_vision_observation(observation)
    store.add_event(f"Vision {saved.room}: {saved.summary}")
    if saved.risk_level == "high":
        alert = store.add_alert(
            SmartAlert(
                severity="critical",
                title="Risque detecte par vision IA",
                message=saved.action_hint,
                source=saved.source,
                kind="camera",
                recommended_routine="security",
            )
        )
        nest_hub.alert(alert)
        escalate_alert(alert)
    elif saved.risk_level == "medium":
        alert = store.add_alert(
            SmartAlert(
                severity="warning",
                title="Vision IA a verifier",
                message=saved.action_hint,
                source=saved.source,
                kind="camera",
                recommended_routine="security",
            )
        )
        nest_hub.alert(alert)
    else:
        nest_hub.update(
            NestHubUpdate(
                screen="security",
                title="Vision IA locale",
                message=saved.summary,
            )
        )
    return saved


@app.get("/vision/summary")
def vision_summary() -> dict[str, object]:
    observations = store.list_vision_observations(12)
    if not observations:
        return {
            "message": "Aucune observation vision enregistree. Lancez une analyse camera, OCR ou frigo.",
            "observations": [],
        }
    latest = observations[0]
    return {
        "message": f"Derniere vision : {latest.summary} {latest.action_hint}",
        "observations": [item.model_dump() for item in observations],
    }


@app.get("/alerts", response_model=list[SmartAlert])
def alerts(include_acknowledged: bool = False) -> list[SmartAlert]:
    return store.list_alerts(include_acknowledged=include_acknowledged)


@app.post("/alerts/{alert_id}/ack")
def acknowledge_alert(alert_id: int) -> dict[str, bool]:
    acknowledged = store.acknowledge_alert(alert_id)
    if acknowledged:
        store.add_event(f"Alerte {alert_id} acquittee.")
    return {"acknowledged": acknowledged}


@app.get("/notifications", response_model=list[CompanionNotification])
def notifications(include_acknowledged: bool = False) -> list[CompanionNotification]:
    return store.list_notifications(include_acknowledged=include_acknowledged)


@app.post("/notifications/generate", response_model=list[CompanionNotification])
def generate_notifications() -> list[CompanionNotification]:
    generated = build_notifications()
    saved = [store.add_notification(item) for item in generated]
    if saved:
        store.add_event(f"{len(saved)} notification(s) IA generee(s).")
    return saved


@app.post("/notifications/{notification_id}/ack")
def acknowledge_notification(notification_id: int) -> dict[str, bool]:
    acknowledged = store.acknowledge_notification(notification_id)
    if acknowledged:
        store.add_event(f"Notification {notification_id} acquittee.")
    return {"acknowledged": acknowledged}


@app.get("/security/contacts", response_model=list[EmergencyContact])
def emergency_contacts(active_only: bool = False) -> list[EmergencyContact]:
    return store.list_emergency_contacts(active_only=active_only)


@app.post("/security/contacts", response_model=EmergencyContact)
def add_emergency_contact(contact: EmergencyContact) -> EmergencyContact:
    saved = store.add_emergency_contact(contact)
    store.add_event(f"Contact urgence ajoute : {saved.name}")
    return saved


@app.post("/security/alerts/{alert_id}/escalate", response_model=EscalationResult)
def escalate_alert_by_id(alert_id: int) -> EscalationResult:
    alert = next((item for item in store.list_alerts(include_acknowledged=True) if item.id == alert_id), None)
    if alert is None:
        return EscalationResult(alert_id=alert_id, alert_title="Alerte introuvable", message="Aucune alerte trouvee.")
    return escalate_alert(alert)


@app.get("/nest/state", response_model=NestHubState)
def nest_state() -> NestHubState:
    return nest_hub.load()


@app.post("/nest/screen", response_model=NestHubState)
def set_nest_screen(update: NestHubUpdate) -> NestHubState:
    state = nest_hub.update(update)
    store.add_event(f"Nest Hub -> {state.screen}: {state.title}")
    return state


@app.get("/nest/display", response_class=HTMLResponse)
def nest_display() -> HTMLResponse:
    return HTMLResponse(render_display(nest_hub.load()))


@app.get("/integrations/config", response_model=IntegrationConfig)
def get_integration_config() -> IntegrationConfig:
    config = integrations.load()
    updates: dict[str, str] = {}
    if config.home_assistant_token:
        updates["home_assistant_token"] = "***"
    if config.remote_access_token:
        updates["remote_access_token"] = "***"
    if updates:
        config = config.model_copy(update=updates)
    return config


@app.post("/integrations/config", response_model=IntegrationConfig)
def save_integration_config(config: IntegrationConfig) -> IntegrationConfig:
    current = integrations.load()
    if config.home_assistant_token == "***":
        config.home_assistant_token = current.home_assistant_token
    if config.remote_access_token == "***":
        config.remote_access_token = current.remote_access_token
    saved = integrations.save(config)
    store.add_event("Configuration maison connectee mise a jour.")
    updates: dict[str, str] = {}
    if saved.home_assistant_token:
        updates["home_assistant_token"] = "***"
    if saved.remote_access_token:
        updates["remote_access_token"] = "***"
    if updates:
        saved = saved.model_copy(update=updates)
    return saved


@app.get("/integrations/google-home/status", response_model=GoogleHomeStatus)
def google_home_status() -> GoogleHomeStatus:
    return build_google_home_status(integrations.load())


@app.get("/system/diagnostic", response_model=SystemDiagnostic)
def system_diagnostic() -> SystemDiagnostic:
    return build_system_diagnostic()


@app.get("/state", response_model=HubState)
def state() -> HubState:
    context = ContextSignal()
    insight = build_context_insight(context)
    decision = evaluate_learned_automations(context) or decision_from_insight(insight, context) or decide_from_context(context)
    return HubState(
        status="online",
        context=context,
        suggestion=decision,
        context_insight=insight,
        memories=store.list_memories(),
        user_profiles=store.list_user_profiles(),
        presence_signals=store.list_presence_signals(),
        family_moments=store.list_family_moments(),
        family_albums=store.list_family_albums(),
        health_reminders=store.list_health_reminders(),
        wellbeing_checkins=store.list_wellbeing_checkins(),
        behavior_anomalies=store.list_behavior_anomalies(),
        calendar_events=store.list_calendar_events(),
        environmental_snapshots=store.list_environmental_snapshots(),
        energy_readings=store.list_energy_readings(),
        kitchen_items=store.list_kitchen_items(),
        smart_devices=store.list_smart_devices(),
        car_reminders=store.list_car_reminders(),
        custom_routines=store.list_custom_routines(),
        learned_automations=store.list_learned_automations(),
        automation_proposals=store.list_automation_proposals(),
        vision_observations=store.list_vision_observations(),
        alerts=store.list_alerts(),
        notifications=store.list_notifications(),
        emergency_contacts=store.list_emergency_contacts(),
        nest_hub=nest_hub.load(),
        events=store.list_events(),
    )


@app.get("/privacy/audit")
def privacy_audit() -> dict[str, object]:
    counts = store.audit_counts()
    return {
        "mode": "local-first",
        "cloud_enabled": ai_config.load().enabled,
        "counts": counts,
        "total_records": sum(counts.values()),
    }


@app.get("/privacy/export")
def privacy_export() -> dict[str, object]:
    return {
        "app": "Companion Hub AI",
        "mode": "local-first",
        "exported_at": date.today().isoformat(),
        "data": store.export_data(),
    }


@app.post("/privacy/import")
def privacy_import(payload: dict[str, object], replace: bool = False) -> dict[str, object]:
    if replace:
        store.clear()
    data = payload.get("data", payload)
    if not isinstance(data, dict):
        return {"imported": {}, "total": 0, "replace": replace}
    imported = import_exported_data(data)
    total = sum(imported.values())
    store.add_event(f"Import local effectue : {total} element(s).")
    return {"imported": imported, "total": total, "replace": replace}


@app.delete("/privacy/sections/{section}")
def clear_privacy_section(section: str) -> dict[str, object]:
    deleted = store.clear_section(section)
    store.add_event(f"Section vie privee effacee : {section} ({deleted})")
    return {"section": section, "deleted": deleted}


@app.get("/memories", response_model=list[MemoryItem])
def memories() -> list[MemoryItem]:
    return store.list_memories()


@app.post("/memories", response_model=MemoryItem)
def add_memory(item: MemoryItem) -> MemoryItem:
    memory = store.add_memory(item.text, item.category)
    store.add_event(f"Memoire ajoutee : {memory.text}")
    return memory


@app.delete("/memories")
def clear_memories() -> dict[str, str]:
    store.clear()
    return {"status": "cleared"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json(state().model_dump())
    try:
        while True:
            payload = await websocket.receive_json()
            kind = payload.get("type")
            if kind == "command":
                request = CommandRequest(text=str(payload.get("text", "")))
                await websocket.send_json({"type": "decision", "data": command(request)})
            elif kind == "execute-routine":
                routine_name = str(payload.get("routine", "comfort"))
                await websocket.send_json({
                    "type": "execution",
                    "data": [item.model_dump() for item in execute_routine(routine_name)],
                })
            elif kind == "context":
                context = ContextSignal(**payload.get("context", {}))
                await websocket.send_json({"type": "state", "data": update_context(context).model_dump()})
            elif kind == "sensor-event":
                event = SensorEvent(**payload.get("event", {}))
                alert = ingest_sensor_event(event)
                await websocket.send_json({
                    "type": "alert",
                    "data": None if alert is None else alert.model_dump(),
                })
            elif kind == "vision-observation":
                observation = VisionObservation(**payload.get("observation", {}))
                await websocket.send_json({
                    "type": "vision",
                    "data": add_vision_observation(observation).model_dump(),
                })
            elif kind == "nest-screen":
                update = NestHubUpdate(**payload.get("screen", {}))
                await websocket.send_json({
                    "type": "nest",
                    "data": set_nest_screen(update).model_dump(),
                })
            elif kind == "health-reminders":
                await websocket.send_json({
                    "type": "health",
                    "data": health_summary(),
                })
            elif kind == "behavior-anomalies":
                await websocket.send_json({
                    "type": "behavior-anomaly",
                    "data": analyze_behavior_anomalies().model_dump(),
                })
            elif kind == "calendar-events":
                await websocket.send_json({
                    "type": "calendar",
                    "data": [item.model_dump() for item in calendar_events()],
                })
            elif kind == "environment":
                await websocket.send_json({
                    "type": "environment",
                    "data": environment_comfort(),
                })
            elif kind == "energy":
                await websocket.send_json({
                    "type": "energy",
                    "data": energy_summary(),
                })
            elif kind == "presence-events":
                await websocket.send_json({
                    "type": "presence",
                    "data": presence_summary(),
                })
            elif kind == "daily-brief":
                context = ContextSignal(**payload.get("context", {}))
                await websocket.send_json({
                    "type": "daily-brief",
                    "data": daily_brief(context).model_dump(),
                })
            elif kind == "vision-observations":
                await websocket.send_json({
                    "type": "vision-summary",
                    "data": vision_summary(),
                })
            elif kind == "kitchen-items":
                await websocket.send_json({
                    "type": "kitchen",
                    "data": kitchen_summary(),
                })
            elif kind == "devices":
                await websocket.send_json({
                    "type": "devices",
                    "data": [item.model_dump() for item in smart_devices()],
                })
            elif kind == "car-reminders":
                await websocket.send_json({
                    "type": "car",
                    "data": car_summary(),
                })
            elif kind == "custom-routines":
                await websocket.send_json({
                    "type": "custom-routines",
                    "data": [item.model_dump() for item in custom_routines()],
                })
            elif kind == "automation-evaluate":
                context = ContextSignal(**payload.get("context", {}))
                await websocket.send_json({
                    "type": "decision",
                    "data": evaluate_automations(context).model_dump(),
                })
            elif kind == "automation-proposals":
                context = ContextSignal(**payload.get("context", {}))
                await websocket.send_json({
                    "type": "automation-proposals",
                    "data": [item.model_dump() for item in propose_automations(context)],
                })
            elif kind == "user-profiles":
                await websocket.send_json({
                    "type": "users",
                    "data": [item.model_dump() for item in user_profiles()],
                })
            elif kind == "family-journal":
                await websocket.send_json({
                    "type": "family",
                    "data": family_journal(),
                })
            elif kind == "security-contacts":
                await websocket.send_json({
                    "type": "security-contacts",
                    "data": [item.model_dump() for item in emergency_contacts()],
                })
            elif kind == "notifications":
                await websocket.send_json({
                    "type": "notifications",
                    "data": [item.model_dump() for item in notifications()],
                })
            else:
                await websocket.send_json({"type": "state", "data": state().model_dump()})
    except WebSocketDisconnect:
        return


def build_daily_brief(context: ContextSignal) -> DailyBrief:
    insight = build_context_insight(context)
    agenda = store.list_calendar_events(6)
    reminders = store.list_health_reminders(active_only=True)
    checkins = store.list_wellbeing_checkins(3)
    kitchen_items = store.list_kitchen_items(30)
    car_items = sorted(store.list_car_reminders(10), key=car_priority)
    alerts = store.list_alerts(10)
    environment = store.list_environmental_snapshots(1)
    energy = store.list_energy_readings(1)

    priorities: list[str] = [insight.summary]
    if agenda:
        priorities.append(f"Agenda : {calendar_event_line(agenda[0])}")
    if reminders:
        priorities.append(f"Sante : {len(reminders)} rappel(s), prochain a {reminders[0].schedule_time}.")
    if environment:
        priorities.append(f"Ambiance : {environment[0].recommendation}")
    if energy:
        priorities.append(f"Energie : {energy[0].recommendation}")
    expiring = [item for item in kitchen_items if item.expires_at and days_until(item.expires_at) <= 3]
    if expiring:
        names = ", ".join(item.name for item in expiring[:3])
        priorities.append(f"Cuisine : consommer bientot {names}.")
    urgent_car = [item for item in car_items if item.due_date and days_until(item.due_date) <= 14]
    if urgent_car:
        priorities.append(f"Voiture : {build_car_line(urgent_car[0])}")
    active_alerts = [item for item in alerts if not item.acknowledged]
    if active_alerts:
        priorities.append(f"Securite : {active_alerts[0].title} a verifier.")
    if checkins:
        latest = checkins[0]
        if latest.risk_level in {"medium", "high"}:
            priorities.append(f"Bien-etre : {latest.recommendation}")

    if len(priorities) == 1 and insight.priority == "normal":
        priorities.append("Maison calme : surveillance locale active et aucune urgence detectee.")

    suggested_routine = insight.recommended_routine
    if suggested_routine is None and 6 <= context.hour < 11:
        suggested_routine = "morning"

    summary_parts = [f"{context.user}, {priorities[0]}"]
    if len(priorities) > 1:
        summary_parts.append("A retenir : " + " ".join(priorities[1:4]))
    if suggested_routine:
        summary_parts.append(f"Routine suggeree : {suggested_routine}.")

    return DailyBrief(
        summary=" ".join(summary_parts),
        agenda=agenda,
        priorities=priorities[:7],
        suggested_routine=suggested_routine,
    )


def build_notifications() -> list[CompanionNotification]:
    notifications: list[CompanionNotification] = []
    for alert in store.list_alerts(5):
        priority = "urgent" if alert.severity == "critical" else "high"
        notifications.append(
            CompanionNotification(
                title=alert.title,
                message=alert.message,
                priority=priority,
                source=f"alert:{alert.kind}",
                action_hint=alert.recommended_routine or "security",
            )
        )

    reminders = [item for item in store.list_health_reminders(active_only=True) if item.last_done_at is None]
    if reminders:
        notifications.append(
            CompanionNotification(
                title="Rappel sante",
                message=f"{reminders[0].title} prevu a {reminders[0].schedule_time}.",
                priority="high",
                source="health",
                action_hint="wellbeing",
            )
        )

    agenda = store.list_calendar_events(3)
    if agenda:
        notifications.append(
            CompanionNotification(
                title="Agenda a venir",
                message=calendar_event_line(agenda[0]),
                priority="normal",
                source="calendar",
                action_hint="daily_brief",
            )
        )

    expiring = [item for item in store.list_kitchen_items(30) if item.expires_at and days_until(item.expires_at) <= 2]
    if expiring:
        notifications.append(
            CompanionNotification(
                title="Cuisine a anticiper",
                message=f"{len(expiring)} aliment(s) a consommer bientot : {', '.join(item.name for item in expiring[:3])}.",
                priority="normal",
                source="kitchen",
                action_hint="kitchen",
            )
        )

    environment = store.list_environmental_snapshots(1)
    if environment and environment[0].recommendation:
        notifications.append(
            CompanionNotification(
                title=f"Ambiance {environment[0].room}",
                message=environment[0].recommendation,
                priority="normal" if environment[0].air_quality != "mauvaise" else "high",
                source="environment",
                action_hint="comfort",
            )
        )

    energy = store.list_energy_readings(1)
    if energy and energy[0].recommendation:
        notifications.append(
            CompanionNotification(
                title=f"Energie {energy[0].zone}",
                message=energy[0].recommendation,
                priority="high" if energy[0].kwh >= 20 or energy[0].mode == "peak" else "normal",
                source="energy",
                action_hint="eco",
            )
        )

    anomaly = next(iter(store.list_behavior_anomalies(1)), None)
    if anomaly and anomaly.risk_level in {"medium", "high"}:
        notifications.append(
            CompanionNotification(
                title="Comportement inhabituel",
                message=anomaly.summary,
                priority="urgent" if anomaly.risk_level == "high" else "high",
                source="health.anomaly",
                action_hint="wellbeing",
            )
        )

    proposals = store.list_automation_proposals(3)
    if proposals:
        notifications.append(
            CompanionNotification(
                title="Habitude a valider",
                message=f"{proposals[0].name} peut devenir automatique.",
                priority="normal",
                source="automation",
                action_hint="automations",
            )
        )

    urgent_car = [item for item in store.list_car_reminders(10) if item.due_date and days_until(item.due_date) <= 14]
    if urgent_car:
        notifications.append(
            CompanionNotification(
                title="Voiture a preparer",
                message=build_car_line(urgent_car[0]),
                priority="normal",
                source="car",
                action_hint="car",
            )
        )

    if not notifications:
        notifications.append(
            CompanionNotification(
                title="Maison stable",
                message="Aucune urgence detectee. Surveillance locale active.",
                priority="low",
                source="context",
                action_hint="observe",
            )
        )
    return notifications[:8]


def calendar_event_line(event: CalendarEvent) -> str:
    location = f" ({event.location})" if event.location else ""
    notes = f" - {event.notes}" if event.notes else ""
    return f"{event.title} a {event.starts_at}{location}{notes}"


def build_presence_summary(signals: list[PresenceSignal]) -> str:
    if not signals:
        return "Aucune presence recente. Le hub reste en affichage maison par defaut."
    active = [item for item in signals if item.proximity != "away"]
    if not active:
        return "Tout le monde semble absent. Mode surveillance et economie conseilles."
    names: list[str] = []
    rooms: list[str] = []
    for signal in active:
        if signal.user_name not in names:
            names.append(signal.user_name)
        if signal.room not in rooms:
            rooms.append(signal.room)
    return f"Presence detectee : {', '.join(names[:4])}. Zone active : {', '.join(rooms[:3])}."


def build_presence_message(signal: PresenceSignal, profile: UserProfile | None = None) -> str:
    light = f"Lumiere {profile.preferred_light}" if profile else "Profil en cours d'apprentissage"
    quiet = f", calme apres {profile.quiet_hours_start}" if profile else ""
    return f"{signal.user_name} detecte dans {signal.room}, proximite {signal.proximity}. {light}{quiet}."


def build_environment_summary(snapshots: list[EnvironmentalSnapshot]) -> str:
    if not snapshots:
        return "Aucun releve ambiance. Ajoutez temperature, humidite ou qualite d'air pour piloter le confort."
    latest = snapshots[0]
    details: list[str] = [f"{latest.room}"]
    if latest.temperature_c is not None:
        details.append(f"{latest.temperature_c:g} C")
    if latest.humidity_pct is not None:
        details.append(f"{latest.humidity_pct}% humidite")
    details.append(f"air {latest.air_quality}")
    details.append(f"bruit {latest.noise_level}")
    return "Ambiance " + ", ".join(details) + f". {latest.recommendation}"


def build_energy_summary(readings: list[EnergyReading]) -> str:
    if not readings:
        return "Aucun releve energie. Ajoutez une consommation pour piloter le mode eco."
    latest = readings[0]
    cost = f", {latest.cost_eur:.2f} EUR" if latest.cost_eur is not None else ""
    return f"Energie {latest.zone}: {latest.kwh:g} kWh{cost}, mode {latest.mode}. {latest.recommendation}"


def build_google_home_status(config: IntegrationConfig) -> GoogleHomeStatus:
    missing: list[str] = []
    if not config.google_home_enabled:
        missing.append("Activer Google Home dans les connecteurs.")
    if not config.google_home_project_id.strip():
        missing.append("Renseigner l'ID du projet Google Home Developer Console.")
    if not config.google_home_oauth_client_id.strip():
        missing.append("Renseigner le client OAuth Android lie au SHA-1 de l'app.")

    links = {
        "home_apis": "https://developers.home.google.com/apis/android/overview",
        "oauth_android": "https://developers.home.google.com/apis/android/oauth",
        "commissioning": "https://developers.home.google.com/apis/android/commissioning",
        "google_home_app": "https://home.google.com/",
    }
    activation_step = (
        "Relancer Companion Hub AI, activer Google Home et verifier que le mode reel est actif."
        if not config.dry_run
        else "Relancer Companion Hub AI, activer Google Home et garder le mode simulation pendant le test."
    )
    steps = [
        "Creer ou ouvrir un projet dans Google Home Developer Console.",
        "Ajouter un client OAuth Android avec le package de l'app et le SHA-1 de signature.",
        "Autoriser les Home APIs pour lire structures, pieces, appareils et automatisations.",
        activation_step,
        "Ajouter les appareils avec le connecteur Google Home et leur nom cible exact.",
    ]
    if config.dry_run:
        mode = "simulation"
        summary = "Google Home est prepare en simulation : aucune commande reelle ne sera envoyee."
    elif missing:
        mode = "oauth_needed"
        summary = "Google Home demande encore la configuration OAuth avant les commandes reelles."
    else:
        mode = "ready"
        summary = f"Google Home pret pour la structure {config.google_home_structure_name or 'Maison'}."
    if not config.google_home_enabled and missing:
        mode = "setup"
        summary = "Google Home n'est pas encore active dans Companion Hub AI."
    return GoogleHomeStatus(
        ready=not missing and not config.dry_run,
        mode=mode,  # type: ignore[arg-type]
        summary=summary,
        missing=missing,
        steps=steps,
        links=links,
    )


def should_require_remote_token(request: Request, config: IntegrationConfig) -> bool:
    if request.method == "OPTIONS":
        return False
    if not config.remote_access_enabled or not config.remote_access_token:
        return False
    if request.url.path in {"/health", "/remote/status"}:
        return False
    host = forwarded_client_ip(request) or (request.client.host if request.client else "")
    return not is_local_network_host(host)


def forwarded_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.headers.get("x-real-ip", "").strip()


def is_local_network_host(host: str) -> bool:
    if not host:
        return False
    if host in {"localhost", "::1"}:
        return True
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_loopback or ip.is_private or ip.is_link_local
    except ValueError:
        return host.endswith(".local")


def remote_access_message(config: IntegrationConfig) -> str:
    if not config.remote_access_enabled:
        return "Acces distant desactive. Activez-le puis utilisez une URL publique securisee."
    if not config.remote_public_url:
        return "Acces distant actif, mais aucune URL publique n'est configuree."
    if not config.remote_access_token:
        return "Ajoutez une cle secrete avant d'exposer Companion a Internet."
    if not build_google_home_status(config).ready:
        return "Acces distant securise, Google Home doit encore etre pret pour piloter la maison."
    return "Acces distant securise pret : l'app peut piloter la maison hors Wi-Fi."


def build_system_diagnostic() -> SystemDiagnostic:
    counts = store.audit_counts()
    config = integrations.load()
    ai = ai_config.load()
    nest = nest_hub.load()
    checks = {
        "backend_local": True,
        "memory_ready": counts.get("memories", 0) > 0,
        "profiles_ready": counts.get("user_profiles", 0) > 0,
        "presence_ready": counts.get("presence_signals", 0) > 0,
        "health_ready": counts.get("health_reminders", 0) > 0 or counts.get("wellbeing_checkins", 0) > 0,
        "security_ready": counts.get("alerts", 0) > 0 or counts.get("emergency_contacts", 0) > 0,
        "vision_ready": counts.get("vision_observations", 0) > 0,
        "home_ready": counts.get("smart_devices", 0) > 0,
        "automation_ready": counts.get("custom_routines", 0) > 0 or counts.get("learned_automations", 0) > 0,
        "brief_ready": counts.get("calendar_events", 0) > 0,
        "environment_ready": counts.get("environmental_snapshots", 0) > 0,
        "energy_ready": counts.get("energy_readings", 0) > 0,
        "nest_ready": bool(nest.updated_at),
        "privacy_ready": True,
        "cloud_controlled": not ai.enabled or ai.provider in {"local", "ollama"},
        "connector_configured": config.dry_run or bool(config.home_assistant_url or config.mqtt_host or config.google_home_enabled),
        "google_home_ready": build_google_home_status(config).ready or config.dry_run,
    }
    weights = {
        "backend_local": 8,
        "memory_ready": 6,
        "profiles_ready": 6,
        "presence_ready": 5,
        "health_ready": 7,
        "security_ready": 7,
        "vision_ready": 6,
        "home_ready": 7,
        "automation_ready": 8,
        "brief_ready": 5,
        "environment_ready": 5,
        "energy_ready": 4,
        "nest_ready": 6,
        "privacy_ready": 8,
        "cloud_controlled": 7,
        "connector_configured": 5,
        "google_home_ready": 5,
    }
    score = sum(weights[name] for name, ok in checks.items() if ok)
    issues: list[str] = []
    next_actions: list[str] = []
    if not checks["profiles_ready"]:
        issues.append("Aucun profil familial configure.")
        next_actions.append("Ajouter les profils famille avec preferences et heures calmes.")
    if not checks["home_ready"]:
        issues.append("Aucun appareil maison connectee enregistre.")
        next_actions.append("Ajouter lampes, chauffage, capteurs ou connecteurs Home Assistant/MQTT/Google Home.")
    if not checks["google_home_ready"]:
        issues.append("Google Home n'est pas encore pret pour les commandes reelles.")
        next_actions.append("Completer OAuth Google Home Android puis desactiver le mode simulation.")
    if not checks["security_ready"]:
        issues.append("Securite sans contact urgence ni alerte testee.")
        next_actions.append("Ajouter au moins un contact urgence et tester fumee/chute/fuite.")
    if not checks["automation_ready"]:
        issues.append("Aucun scenario personnalise ou automatisation apprise.")
        next_actions.append("Creer un scenario multi-actions et valider une proposition IA.")
    if not checks["vision_ready"]:
        next_actions.append("Ajouter une observation vision/OCR pour activer la memoire visuelle.")
    if not checks["energy_ready"]:
        next_actions.append("Ajouter un releve energie pour activer les conseils eco.")

    if score >= 90:
        status = "production"
    elif score >= 72:
        status = "strong"
    elif score >= 48:
        status = "ready"
    else:
        status = "setup"
    summary = f"Diagnostic local {status}: {score}% de preparation. {len(issues)} point(s) a corriger."
    return SystemDiagnostic(
        score=min(score, 100),
        status=status,
        summary=summary,
        checks=checks,
        issues=issues,
        next_actions=next_actions[:8],
    )


def import_exported_data(data: dict[str, object]) -> dict[str, int]:
    counts: dict[str, int] = {}

    def rows(name: str) -> list[dict[str, object]]:
        value = data.get(name, [])
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

    for item in rows("memories"):
        try:
            store.add_memory(str(item.get("text", "")), str(item.get("category", "preference")))
            counts["memories"] = counts.get("memories", 0) + 1
        except ValueError:
            continue

    for item in rows("user_profiles"):
        try:
            store.add_user_profile(UserProfile(**without_db_fields(item)))
            counts["user_profiles"] = counts.get("user_profiles", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("presence_signals"):
        try:
            store.add_presence_signal(PresenceSignal(**without_db_fields(item)))
            counts["presence_signals"] = counts.get("presence_signals", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("health_reminders"):
        try:
            store.add_health_reminder(HealthReminder(**without_db_fields(item)))
            counts["health_reminders"] = counts.get("health_reminders", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("wellbeing_checkins"):
        try:
            store.add_wellbeing_checkin(WellbeingCheckIn(**without_db_fields(item)))
            counts["wellbeing_checkins"] = counts.get("wellbeing_checkins", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("behavior_anomalies"):
        try:
            cleaned = without_db_fields(item)
            cleaned["signals"] = list_from_export(cleaned.get("signals", []))
            store.add_behavior_anomaly(BehaviorAnomaly(**cleaned))
            counts["behavior_anomalies"] = counts.get("behavior_anomalies", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("calendar_events"):
        try:
            store.add_calendar_event(CalendarEvent(**without_db_fields(item)))
            counts["calendar_events"] = counts.get("calendar_events", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("environmental_snapshots"):
        try:
            store.add_environmental_snapshot(EnvironmentalSnapshot(**without_db_fields(item)))
            counts["environmental_snapshots"] = counts.get("environmental_snapshots", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("energy_readings"):
        try:
            store.add_energy_reading(EnergyReading(**without_db_fields(item)))
            counts["energy_readings"] = counts.get("energy_readings", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("kitchen_items"):
        try:
            store.add_kitchen_item(KitchenItem(**without_db_fields(item)))
            counts["kitchen_items"] = counts.get("kitchen_items", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("smart_devices"):
        try:
            cleaned = without_db_fields(item)
            cleaned["metadata"] = object_from_export(cleaned.get("metadata", {}))
            store.add_smart_device(SmartDevice(**cleaned))
            counts["smart_devices"] = counts.get("smart_devices", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("car_reminders"):
        try:
            store.add_car_reminder(CarReminder(**without_db_fields(item)))
            counts["car_reminders"] = counts.get("car_reminders", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("custom_routines"):
        try:
            cleaned = without_db_fields(item)
            action_rows = object_from_export(cleaned.get("actions", {})).get("actions", cleaned.get("actions", []))
            cleaned["actions"] = [RoutineAction(**action) for action in action_rows if isinstance(action, dict)]
            store.add_custom_routine(CustomRoutine(**cleaned))
            counts["custom_routines"] = counts.get("custom_routines", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("learned_automations"):
        try:
            store.add_learned_automation(LearnedAutomation(**without_db_fields(item)))
            counts["learned_automations"] = counts.get("learned_automations", 0) + 1
        except (TypeError, ValueError):
            continue

    for item in rows("notifications"):
        try:
            store.add_notification(CompanionNotification(**without_db_fields(item)))
            counts["notifications"] = counts.get("notifications", 0) + 1
        except (TypeError, ValueError):
            continue

    return counts


def without_db_fields(item: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in item.items() if key not in {"id", "created_at", "last_seen_at", "last_done_at", "last_command_at", "trigger_count", "last_triggered_at"}}


def object_from_export(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            loaded = json.loads(value)
        except ValueError:
            return {}
        return loaded if isinstance(loaded, dict) else {}
    return {}


def list_from_export(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        try:
            loaded = json.loads(value)
        except ValueError:
            return []
        return [str(item) for item in loaded] if isinstance(loaded, list) else []
    return []


def build_behavior_anomaly() -> BehaviorAnomaly:
    score = 8
    signals: list[str] = []
    user = "Famille"

    latest_checkin = next(iter(store.list_wellbeing_checkins(1)), None)
    if latest_checkin:
        user = latest_checkin.user
        if latest_checkin.risk_level == "high":
            score += 38
            signals.append(f"bien-etre eleve: stress {latest_checkin.stress_level}, fatigue {latest_checkin.fatigue_level}")
        elif latest_checkin.risk_level == "medium":
            score += 22
            signals.append(f"bien-etre a surveiller: stress {latest_checkin.stress_level}, fatigue {latest_checkin.fatigue_level}")
        if latest_checkin.sleep_hours is not None and latest_checkin.sleep_hours < 5:
            score += 16
            signals.append(f"sommeil court: {latest_checkin.sleep_hours:g}h")

    presence = store.list_presence_signals(8)
    if presence:
        away_count = sum(1 for item in presence[:5] if item.proximity == "away")
        near_count = sum(1 for item in presence[:5] if item.proximity == "near")
        if away_count >= 3:
            score += 18
            signals.append("presence absente repetee")
        if near_count == 0 and away_count == 0:
            score += 10
            signals.append("presence faible ou lointaine")

    alerts = store.list_alerts(10)
    if any(item.kind == "fall" or "chute" in item.title.lower() for item in alerts):
        score += 44
        signals.append("alerte chute recente")
    if any(item.kind in {"smoke", "water"} for item in alerts):
        score += 16
        signals.append("alerte securite domestique active")

    if not signals:
        signals.append("aucun comportement inhabituel fort")
    score = min(score, 100)
    if score >= 70:
        level = "high"
        recommendation = "Verifier immediatement la personne, proposer appel proche et activer routine bien-etre/securite."
    elif score >= 40:
        level = "medium"
        recommendation = "Surveiller dans la journee, proposer hydratation, repos et contact familial si cela persiste."
    else:
        level = "low"
        recommendation = "Comportement stable. Continuer la surveillance douce locale."
    return BehaviorAnomaly(
        user=user,
        risk_level=level,
        risk_score=score,
        summary=f"Analyse comportement {user}: {', '.join(signals[:4])}.",
        recommendation=recommendation,
        signals=signals[:6],
    )


def build_health_summary(reminders: list[HealthReminder], checkins: list[WellbeingCheckIn] | None = None) -> str:
    checkins = checkins or []
    if checkins:
        latest = checkins[0]
        if latest.risk_level == "high":
            return f"Attention bien-etre : {latest.user} montre un stress ou une fatigue elevee. {latest.recommendation}"
        if latest.risk_level == "medium":
            return f"Bien-etre a surveiller pour {latest.user}. {latest.recommendation}"
    if not reminders:
        return "Aucun rappel sante actif. Les rappels medicaments, hydratation, sommeil et activite peuvent etre ajoutes localement."
    next_items = ", ".join(f"{item.title} ({item.schedule_time})" for item in reminders[:3])
    return f"{len(reminders)} rappel(s) actif(s). Prochains suivis : {next_items}."


def device_target(device: SmartDevice) -> str:
    if device.connector == "mqtt":
        return "mqtt.device"
    if device.connector == "google_home":
        return "google_home.device"
    if device.kind == "climate":
        return "home.heating"
    if device.kind == "media":
        return "nest.volume"
    if device.kind == "lock":
        return "home.lock"
    return "home.lights"


def device_payload(device: SmartDevice, command: DeviceCommand) -> dict[str, object]:
    payload: dict[str, object] = {"entity_id": device.target} if device.target else {}
    if command.value is not None:
        if device.kind == "climate":
            payload["temperature"] = command.value
        else:
            payload["value"] = command.value
    if device.connector == "mqtt":
        payload["topic"] = device.target or device.name.lower().replace(" ", "_")
        payload["command"] = command.command
    if device.connector == "google_home":
        payload["device_name"] = device.target or device.name
        payload["room"] = device.room
        payload["kind"] = device.kind
        payload["command"] = command.command
    return payload


def build_context_insight(context: ContextSignal) -> ContextInsight:
    signals: list[str] = []
    score = 10
    priority = "normal"
    title = "Maison stable"
    routine: str | None = None

    active_alerts = store.list_alerts(10)
    critical_alerts = [item for item in active_alerts if item.severity == "critical"]
    warning_alerts = [item for item in active_alerts if item.severity == "warning"]
    if critical_alerts:
        priority = "security"
        title = "Securite prioritaire"
        routine = "security"
        score += 55
        signals.append(f"{len(critical_alerts)} alerte(s) critique(s) active(s)")
    elif warning_alerts:
        priority = "security"
        title = "Verification conseillee"
        routine = "security"
        score += 30
        signals.append(f"{len(warning_alerts)} alerte(s) a verifier")

    latest_wellbeing = next(iter(store.list_wellbeing_checkins(1)), None)
    if latest_wellbeing and latest_wellbeing.risk_level in {"medium", "high"}:
        if priority == "normal" or latest_wellbeing.risk_level == "high":
            priority = "health"
            title = "Bien-etre a accompagner"
            routine = "wellbeing"
        score += 18 if latest_wellbeing.risk_level == "medium" else 34
        signals.append(f"{latest_wellbeing.user}: stress {latest_wellbeing.stress_level}, fatigue {latest_wellbeing.fatigue_level}")

    latest_vision = next(iter(store.list_vision_observations(1)), None)
    if latest_vision and latest_vision.risk_level in {"medium", "high"}:
        if priority in {"normal", "comfort"} or latest_vision.risk_level == "high":
            priority = "security"
            title = "Vision IA a traiter"
            routine = "security"
        score += 16 if latest_vision.risk_level == "medium" else 34
        signals.append(f"Vision {latest_vision.room}: {latest_vision.risk_level}")

    expiring = [item for item in store.list_kitchen_items(30) if item.expires_at and days_until(item.expires_at) <= 2]
    if expiring:
        if priority == "normal":
            priority = "kitchen"
            title = "Cuisine a anticiper"
            routine = "kitchen"
        score += min(14, len(expiring) * 4)
        signals.append(f"{len(expiring)} aliment(s) a consommer bientot")

    urgent_car = [item for item in store.list_car_reminders(20) if item.due_date and days_until(item.due_date) <= 14]
    if urgent_car:
        if priority == "normal":
            priority = "car"
            title = "Voiture a preparer"
            routine = "car"
        score += min(12, len(urgent_car) * 4)
        signals.append(f"{len(urgent_car)} rappel(s) vehicule proche(s)")

    latest_environment = next(iter(store.list_environmental_snapshots(1)), None)
    if latest_environment:
        if latest_environment.air_quality == "mauvaise" or latest_environment.noise_level == "bruyant":
            if priority == "normal":
                priority = "comfort"
                title = "Ambiance a ajuster"
                routine = "comfort"
            score += 12
            signals.append(latest_environment.recommendation)
        elif latest_environment.temperature_c is not None and (latest_environment.temperature_c < 18 or latest_environment.temperature_c > 26):
            if priority == "normal":
                priority = "comfort"
                title = "Confort thermique"
                routine = "comfort"
            score += 10
            signals.append(latest_environment.recommendation)

    if context.location == "maison" and context.weather in {"pluie", "orage"} and context.hour >= 18:
        if priority == "normal":
            priority = "comfort"
            title = "Retour pluie detecte"
            routine = "return_rain"
        score += 16
        signals.append("pluie en soiree")
    if context.fatigue == "elevee":
        if priority == "normal":
            priority = "comfort"
            title = "Fatigue detectee"
            routine = "comfort"
        score += 14
        signals.append("fatigue elevee")
    if context.calendar_next:
        score += 8
        signals.append(f"agenda: {context.calendar_next}")
    recent_presence = store.list_presence_signals(6)
    active_presence = [item for item in recent_presence if item.proximity != "away"]
    if active_presence:
        score += min(10, len({item.user_name for item in active_presence}) * 3)
        signals.append(build_presence_summary(active_presence))
    elif recent_presence and all(item.proximity == "away" for item in recent_presence[:3]):
        if priority == "normal":
            priority = "security"
            title = "Maison vide"
            routine = "security"
        score += 10
        signals.append("presence absente recente")
    if context.luminosity == "basse" and context.hour >= 20:
        score += 6
        signals.append("luminosite basse")

    if not signals:
        signals.append("aucun signal fort")

    summary = build_context_summary(priority, signals, routine)
    return ContextInsight(
        priority=priority,
        score=min(score, 100),
        title=title,
        summary=summary,
        signals=signals[:6],
        recommended_routine=routine,
    )


def decision_from_insight(insight: ContextInsight, context: ContextSignal) -> CompanionDecision | None:
    if not insight.recommended_routine or insight.score < 38:
        return None
    try:
        decision = build_routine(insight.recommended_routine, context)
    except KeyError:
        return None
    decision.intent = f"context.{insight.priority}"
    decision.answer = f"{insight.title}. {insight.summary}"
    decision.confidence = max(decision.confidence, min(0.96, insight.score / 100))
    return decision


def build_context_summary(priority: str, signals: list[str], routine: str | None) -> str:
    joined = ", ".join(signals[:3])
    if priority == "security":
        return f"Signal securite prioritaire : {joined}. Routine securite conseillee."
    if priority == "health":
        return f"Signal bien-etre prioritaire : {joined}. Routine douce conseillee."
    if priority == "kitchen":
        return f"Cuisine a anticiper : {joined}. Verifier frigo et courses."
    if priority == "car":
        return f"Vehicule a anticiper : {joined}. Preparer le trajet ou le rappel."
    if priority == "comfort":
        return f"Confort recommande : {joined}. Routine {routine or 'confort'} disponible."
    return "Contexte calme : surveillance locale active, aucune action urgente."


def escalate_alert(alert: SmartAlert) -> EscalationResult:
    contacts = [
        contact
        for contact in store.list_emergency_contacts(active_only=True)
        if alert.severity in contact.notify_on or alert.kind in contact.notify_on or "all" in contact.notify_on
    ]
    message = f"Escalade simulee pour {alert.title}: {len(contacts)} contact(s) prioritaire(s)."
    store.add_event(message)
    return EscalationResult(
        alert_id=alert.id,
        alert_title=alert.title,
        contacts=contacts,
        message=message,
        simulated=True,
    )


def days_until(value: str) -> int:
    try:
        target = date.fromisoformat(value)
    except ValueError:
        return 9999
    return (target - date.today()).days


def build_shopping_list(items: list[KitchenItem]) -> list[str]:
    present = {item.name.strip().lower() for item in items}
    basics = {
        "oeufs": "Proteines rapides",
        "lait": "Petit-dejeuner et recettes",
        "yaourt": "Collation",
        "salade": "Repas leger",
        "pain": "Base repas",
    }
    missing = [f"{name} - {reason}" for name, reason in basics.items() if name not in present]
    expired = [item.name for item in items if item.expires_at and days_until(item.expires_at) < 0]
    missing.extend(f"Remplacer {name}" for name in expired[:3])
    return missing[:8]


def build_kitchen_summary(items: list[KitchenItem], expiring: list[KitchenItem], missing: list[str]) -> str:
    if not items:
        return "Inventaire vide. Ajoutez les aliments ou lancez le scan frigo pour creer la liste de courses."
    if expiring:
        names = ", ".join(item.name for item in expiring[:3])
        return f"{len(items)} aliment(s) suivis. A consommer bientot : {names}."
    if missing:
        return f"{len(items)} aliment(s) suivis. Courses suggerees : {missing[0]}."
    return f"{len(items)} aliment(s) suivis. La cuisine est a jour."


def suggest_recipe(items: list[KitchenItem]) -> str:
    names = {item.name.lower() for item in items}
    if {"oeufs", "salade"} <= names:
        return "Omelette rapide avec salade."
    if {"yaourt", "lait"} & names:
        return "Petit-dejeuner doux avec yaourt, fruit et boisson chaude."
    if not items:
        return "Ajoutez quelques aliments pour obtenir une suggestion."
    first = ", ".join(item.name for item in items[:3])
    return f"Repas simple autour de : {first}."


def car_priority(reminder: CarReminder) -> tuple[int, str]:
    if reminder.due_date:
        days = days_until(reminder.due_date)
        if days < 0:
            return (0, reminder.due_date)
        if days <= 14:
            return (1, reminder.due_date)
        return (2, reminder.due_date)
    if reminder.kind in {"insurance", "inspection"}:
        return (3, "")
    return (4, "")


def build_car_line(reminder: CarReminder) -> str:
    due = f" avant {reminder.due_date}" if reminder.due_date else ""
    mileage = f" a {reminder.mileage_km} km" if reminder.mileage_km is not None else ""
    return f"{reminder.title}{due}{mileage}."


def build_car_summary(reminders: list[CarReminder]) -> str:
    if not reminders:
        return "Aucun rappel vehicule actif. Ajoutez controle technique, assurance, carburant ou maintenance."
    urgent = [item for item in reminders if item.due_date and days_until(item.due_date) <= 14]
    if urgent:
        names = ", ".join(item.title for item in urgent[:3])
        return f"{len(reminders)} rappel(s) vehicule. Priorite proche : {names}."
    return f"{len(reminders)} rappel(s) vehicule actif(s). Prochain suivi : {build_car_line(reminders[0])}"


def build_trip_advice(context: ContextSignal) -> str:
    parts = ["Verifier carburant et autonomie avant depart"]
    if "pluie" in context.weather.lower():
        parts.append("prevoir trajet plus prudent car pluie detectee")
    if context.hour in range(7, 10) or context.hour in range(17, 20):
        parts.append("trafic probable aux heures de pointe")
    if context.calendar_next:
        parts.append(f"prochain rendez-vous : {context.calendar_next}")
    return ". ".join(parts) + "."


def build_automation_proposals(context: ContextSignal) -> list[AutomationProposal]:
    proposals: list[AutomationProposal] = []
    insight = build_context_insight(context)
    if insight.recommended_routine and insight.score >= 38:
        trigger, trigger_value = proposal_trigger_from_context(context, insight)
        proposals.append(
            AutomationProposal(
                name=f"{insight.title} automatique",
                trigger=trigger,
                trigger_value=trigger_value,
                routine=insight.recommended_routine,
                confidence=min(0.9, max(0.62, insight.score / 100)),
                reason=insight.summary,
            )
        )

    latest_wellbeing = next(iter(store.list_wellbeing_checkins(1)), None)
    if latest_wellbeing and latest_wellbeing.risk_level in {"medium", "high"}:
        proposals.append(
            AutomationProposal(
                name=f"Routine bien-etre pour {latest_wellbeing.user}",
                trigger="fatigue",
                trigger_value="elevee",
                routine="wellbeing",
                confidence=0.78 if latest_wellbeing.risk_level == "high" else 0.68,
                reason=latest_wellbeing.recommendation,
            )
        )

    expiring = [item for item in store.list_kitchen_items(20) if item.expires_at and days_until(item.expires_at) <= 2]
    if expiring:
        proposals.append(
            AutomationProposal(
                name="Verifier frigo avant courses",
                trigger="time",
                trigger_value="18",
                routine="kitchen",
                confidence=0.7,
                reason=f"{len(expiring)} aliment(s) arrivent a expiration.",
            )
        )

    devices = store.list_smart_devices(20)
    if any(device.kind == "light" and device.state in {"warm", "on"} for device in devices) and context.hour >= 21:
        proposals.append(
            AutomationProposal(
                name="Lumiere chaude le soir",
                trigger="time",
                trigger_value=str(context.hour),
                routine="comfort",
                confidence=0.66,
                reason="Lumiere active tard le soir, proposition de confort automatique.",
            )
        )
    return dedupe_proposals(proposals)


def proposal_trigger_from_context(context: ContextSignal, insight: ContextInsight) -> tuple[str, str]:
    if insight.priority == "comfort" and context.weather in {"pluie", "orage"}:
        return ("weather", context.weather)
    if insight.priority == "health":
        return ("fatigue", "elevee")
    if insight.priority == "security":
        return ("presence", str(max(1, context.presence_count)))
    if insight.priority == "car":
        return ("location", "voiture")
    if insight.priority == "kitchen":
        return ("time", str(context.hour))
    return ("time", str(context.hour))


def dedupe_proposals(proposals: list[AutomationProposal]) -> list[AutomationProposal]:
    seen: set[tuple[str, str, str]] = set()
    result: list[AutomationProposal] = []
    for proposal in proposals:
        key = (proposal.trigger, proposal.trigger_value, proposal.routine)
        if key in seen:
            continue
        seen.add(key)
        result.append(proposal)
    return result[:5]


def evaluate_learned_automations(context: ContextSignal) -> CompanionDecision | None:
    matches: list[LearnedAutomation] = []
    for automation in store.list_learned_automations(enabled_only=True):
        if automation_matches_context(automation, context):
            matches.append(automation)
    if not matches:
        return None
    best = sorted(matches, key=lambda item: (item.confidence, item.trigger_count), reverse=True)[0]
    store.record_automation_trigger(best.id or 0)
    try:
        routine = build_routine(best.routine, context)
    except KeyError:
        routine = CompanionDecision(
            intent="automation.learned",
            routine=best.routine,
            answer=f"Automatisation apprise detectee : {best.name}.",
            confidence=best.confidence,
        )
    routine.intent = "automation.learned"
    routine.answer = f"Habitude detectee : {best.name}. {routine.answer}"
    routine.confidence = max(routine.confidence, best.confidence)
    return routine


def automation_matches_context(automation: LearnedAutomation, context: ContextSignal) -> bool:
    value = automation.trigger_value.strip().lower()
    if automation.trigger == "time":
        try:
            return context.hour == int(value)
        except ValueError:
            return False
    if automation.trigger == "weather":
        return value in context.weather.lower()
    if automation.trigger == "fatigue":
        return value == context.fatigue
    if automation.trigger == "location":
        return value == context.location
    if automation.trigger == "presence":
        try:
            return context.presence_count >= int(value)
        except ValueError:
            return False
    return False
