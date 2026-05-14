from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import AutomationProposal, BehaviorAnomaly, CalendarEvent, CarReminder, CompanionNotification, CustomRoutine, DeviceCommand, EmergencyContact, EnergyReading, EnvironmentalSnapshot, FamilyAlbum, FamilyMoment, HealthReminder, KitchenItem, LearnedAutomation, MemoryItem, PresenceSignal, RoutineAction, SmartAlert, SmartDevice, UserProfile, VisionObservation, WellbeingCheckIn


class MemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'preference',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    source TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    recommended_routine TEXT,
                    acknowledged INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    priority TEXT NOT NULL DEFAULT 'normal',
                    source TEXT NOT NULL DEFAULT 'companion',
                    action_hint TEXT NOT NULL DEFAULT '',
                    acknowledged INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS vision_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL DEFAULT 'camera',
                    room TEXT NOT NULL DEFAULT 'maison',
                    scene TEXT NOT NULL DEFAULT 'piece',
                    objects TEXT NOT NULL DEFAULT '[]',
                    people_count INTEGER NOT NULL DEFAULT 0,
                    activities TEXT NOT NULL DEFAULT '[]',
                    ocr_text TEXT NOT NULL DEFAULT '',
                    confidence REAL NOT NULL DEFAULT 0.75,
                    risk_level TEXT NOT NULL DEFAULT 'low',
                    summary TEXT NOT NULL DEFAULT '',
                    action_hint TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS emergency_contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    relation TEXT NOT NULL DEFAULT 'proche',
                    phone TEXT NOT NULL DEFAULT '',
                    email TEXT NOT NULL DEFAULT '',
                    priority INTEGER NOT NULL DEFAULT 1,
                    notify_on TEXT NOT NULL DEFAULT '["critical"]',
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS family_moments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    people TEXT NOT NULL DEFAULT '[]',
                    mood TEXT NOT NULL DEFAULT 'doux',
                    occurred_at TEXT,
                    summary TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS family_albums (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL DEFAULT 'Album familial',
                    theme TEXT NOT NULL DEFAULT 'souvenirs',
                    people TEXT NOT NULL DEFAULT '[]',
                    moment_ids TEXT NOT NULL DEFAULT '[]',
                    narration TEXT NOT NULL DEFAULT '',
                    cover_hint TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'famille',
                    voice_label TEXT NOT NULL DEFAULT '',
                    preferred_light TEXT NOT NULL DEFAULT 'chaude',
                    quiet_hours_start TEXT NOT NULL DEFAULT '21:00',
                    notes TEXT NOT NULL DEFAULT '',
                    last_seen_at TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS presence_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_profile_id INTEGER,
                    user_name TEXT NOT NULL DEFAULT 'Inconnu',
                    room TEXT NOT NULL DEFAULT 'maison',
                    proximity TEXT NOT NULL DEFAULT 'near',
                    source TEXT NOT NULL DEFAULT 'manual',
                    confidence REAL NOT NULL DEFAULT 0.8,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS health_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL DEFAULT 'medicine',
                    title TEXT NOT NULL,
                    schedule_time TEXT NOT NULL DEFAULT '09:00',
                    notes TEXT NOT NULL DEFAULT '',
                    active INTEGER NOT NULL DEFAULT 1,
                    last_done_at TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS wellbeing_checkins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL DEFAULT 'Anthony',
                    mood TEXT NOT NULL DEFAULT 'neutre',
                    stress_level INTEGER NOT NULL DEFAULT 3,
                    fatigue_level INTEGER NOT NULL DEFAULT 3,
                    sleep_hours REAL,
                    note TEXT NOT NULL DEFAULT '',
                    risk_level TEXT NOT NULL DEFAULT 'low',
                    recommendation TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS behavior_anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL DEFAULT 'Famille',
                    risk_level TEXT NOT NULL DEFAULT 'low',
                    risk_score INTEGER NOT NULL DEFAULT 0,
                    summary TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    signals TEXT NOT NULL DEFAULT '[]',
                    acknowledged INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS calendar_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    starts_at TEXT NOT NULL,
                    location TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL DEFAULT '',
                    source TEXT NOT NULL DEFAULT 'manual',
                    done INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS environmental_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room TEXT NOT NULL DEFAULT 'maison',
                    temperature_c REAL,
                    humidity_pct INTEGER,
                    luminosity TEXT NOT NULL DEFAULT 'normale',
                    noise_level TEXT NOT NULL DEFAULT 'calme',
                    air_quality TEXT NOT NULL DEFAULT 'bonne',
                    source TEXT NOT NULL DEFAULT 'manual',
                    recommendation TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS energy_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zone TEXT NOT NULL DEFAULT 'maison',
                    kwh REAL NOT NULL DEFAULT 0,
                    cost_eur REAL,
                    mode TEXT NOT NULL DEFAULT 'normal',
                    source TEXT NOT NULL DEFAULT 'manual',
                    recommendation TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS kitchen_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity TEXT NOT NULL DEFAULT '1',
                    category TEXT NOT NULL DEFAULT 'frigo',
                    expires_at TEXT,
                    source TEXT NOT NULL DEFAULT 'manual',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS smart_devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    room TEXT NOT NULL DEFAULT 'maison',
                    kind TEXT NOT NULL DEFAULT 'switch',
                    connector TEXT NOT NULL DEFAULT 'local',
                    target TEXT NOT NULL DEFAULT '',
                    state TEXT NOT NULL DEFAULT 'off',
                    metadata TEXT NOT NULL DEFAULT '{}',
                    last_command_at TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS car_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL DEFAULT 'maintenance',
                    title TEXT NOT NULL,
                    due_date TEXT,
                    mileage_km INTEGER,
                    notes TEXT NOT NULL DEFAULT '',
                    done INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS custom_routines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    actions TEXT NOT NULL DEFAULT '[]',
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS learned_automations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    trigger TEXT NOT NULL DEFAULT 'time',
                    trigger_value TEXT NOT NULL,
                    routine TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 0.65,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    last_triggered_at TEXT,
                    trigger_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS automation_proposals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    trigger TEXT NOT NULL DEFAULT 'time',
                    trigger_value TEXT NOT NULL,
                    routine TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 0.62,
                    reason TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'proposed',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def add_memory(self, text: str, category: str = "preference") -> MemoryItem:
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Memory text cannot be empty")
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO memories(text, category) VALUES (?, ?)",
                (cleaned, category),
            )
            row = connection.execute(
                "SELECT id, text, category, created_at FROM memories WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return MemoryItem(**dict(row))

    def list_memories(self, limit: int = 30) -> list[MemoryItem]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, text, category, created_at FROM memories ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [MemoryItem(**dict(row)) for row in rows]

    def add_event(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        with self._connect() as connection:
            connection.execute("INSERT INTO events(text) VALUES (?)", (cleaned,))

    def list_events(self, limit: int = 20) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT created_at, text FROM events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [f"{row['created_at']} - {row['text']}" for row in rows]

    def add_alert(self, alert: SmartAlert) -> SmartAlert:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO alerts(
                    severity,
                    title,
                    message,
                    source,
                    kind,
                    recommended_routine,
                    acknowledged
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert.severity,
                    alert.title,
                    alert.message,
                    alert.source,
                    alert.kind,
                    alert.recommended_routine,
                    1 if alert.acknowledged else 0,
                ),
            )
            row = connection.execute(
                """
                SELECT id, severity, title, message, source, kind, recommended_routine,
                       created_at, acknowledged
                FROM alerts WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_alert(row)

    def add_notification(self, notification: CompanionNotification) -> CompanionNotification:
        title = notification.title.strip()
        message = notification.message.strip()
        if not title or not message:
            raise ValueError("Notification title and message cannot be empty")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO notifications(title, message, priority, source, action_hint, acknowledged)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    message,
                    notification.priority,
                    notification.source.strip() or "companion",
                    notification.action_hint.strip(),
                    1 if notification.acknowledged else 0,
                ),
            )
            row = connection.execute(
                """
                SELECT id, title, message, priority, source, action_hint, acknowledged, created_at
                FROM notifications WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_notification(row)

    def list_notifications(self, limit: int = 30, include_acknowledged: bool = False) -> list[CompanionNotification]:
        where = "" if include_acknowledged else "WHERE acknowledged = 0"
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, title, message, priority, source, action_hint, acknowledged, created_at
                FROM notifications
                {where}
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_notification(row) for row in rows]

    def acknowledge_notification(self, notification_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE notifications SET acknowledged = 1 WHERE id = ?",
                (notification_id,),
            )
        return cursor.rowcount > 0

    def add_family_moment(self, moment: FamilyMoment) -> FamilyMoment:
        summary = moment.summary or self._summarize_moment(moment)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO family_moments(title, description, people, mood, occurred_at, summary)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    moment.title.strip(),
                    moment.description.strip(),
                    json_dumps(moment.people),
                    moment.mood.strip() or "doux",
                    moment.occurred_at,
                    summary,
                ),
            )
            row = connection.execute(
                """
                SELECT id, title, description, people, mood, occurred_at, summary, created_at
                FROM family_moments WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_family_moment(row)

    def list_family_moments(self, limit: int = 20) -> list[FamilyMoment]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, title, description, people, mood, occurred_at, summary, created_at
                FROM family_moments
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_family_moment(row) for row in rows]

    def add_family_album(self, album: FamilyAlbum) -> FamilyAlbum:
        title = album.title.strip() or "Album familial"
        narration = album.narration.strip() or self._build_album_narration(album)
        cover_hint = album.cover_hint.strip() or self._build_album_cover_hint(album)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO family_albums(title, theme, people, moment_ids, narration, cover_hint)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    album.theme.strip() or "souvenirs",
                    json_dumps(album.people),
                    json_dumps([str(item) for item in album.moment_ids]),
                    narration,
                    cover_hint,
                ),
            )
            row = connection.execute(
                """
                SELECT id, title, theme, people, moment_ids, narration, cover_hint, created_at
                FROM family_albums WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_family_album(row)

    def list_family_albums(self, limit: int = 20) -> list[FamilyAlbum]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, title, theme, people, moment_ids, narration, cover_hint, created_at
                FROM family_albums
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_family_album(row) for row in rows]

    def auto_family_album(self, theme: str = "semaine") -> FamilyAlbum:
        moments = self.list_family_moments(6)
        people: list[str] = []
        moment_ids: list[int] = []
        for moment in moments:
            if moment.id is not None:
                moment_ids.append(moment.id)
            for person in moment.people:
                if person not in people:
                    people.append(person)
        title = "Album souvenirs"
        if moments:
            title = f"Album {theme} - {moments[0].title}"
        return self.add_family_album(
            FamilyAlbum(
                title=title,
                theme=theme,
                people=people[:8],
                moment_ids=moment_ids,
            )
        )

    def add_user_profile(self, profile: UserProfile) -> UserProfile:
        name = profile.name.strip()
        if not name:
            raise ValueError("User profile name cannot be empty")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO user_profiles(
                    name, role, voice_label, preferred_light, quiet_hours_start, notes
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    profile.role.strip() or "famille",
                    profile.voice_label.strip(),
                    profile.preferred_light,
                    profile.quiet_hours_start.strip() or "21:00",
                    profile.notes.strip(),
                ),
            )
            row = connection.execute(
                """
                SELECT id, name, role, voice_label, preferred_light, quiet_hours_start,
                       notes, last_seen_at, created_at
                FROM user_profiles WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return UserProfile(**dict(row))

    def list_user_profiles(self, limit: int = 20) -> list[UserProfile]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, name, role, voice_label, preferred_light, quiet_hours_start,
                       notes, last_seen_at, created_at
                FROM user_profiles
                ORDER BY COALESCE(last_seen_at, created_at) DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [UserProfile(**dict(row)) for row in rows]

    def mark_user_seen(self, profile_id: int) -> UserProfile | None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE user_profiles SET last_seen_at = CURRENT_TIMESTAMP WHERE id = ?",
                (profile_id,),
            )
            row = connection.execute(
                """
                SELECT id, name, role, voice_label, preferred_light, quiet_hours_start,
                       notes, last_seen_at, created_at
                FROM user_profiles WHERE id = ?
                """,
                (profile_id,),
            ).fetchone()
        if row is None:
            return None
        return UserProfile(**dict(row))

    def add_presence_signal(self, signal: PresenceSignal) -> PresenceSignal:
        name = signal.user_name.strip() or "Inconnu"
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO presence_signals(user_profile_id, user_name, room, proximity, source, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    signal.user_profile_id,
                    name,
                    signal.room.strip() or "maison",
                    signal.proximity,
                    signal.source,
                    signal.confidence,
                ),
            )
            row = connection.execute(
                """
                SELECT id, user_profile_id, user_name, room, proximity, source, confidence, created_at
                FROM presence_signals WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return PresenceSignal(**dict(row))

    def list_presence_signals(self, limit: int = 20) -> list[PresenceSignal]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, user_profile_id, user_name, room, proximity, source, confidence, created_at
                FROM presence_signals
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [PresenceSignal(**dict(row)) for row in rows]

    def add_health_reminder(self, reminder: HealthReminder) -> HealthReminder:
        title = reminder.title.strip()
        if not title:
            raise ValueError("Reminder title cannot be empty")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO health_reminders(kind, title, schedule_time, notes, active)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    reminder.kind,
                    title,
                    reminder.schedule_time.strip() or "09:00",
                    reminder.notes.strip(),
                    1 if reminder.active else 0,
                ),
            )
            row = connection.execute(
                """
                SELECT id, kind, title, schedule_time, notes, active, last_done_at, created_at
                FROM health_reminders WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_health_reminder(row)

    def list_health_reminders(self, limit: int = 20, active_only: bool = False) -> list[HealthReminder]:
        where = "WHERE active = 1" if active_only else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, kind, title, schedule_time, notes, active, last_done_at, created_at
                FROM health_reminders
                {where}
                ORDER BY schedule_time ASC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_health_reminder(row) for row in rows]

    def mark_health_reminder_done(self, reminder_id: int) -> HealthReminder | None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE health_reminders SET last_done_at = CURRENT_TIMESTAMP WHERE id = ?",
                (reminder_id,),
            )
            row = connection.execute(
                """
                SELECT id, kind, title, schedule_time, notes, active, last_done_at, created_at
                FROM health_reminders WHERE id = ?
                """,
                (reminder_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_health_reminder(row)

    def add_calendar_event(self, event: CalendarEvent) -> CalendarEvent:
        title = event.title.strip()
        starts_at = event.starts_at.strip()
        if not title:
            raise ValueError("Calendar event title cannot be empty")
        if not starts_at:
            raise ValueError("Calendar event start cannot be empty")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO calendar_events(title, starts_at, location, notes, source, done)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    starts_at,
                    event.location.strip(),
                    event.notes.strip(),
                    event.source,
                    1 if event.done else 0,
                ),
            )
            row = connection.execute(
                """
                SELECT id, title, starts_at, location, notes, source, done, created_at
                FROM calendar_events WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_calendar_event(row)

    def list_calendar_events(self, limit: int = 20, include_done: bool = False) -> list[CalendarEvent]:
        where = "" if include_done else "WHERE done = 0"
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, title, starts_at, location, notes, source, done, created_at
                FROM calendar_events
                {where}
                ORDER BY starts_at ASC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_calendar_event(row) for row in rows]

    def mark_calendar_event_done(self, event_id: int) -> CalendarEvent | None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE calendar_events SET done = 1 WHERE id = ?",
                (event_id,),
            )
            row = connection.execute(
                """
                SELECT id, title, starts_at, location, notes, source, done, created_at
                FROM calendar_events WHERE id = ?
                """,
                (event_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_calendar_event(row)

    def add_environmental_snapshot(self, snapshot: EnvironmentalSnapshot) -> EnvironmentalSnapshot:
        analyzed = analyze_environmental_snapshot(snapshot)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO environmental_snapshots(
                    room, temperature_c, humidity_pct, luminosity, noise_level,
                    air_quality, source, recommendation
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analyzed.room.strip() or "maison",
                    analyzed.temperature_c,
                    analyzed.humidity_pct,
                    analyzed.luminosity,
                    analyzed.noise_level,
                    analyzed.air_quality,
                    analyzed.source,
                    analyzed.recommendation,
                ),
            )
            row = connection.execute(
                """
                SELECT id, room, temperature_c, humidity_pct, luminosity, noise_level,
                       air_quality, source, recommendation, created_at
                FROM environmental_snapshots WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return EnvironmentalSnapshot(**dict(row))

    def list_environmental_snapshots(self, limit: int = 20) -> list[EnvironmentalSnapshot]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, room, temperature_c, humidity_pct, luminosity, noise_level,
                       air_quality, source, recommendation, created_at
                FROM environmental_snapshots
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [EnvironmentalSnapshot(**dict(row)) for row in rows]

    def add_energy_reading(self, reading: EnergyReading) -> EnergyReading:
        analyzed = analyze_energy_reading(reading)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO energy_readings(zone, kwh, cost_eur, mode, source, recommendation)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    analyzed.zone.strip() or "maison",
                    analyzed.kwh,
                    analyzed.cost_eur,
                    analyzed.mode,
                    analyzed.source,
                    analyzed.recommendation,
                ),
            )
            row = connection.execute(
                """
                SELECT id, zone, kwh, cost_eur, mode, source, recommendation, created_at
                FROM energy_readings WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return EnergyReading(**dict(row))

    def list_energy_readings(self, limit: int = 20) -> list[EnergyReading]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, zone, kwh, cost_eur, mode, source, recommendation, created_at
                FROM energy_readings
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [EnergyReading(**dict(row)) for row in rows]

    def add_wellbeing_checkin(self, checkin: WellbeingCheckIn) -> WellbeingCheckIn:
        analyzed = analyze_wellbeing_checkin(checkin)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO wellbeing_checkins(
                    user, mood, stress_level, fatigue_level, sleep_hours, note, risk_level, recommendation
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analyzed.user.strip() or "Anthony",
                    analyzed.mood,
                    analyzed.stress_level,
                    analyzed.fatigue_level,
                    analyzed.sleep_hours,
                    analyzed.note.strip(),
                    analyzed.risk_level,
                    analyzed.recommendation,
                ),
            )
            row = connection.execute(
                """
                SELECT id, user, mood, stress_level, fatigue_level, sleep_hours,
                       note, risk_level, recommendation, created_at
                FROM wellbeing_checkins WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_wellbeing_checkin(row)

    def list_wellbeing_checkins(self, limit: int = 20) -> list[WellbeingCheckIn]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, user, mood, stress_level, fatigue_level, sleep_hours,
                       note, risk_level, recommendation, created_at
                FROM wellbeing_checkins
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_wellbeing_checkin(row) for row in rows]

    def add_behavior_anomaly(self, anomaly: BehaviorAnomaly) -> BehaviorAnomaly:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO behavior_anomalies(
                    user, risk_level, risk_score, summary, recommendation, signals, acknowledged
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    anomaly.user.strip() or "Famille",
                    anomaly.risk_level,
                    anomaly.risk_score,
                    anomaly.summary.strip(),
                    anomaly.recommendation.strip(),
                    json_dumps(anomaly.signals),
                    1 if anomaly.acknowledged else 0,
                ),
            )
            row = connection.execute(
                """
                SELECT id, user, risk_level, risk_score, summary, recommendation,
                       signals, acknowledged, created_at
                FROM behavior_anomalies WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_behavior_anomaly(row)

    def list_behavior_anomalies(self, limit: int = 20, include_acknowledged: bool = False) -> list[BehaviorAnomaly]:
        where = "" if include_acknowledged else "WHERE acknowledged = 0"
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, user, risk_level, risk_score, summary, recommendation,
                       signals, acknowledged, created_at
                FROM behavior_anomalies
                {where}
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_behavior_anomaly(row) for row in rows]

    def acknowledge_behavior_anomaly(self, anomaly_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE behavior_anomalies SET acknowledged = 1 WHERE id = ?",
                (anomaly_id,),
            )
        return cursor.rowcount > 0

    def add_kitchen_item(self, item: KitchenItem) -> KitchenItem:
        name = item.name.strip()
        if not name:
            raise ValueError("Kitchen item name cannot be empty")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO kitchen_items(name, quantity, category, expires_at, source)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    item.quantity.strip() or "1",
                    item.category.strip() or "frigo",
                    item.expires_at,
                    item.source,
                ),
            )
            row = connection.execute(
                """
                SELECT id, name, quantity, category, expires_at, source, created_at
                FROM kitchen_items WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return KitchenItem(**dict(row))

    def list_kitchen_items(self, limit: int = 50) -> list[KitchenItem]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, name, quantity, category, expires_at, source, created_at
                FROM kitchen_items
                ORDER BY COALESCE(expires_at, '9999-12-31') ASC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [KitchenItem(**dict(row)) for row in rows]

    def remove_kitchen_item(self, item_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM kitchen_items WHERE id = ?", (item_id,))
        return cursor.rowcount > 0

    def add_smart_device(self, device: SmartDevice) -> SmartDevice:
        name = device.name.strip()
        if not name:
            raise ValueError("Device name cannot be empty")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO smart_devices(name, room, kind, connector, target, state, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    device.room.strip() or "maison",
                    device.kind,
                    device.connector,
                    device.target.strip(),
                    device.state.strip() or "off",
                    json_dumps_object(device.metadata),
                ),
            )
            row = connection.execute(
                """
                SELECT id, name, room, kind, connector, target, state, metadata,
                       last_command_at, created_at
                FROM smart_devices WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_smart_device(row)

    def ensure_default_devices(self) -> None:
        if self.list_smart_devices(limit=1):
            return
        defaults = [
            SmartDevice(name="Lumiere salon", room="salon", kind="light", connector="home_assistant", target="light.salon", state="on"),
            SmartDevice(name="Chauffage", room="maison", kind="climate", connector="home_assistant", target="climate.chauffage", state="20.5"),
            SmartDevice(name="Porte entree", room="entree", kind="lock", connector="home_assistant", target="lock.porte_entree", state="locked"),
            SmartDevice(name="Nest Hub", room="salon", kind="media", connector="google_home", target="media_player.nest_hub", state="idle"),
        ]
        for device in defaults:
            self.add_smart_device(device)

    def list_smart_devices(self, limit: int = 50) -> list[SmartDevice]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, name, room, kind, connector, target, state, metadata,
                       last_command_at, created_at
                FROM smart_devices
                ORDER BY room ASC, id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_smart_device(row) for row in rows]

    def command_smart_device(self, device_id: int, command: DeviceCommand) -> SmartDevice | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, name, room, kind, connector, target, state, metadata,
                       last_command_at, created_at
                FROM smart_devices WHERE id = ?
                """,
                (device_id,),
            ).fetchone()
            if row is None:
                return None
            device = self._row_to_smart_device(row)
            next_state = next_device_state(device, command)
            connection.execute(
                """
                UPDATE smart_devices
                SET state = ?, last_command_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (next_state, device_id),
            )
            updated = connection.execute(
                """
                SELECT id, name, room, kind, connector, target, state, metadata,
                       last_command_at, created_at
                FROM smart_devices WHERE id = ?
                """,
                (device_id,),
            ).fetchone()
        return self._row_to_smart_device(updated)

    def update_devices_for_actions(self, actions: list[object]) -> None:
        devices = self.list_smart_devices()
        if not devices:
            return
        with self._connect() as connection:
            for action in actions:
                target = getattr(action, "target", "")
                payload = getattr(action, "payload", {}) or {}
                matches = [device for device in devices if target_matches_device(target, payload, device)]
                for device in matches:
                    state = state_for_action(getattr(action, "id", ""), target, payload, device)
                    connection.execute(
                        """
                        UPDATE smart_devices
                        SET state = ?, last_command_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (state, device.id),
                    )

    def add_car_reminder(self, reminder: CarReminder) -> CarReminder:
        title = reminder.title.strip()
        if not title:
            raise ValueError("Car reminder title cannot be empty")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO car_reminders(kind, title, due_date, mileage_km, notes, done)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    reminder.kind,
                    title,
                    reminder.due_date,
                    reminder.mileage_km,
                    reminder.notes.strip(),
                    1 if reminder.done else 0,
                ),
            )
            row = connection.execute(
                """
                SELECT id, kind, title, due_date, mileage_km, notes, done, created_at
                FROM car_reminders WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_car_reminder(row)

    def list_car_reminders(self, limit: int = 30, include_done: bool = False) -> list[CarReminder]:
        where = "" if include_done else "WHERE done = 0"
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, kind, title, due_date, mileage_km, notes, done, created_at
                FROM car_reminders
                {where}
                ORDER BY COALESCE(due_date, '9999-12-31') ASC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_car_reminder(row) for row in rows]

    def add_custom_routine(self, routine: CustomRoutine) -> CustomRoutine:
        name = routine.name.strip()
        if not name:
            raise ValueError("Custom routine name cannot be empty")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO custom_routines(name, description, actions, enabled)
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    routine.description.strip(),
                    json_dumps_object({"actions": [action.model_dump() for action in routine.actions]}),
                    1 if routine.enabled else 0,
                ),
            )
            row = connection.execute(
                """
                SELECT id, name, description, actions, enabled, created_at
                FROM custom_routines WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_custom_routine(row)

    def list_custom_routines(self, limit: int = 30, enabled_only: bool = False) -> list[CustomRoutine]:
        where = "WHERE enabled = 1" if enabled_only else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, name, description, actions, enabled, created_at
                FROM custom_routines
                {where}
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_custom_routine(row) for row in rows]

    def find_custom_routine(self, routine_id_or_name: str) -> CustomRoutine | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, name, description, actions, enabled, created_at
                FROM custom_routines
                WHERE id = ? OR lower(name) = lower(?)
                ORDER BY id DESC
                LIMIT 1
                """,
                (routine_id_or_name, routine_id_or_name),
            ).fetchone()
        return None if row is None else self._row_to_custom_routine(row)

    def set_custom_routine_enabled(self, routine_id: int, enabled: bool) -> CustomRoutine | None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE custom_routines SET enabled = ? WHERE id = ?",
                (1 if enabled else 0, routine_id),
            )
            row = connection.execute(
                """
                SELECT id, name, description, actions, enabled, created_at
                FROM custom_routines WHERE id = ?
                """,
                (routine_id,),
            ).fetchone()
        return None if row is None else self._row_to_custom_routine(row)

    def mark_car_reminder_done(self, reminder_id: int) -> CarReminder | None:
        with self._connect() as connection:
            connection.execute("UPDATE car_reminders SET done = 1 WHERE id = ?", (reminder_id,))
            row = connection.execute(
                """
                SELECT id, kind, title, due_date, mileage_km, notes, done, created_at
                FROM car_reminders WHERE id = ?
                """,
                (reminder_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_car_reminder(row)

    def add_learned_automation(self, automation: LearnedAutomation) -> LearnedAutomation:
        name = automation.name.strip()
        if not name:
            raise ValueError("Automation name cannot be empty")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO learned_automations(name, trigger, trigger_value, routine, confidence, enabled)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    automation.trigger,
                    automation.trigger_value.strip(),
                    automation.routine.strip(),
                    automation.confidence,
                    1 if automation.enabled else 0,
                ),
            )
            row = connection.execute(
                """
                SELECT id, name, trigger, trigger_value, routine, confidence, enabled,
                       last_triggered_at, trigger_count, created_at
                FROM learned_automations WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_learned_automation(row)

    def list_learned_automations(self, limit: int = 30, enabled_only: bool = False) -> list[LearnedAutomation]:
        where = "WHERE enabled = 1" if enabled_only else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, name, trigger, trigger_value, routine, confidence, enabled,
                       last_triggered_at, trigger_count, created_at
                FROM learned_automations
                {where}
                ORDER BY confidence DESC, trigger_count DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_learned_automation(row) for row in rows]

    def record_automation_trigger(self, automation_id: int) -> LearnedAutomation | None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE learned_automations
                SET trigger_count = trigger_count + 1,
                    last_triggered_at = CURRENT_TIMESTAMP,
                    confidence = MIN(confidence + 0.03, 0.98)
                WHERE id = ?
                """,
                (automation_id,),
            )
            row = connection.execute(
                """
                SELECT id, name, trigger, trigger_value, routine, confidence, enabled,
                       last_triggered_at, trigger_count, created_at
                FROM learned_automations WHERE id = ?
                """,
                (automation_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_learned_automation(row)

    def add_automation_proposal(self, proposal: AutomationProposal) -> AutomationProposal:
        name = proposal.name.strip()
        if not name:
            raise ValueError("Automation proposal name cannot be empty")
        existing = self.find_similar_automation(proposal.trigger, proposal.trigger_value, proposal.routine)
        if existing is not None:
            return existing
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO automation_proposals(name, trigger, trigger_value, routine, confidence, reason, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    proposal.trigger,
                    proposal.trigger_value.strip(),
                    proposal.routine.strip(),
                    proposal.confidence,
                    proposal.reason.strip(),
                    proposal.status,
                ),
            )
            row = connection.execute(
                """
                SELECT id, name, trigger, trigger_value, routine, confidence, reason, status, created_at
                FROM automation_proposals WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_automation_proposal(row)

    def list_automation_proposals(self, limit: int = 20, status: str = "proposed") -> list[AutomationProposal]:
        where = "WHERE status = ?" if status else ""
        params: tuple[object, ...] = (status, limit) if status else (limit,)
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, name, trigger, trigger_value, routine, confidence, reason, status, created_at
                FROM automation_proposals
                {where}
                ORDER BY confidence DESC, id DESC
                LIMIT ?
                """,
                params,
            ).fetchall()
        return [self._row_to_automation_proposal(row) for row in rows]

    def accept_automation_proposal(self, proposal_id: int) -> LearnedAutomation | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, name, trigger, trigger_value, routine, confidence, reason, status, created_at
                FROM automation_proposals WHERE id = ?
                """,
                (proposal_id,),
            ).fetchone()
            if row is None:
                return None
            proposal = self._row_to_automation_proposal(row)
            connection.execute("UPDATE automation_proposals SET status = 'accepted' WHERE id = ?", (proposal_id,))
        return self.add_learned_automation(
            LearnedAutomation(
                name=proposal.name,
                trigger=proposal.trigger,
                trigger_value=proposal.trigger_value,
                routine=proposal.routine,
                confidence=max(0.7, proposal.confidence),
                enabled=True,
            )
        )

    def dismiss_automation_proposal(self, proposal_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE automation_proposals SET status = 'dismissed' WHERE id = ?",
                (proposal_id,),
            )
        return cursor.rowcount > 0

    def find_similar_automation(self, trigger: str, trigger_value: str, routine: str) -> AutomationProposal | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, name, trigger, trigger_value, routine, confidence, reason, status, created_at
                FROM automation_proposals
                WHERE trigger = ? AND trigger_value = ? AND routine = ? AND status = 'proposed'
                ORDER BY id DESC
                LIMIT 1
                """,
                (trigger, trigger_value, routine),
            ).fetchone()
        return None if row is None else self._row_to_automation_proposal(row)

    def list_alerts(self, limit: int = 20, include_acknowledged: bool = False) -> list[SmartAlert]:
        where = "" if include_acknowledged else "WHERE acknowledged = 0"
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, severity, title, message, source, kind, recommended_routine,
                       created_at, acknowledged
                FROM alerts
                {where}
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_alert(row) for row in rows]

    def acknowledge_alert(self, alert_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE alerts SET acknowledged = 1 WHERE id = ?",
                (alert_id,),
            )
        return cursor.rowcount > 0

    def add_vision_observation(self, observation: VisionObservation) -> VisionObservation:
        analyzed = analyze_vision_observation(observation)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO vision_observations(
                    source, room, scene, objects, people_count, activities, ocr_text,
                    confidence, risk_level, summary, action_hint
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analyzed.source.strip() or "camera",
                    analyzed.room.strip() or "maison",
                    analyzed.scene.strip() or "piece",
                    json_dumps(analyzed.objects),
                    analyzed.people_count,
                    json_dumps(analyzed.activities),
                    analyzed.ocr_text.strip(),
                    analyzed.confidence,
                    analyzed.risk_level,
                    analyzed.summary,
                    analyzed.action_hint,
                ),
            )
            row = connection.execute(
                """
                SELECT id, source, room, scene, objects, people_count, activities,
                       ocr_text, confidence, risk_level, summary, action_hint, created_at
                FROM vision_observations WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_vision_observation(row)

    def list_vision_observations(self, limit: int = 20) -> list[VisionObservation]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, source, room, scene, objects, people_count, activities,
                       ocr_text, confidence, risk_level, summary, action_hint, created_at
                FROM vision_observations
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_vision_observation(row) for row in rows]

    def add_emergency_contact(self, contact: EmergencyContact) -> EmergencyContact:
        name = contact.name.strip()
        if not name:
            raise ValueError("Emergency contact name cannot be empty")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO emergency_contacts(
                    name, relation, phone, email, priority, notify_on, active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    contact.relation.strip() or "proche",
                    contact.phone.strip(),
                    contact.email.strip(),
                    contact.priority,
                    json_dumps(contact.notify_on),
                    1 if contact.active else 0,
                ),
            )
            row = connection.execute(
                """
                SELECT id, name, relation, phone, email, priority, notify_on, active, created_at
                FROM emergency_contacts WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return self._row_to_emergency_contact(row)

    def list_emergency_contacts(self, limit: int = 20, active_only: bool = False) -> list[EmergencyContact]:
        where = "WHERE active = 1" if active_only else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT id, name, relation, phone, email, priority, notify_on, active, created_at
                FROM emergency_contacts
                {where}
                ORDER BY priority ASC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_emergency_contact(row) for row in rows]

    def audit_counts(self) -> dict[str, int]:
        tables = {
            "memories": "memories",
            "events": "events",
            "alerts": "alerts",
            "notifications": "notifications",
            "vision_observations": "vision_observations",
            "emergency_contacts": "emergency_contacts",
            "family_moments": "family_moments",
            "family_albums": "family_albums",
            "user_profiles": "user_profiles",
            "presence_signals": "presence_signals",
            "health_reminders": "health_reminders",
            "wellbeing_checkins": "wellbeing_checkins",
            "behavior_anomalies": "behavior_anomalies",
            "calendar_events": "calendar_events",
            "environmental_snapshots": "environmental_snapshots",
            "energy_readings": "energy_readings",
            "kitchen_items": "kitchen_items",
            "smart_devices": "smart_devices",
            "car_reminders": "car_reminders",
            "custom_routines": "custom_routines",
            "learned_automations": "learned_automations",
            "automation_proposals": "automation_proposals",
        }
        with self._connect() as connection:
            return {
                name: int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                for name, table in tables.items()
            }

    def export_data(self) -> dict[str, object]:
        with self._connect() as connection:
            return {
                "memories": rows_as_dicts(connection, "SELECT id, text, category, created_at FROM memories ORDER BY id"),
                "events": rows_as_dicts(connection, "SELECT id, text, created_at FROM events ORDER BY id"),
                "alerts": rows_as_dicts(
                    connection,
                    """
                    SELECT id, severity, title, message, source, kind, recommended_routine,
                           acknowledged, created_at
                    FROM alerts ORDER BY id
                    """,
                ),
                "notifications": rows_as_dicts(
                    connection,
                    """
                    SELECT id, title, message, priority, source, action_hint,
                           acknowledged, created_at
                    FROM notifications ORDER BY id
                    """,
                ),
                "vision_observations": rows_as_dicts(
                    connection,
                    """
                    SELECT id, source, room, scene, objects, people_count, activities,
                           ocr_text, confidence, risk_level, summary, action_hint, created_at
                    FROM vision_observations ORDER BY id
                    """,
                ),
                "emergency_contacts": rows_as_dicts(
                    connection,
                    """
                    SELECT id, name, relation, phone, email, priority, notify_on, active, created_at
                    FROM emergency_contacts ORDER BY priority ASC, id
                    """,
                ),
                "family_moments": rows_as_dicts(
                    connection,
                    """
                    SELECT id, title, description, people, mood, occurred_at, summary, created_at
                    FROM family_moments ORDER BY id
                    """,
                ),
                "family_albums": rows_as_dicts(
                    connection,
                    """
                    SELECT id, title, theme, people, moment_ids, narration, cover_hint, created_at
                    FROM family_albums ORDER BY id
                    """,
                ),
                "user_profiles": rows_as_dicts(
                    connection,
                    """
                    SELECT id, name, role, voice_label, preferred_light, quiet_hours_start,
                           notes, last_seen_at, created_at
                    FROM user_profiles ORDER BY id
                    """,
                ),
                "presence_signals": rows_as_dicts(
                    connection,
                    """
                    SELECT id, user_profile_id, user_name, room, proximity, source, confidence, created_at
                    FROM presence_signals ORDER BY id
                    """,
                ),
                "health_reminders": rows_as_dicts(
                    connection,
                    """
                    SELECT id, kind, title, schedule_time, notes, active, last_done_at, created_at
                    FROM health_reminders ORDER BY id
                    """,
                ),
                "wellbeing_checkins": rows_as_dicts(
                    connection,
                    """
                    SELECT id, user, mood, stress_level, fatigue_level, sleep_hours,
                           note, risk_level, recommendation, created_at
                    FROM wellbeing_checkins ORDER BY id
                    """,
                ),
                "behavior_anomalies": rows_as_dicts(
                    connection,
                    """
                    SELECT id, user, risk_level, risk_score, summary, recommendation,
                           signals, acknowledged, created_at
                    FROM behavior_anomalies ORDER BY id
                    """,
                ),
                "calendar_events": rows_as_dicts(
                    connection,
                    """
                    SELECT id, title, starts_at, location, notes, source, done, created_at
                    FROM calendar_events ORDER BY starts_at ASC, id
                    """,
                ),
                "environmental_snapshots": rows_as_dicts(
                    connection,
                    """
                    SELECT id, room, temperature_c, humidity_pct, luminosity, noise_level,
                           air_quality, source, recommendation, created_at
                    FROM environmental_snapshots ORDER BY id
                    """,
                ),
                "energy_readings": rows_as_dicts(
                    connection,
                    """
                    SELECT id, zone, kwh, cost_eur, mode, source, recommendation, created_at
                    FROM energy_readings ORDER BY id
                    """,
                ),
                "kitchen_items": rows_as_dicts(
                    connection,
                    """
                    SELECT id, name, quantity, category, expires_at, source, created_at
                    FROM kitchen_items ORDER BY id
                    """,
                ),
                "smart_devices": rows_as_dicts(
                    connection,
                    """
                    SELECT id, name, room, kind, connector, target, state, metadata,
                           last_command_at, created_at
                    FROM smart_devices ORDER BY id
                    """,
                ),
                "car_reminders": rows_as_dicts(
                    connection,
                    """
                    SELECT id, kind, title, due_date, mileage_km, notes, done, created_at
                    FROM car_reminders ORDER BY id
                    """,
                ),
                "custom_routines": rows_as_dicts(
                    connection,
                    """
                    SELECT id, name, description, actions, enabled, created_at
                    FROM custom_routines ORDER BY id
                    """,
                ),
                "learned_automations": rows_as_dicts(
                    connection,
                    """
                    SELECT id, name, trigger, trigger_value, routine, confidence, enabled,
                           last_triggered_at, trigger_count, created_at
                    FROM learned_automations ORDER BY id
                    """,
                ),
                "automation_proposals": rows_as_dicts(
                    connection,
                    """
                    SELECT id, name, trigger, trigger_value, routine, confidence, reason, status, created_at
                    FROM automation_proposals ORDER BY id
                    """,
                ),
            }

    def clear_section(self, section: str) -> int:
        tables = {
            "memories": ["memories"],
            "events": ["events"],
            "alerts": ["alerts"],
            "notifications": ["notifications"],
            "vision": ["vision_observations"],
            "emergency": ["emergency_contacts"],
            "family": ["family_moments", "family_albums", "user_profiles", "presence_signals"],
            "health": ["health_reminders", "wellbeing_checkins", "behavior_anomalies"],
            "calendar": ["calendar_events"],
            "environment": ["environmental_snapshots"],
            "energy": ["energy_readings"],
            "kitchen": ["kitchen_items"],
            "devices": ["smart_devices"],
            "car": ["car_reminders"],
            "automations": ["custom_routines", "learned_automations", "automation_proposals"],
        }
        selected = tables.get(section)
        if selected is None:
            raise ValueError(f"Unknown section: {section}")
        deleted = 0
        with self._connect() as connection:
            for table in selected:
                cursor = connection.execute(f"DELETE FROM {table}")
                deleted += cursor.rowcount
        return deleted

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM memories")
            connection.execute("DELETE FROM events")
            connection.execute("DELETE FROM alerts")
            connection.execute("DELETE FROM notifications")
            connection.execute("DELETE FROM vision_observations")
            connection.execute("DELETE FROM emergency_contacts")
            connection.execute("DELETE FROM family_moments")
            connection.execute("DELETE FROM family_albums")
            connection.execute("DELETE FROM user_profiles")
            connection.execute("DELETE FROM presence_signals")
            connection.execute("DELETE FROM health_reminders")
            connection.execute("DELETE FROM wellbeing_checkins")
            connection.execute("DELETE FROM behavior_anomalies")
            connection.execute("DELETE FROM calendar_events")
            connection.execute("DELETE FROM environmental_snapshots")
            connection.execute("DELETE FROM energy_readings")
            connection.execute("DELETE FROM kitchen_items")
            connection.execute("DELETE FROM smart_devices")
            connection.execute("DELETE FROM car_reminders")
            connection.execute("DELETE FROM custom_routines")
            connection.execute("DELETE FROM learned_automations")
            connection.execute("DELETE FROM automation_proposals")

    def _row_to_alert(self, row: sqlite3.Row) -> SmartAlert:
        data = dict(row)
        data["acknowledged"] = bool(data["acknowledged"])
        return SmartAlert(**data)

    def _row_to_notification(self, row: sqlite3.Row) -> CompanionNotification:
        data = dict(row)
        data["acknowledged"] = bool(data["acknowledged"])
        return CompanionNotification(**data)

    def _row_to_vision_observation(self, row: sqlite3.Row) -> VisionObservation:
        data = dict(row)
        data["objects"] = json_loads_list(data.get("objects", "[]"))
        data["activities"] = json_loads_list(data.get("activities", "[]"))
        return VisionObservation(**data)

    def _row_to_emergency_contact(self, row: sqlite3.Row) -> EmergencyContact:
        data = dict(row)
        data["notify_on"] = json_loads_list(data.get("notify_on", "[]")) or ["critical"]
        data["active"] = bool(data["active"])
        return EmergencyContact(**data)

    def _row_to_family_moment(self, row: sqlite3.Row) -> FamilyMoment:
        data = dict(row)
        data["people"] = json_loads_list(data.get("people", "[]"))
        return FamilyMoment(**data)

    def _row_to_family_album(self, row: sqlite3.Row) -> FamilyAlbum:
        data = dict(row)
        data["people"] = json_loads_list(data.get("people", "[]"))
        data["moment_ids"] = json_loads_int_list(data.get("moment_ids", "[]"))
        return FamilyAlbum(**data)

    def _row_to_health_reminder(self, row: sqlite3.Row) -> HealthReminder:
        data = dict(row)
        data["active"] = bool(data["active"])
        return HealthReminder(**data)

    def _row_to_wellbeing_checkin(self, row: sqlite3.Row) -> WellbeingCheckIn:
        return WellbeingCheckIn(**dict(row))

    def _row_to_behavior_anomaly(self, row: sqlite3.Row) -> BehaviorAnomaly:
        data = dict(row)
        data["signals"] = json_loads_list(data.get("signals", "[]"))
        data["acknowledged"] = bool(data["acknowledged"])
        return BehaviorAnomaly(**data)

    def _row_to_calendar_event(self, row: sqlite3.Row) -> CalendarEvent:
        data = dict(row)
        data["done"] = bool(data["done"])
        return CalendarEvent(**data)

    def _row_to_car_reminder(self, row: sqlite3.Row) -> CarReminder:
        data = dict(row)
        data["done"] = bool(data["done"])
        return CarReminder(**data)

    def _row_to_custom_routine(self, row: sqlite3.Row) -> CustomRoutine:
        data = dict(row)
        actions_data = json_loads_object(data.get("actions", "{}")).get("actions", [])
        data["actions"] = [RoutineAction(**item) for item in actions_data if isinstance(item, dict)]
        data["enabled"] = bool(data["enabled"])
        return CustomRoutine(**data)

    def _row_to_smart_device(self, row: sqlite3.Row) -> SmartDevice:
        data = dict(row)
        data["metadata"] = json_loads_object(data.get("metadata", "{}"))
        return SmartDevice(**data)

    def _row_to_learned_automation(self, row: sqlite3.Row) -> LearnedAutomation:
        data = dict(row)
        data["enabled"] = bool(data["enabled"])
        return LearnedAutomation(**data)

    def _row_to_automation_proposal(self, row: sqlite3.Row) -> AutomationProposal:
        return AutomationProposal(**dict(row))

    def _summarize_moment(self, moment: FamilyMoment) -> str:
        people = ", ".join(moment.people) if moment.people else "la famille"
        date = f" le {moment.occurred_at}" if moment.occurred_at else ""
        return f"{moment.title}{date}. Avec {people}, un moment {moment.mood}: {moment.description}"

    def _build_album_narration(self, album: FamilyAlbum) -> str:
        moments = self.list_family_moments(8)
        selected = [moment for moment in moments if not album.moment_ids or moment.id in album.moment_ids]
        if not selected:
            people = ", ".join(album.people) if album.people else "la famille"
            return f"{album.title}. Un album {album.theme} pour rassembler les souvenirs de {people}."
        lines = [moment.summary or self._summarize_moment(moment) for moment in selected[:5]]
        people = ", ".join(album.people) if album.people else "la famille"
        return f"{album.title}. Avec {people}, cet album raconte : " + " ".join(lines)

    def _build_album_cover_hint(self, album: FamilyAlbum) -> str:
        people = ", ".join(album.people[:3]) if album.people else "la famille"
        return f"Image douce de {people}, theme {album.theme}, style souvenir familial lumineux."


