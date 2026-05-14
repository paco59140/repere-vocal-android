from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path

from .models import NestHubState, NestHubUpdate, SmartAlert


class NestHubStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> NestHubState:
        if not self.path.exists():
            return NestHubState()
        try:
            return NestHubState(**json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError):
            return NestHubState()

    def save(self, state: NestHubState) -> NestHubState:
        self.path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        return state

    def update(self, update: NestHubUpdate) -> NestHubState:
        preset = preset_for_screen(update.screen)
        state = NestHubState(
            screen=update.screen,
            title=update.title or preset.title,
            message=update.message or preset.message,
            accent=preset.accent,
            updated_at=datetime.now().isoformat(timespec="seconds"),
        )
        return self.save(state)

    def alert(self, alert: SmartAlert) -> NestHubState:
        accent = "rose" if alert.severity == "critical" else "amber"
        state = NestHubState(
            screen="security",
            title=alert.title,
            message=alert.message,
            accent=accent,
            updated_at=datetime.now().isoformat(timespec="seconds"),
        )
        return self.save(state)


def preset_for_screen(screen: str) -> NestHubState:
    presets = {
        "home": NestHubState(
            screen="home",
            title="Maison attentive",
            message="Presence, meteo, energie et routines sont surveillees en local.",
            accent="aqua",
        ),
        "security": NestHubState(
            screen="security",
            title="Securite intelligente",
            message="Intrusion, fumee, fuite d'eau, chute et sons suspects sont priorises.",
            accent="rose",
        ),
        "family": NestHubState(
            screen="family",
            title="Memoire familiale",
            message="Souvenirs, habitudes et moments importants restent disponibles localement.",
            accent="lime",
        ),
        "health": NestHubState(
            screen="health",
            title="Bien-etre",
            message="Medicaments, hydratation, sommeil et fatigue sont suivis doucement.",
            accent="amber",
        ),
        "kitchen": NestHubState(
            screen="kitchen",
            title="Cuisine intelligente",
            message="Recettes vocales, frigo, aliments et liste de courses sont prets.",
            accent="lime",
        ),
        "sleep": NestHubState(
            screen="sleep",
            title="Bonne nuit",
            message="Lumieres basses, volume reduit, reveil et meteo du matin sont prepares.",
            accent="aqua",
        ),
    }
    return presets.get(screen, presets["home"])


def render_display(state: NestHubState) -> str:
    accent = {
        "aqua": "#7ce7d4",
        "lime": "#b8ef72",
        "amber": "#ffd166",
        "rose": "#ff8a9a",
    }.get(state.accent, "#7ce7d4")
    title = html.escape(state.title)
    message = html.escape(state.message)
    screen = html.escape(state.screen)
    updated_at = html.escape(state.updated_at)
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="20">
  <title>Companion Hub AI - Nest</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, Verdana, sans-serif; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      color: #f5fbf7;
      background:
        radial-gradient(circle at 25% 25%, {accent}55, transparent 34rem),
        linear-gradient(135deg, #071216, #14262d 55%, #071216);
    }}
    main {{
      width: min(92vw, 62rem);
      display: grid;
      gap: 1.4rem;
      text-align: center;
    }}
    .orb {{
      justify-self: center;
      width: min(28vw, 12rem);
      aspect-ratio: 1;
      border-radius: 50%;
      background: conic-gradient(from 90deg, {accent}, #b8ef72, #ffd166, {accent});
      box-shadow: 0 0 5rem {accent}66;
    }}
    p {{ margin: 0; color: #b8c8c3; font-size: clamp(1.2rem, 3vw, 2.1rem); }}
    h1 {{ margin: 0; font-size: clamp(3rem, 10vw, 8.5rem); line-height: 0.9; letter-spacing: 0; }}
    footer {{ color: #91a29d; font-size: 1rem; }}
  </style>
</head>
<body>
  <main>
    <div class="orb" aria-hidden="true"></div>
    <p>{screen}</p>
    <h1>{title}</h1>
    <p>{message}</p>
    <footer>Mis a jour {updated_at}</footer>
  </main>
</body>
</html>"""
