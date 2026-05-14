from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .models import ActionExecutionResult, IntegrationConfig, RoutineAction


class IntegrationStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> IntegrationConfig:
        if not self.path.exists():
            return IntegrationConfig()
        try:
            return IntegrationConfig(**json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError):
            return IntegrationConfig()

    def save(self, config: IntegrationConfig) -> IntegrationConfig:
        safe_config = config.model_copy()
        self.path.write_text(safe_config.model_dump_json(indent=2), encoding="utf-8")
        return safe_config


class ActionExecutor:
    def __init__(self, config: IntegrationConfig) -> None:
        self.config = config

    def execute_many(self, actions: list[RoutineAction]) -> list[ActionExecutionResult]:
        return [self.execute(action) for action in actions]

    def execute(self, action: RoutineAction) -> ActionExecutionResult:
        if self.config.dry_run:
            return self._result(action, "simulated", "Mode simulation actif.")

        if action.target.startswith("home."):
            return self._execute_home_assistant(action)
        if action.target.startswith("google_home."):
            return self._execute_google_home(action)
        if action.target.startswith("mqtt."):
            return self._execute_mqtt(action)
        if action.target.startswith(("vision.", "audio.", "health.", "calendar.", "weather", "car.", "media.", "nest.")):
            return self._result(action, "skipped", "Action locale exposee a l'app Android, pas executee par le backend.")
        return self._result(action, "skipped", "Aucun connecteur disponible pour cette cible.")

    def _execute_home_assistant(self, action: RoutineAction) -> ActionExecutionResult:
        if not self.config.home_assistant_url or not self.config.home_assistant_token:
            return self._result(action, "simulated", "Home Assistant non configure.")

        domain, service = self._home_assistant_service(action)
        url = self.config.home_assistant_url.rstrip("/") + f"/api/services/{domain}/{service}"
        body = json.dumps(self._home_assistant_payload(action)).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.config.home_assistant_token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=6) as response:
                return self._result(action, "sent", f"Home Assistant HTTP {response.status}.")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return self._result(action, "error", f"Home Assistant erreur : {exc}")

    def _execute_mqtt(self, action: RoutineAction) -> ActionExecutionResult:
        if not self.config.mqtt_host:
            return self._result(action, "simulated", "MQTT non configure.")
        try:
            with socket.create_connection((self.config.mqtt_host, self.config.mqtt_port), timeout=4):
                return self._result(action, "sent", "Broker MQTT joignable. Publication native a brancher.")
        except OSError as exc:
            return self._result(action, "error", f"MQTT erreur : {exc}")

    def _execute_google_home(self, action: RoutineAction) -> ActionExecutionResult:
        if self.config.dry_run:
            return self._result(action, "simulated", "Google Home pret en simulation.")
        if not self.config.google_home_enabled:
            return self._result(action, "simulated", "Google Home non active dans Companion Hub AI.")
        if not self.config.google_home_project_id or not self.config.google_home_oauth_client_id:
            return self._result(action, "error", "OAuth Google Home incomplet : projet ou client Android manquant.")
        return self._result(
            action,
            "skipped",
            "Connexion Google Home preparee. L'autorisation utilisateur doit etre terminee dans l'app Android via Home APIs.",
        )

    def _home_assistant_service(self, action: RoutineAction) -> tuple[str, str]:
        if action.id.endswith("_off") or "off" in action.id:
            return "light", "turn_off"
        if action.target in {"home.heating"}:
            return "climate", "set_temperature"
        return "light", "turn_on"

    def _home_assistant_payload(self, action: RoutineAction) -> dict[str, Any]:
        entity_id = action.payload.get("entity_id")
        if not entity_id:
            if action.target == "home.entry_light":
                entity_id = "light.entree"
            elif action.target == "home.heating":
                entity_id = "climate.chauffage"
            else:
                entity_id = "light.maison"
        payload: dict[str, Any] = {"entity_id": entity_id}
        if "temperature" in action.payload and action.target == "home.heating":
            payload["temperature"] = action.payload["temperature"]
        if action.payload.get("temperature") == "warm":
            payload["color_temp_kelvin"] = 2700
        return payload

    def _result(
        self,
        action: RoutineAction,
        status: str,
        detail: str,
    ) -> ActionExecutionResult:
        return ActionExecutionResult(
            action_id=action.id,
            label=action.label,
            target=action.target,
            status=status,  # type: ignore[arg-type]
            detail=detail,
        )