def json_dumps(values: list[str]) -> str:
    import json

    return json.dumps([item.strip() for item in values if item.strip()], ensure_ascii=False)


def json_dumps_object(value: dict[str, object]) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)


def json_loads_list(value: str) -> list[str]:
    import json

    try:
        loaded = json.loads(value)
    except (TypeError, ValueError):
        return []
    if not isinstance(loaded, list):
        return []
    return [str(item) for item in loaded]


def json_loads_object(value: str) -> dict[str, object]:
    import json

    try:
        loaded = json.loads(value)
    except (TypeError, ValueError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def json_loads_int_list(value: str) -> list[int]:
    raw = json_loads_list(value)
    ids: list[int] = []
    for item in raw:
        try:
            ids.append(int(item))
        except ValueError:
            continue
    return ids


def next_device_state(device: SmartDevice, command: DeviceCommand) -> str:
    if command.command == "status":
        return device.state
    if command.command == "set" and command.value is not None:
        return str(command.value)
    if command.command == "lock":
        return "locked"
    if command.command == "unlock":
        return "unlocked"
    if command.command == "on":
        return "on"
    if command.command == "off":
        return "off"
    if device.kind == "lock":
        return "unlocked" if device.state == "locked" else "locked"
    if device.kind == "climate":
        return str(command.value if command.value is not None else device.state)
    return "off" if device.state in {"on", "active"} else "on"


def target_matches_device(target: str, payload: dict[str, object], device: SmartDevice) -> bool:
    entity_id = str(payload.get("entity_id", ""))
    if entity_id and entity_id == device.target:
        return True
    if target == "home.lights" and device.kind == "light":
        return True
    if target == "home.entry_light" and device.kind == "light" and device.room == "entree":
        return True
    if target == "home.heating" and device.kind == "climate":
        return True
    if target == "nest.volume" and device.kind == "media":
        return True
    return False


def state_for_action(action_id: str, target: str, payload: dict[str, object], device: SmartDevice) -> str:
    if action_id.endswith("_off") or "off" in action_id:
        return "off"
    if device.kind == "climate" and "temperature" in payload:
        return str(payload["temperature"])
    if device.kind == "media" and "level" in payload:
        return f"volume {payload['level']}"
    if device.kind == "light":
        return "warm" if payload.get("temperature") == "warm" else "on"
    return "active"


def analyze_wellbeing_checkin(checkin: WellbeingCheckIn) -> WellbeingCheckIn:
    score = max(checkin.stress_level, checkin.fatigue_level)
    if checkin.sleep_hours is not None and checkin.sleep_hours < 5:
        score += 2
    if checkin.mood in {"stress", "triste", "fatigue"}:
        score += 1

    if score >= 9:
        risk = "high"
        recommendation = "Priorite calme : lumiere douce, volume bas, hydratation et proposition de prevenir un proche si cela persiste."
    elif score >= 6:
        risk = "medium"
        recommendation = "Pause conseillee : respiration guidee, verre d'eau et routine bien-etre pendant 10 minutes."
    else:
        risk = "low"
        recommendation = "Etat stable. Continuer le suivi doux des habitudes."
    return checkin.model_copy(update={"risk_level": risk, "recommendation": recommendation})


def analyze_environmental_snapshot(snapshot: EnvironmentalSnapshot) -> EnvironmentalSnapshot:
    recommendations: list[str] = []
    if snapshot.temperature_c is not None:
        if snapshot.temperature_c < 18:
            recommendations.append("augmenter legerement le chauffage")
        elif snapshot.temperature_c > 26:
            recommendations.append("rafraichir ou ventiler la piece")
    if snapshot.humidity_pct is not None:
        if snapshot.humidity_pct < 35:
            recommendations.append("air sec : proposer humidification douce")
        elif snapshot.humidity_pct > 70:
            recommendations.append("humidite elevee : ventiler")
    if snapshot.air_quality == "mauvaise":
        recommendations.append("qualite d'air mauvaise : ouvrir ou purifier")
    elif snapshot.air_quality == "moyenne":
        recommendations.append("qualite d'air a surveiller")
    if snapshot.noise_level == "bruyant":
        recommendations.append("bruit eleve : reduire volume et proposer mode calme")
    if snapshot.luminosity == "basse":
        recommendations.append("luminosite basse : lumiere douce conseillee")
    if not recommendations:
        recommendations.append("ambiance stable : confort maison correct")
    return snapshot.model_copy(update={"recommendation": ". ".join(recommendations) + "."})


def analyze_energy_reading(reading: EnergyReading) -> EnergyReading:
    recommendations: list[str] = []
    if reading.kwh >= 20:
        recommendations.append("consommation elevee : verifier chauffage, chauffe-eau et appareils en veille")
    elif reading.kwh >= 10:
        recommendations.append("consommation a surveiller : proposer mode eco sur les pieces vides")
    else:
        recommendations.append("consommation contenue")
    if reading.mode == "peak":
        recommendations.append("heure de pointe : reporter les appareils non urgents")
    if reading.mode == "away":
        recommendations.append("maison absente : couper lumieres et passer chauffage en eco")
    if reading.cost_eur is not None and reading.cost_eur >= 6:
        recommendations.append("cout eleve aujourd'hui")
    return reading.model_copy(update={"recommendation": ". ".join(recommendations) + "."})


def analyze_vision_observation(observation: VisionObservation) -> VisionObservation:
    objects = [item.strip().lower() for item in observation.objects if item.strip()]
    activities = [item.strip().lower() for item in observation.activities if item.strip()]
    ocr_text = observation.ocr_text.strip()
    risk = "low"
    action_hint = "Observation archivee dans la memoire visuelle locale."

    danger_terms = {"fumee", "feu", "eau", "fuite", "chute", "personne au sol", "intrusion", "porte ouverte"}
    if danger_terms & set(objects + activities):
        risk = "high"
        action_hint = "Verifier immediatement la piece et preparer la routine securite."
    elif observation.people_count == 0 and {"four", "plaque", "casserole"} & set(objects):
        risk = "medium"
        action_hint = "Verifier la cuisine : cuisson detectee sans personne visible."
    elif ocr_text:
        lowered = ocr_text.lower()
        if any(term in lowered for term in ["facture", "relance", "rendez-vous", "urgent"]):
            risk = "medium"
            action_hint = "Creer un rappel ou ajouter le document au journal familial."
        else:
            action_hint = "Texte lu localement, pret pour resume ou rappel."
    elif {"lait", "oeufs", "yaourt", "salade", "pain"} & set(objects):
        action_hint = "Objets alimentaires detectes : proposer ajout a l'inventaire cuisine."

    pieces = [observation.scene.strip() or "scene"]
    if objects:
        pieces.append("objets: " + ", ".join(objects[:6]))
    if activities:
        pieces.append("activites: " + ", ".join(activities[:4]))
    if observation.people_count:
        pieces.append(f"{observation.people_count} personne(s)")
    if ocr_text:
        pieces.append("texte: " + ocr_text[:120])
    summary = ". ".join(pieces) + "."
    return observation.model_copy(update={"risk_level": risk, "summary": summary, "action_hint": action_hint})


def rows_as_dicts(connection: sqlite3.Connection, query: str) -> list[dict[str, object]]:
    return [dict(row) for row in connection.execute(query).fetchall()]
