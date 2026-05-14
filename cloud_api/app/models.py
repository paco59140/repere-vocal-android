from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ContextSignal(BaseModel):
    user: str = "Anthony"
    hour: int = Field(default_factory=lambda: datetime.now().hour, ge=0, le=23)
    weather: str = "calme"
    presence_count: int = Field(default=1, ge=0, le=20)
    luminosity: Literal["basse", "normale", "forte"] = "normale"
    fatigue: Literal["faible", "normale", "elevee"] = "normale"
    location: Literal["maison", "dehors", "voiture", "inconnue"] = "maison"
    calendar_next: str = ""


class MemoryItem(BaseModel):
    id: int | None = None
    text: str
    category: str = "preference"
    created_at: str | None = None


class FamilyMoment(BaseModel):
    id: int | None = None
    title: str
    description: str
    people: list[str] = Field(default_factory=list)
    mood: str = "doux"
    occurred_at: str | None = None
    summary: str | None = None
    created_at: str | None = None


class FamilyAlbum(BaseModel):
    id: int | None = None
    title: str = "Album familial"
    theme: str = "souvenirs"
    people: list[str] = Field(default_factory=list)
    moment_ids: list[int] = Field(default_factory=list)
    narration: str = ""
    cover_hint: str = ""
    created_at: str | None = None


class UserProfile(BaseModel):
    id: int | None = None
    name: str
    role: str = "famille"
    voice_label: str = ""
    preferred_light: Literal["chaude", "neutre", "froide"] = "chaude"
    quiet_hours_start: str = "21:00"
    notes: str = ""
    last_seen_at: str | None = None
    created_at: str | None = None


class PresenceSignal(BaseModel):
    id: int | None = None
    user_profile_id: int | None = None
    user_name: str = "Inconnu"
    room: str = "maison"
    proximity: Literal["near", "mid", "far", "away"] = "near"
    source: Literal["manual", "voice", "camera", "bluetooth", "wifi", "nest"] = "manual"
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    created_at: str | None = None


class HealthReminder(BaseModel):
    id: int | None = None
    kind: Literal["medicine", "hydration", "sleep", "activity", "care"] = "medicine"
    title: str
    schedule_time: str = "09:00"
    notes: str = ""
    active: bool = True
    last_done_at: str | None = None
    created_at: str | None = None


class WellbeingCheckIn(BaseModel):
    id: int | None = None
    user: str = "Anthony"
    mood: Literal["calme", "joyeux", "neutre", "stress", "triste", "fatigue"] = "neutre"
    stress_level: int = Field(default=3, ge=1, le=10)
    fatigue_level: int = Field(default=3, ge=1, le=10)
    sleep_hours: float | None = Field(default=None, ge=0.0, le=24.0)
    note: str = ""
    risk_level: Literal["low", "medium", "high"] = "low"
    recommendation: str = ""
    created_at: str | None = None


class BehaviorAnomaly(BaseModel):
    id: int | None = None
    user: str = "Famille"
    risk_level: Literal["low", "medium", "high"] = "low"
    risk_score: int = Field(default=0, ge=0, le=100)
    summary: str
    recommendation: str
    signals: list[str] = Field(default_factory=list)
    acknowledged: bool = False
    created_at: str | None = None


class CalendarEvent(BaseModel):
    id: int | None = None
    title: str
    starts_at: str
    location: str = ""
    notes: str = ""
    source: Literal["manual", "voice", "import", "calendar"] = "manual"
    done: bool = False
    created_at: str | None = None


class EnvironmentalSnapshot(BaseModel):
    id: int | None = None
    room: str = "maison"
    temperature_c: float | None = Field(default=None, ge=-20.0, le=60.0)
    humidity_pct: int | None = Field(default=None, ge=0, le=100)
    luminosity: Literal["basse", "normale", "forte"] = "normale"
    noise_level: Literal["calme", "normal", "bruyant"] = "calme"
    air_quality: Literal["bonne", "moyenne", "mauvaise"] = "bonne"
    source: Literal["manual", "sensor", "weather", "nest", "home_assistant"] = "manual"
    recommendation: str = ""
    created_at: str | None = None


class EnergyReading(BaseModel):
    id: int | None = None
    zone: str = "maison"
    kwh: float = Field(default=0.0, ge=0.0)
    cost_eur: float | None = Field(default=None, ge=0.0)
    mode: Literal["normal", "eco", "peak", "away"] = "normal"
    source: Literal["manual", "sensor", "home_assistant", "mqtt"] = "manual"
    recommendation: str = ""
    created_at: str | None = None


