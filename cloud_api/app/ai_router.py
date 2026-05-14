from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

from .models import AIConfig, ChatRequest, ChatResponse


class AIConfigStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> AIConfig:
        if not self.path.exists():
            return AIConfig()
        try:
            return AIConfig(**json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError):
            return AIConfig()

    def save(self, config: AIConfig) -> AIConfig:
        self.path.write_text(config.model_dump_json(indent=2), encoding="utf-8")
        return config


class AIRouter:
    def __init__(self, config: AIConfig) -> None:
        self.config = config

    def chat(self, request: ChatRequest) -> ChatResponse:
        if not self.config.enabled or self.config.provider == "local":
            return self._local_response(request)
        if self.config.provider == "ollama":
            return self._ollama(request)
        if self.config.provider == "openai":
            return self._openai_compatible(request)
        if self.config.provider in {"gemini", "claude"}:
            return ChatResponse(
                provider=self.config.provider,
                model=self.config.model,
                answer="Connecteur configure mais appel direct non active dans cette V1 locale. La reponse reste locale.",
                used_cloud=False,
            )
        return self._local_response(request)

    def _local_response(self, request: ChatRequest) -> ChatResponse:
        memory_hint = ""
        if request.memories:
            memory_hint = f" Je garde en tete : {request.memories[0]}"
        hour = request.context.hour
        if hour >= 21:
            mood = "Je privilegie une reponse courte, calme et orientee routine du soir."
        elif hour < 9:
            mood = "Je peux preparer un brief matin avec meteo, agenda, maison et trajet."
        else:
            mood = "Je reste en observation proactive et je propose seulement ce qui est utile."
        return ChatResponse(
            provider="local",
            model="rules",
            answer=f"{mood}{memory_hint}",
            used_cloud=False,
        )

    def _ollama(self, request: ChatRequest) -> ChatResponse:
        endpoint = (self.config.endpoint or "").rstrip("/")
        if not endpoint:
            fallback = self._local_response(request)
            fallback.answer = "Endpoint Ollama distant non configure. Configure une URL HTTPS publique ou choisis un fournisseur cloud."
            return fallback
        model = self.config.model or "llama3.2"
        prompt = self._prompt(request)
        body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
        try:
            http_request = urllib.request.Request(
                endpoint + "/api/generate",
                data=body,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(http_request, timeout=18) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return ChatResponse(
                provider="ollama",
                model=model,
                answer=str(payload.get("response", "")).strip() or "Ollama n'a pas retourne de texte.",
                used_cloud=False,
            )
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            fallback = self._local_response(request)
            fallback.answer = f"Ollama indisponible, reponse locale. Detail : {exc}"
            return fallback

    def _openai_compatible(self, request: ChatRequest) -> ChatResponse:
        if not self.config.api_key:
            return self._local_response(request)
        endpoint = (self.config.endpoint or "https://api.openai.com/v1").rstrip("/")
        model = self.config.model or "gpt-4o-mini"
        body = json.dumps(
            {
                "model": model,
                "messages": [
                    {"role": "system", "content": "Tu es Companion Hub AI, assistant domestique local-first, concis et prudent."},
                    {"role": "user", "content": self._prompt(request)},
                ],
                "temperature": 0.4,
            }
        ).encode("utf-8")
        try:
            http_request = urllib.request.Request(
                endpoint + "/chat/completions",
                data=body,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(http_request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            answer = payload["choices"][0]["message"]["content"].strip()
            return ChatResponse(provider="openai", model=model, answer=answer, used_cloud=True)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError, IndexError) as exc:
            fallback = self._local_response(request)
            fallback.answer = f"Cloud IA indisponible, reponse locale. Detail : {exc}"
            return fallback

    def _prompt(self, request: ChatRequest) -> str:
        memories = "\n".join(f"- {item}" for item in request.memories[:8]) or "- Aucune memoire fournie"
        return (
            "Reponds en francais, tres utilement, sans inventer d'action executee.\n"
            f"Utilisateur: {request.context.user}\n"
            f"Heure: {request.context.hour}h\n"
            f"Lieu: {request.context.location}\n"
            f"Meteo: {request.context.weather}\n"
            f"Fatigue: {request.context.fatigue}\n"
            f"Memoires:\n{memories}\n"
            f"Message: {request.text}"
        )
