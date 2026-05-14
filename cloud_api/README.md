# Companion Hub AI Cloud API

API cloud deployable pour Companion Hub AI. Cette API ne doit pas tourner sur le PC de la maison : elle est prevue pour un hebergeur HTTPS afin que l'app Android et Google Home restent utilisables hors domicile.

## Capacites V1

- API FastAPI cloud.
- WebSocket temps reel `/ws`.
- Memoire longue SQLite sur serveur cloud.
- Analyse de contexte heure/presence/meteo/luminosite/fatigue.
- Insight contextuel multi-signaux : alertes, vision, bien-etre, cuisine, voiture, meteo, agenda et routine recommandee.
- Moteur de routines adaptatives.
- Commandes naturelles en francais.
- Registre d'appareils et execution des routines vers Home Assistant Cloud/MQTT public, plus assistant de configuration Google Home avec mode simulation.
- Energie & eco : releves kWh/cout, mode eco/pointe/absence et recommandations locales.
- Alertes intelligentes depuis capteurs : fumee, fuite eau, chute, porte, son suspect, bien-etre.
- Centre de notifications IA : priorites locales generees depuis les modules maison.
- Vision IA locale : observations camera/OCR, objets, activites, texte lu, detection de risques et recommandations.
- Mode Nest Hub : etat partage et page HTML plein ecran pour Cast.
- Routeur IA cloud-first : regles appareil, Ollama distant, OpenAI-compatible optionnel.
- Memoire familiale : moments structures, albums automatiques, resumes narratifs, journal familial.
- Sante & bien-etre : rappels locaux medicaments, hydratation, sommeil, activite et soins.
- Agenda & brief quotidien : evenements locaux, priorites proactives et affichage Nest Hub.
- Ambiance environnementale : temperature, humidite, bruit, luminosite, qualite d'air et recommandations.
- IA emotionnelle locale : humeur, stress, fatigue, sommeil, recommandations et alertes preventives.
- Detection comportement inhabituel : analyse presence, bien-etre et alertes pour seniors/famille.
- Cuisine intelligente : inventaire local, expirations, courses et suggestion recette.
- Assistant voiture : rappels maintenance/carburant/assurance/controle et conseil trajet.
- Automatisation adaptative : habitudes apprises localement, propositions IA validables et confiance evolutive.
- Scenarios personnalises : routines multi-actions locales, reutilisables et compatibles connecteurs.
- Multi-utilisateurs : profils familiaux, preferences personnelles et presence.
- Presence/proximite : signaux locaux par piece et affichage Nest Hub personnalise.
- Confidentialite : audit local, export JSON et effacement cible par section.
- Portabilite locale : import/restauration JSON pour migrer ou restaurer un hub.
- Diagnostic systeme : score de preparation local, modules actifs et prochaines actions.
- Securite avancee : contacts urgence et escalade locale des alertes critiques.
- Journal d'evenements pour Android, Nest Hub, dashboard et futurs hubs Linux/Raspberry Pi.

## Deployer

```powershell
cd "C:\Users\paco\Documents\New project\companion_backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8787
```

L'interface Android/WebView ne se connecte plus a `127.0.0.1` par defaut. Renseigne une URL HTTPS publique dans Reglages > API cloud. Google Home direct fonctionne depuis le telephone sans cette API.

### Google Cloud Run

Le projet Google Cloud deja utilise pour OAuth est `paco-ded005cb`. Depuis ce dossier, apres installation et connexion a Google Cloud CLI :

```powershell
.\deploy-cloud-run.ps1
```

Le script active Cloud Run/Cloud Build/Artifact Registry, construit l'image Docker, deploie le service `companion-hub-ai-api` en `europe-west1`, puis affiche l'URL HTTPS a coller dans l'app Android > Reglages > API cloud.

### Render ou Railway

Les fichiers `render.yaml`, `railway.json`, `Dockerfile` et `.env.example` sont inclus pour un deploiement sans PC. Sur Render/Railway, choisissez ce dossier `companion_backend` comme racine du service et laissez la plateforme utiliser le Dockerfile.