class KitchenItem(BaseModel):
    id: int | None = None
    name: str
    quantity: str = "1"
    category: str = "frigo"
    expires_at: str | None = None
    source: Literal["manual", "vision", "voice", "import"] = "manual"
    created_at: str | None = None


class CarReminder(BaseModel):
    id: int | None = None
    kind: Literal["maintenance", "fuel", "insurance", "inspection", "parking", "trip"] = "maintenance"
    title: str
    due_date: str | None = None
    mileage_km: int | None = Field(default=None, ge=0)
    notes: str = ""
    done: bool = False
    created_at: str | None = None


class LearnedAutomation(BaseModel):
    id: int | None = None
    name: str
    trigger: Literal["time", "weather", "fatigue", "presence", "location"] = "time"
    trigger_value: str
    routine: str
    confidence: float = Field(default=0.65, ge=0.0, le=1.0)
    enabled: bool = True
    last_triggered_at: str | None = None
    trigger_count: int = 0
    created_at: str | None = None


class AutomationProposal(BaseModel):
    id: int | None = None
    name: str
    trigger: Literal["time", "weather", "fatigue", "presence", "location"] = "time"
    trigger_value: str
    routine: str
    confidence: float = Field(default=0.62, ge=0.0, le=1.0)
    reason: str = ""
    status: Literal["proposed", "accepted", "dismissed"] = "proposed"
    created_at: str | None = None


class CommandRequest(BaseModel):
    text: str
    context: ContextSignal = Field(default_factory=ContextSignal)


class RoutineAction(BaseModel):
    id: str
    label: str
    target: str
    payload: dict[str, Any] = Field(default_factory=dict)
    requires_confirmation: bool = False


class ActionExecutionResult(BaseModel):
    action_id: str
    label: str
    target: str
    status: Literal["sent", "simulated", "skipped", "error"]
    detail: str


class IntegrationConfig(BaseModel):
    home_assistant_url: str = ""
    home_assistant_token: str = ""
    mqtt_host: str = ""
    mqtt_port: int = Field(default=1883, ge=1, le=65535)
    mqtt_topic_prefix: str = "companion/home"
    remote_access_enabled: bool = False
    remote_public_url: str = ""
    remote_access_token: str = ""
    google_home_enabled: bool = False
    google_home_project_id: str = ""
    google_home_oauth_client_id: str = ""
    google_home_structure_name: str = "Maison"
    google_home_app_package: str = "com.reperevocal.app"
    dry_run: bool = True


class GoogleHomeStatus(BaseModel):
    ready: bool = False
    mode: Literal["setup", "oauth_needed", "ready", "simulation"] = "setup"
    summary: str
    missing: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    links: dict[str, str] = Field(default_factory=dict)
    supports_commissioning_intent: bool = True


class SmartDevice(BaseModel):
    id: int | None = None
    name: str
    room: str = "maison"
    kind: Literal["light", "climate", "lock", "sensor", "media", "switch", "camera"] = "switch"
    connector: Literal["local", "home_assistant", "mqtt", "google_home", "tuya", "shelly"] = "local"
    target: str = ""
    state: str = "off"
    metadata: dict[str, Any] = Field(default_factory=dict)
    last_command_at: str | None = None
    created_at: str | None = None


class DeviceCommand(BaseModel):
    command: Literal["on", "off", "toggle", "lock", "unlock", "set", "status"] = "toggle"
    value: str | float | int | bool | None = None


class ExecuteActionsRequest(BaseModel):
    actions: list[RoutineAction]
    config: IntegrationConfig | None = None


class CustomRoutine(BaseModel):
    id: int | None = None
    name: str
    description: str = ""
    actions: list[RoutineAction] = Field(default_factory=list)
    enabled: bool = True
    created_at: str | None = None


class AIConfig(BaseModel):
    provider: Literal["local", "ollama", "openai", "gemini", "claude"] = "local"
    model: str = ""
    api_key: str = ""
    endpoint: str = ""
    enabled: bool = False


class ChatRequest(BaseModel):
    text: str
    context: ContextSignal = Field(default_factory=ContextSignal)
    memories: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    provider: str
    model: str
    answer: str
    used_cloud: bool = False


class SensorEvent(BaseModel):
    source: str
    kind: Literal[
        "motion",
        "door",
        "sound",
        "smoke",
        "water",
        "fall",
        "presence",
        "temperature",
        "humidity",
        "camera",
        "health",
    ]
    value: str | float | int | bool
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    room: str = "maison"
    timestamp: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class VisionObservation(BaseModel):
    id: int | None = None
    source: str = "camera"
    room: str = "maison"
    scene: str = "piece"
    objects: list[str] = Field(default_factory=list)
    people_count: int = Field(default=0, ge=0, le=30)
    activities: list[str] = Field(default_factory=list)
    ocr_text: str = ""
    confidence: float = Field(default=0.75, ge=0.0, le=1.0)
    risk_level: Literal["low", "medium", "high"] = "low"
    summary: str = ""
    action_hint: str = ""
    created_at: str | None = None