## Test Nest Hub

Une fois l'API cloud deployee :

```powershell
..\tools\nest_hub_test.ps1 -CloudUrl "https://votre-api-cloud" -Screen home -Title "Companion Hub AI" -Message "Test cloud sur Nest Hub"
```

Le script met a jour l'ecran `/nest/display`. Ouvrez ou castez ensuite `https://votre-api-cloud/nest/display` sur le Google Nest Hub.

## Maison connectee

Par defaut `dry_run` est actif : les routines indiquent les actions qui seraient envoyees sans toucher a la maison.

### Google Home

Le panneau Maison affiche maintenant un assistant Google Home. Pour les commandes reelles, Google demande une app Android enregistree dans Google Home Developer Console, un client OAuth Android lie au SHA-1 de signature, puis l'autorisation Home APIs par l'utilisateur. Tant que `dry_run` reste actif, Companion Hub AI garde les commandes Google Home en simulation.

Endpoints :

- `GET /integrations/config`
- `POST /integrations/config`
- `GET /integrations/google-home/status`
- `GET /devices`
- `POST /devices`
- `POST /devices/{device_id}/command`
- `POST /routines/sleep/execute`
- `GET /routines/custom`
- `POST /routines/custom`
- `POST /routines/custom/{routine_id_or_name}/execute`
- `POST /actions/execute`
- `POST /context/insight`
- `GET /system/diagnostic`
- `POST /sensors/events`
- `GET /vision/observations`
- `POST /vision/observations`
- `GET /vision/summary`
- `GET /alerts`
- `POST /alerts/{alert_id}/ack`
- `GET /notifications`
- `POST /notifications/generate`
- `POST /notifications/{notification_id}/ack`
- `GET /nest/state`
- `POST /nest/screen`
- `GET /nest/display`
- `GET /ai/config`
- `POST /ai/config`
- `POST /ai/chat`
- `GET /family/moments`
- `POST /family/moments`
- `GET /family/journal`
- `GET /family/albums`
- `POST /family/albums`
- `POST /family/albums/auto`
- `GET /presence/events`
- `POST /presence/events`
- `GET /presence/summary`
- `GET /health/reminders`
- `POST /health/reminders`
- `POST /health/reminders/{reminder_id}/done`
- `GET /health/checkins`
- `POST /health/checkins`
- `GET /health/summary`
- `GET /health/anomalies`
- `POST /health/anomalies/analyze`
- `POST /health/anomalies/{anomaly_id}/ack`
- `GET /calendar/events`
- `POST /calendar/events`
- `POST /calendar/events/{event_id}/done`
- `GET /environment/snapshots`
- `POST /environment/snapshots`
- `GET /environment/comfort`
- `GET /energy/readings`
- `POST /energy/readings`
- `GET /energy/summary`
- `GET /brief/daily`
- `POST /brief/daily`
- `GET /kitchen/items`
- `POST /kitchen/items`
- `DELETE /kitchen/items/{item_id}`
- `GET /kitchen/summary`
- `GET /kitchen/shopping-list`
- `GET /car/reminders`
- `POST /car/reminders`
- `POST /car/reminders/{reminder_id}/done`
- `GET /car/summary`
- `POST /car/trip`
- `GET /automations/learned`
- `POST /automations/learned`
- `GET /automations/proposals`
- `POST /automations/propose`
- `POST /automations/proposals/{proposal_id}/accept`
- `POST /automations/proposals/{proposal_id}/dismiss`
- `POST /automations/evaluate`
- `GET /users/profiles`
- `POST /users/profiles`
- `POST /users/profiles/{profile_id}/seen`
- `GET /privacy/audit`
- `GET /privacy/export`
- `POST /privacy/import`
- `DELETE /privacy/sections/{section}`
- `GET /security/contacts`
- `POST /security/contacts`
- `POST /security/alerts/{alert_id}/escalate`