class SmartAlert(BaseModel):
    id: int | None = None
    severity: Literal["info", "warning", "critical"]
    title: str
    message: str
    source: str
    kind: str
    recommended_routine: str | None = None
    created_at: str | None = None
    acknowledged: bool = False


class CompanionNotification(BaseModel):
    id: int | None = None
    title: str
    message: str
    priority: Literal["low", "normal", "high", "urgent"] = "normal"
    source: str = "companion"
    action_hint: str = ""
    acknowledged: bool = False
    created_at: str | None = None


class EmergencyContact(BaseModel):
    id: int | None = None
    name: str
    relation: str = "proche"
    phone: str = ""
    email: str = ""
    priority: int = Field(default=1, ge=1, le=5)
    notify_on: list[str] = Field(default_factory=lambda: ["critical"])
    active: bool = True
    created_at: str | None = None


class EscalationResult(BaseModel):
    alert_id: int | None = None
    alert_title: str
    contacts: list[EmergencyContact] = Field(default_factory=list)
    message: str
    simulated: bool = True


class NestHubState(BaseModel):
    screen: Literal["home", "security", "family", "health", "kitchen", "car", "sleep"] = "home"
    title: str = "Companion Hub AI"
    message: str = "La maison qui vous comprend vraiment."
    accent: str = "aqua"
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


class NestHubUpdate(BaseModel):
    screen: Literal["home", "security", "family", "health", "kitchen", "car", "sleep"]
    title: str | None = None
    message: str | None = None


class CompanionDecision(BaseModel):
    intent: str
    answer: str
    routine: str | None = None
    confidence: float = 0.75
    actions: list[RoutineAction] = Field(default_factory=list)
    execution_results: list[ActionExecutionResult] = Field(default_factory=list)
    memory_to_store: str | None = None


class ContextInsight(BaseModel):
    priority: Literal["normal", "comfort", "health", "security", "kitchen", "car"] = "normal"
    score: int = Field(default=0, ge=0, le=100)
    title: str = "Maison stable"
    summary: str = "Aucun signal prioritaire."
    signals: list[str] = Field(default_factory=list)
    recommended_routine: str | None = None
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


class DailyBrief(BaseModel):
    title: str = "Brief quotidien"
    summary: str
    agenda: list[CalendarEvent] = Field(default_factory=list)
    priorities: list[str] = Field(default_factory=list)
    suggested_routine: str | None = None
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


class SystemDiagnostic(BaseModel):
    score: int = Field(default=0, ge=0, le=100)
    status: Literal["setup", "ready", "strong", "production"] = "setup"
    summary: str
    checks: dict[str, bool] = Field(default_factory=dict)
    issues: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


class HubState(BaseModel):
    status: str
    context: ContextSignal
    suggestion: CompanionDecision
    context_insight: ContextInsight = Field(default_factory=ContextInsight)
    memories: list[MemoryItem]
    user_profiles: list[UserProfile] = Field(default_factory=list)
    presence_signals: list[PresenceSignal] = Field(default_factory=list)
    family_moments: list[FamilyMoment] = Field(default_factory=list)
    family_albums: list[FamilyAlbum] = Field(default_factory=list)
    health_reminders: list[HealthReminder] = Field(default_factory=list)
    wellbeing_checkins: list[WellbeingCheckIn] = Field(default_factory=list)
    behavior_anomalies: list[BehaviorAnomaly] = Field(default_factory=list)
    calendar_events: list[CalendarEvent] = Field(default_factory=list)
    environmental_snapshots: list[EnvironmentalSnapshot] = Field(default_factory=list)
    energy_readings: list[EnergyReading] = Field(default_factory=list)
    kitchen_items: list[KitchenItem] = Field(default_factory=list)
    smart_devices: list[SmartDevice] = Field(default_factory=list)
    car_reminders: list[CarReminder] = Field(default_factory=list)
    custom_routines: list[CustomRoutine] = Field(default_factory=list)
    learned_automations: list[LearnedAutomation] = Field(default_factory=list)
    automation_proposals: list[AutomationProposal] = Field(default_factory=list)
    vision_observations: list[VisionObservation] = Field(default_factory=list)
    alerts: list[SmartAlert] = Field(default_factory=list)
    notifications: list[CompanionNotification] = Field(default_factory=list)
    emergency_contacts: list[EmergencyContact] = Field(default_factory=list)
    nest_hub: NestHubState = Field(default_factory=NestHubState)
    events: list[str]
