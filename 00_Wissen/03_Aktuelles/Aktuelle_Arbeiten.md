# 📋 Aktuelle Arbeiten — Arbeitsjournal

> Tägliche Dokumentation der kompletten Arbeit am AI-OS (von Claude geführt).
> Zweck: Überblick behalten + aus dem Code lernen. Neuester Tag oben.
> Details zur Architektur: [[../../docs/AI-Engineering-Roadmap|Roadmap]] · Lernguide: `docs/AI-OS-Backend-Lernguide.html`

---

## 2026-10-13 — Profit-Intelligence (Amazon-Arbitrage): Konzept + Wirtschaftlichkeits-Gate

**Was:** `10_Business/01_Marktprodukte/Trace AI Commerce/Modul-Profit-Intelligence/` (nachträglich als Modul 6 unter Trace AI Commerce eingeordnet, das bisher nur als KI-Fabrik-Auftrag existierte) – Produktplan
(README), Mermaid-Architektur (`Plannung/Architektur.md`) und Gate-Dokument
`wirtschaftlichkeit-profit-intelligence.md`. Noch **kein Code** – Status WARTET_AUF_FREIGABE.

**Warum so:** Der Ursprungsvorschlag (n8n + neues FastAPI + Streamlit + Postgres) hätte
Parallel-Infrastruktur gebaut; im AI-OS gibt es `backend/` (:8000), Node-RED, LiteLLM und
das Dashboard schon → Plan auf Bestand umgebogen.

**Lern-Highlights:**
- Profit Engine = deterministischer `Decimal`-Kern, LLM nur für Bericht/Datenlücken.
- Jede Zahl braucht eine Datenklasse (BEOBACHTET/OFFIZIELL/GESCHAETZT/UNBEKANNT).
- Gate-Ergebnis: Die Software verdient selbst nichts – Geld kommt nur aus Handelsmarge.
  Basis ≈ 242 €/Monat bei ≈ 9 €/h → erst 4 Wochen manueller Test (max. 500 € Ware),
  Software nur bei bestandenem Meilenstein.
- Modul B (Seller-Growth / „Schwungrad"-Werbung von Fischer & Habel) geparkt: Anbieter-
  Fallstudien sind keine Planungsgrundlage, Umsatz ≠ Gewinn.
- **Nachtrag:** CEO-Freigabe erteilt (GO_MIT_AUFLAGEN), Fokus Plattform-APIs (SP-API inkl.
  Listings Restrictions für Ungating, Keepa, eBay Browse, Kaufland/Otto). Architektur-Bild
  `Plannung/Architektur-Modul6.svg/.png` – PNG ohne Zusatztool über Chrome headless
  (`chrome --headless=new --screenshot=... datei.svg`) gerendert.
- KI-Assistenten-Werbung recherchiert (ChatGPT Ads Self-Serve in DE seit Ende Aug. 2026,
  Google AI Mode nur Tests, Perplexity ohne Ads) → in Trace-AI-Commerce-README für Modul 3/7.

---

## 2026-10-12 (2) — Tagesimpuls & Kalender-Wecker für den Raspberry Pi 4

**Was:** `03_Abläufe/Remote/Daily/Tagesimpuls-Kalender/` – Python-Dienst mit systemd-Timern:
07:00 Morgen-Push (Termine + Sprichwort/Wortwahl-Tausch/EQ-Übung/Affirmation/Witz, DE + VI),
minütlicher Kalender-Wecker (ntfy-Push mit Ton, Wecker-Termine Priorität 5 + Ton am Pi),
01.06./01.12. Finanz-/Steuer-Erinnerung mit Buttons zu WISO, Finanzplan (Drive), ELSTER.
Ziel des CEO: EQ, Umgang mit Menschen und positive Wortwahl täglich trainieren.

**Warum so:**
- Google Calendar kann selbst nur stille Pop-ups/E-Mails → Ton/Wecker über **ntfy** (Priorität 5 =
  Dauer-Alarm in der Android-App). Wecker-Kennzeichen direkt im Kalender: ⏰ im Titel oder Farbe Tomate.
- **Service-Account** statt OAuth: Pi ist kopflos, kein ablaufendes Refresh-Token.
- Inhalte **kuratiert** in `inhalte.json` statt LLM: vietnamesische Texte müssen stimmen, Pi4 hat kein gutes Modell.
- Rotation **zustandslos** (jährlich gemischte Reihenfolge, Tag-des-Jahres-Index).
- ntfy per **JSON-POST**: HTTP-Header sind Latin-1 → Vietnamesisch/Emoji im Titel würden brechen.

**Stolpersteine:** Claude-Kalender-Connector hatte nur Leserechte (create_event abgelehnt) → Termine legt der
Pi selbst an (`finanztermine-anlegen`, idempotent über extendedProperties) + .ics zum Sofort-Import.
Finanz-Excel lag nicht im Drive des verbundenen Kontos (ai.tiepvu@) → Link vom CEO, nur in `.env`/.ics (gitignored).
ICS: Kommas/Semikolons escapen. `.gitattributes eol=lf`, sonst bricht `install_pi.sh` nach Windows-Checkout.

---

## 2026-10-12 — EMVIA: Planung KI-Assistenten-Familie (Copilot Studio)

**Was:** Planungspaket `00_Wissen/03_Aktuelles/Active/EMVIA-KI-Assistenten/` für den Start am 15.10.:
Gesamtplan mit Mermaid-Architektur (Admin-Cockpit als Orchestrator + 6 Fach-Agenten: Ticket,
Monitoring/Verfügbarkeit, Sicherheit, Automatisierung JML, Helpdesk, Kommunikation), Fahrplan in
5 Phasen, Kosten, Datenschutz/Betriebsrat, Kennzahlen; Instructions-Texte je Agent (RKZFE);
Infosammlung Woche 1 (rexx, Ticketsystem, MDM, Fachanwendungen, Copilot-Lizenzen).

**Warum so geschnitten:**
- **Flows vor Agenten:** Health-Checks, SLA-Uhr, Ablaufwarnungen laufen als Power Automate *ohne KI*
  (keine Copilot Credits). Die KI kommt erst beim Zusammenfassen/Bewerten/Formulieren dazu —
  autonome Auslöser kosten Credits pro Ausführung, auch ohne Nutzer.
- **rexx = Quelle der Wahrheit für Ein-/Austritte** → späterer Auslöser für JML über Entra
  API-gesteuerte Bereitstellung (Entra P1). Ob rexx eine Schnittstelle hat, ist offen.
- **Zwei Zielgruppen trennen:** Mitarbeitende (Helpdesk, nur geprüfte Artikel) vs. IT-Team (Cockpit).

**Stolpersteine / offen:** Ticketsystem- und MDM-Produkt unbekannt; Apple-MDM-Push-Zertifikat als
erstes in die Ablaufüberwachung; Security Copilot ggf. schon über E5 vorhanden → dann nicht nachbauen.
Kostenzahlen stammen aus Drittquellen, vor dem Pitch offiziell prüfen.

---

## 2026-10-10 — IT-Werkbank: M365 Admin-Betrieb 2026 (Diagramm, Wiki, Vorlagen)

Anlass: Vorbereitung EMVIA-Start. Frage: Was ist neu in M365, und wie löse ich
Kennwort-/Konto-/Berechtigungs-/VPN-Tickets schneller, automatisiere sie und
erkenne Probleme proaktiv aus Logs?

**Gebaut**
- Diagramm `web/m365-admin-betrieb-2026.svg`: ① Eingang/Triage → ② Self-Service →
  ③ Automatisierung → ④ Admin manuell, ⑤ Logs → Log Analytics → Alarm → Ticket
  (Rückkopplung = proaktiv), dazu Box „Neu 10/2026“ und Zugang via Entra Private Access.
- Wiki `wissen/emvia/08`–`11`: Neu in M365, Ticket-Schnellhilfe (Fehlercodes,
  TAP, Sperren, Berechtigung „woher soll der Zugriff kommen?“, VPN/GSA),
  Automatisierung (Lifecycle Workflows, Managed Identity, Remediations),
  Monitoring (KQL, Alarme, Routine, Datenschutz).
- Paket `app/paket_emvia_betrieb.py` (eigene PAKET_ID `emvia-betrieb-v1`, 11 Vorlagen):
  Benutzer-Schnelldiagnose, TAP/Sitzungen widerrufen, Berechtigungs-Check,
  Morgen-Check, ablaufende Secrets, Remediation-Muster, 2× KQL, 2 Tickets, Routine.

**Warum eigenes Paket statt Erweiterung von `paket_emvia_m365`?** Pakete werden je
Instanz genau einmal eingespielt (Marker in `vorlage_paket`). Neue Einträge im alten
Paket kämen in bestehenden DBs (lokal, Pi4) nie an → neue PAKET_ID nötig.

**Recherche-Stolpersteine (Stand 10.10.2026)**
- Seit 01.10.2026 ist EWS in Exchange Online standardmäßig blockiert (endgültig 01.04.2027,
  MC1227454). Das wird typische „Scanner/Fachanwendung geht plötzlich nicht“-Tickets erzeugen.
- Seit 01.10.2026 greifen die alten ID-Protection-Risikorichtlinien nicht mehr. Der Ausfall
  ist still, ohne Fehlermeldung → als CA-Richtlinien nachbauen.
- Intune-Suite-Funktionen sind seit 07/2026 in E3/E5 (Remote Help in beiden, EPM nur E5).
- Angekündigte Termine (Passkey-Standard 09/2026, B2B-Passkeys 10/2026) im Wiki bewusst
  als „angekündigt“ formuliert, weil nicht bestätigt.

**Verifikation:** 6 PowerShell-Skripte mit dem PS-Parser geprüft (0 Fehler), Text-Überlauf im
SVG per getBBox geprüft, lokaler Container neu gebaut (Vorlagen 27 → 38), Wiki lokal
eingespielt (12 Seiten). Pi4: noch nicht (Basic-Auth + Rebuild offen).

## 2026-10-09 (2) — IT-Werkbank: EMVIA M365 & MDM + Generator-Module

Anlass: Start als IT-Admin M365 & MDM bei der EMVIA Living GmbH (Hamburg) am
15.10.2026. Gebaut: Modul `emvia` (Steckbrief automatisch im Chat-Kontext),
27 Vorlagen (Graph/EXO/Intune-Skripte mit Testlauf, Mails, Tickets, Checklisten),
Werkzeug „On-/Offboarding“, FAQ-Wiki (`app-live/wissen/emvia`), M365-Architektur-
diagramm, Module PowerShell-/Prompt-/Datenbank-Generator.

### Stolpersteine (lernen!)

1. **Das Modell ist der Engpass, nicht der Prompt:** Cloudflare `llama-3.1-8b`
   erfand Cmdlets (`New-MgGraphClient`, `Set-MgUserMailbox`). Mit DEMSELBEN
   Cloudflare-Zugang laufen `qwen2.5-coder-32b` und `llama-3.3-70b` korrekt in
   < 2 s → Modellwahl je Modul (`llm.frage(code=True)`), 8B nur noch Fallback.
2. **Prompts können falsch lenken:** „MSOnline/AzureAD → Graph“ ließ das Modell
   Postfach-Einstellungen über Graph lösen (geht nicht, das ist Exchange). Lösung:
   explizite Zuordnung „Postfächer = ExchangeOnlineManagement“.
3. **Zu viele Rückfragen:** Regel „frage bei fehlenden Angaben“ → kleines Modell
   fragte bei klaren Aufgaben nach Tenant-ID. Besser: sofort liefern, Annahmen nennen.
4. **Prompt-Generator schrieb Python-Code**, weil „Codeblock“ im Prompt stand →
   ausdrücklich „KEIN Programmcode, nur Prompt-Text“ und Überschriften vorgeben.
5. **Seed-Daten in genutzten DBs:** Die alte Erstbefüllung lief nur bei leerer
   Tabelle → neue Tabelle `vorlage_paket` merkt sich je Paket „schon eingespielt“.
6. **Akzente:** „Zoë“ wurde zu „zo“ → erst ä/ö/ü/ß ersetzen, dann Unicode-NFD und
   Akzentzeichen entfernen (PowerShell `\p{Mn}`, JS `[̀-ͯ]`), in Skript
   UND Generator identisch.
7. Generierter Code ist erst „fertig“, wenn er durch den echten PowerShell-Parser
   gelaufen ist (`[Parser]::ParseFile`), hier: 30/30 ok.

---

## 2026-10-09 — LeadPilot: Markt-Radar (regional + global) + Marktanalyse

CEO-Strategie „Kombi-Modell": Großprojekte Healthcare-IT (KIS/PVS, HL7/FHIR,
Berechtigungen in Kliniken, öffentlicher Sektor) + lokale KMU (Praxen, Zahnärzte,
Physio, Pflegedienste, Steuerberater) + eigene Produkte. Auftrag: besserer
Lead-Generator + Marktrecherche. Umgesetzt im bestehenden LeadPilot (:5330),
neues Modul `app/marktradar.py`.

**Neue Quellen (alle live getestet):** Arbeitsagentur-Jobsuche `pc/v6` (v4 gibt
inzwischen 403!) mit Header `X-API-Key: jobboerse-jobsuche`, `angebotsart=2` =
Selbständigkeit; service.bund.de-RSS (500 Ausschreibungen); TED-API v3 (EU,
anonym, Expert-Query mit CPV 72*/48*); Arbeitnow. Verworfen: HN-„Freelancer?“-Thread
(letzter Thread 10/2025, also tot), freelancermap-RSS (404).

**Bewertung:** gewichtete Segmente statt reiner Keyword-Zählung, Titeltreffer
zählen doppelt, +4 Region MV/HH, +3 Ausschreibung/Freelance, +3 Kombi-Bonus
Healthcare × (IAM|Integration|KI), Mindest-Score 8.

**Marktanalyse-Tab:** Markt-Log (bleibt auch nach „Übernehmen“) → Segmente,
Keywords, Wochen-Trend, Produkt-Hypothesen. Branchen-Chancen = OSM-Betriebszahl
(`out count`, keine Einzeldaten) × Profil (Abhängigkeit, Zahlungsbereitschaft,
IT-Reife-Lücke, Wettbewerb).

### Stolpersteine (lernen!)

1. **Falsche Treffer nach Bedeutung, nicht nach Syntax:** Kliniken schreiben
   viel *Bau* aus → „Neubau OP-Trakt“ kam als Healthcare-IT rein. Und die
   BA-Suche nach „Krankenhausinformationssystem“ liefert auch Pflege-/MFA-Stellen
   derselben Klinik. Lösung: zwei Schranken: `IT_PFLICHT` + `BAU_AUSSCHLUSS` für
   Ausschreibungen, `IT_ROLLE` für Stellen (im Titel/Beruf).
2. **Regex ohne Wortgrenze:** `entra` traf „zentral“, `kommun` traf
   „Kommunikation“, `administrat` traf „administrative Terminambulanz“. Erst die
   Top-Keyword-Liste in der UI hat das sichtbar gemacht. **Ergebnisse ansehen,
   nicht nur zählen.**
3. **`\b` wurde zu Backspace:** Python-Code per Bash-Heredoc geschrieben, dabei
   wurde `\\b` → Steuerzeichen 0x08. Die Regex war dann still kaputt (kein
   Fehler!). Erkannt an `grep -c $'\x08'`. Lehre: Regex-Code nur mit dem
   Editor-Tool schreiben, nicht über die Shell.
4. **Öffentliche Overpass-Server sind unzuverlässig** (406/500/504). Eine
   Sammelabfrage für Hamburg ist zu schwer → eine Abfrage je Branche, drei
   Spiegel, und eine **Fehlversuch-Sperre (1 h)**, damit nicht jeder Seitenaufruf
   80 s hängt. Gemessen: 82 s → 0,4 s.
5. **Zwei Instanzen auf Port 5330:** Windows lässt doppeltes Binden zu; die alte
   Instanz hat weiter alten Code ausgeliefert. Vor jedem Neustart `netstat` prüfen.

---

## 2026-07-25 (Tag 13) — Hermes-Debugging-Marathon: echte Root Causes gefunden, Multi-Instanz-Architektur etabliert

CEO-Auftrag: "prüfe die hermes und seine konfiguration und mach weiter was
gestern noch da ist". Wurde zu einem sehr langen Debugging-Tag mit
mehreren echten, tief verschachtelten Ursachen — am Ende stabile,
dokumentierte Lösung für beide Hermes-Instanzen.

1. **Windows-Autostart-Race-Condition gefunden**: nach PC-Neustart heute
   Morgen liefen 3 von 4 Diensten (MCP-Server, Agent-System, LiteLLM) NICHT
   mehr — Crash mit `WinError 10049` ("Adresse ungültig in diesem
   Kontext"), weil die Aufgabenplanung ("Bei Anmeldung") sofort beim Login
   feuert, die Tailscale-Netzwerkschnittstelle aber verzögert hochfährt.
   **Fix**: `wait_for_bindable()`-Hilfsfunktion in allen drei Skripten
   (`mcp_server.py`, `agent_system.py`, `litellm_gateway.py`) — wartet bis
   zu 60s auf die Zieladresse, bevor der Server bindet.
2. **Ollama-Autostart hatte einen eigenen, subtileren Bug**: ein separater
   `ollama app.exe`-Elternprozess (Tray-Icon-Manager) respawnt bei jedem
   Neustartversuch einen neuen `ollama.exe serve`-Kindprozess mit SEINER
   eigenen (alten) Umgebung — Beenden nur des Kindprozesses wirkungslos.
   Neuer Autostart-Wrapper `04_Infrastruktur/Runtime/ollama_autostart.py`
   beendet beide Prozessnamen, bindet an `0.0.0.0`/`::` (deckt lokalen UND
   Tailscale-Zugriff gleichzeitig ab, statt nur eine spezifische IP).
3. **Cronjob-Sicherheitsbremse entdeckt**: der gestrige Blog-Cronjob lief
   pünktlich um 8 Uhr, wurde aber von Hermes' eigenem "config drift"-Schutz
   gestoppt (Modell hatte sich seit Job-Erstellung geändert) — bewusstes
   Sicherheitsfeature, kein Bug, aber zeigt: Modell-Wechsel sollten bewusst
   erfolgen, nicht nebenbei.
4. **ECHTER Durchbruch beim Tool-Calling-Problem (mehrschichtige Ursache,
   endlich vollständig aufgeklärt)**:
   - Kontextfenster 16K → 64K erhöht (Ollama `OLLAMA_CONTEXT_LENGTH`) —
     nötig, aber allein nicht ausreichend UND macht jede Anfrage langsamer.
   - Cloudflare Workers AI getestet: schnell, aber "Request payload too
     large" — Hermes' großer Prompt sprengt das Anfragelimit.
   - OpenRouter mit falschem Modell-Slug probiert (`anthropic/claude-3.5-
     haiku` existiert nicht, richtig: `anthropic/claude-haiku-4.5`).
   - **Der eigentliche Haupttreiber war die schiere PROMPT-GRÖSSE**: 77
     vorinstallierte Skills bliesen den System-Prompt auf ~20.000 Zeichen
     auf. `hermes skills opt-out --remove --yes` auf 3 lokale Skills
     reduziert (System-Prompt von ~20.000 auf 12.559 Zeichen) — spürbare,
     aber nicht vollständige Verbesserung (Tool-Schemas selbst bleiben mit
     45,7KB/27 Tools der größere Rest-Posten).
   - Trotzdem blieben Multi-Schritt-Skill-Aufgaben (Datei lesen → Befehl
     ausführen → Ergebnis interpretieren) auf JEDEM getesteten Anbieter
     langsam bis zum Hängenbleiben (>10 Minuten in einem Fall).
   - **CEO-Fund per eigenem Dashboard-Test**: Modell `nvidia/nemotron-3-
     super-120b-a12b:free` (OpenRouter, kostenlos, MoE-effizient) läuft
     "wirklich gut und schnell" — jetzt auf beiden Instanzen aktiv.
5. **KRITISCHER Konfigurationsfehler auf der PC-Seite gefunden**: die
   bereits am 10.07. installierte Hermes-Desktop-App (v40.10.2) hatte NIE
   funktioniert ("gar kein Chat") — Ursache: eine Umgebungsvariable
   `HERMES_HOME=C:\Users\vuxua\AppData\Local\hermes` leitete auf eine GANZ
   ANDERE Config um als die, die unter `~/.hermes` sichtbar/editierbar war
   — dort stand `provider: huggingface` mit **aufgebrauchtem Guthaben**
   (HTTP 402), seit Monaten unbemerkt. Kein Hermes-Bug, sondern zwei
   parallele, nie synchronisierte Config-Stände.
6. **CEO-Entscheidung: Multi-Instanz-Architektur mit getrennten Rollen**
   (löst die Geschwindigkeits-Spannung strukturell, nicht durch weiteres
   Tuning): PC-Hermes = interaktiv, AI-OS-fokussiert (eigene `ai-os`-Skill,
   direkter `host.docker.internal:8000`-Zugriff aufs native AI-OS-Backend);
   Pi-Hermes = 24/7-Hintergrundarbeiter (Cronjobs, Websuche/Scraping,
   künftig Messaging-Kanäle) — jede Instanz mit eigenem Gedächtnis/Rolle,
   kein Versuch mehr, EINE Instanz für alles schnell UND mächtig zu machen.
7. **PC-Hermes-Desktop-App komplett deinstalliert, durch Docker ersetzt**
   (CEO-Wunsch: sicherer, sauberer Autostart, isolierte Umgebung wie beim
   Pi). Kein regulärer Windows-Uninstaller vorhanden (portable Installation)
   — manuell bereinigt: Prozesse, zwei Verknüpfungen (Startmenü + Desktop),
   `AppData\Local\hermes`, `AppData\Local\com.nousresearch.hermes.setup`,
   `~/.hermes` (alter, nie genutzter Config-Stand), `HERMES_HOME`-Variable.
   Neu aufgesetzt mit `docker-compose.windows.yml` (offiziell im Repo,
   NousResearch hat Windows-Docker-Desktop-Kompatibilität bereits bedacht:
   kein `network_mode: host`, explizite Portmappings, `host.docker.internal`
   statt `127.0.0.1` für Host-Zugriff aus dem Container). **Zwei Stolper
   dabei**: (a) zwei parallel gestartete `docker compose up`-Prozesse
   blockierten sich beim Image-Pull gegenseitig — sauber einzeln neu
   gestartet; (b) Dashboard verweigerte den Start bei `--host 0.0.0.0`
   ohne Auth-Provider (dieselbe DNS-Rebinding-Schutzlogik wie beim Pi,
   siehe 24.07.) — behoben mit `dashboard.basic_auth` (Username+Passwort-
   Hash in config.yaml).
8. **Alte SSH-Tunnel-Altlast gefunden**: Port 9119 war noch vom gestrigen
   SSH-Tunnel zur Pi-Instanz belegt, blockierte den neuen PC-Container-
   Dashboard-Port — Tunnel-Prozess beendet, seitdem kein Tunnel mehr nötig
   (PC-Dashboard direkt unter `localhost:9119` erreichbar, dank Docker
   Desktops Portmapping).

**Ergebnis am Sitzungsende**: beide Hermes-Instanzen laufen und antworten
korrekt (End-to-End getestet, "Hallo" in ~22s über die PC-Docker-Instanz).

**Offen für nächstes Mal**: (1) Discord/Slack-Bot-Tokens (CEO-Aktion),
(2) Multi-Schritt-Skill-Aufgaben (nicht nur einfache Fragen) auf beiden
Instanzen nochmal unter reduziertem Skill-Set/mit `nemotron-3` testen —
war vor dem Modellwechsel der eigentliche Langsamkeits-Explosionspunkt,
noch nicht nach dem Fix erneut verifiziert, (3) `hermes-agent`-Repo-Klon
auf dem PC (`C:\Users\vuxua\hermes-agent`) ist nur für den Docker-Build/
die Compose-Datei da, kein aktiver Arbeitsklon, (4) defekte Pi-SSD-Situation
weiterhin ungeklärt (Garantie/RMA).

### Nachtrag (selber Tag) — Dashboard-Passwort, Backend-Autostart, Multi-Schritt-Test, Hindsight-Memory

9. **Dashboard-Passwort-Hash-Falle**: CEO trug das Passwort selbst in
   `config.yaml` ein, aber zunächst als Klartext statt als `scrypt$...`-Hash
   (`password_hash` erwartet zwingend den Hash, kein Klartext-Fallback-Feld
   an dieser Config-Position). Symptom war nicht sofort offensichtlich —
   der Dashboard-Container startete äußerlich unauffällig, aber ein
   `docker logs`-Check zeigte "Refusing to bind dashboard ... no auth
   providers are registered" aus vorherigen (kaputten) Start-Zyklen im
   Log-Puffer. Nach korrektem Hash (CEO hat den `hash_password()`-Befehl
   selbst ausgeführt) sauberer Start bestätigt, Login-Endpoint-Test mit
   Falsch-Passwort ergab korrekt `401 Invalid credentials` (Beweis: Auth-
   Pipeline funktioniert, keine Registrierungs-Fehler mehr).
10. **AI-OS-Backend war schlicht nicht gestartet** — das erklärte eine
    vorherige verwirrte/halluzinierte Hermes-Antwort zu "Broki-AI" (Hermes
    versuchte den `ai-os`-Skill zu nutzen, bekam `Connection refused` von
    `host.docker.internal:8000`, keine Klartext-Fehlermeldung, driftete
    stattdessen in Spekulation ab). Backend manuell neu gestartet
    (`backend/.venv/Scripts/python.exe -m uvicorn app.main:app`, da `uv`
    nicht mehr im PATH auffindbar war), danach als 5. Aufgabenplanung-
    Eintrag "AI-OS Backend" verstetigt (neuer Wrapper
    `04_Infrastruktur/Runtime/backend_autostart.py`, gleiches
    `wait_for_bindable()`/pythonw-Logdatei-Muster wie die anderen vier).
    Kill-und-Neustart-über-Task-Test erfolgreich.
11. **Multi-Schritt-Skill-Test nachgeholt** (Punkt (2) von oben, jetzt
    verifiziert): `hermes -z "..." --yolo` Einzeiler auf BEIDEN Instanzen
    mit echten Skill-Ketten (Skill lesen → curl → JSON interpretieren →
    Antwort formulieren) getestet — PC (`ai-os`-Skill, Backend-Status-
    Abfrage) und Pi (`ai-os-second-brain`-Skill, Broki-AI-Recherche im
    Second Brain) liefen beide schnell und korrekt durch, keine Hänger
    mehr. Der Pi-Test beantwortete nebenbei genau die Frage, an der die
    PC-Instanz vorher gescheitert war (Broki-AI) — zeigt aber auch: die
    beiden Instanzen haben unterschiedliches Wissen (PC kennt nur, was im
    AI-OS-Backend/RAG steckt, nicht das Second-Brain-Wiki direkt).
12. **Memory-Provider-Analyse + Hindsight lokal eingerichtet** (Ersatz für
    den beim App-Umzug verlorenen `SUPERMEMORY_API_KEY`): alle drei vom
    CEO genannten Kandidaten (Honcho, Hindsight, Supermemory — "Poncho"
    war vermutlich eine Verhörung von Honcho, das schon im alten Pi-
    Leitfaden als Tier-3-Memory stand) direkt aus dem gebündelten Hermes-
    Plugin-Code geprüft statt aus dem Gedächtnis geraten. Hindsight ist die
    einzige Option mit echtem lokalem Modus (`local_embedded`) ohne API-
    Key/Cloud-Abhängigkeit, nutzt dabei das bestehende Ollama direkt als
    LLM-Backend — passt zur "00_Wissen IMMER lokal"-Regel. Eingerichtet
    über direktes Schreiben der Config-Dateien (der interaktive
    curses-Setup-Wizard ist über `docker exec` nicht scriptbar):
    `config.yaml` (`memory.provider: hindsight`),
    `~/.hermes/hindsight/config.json` (`mode: local_embedded`,
    `llm_provider: ollama`, `llm_model: gemma4`), `.env`
    (`HINDSIGHT_LLM_API_KEY=ollama`), Paket `hindsight-all` per `uv pip
    install` in den Container-venv nachinstalliert (~200MB, dauert).
    **Eigener Stolperstein gefunden+behoben**: erster Versuch mit
    `llm_base_url: http://host.docker.internal:11434` (ohne `/v1`) ergab
    `HTTP 404` bei der LLM-Verbindungsprüfung im Daemon-Log — Ollamas
    OpenAI-kompatibler Endpunkt braucht den `/v1`-Pfad-Suffix (wie schon
    beim bestehenden `fallback_providers`-Eintrag). Nach Korrektur +
    Löschen der zwischengecachten Profil-Env-Datei (`~/.hindsight/
    profiles/hermes.env`, wurde sonst nicht neu geschrieben) + Neustart:
    Verifizierungs-Session ("Merke dir: mein Name ist Tiep...") und
    komplett neue Folge-Session ("Wer bin ich?") über zwei getrennte
    `hermes -z`-Aufrufe bestätigten echtes sessionübergreifendes
    Gedächtnis funktioniert End-to-End.

**Restlich offen**: Discord/Slack-Bot-Tokens weiterhin CEO-Aktion,
Pi-SSD-Garantie/RMA weiterhin ungeklärt (fehlende Kaufinfos).

---

## 2026-07-24 (Tag 12) — Pi4-Bootloader-Reparatur (SSD-Korruption), Authentik-Crash-Loop gestoppt

CEO-Ausgangslage: Pi4 (`pi-ki-tiep`) war seit dem 23.07.-Dateisystem-Fund
("bad block bitmap checksum" auf der externen 2TB-SSD, vertagt) nicht mehr
zuverlässig erreichbar. Fortsetzung: CEO hat ein frisches Raspberry Pi OS auf
eine SD-Karte geflasht, um von dort aus die SSD unabhängig zu prüfen — genau
der am 23.07. als "eigenes, größeres Vorhaben" notierte Reparaturweg.

1. **Zugriffsweg geklärt**: weder Tailscale (Pi zeigte dauerhaft "offline,
   last seen 13h ago") noch SSH funktionierten zum frischen SD-System — CEO
   hatte stattdessen eine Remote-Desktop-Sitzung direkt auf den Pi-Bildschirm.
   Arbeitsmodus: CEO tippt Befehle im Pi-Terminal ein, postet mir die Ausgabe,
   ich werte aus und gebe den nächsten Befehl vor (kein direkter SSH-Zugriff
   während dieser Phase).
2. **Geräte-Umbenennung durch SD-Boot verstanden**: nach dem Boot von der
   SD-Karte wurde die SD-Karte selbst zu `/dev/sda` (root `/`), die externe
   SSD zu `/dev/sdb` — `sdb2` (1,9TB, ext4, Label `rootfs`) war dabei NICHT
   automatisch gemountet, konnte also direkt geprüft werden ohne vorher
   auszuhängen.
3. **Diagnose bestätigt exakt den 23.07.-Befund**: `sudo e2fsck -fn /dev/sdb2`
   zeigte ausschließlich "Group NNNN block bitmap does not match checksum" —
   keine Inode-/Extent-/Verzeichnisstruktur-Fehler, also reine
   Speicherplatz-Buchhaltung, keine Dateiinhalt-Korruption.
4. **Echter Reparaturversuch, aber nicht konvergent**: `sudo e2fsck -fy
   /dev/sdb2` lief durch (Exit 1 = "repariert"), ein direkt anschließender
   Lesecheck (`-fn`) zeigte aber wieder Fehler — stabil bei 892 Checksummen-
   Fehlern über mehrere Wiederholungsrunden hinweg (kein Sinken, kein
   Steigen). `dmesg` zeigte während der gesamten mehrminütigen Scans KEINE
   I/O-Fehler (USB/SCSI), `e2fsck`-Version 1.47.2 ist aktuell, Dateisystem-
   Status laut `tune2fs` "clean", nicht read-only. **Root Cause bleibt
   ungeklärt** (vermutlich eine Eigenheit der `metadata_csum_seed`-Berechnung
   bei dieser sehr großen Gruppenzahl, ~15.600 Gruppen bei 2TB) — aber klar
   abgegrenzt von echter Datenkorruption. **CEO-Entscheidung**: akzeptieren
   und normal weiternutzen (gleiche Linie wie schon am 23.07.), keine
   Neuformatierung.
5. **Bootloader-Fix gefunden, ohne EEPROM-Änderung nötig**: `rpi-eeprom-
   config` zeigte kein explizites `BOOT_ORDER` → Standardreihenfolge
   `0xf41` (SD-Karte zuerst, dann USB/SSD als Fallback, dann Schleife). Die
   SD-Karte hat also nur deshalb dominiert, weil sie einfach zuerst geprüft
   wird und dabei sofort erfolgreich bootet — kein Hardware- oder
   Firmware-Defekt. Lösung: SD-Karte bei ausgeschaltetem Pi entfernen, dann
   fällt der Standard-Bootpfad automatisch auf die (geprüfte) SSD zurück.
6. **Wichtige Sicherheits-Klarstellung zum Herunterfahren** (CEO fragte
   besorgt nach, ob ein "kalter Stromstart" nötig sei): das Korruptionsrisiko
   aus der 23.07.-Analyse betrifft nur den Fall, dass die SSD WÄHREND sie
   gemountet/beschrieben wird ihren Strom verliert (ihr eigenes, vom Pi
   unabhängiges Netzteil ist die eigentliche Fehlerquelle). Ein sauberer
   `sudo shutdown -h now` nach vorherigem `umount` der SSD-Boot-Partition ist
   dagegen unkritisch — die SSD läuft während des gesamten Vorgangs
   durchgehend an ihrem eigenen Netzteil weiter, unberührt vom Pi-Neustart.
   Nach dem Entfernen der SD-Karte und Wiedereinschalten des Pi-eigenen
   Netzteils bootete das System wieder als `PI-KI-Tiep` (SSD-Installation,
   `/dev/sda2` als `/`) — per SSH/Tailscale bestätigt.
7. **Nebenbefund beim Verifizieren: Authentik-Crash-Loop.** Wiederholte
   "Sie sind nun mit »vethXXXXX« verbunden"-Desktop-Benachrichtigungen
   entpuppten sich als Symptom, nicht als eigenständiger Bug — der Swarm-
   Service `security_server`/`security_worker` (Authentik, Teil des
   `security`-Stacks) crashte alle ~5 Sekunden mit "Secret key missing"
   und wurde von Docker Swarm sofort durch einen neuen Container ersetzt
   (jeder Neustart = neues veth-Interface = neue Benachrichtigung). Root
   Cause: das benötigte Secret lag vermutlich in Swarms Raft-State, der beim
   Docker-Daemon-Fix vom 23.07. gelöscht wurde (siehe
   `docker-swarm-backup-23072026`). Passt zur schon am 23.07. offenen Frage,
   ob Authentik neben dem bereits gewählten Keycloak überhaupt noch gebraucht
   wird. **Sofortmaßnahme**: `docker service scale security_server=0
   security_worker=0` — stoppt die Schleife, Service-Definition bleibt für
   eine spätere, bewusste Entscheidung erhalten. Restlicher `infrastructure`-
   Stack (ki-memory/Qdrant, ki-cache/Redis, ki-db/Postgres, ki-hindsight-
   core/-ui) sowie `authentik-db`/`-redis` liefen sauber seit dem Neustart.
8. **Lehre fürs nächste Mal**: bei "Dateisystemfehler nach `-y`-Fix immer
   noch da" nicht automatisch von Hardware-Fehlern ausgehen — erst `dmesg`
   auf tatsächliche I/O-Fehler während des Scans prüfen (hier: keine) und die
   Fehleranzahl über mehrere Durchläufe vergleichen (stabil vs. steigend vs.
   sinkend), bevor man auf Kabel/Netzteil/Hardware tippt. Reine Bitmap-
   Checksummen-Nichtkonvergenz bei sehr großen Dateisystemen scheint eine
   bekannte, aber nicht weiter aufgeklärte `e2fsprogs`-Eigenheit zu sein.

**Nachtrag, gleicher Tag: Hermes-Setup-Versuch deckt echte, aktive
SSD-Korruption auf — Punkt 4 muss revidiert werden.**

9. **Hermes-Ordnerstruktur geprüft, Klon intakt**: `~/hermes-agent` (geklont
   23.07. während der Krise) — `git status` sauber, `git fsck --full` findet
   keine beschädigten Objekte. Kein Neuklonen nötig. Repo bringt eigene
   `docker-compose.yml` mit (`network_mode: host`, zwei Services `gateway`+
   `dashboard`), läuft komplett unabhängig vom Swarm-Stack — die am 23.07.
   befürchtete Netzwerk-Inkompatibilität war kein Problem, weil Hermes gar
   nicht in Swarm läuft. `.env` (HERMES_UID/GID) ergänzt, `~/.hermes/SOUL.md`
   neu angelegt (AI-OS-CTO-Identität nach Hermes' eigener SOUL.md-vs-AGENTS.md-
   Konvention: Identität/Ton gehört in SOUL.md, Projektwissen in AGENTS.md).
10. **Docker-Build deckt verstreute Content-Store-Korruption auf**: erste
    Build-Versuche scheiterten reihenweise mit "invalid character X looking
    for beginning of value" beim Auflösen von Basis-Images (uv, node) —
    keine Netzwerk-/Registry-Probleme (curl zu ghcr.io lieferte valides
    JSON), sondern lokal korrupte Blobs in
    `/var/lib/containerd/.../blobs/sha256/`. Da jeder Blob nach seinem
    eigenen SHA256 benannt ist, ließ sich der GESAMTE Content-Store
    systematisch prüfen (Datei-Hash gegen Dateiname) — Ergebnis: 17 weitere
    korrupte Blobs, alle mit Zeitstempel exakt im 23.07.-Krisenfenster
    (16:20-16:36 Uhr). Per `ctr content rm` bzw. direktem `rm` entfernt.
11. **Docker-Desktop-Fernzugriff eingerichtet**: `docker context create
    pi-ki-tiep --docker "host=ssh://tiep@pi-ki-tiep..."` funktioniert für die
    CLI, ABER Docker Desktops GUI-Dashboard unterstützt keine beliebigen
    Remote-SSH-Contexts (nur die eigenen Desktop-Engines) — echte Lehre für
    künftige Multi-Host-Wünsche. Stattdessen **Portainer** auf dem Pi
    deployt (`docker run ... portainer/portainer-ce`, Port 9443) für eine
    echte grafische Verwaltung der Pi-Container inkl. Swarm-Stacks.
12. **Eskalation: kompletter Docker-Cache-Reset, weil einzelne Blob-Fixes
    nicht reichten.** Nach dem 17-Blob-Fund erschien beim nächsten Build
    ein NEUER Fehlertyp: `docker system df` selbst schlug mit fehlendem
    Snapshot-Verzeichnis fehl (containerd-Snapshotter, nicht nur Content-
    Store). CEO-Entscheidung: kompletten Image-/Snapshot-/Content-Cache
    zurücksetzen (`/var/lib/docker/image`, `/var/lib/docker/overlay2`,
    `/var/lib/containerd/io.containerd.{snapshotter.v1.overlayfs,
    content.v1.content,metadata.v1.bolt}` gelöscht — NICHT
    `/var/lib/docker/volumes`, wo die echten Daten liegen, 1,1GB
    unberührt). Docker/containerd neu gestartet, Swarm hat die meisten
    Dienste selbst neu gezogen und wiederhergestellt (`ki-cache`, `ki-db`,
    `ki-hindsight-core/-ui`, `authentik-db/-redis` wieder 1/1).
13. **ECHTER Wendepunkt: ein einzelnes Snapshot-Verzeichnis (`3124`) lässt
    sich weder löschen noch umbenennen — "Bad message" (EBADMSG) bei JEDER
    Operation**, auch beim reinen `mv` (das nur den Elterneintrag ändert,
    keinen Lesezugriff auf den Kindinhalt braucht). `debugfs -R stat ...
    /dev/sda2` verweigert sogar den reinen Lesezugriff mit **derselben**
    "Block bitmap checksum does not match"-Meldung wie heute Vormittag.
    **Das widerlegt die Einschätzung aus Punkt 4**: die Bitmap-Checksummen-
    Fehler sind NICHT rein kosmetisch — sie blockieren echte
    Dateisystem-Operationen auf betroffenen Inodes/Verzeichnissen. Zusätzlich
    crashte `ki-memory` (Qdrant) mit Exit 132 (SIGILL) im Crash-Loop —
    plausibel ein frisch geschriebenes, dabei in einem korrupten Block
    beschädigtes Binary. **CEO-Entscheidung nach dieser Erkenntnis**: heutige
    Docker/Hermes-Arbeit einfrieren, stattdessen Vollbackup auf externe SSD
    (`/media/tiep/Extreme SSD/PI4-Backups/`, exFAT — deshalb `tar`-Archiv
    statt direktem `rsync`, um Unix-Rechte/Besitzer/Symlinks zu erhalten)
    von `/home/tiep` (11GB) + `/var/lib/docker/volumes` (1,1GB) gestartet;
    Neuformatierung der SSD wird danach ernsthaft geplant statt weiter
    einzelne Symptome zu flicken.
14. **Lehre, die Punkt 8 korrigiert**: "keine dmesg-I/O-Fehler + Zustand
    clean" bewies nur, dass der Datenträger selbst nicht *mechanisch*
    ausfällt (kein USB-Wackelkontakt) — es bewies NICHT, dass die
    Dateisystemstruktur intakt ist. Erst der Versuch, eine ECHTE Operation
    (Verzeichnis löschen/umbenennen) auf einem betroffenen Inode
    durchzuführen, deckte den tatsächlichen Impact auf. Künftig bei
    "Bitmap-Checksum bleibt nach Reparatur bestehen" nicht vorschnell als
    kosmetisch einordnen, sondern gezielt eine schreibende Operation auf
    einer betroffenen Gruppe testen, bevor man sich auf "nur Buchhaltung"
    verlässt.

**Zweiter Nachtrag, gleicher Tag: Vollbackup erfolgreich, SSD als HARDWARE-
DEFEKT identifiziert (nicht nur Dateisystem-Korruption), Pi läuft jetzt
dauerhaft von SD-Karte.**

15. **Vollbackup abgeschlossen und verifiziert**: erster Versuch (`tar` im
    Hintergrund via `nohup ... &`) starb nach ~13 Minuten lautlos ohne
    Fehlermeldung (Ursache nicht abschließend geklärt — vermutlich
    Session-Cleanup trotz `nohup`, da `sudo` involviert war). Neustart mit
    `sudo setsid nohup ... < /dev/null &` (vollständig von der SSH-Sitzung
    gelöst, PPID=1) lief sauber durch: 12,00GB, `tar -tf` bestätigt
    "lesbar", **keine einzige echte `tar:`-Fehlermeldung** — `/home/tiep`
    und `/var/lib/docker/volumes` sind vollständig fehlerfrei gesichert
    auf `/media/tiep/Extreme SSD/PI4-Backups/pi4-backup-20260724.tar`.
    **Lehre**: bei Hintergrundprozessen mit `sudo` künftig immer `setsid`
    zusätzlich zu `nohup` verwenden und `pgrep`-Status-Checks nicht blind
    vertrauen (PID-Wiederverwendung führte hier zu falschen "läuft noch"-
    Meldungen, siehe unten).
16. **Architektur-Entscheidung, gleicher Tag: SD-Karte wird dauerhaftes
    Boot-Medium statt Rückkehr zur SSD.** SD-Karte hat sich als zuverlässig
    erwiesen; die SSD (externe Stromversorgung, wie am 23.07. dokumentiert)
    bleibt das Risiko. Umsetzung: `sudo hostnamectl set-hostname
    pi-ki-tiep` (identisch zum alten Namen, damit Broki-AI/Configs/Memory
    nicht angepasst werden müssen), Tailscale frisch installiert + `tailscale
    up --ssh` (das frische SD-OS hatte weder Tailscale noch einen SSH-Key
    hinterlegt) — Alt-Node der toten SSD-Installation bleibt vorerst als
    "offline" im Tailnet stehen, muss im Adminportal noch aufgeräumt werden.
    **Neuer SSH-Zugang eingerichtet**: kein lokaler Schlüssel auf dem
    Windows-Rechner vorhanden gewesen, daher `ssh-keygen` neu erzeugt und
    manuell in `~/.ssh/authorized_keys` eingetragen (funktioniert stabil
    über die lokale LAN-IP; Tailscale-SSH-Route blieb aus unbekanntem Grund
    "idle" ohne Verbindung — nicht weiter verfolgt, LAN-IP reichte).
17. **ECHTE Ursache endlich isoliert: Hardware-Defekt der SSD, nicht Kabel/
    Port/Software.** Nach Backup + Architektur-Entscheidung "SSD wird
    reines Datenlaufwerk" (keine Boot-Partition mehr nötig) wurde die
    Platte komplett neu partitioniert (GPT statt MBR, ein einzelnes
    ext4 über die volle 2TB). **Bereits beim Anlegen der GPT-Tabelle**:
    "Error: The backup GPT table is corrupt, but the primary appears OK" —
    auf einer GERADE ERST GESCHRIEBENEN Struktur. Nach `mkfs.ext4` (sauber
    durchgelaufen) scheiterte der ERSTE `e2fsck`/`mount`-Versuch sofort:
    "Superblock has an invalid journal (inode 8)",
    `ext4_find_extent: bad header/extent: invalid magic`. **Isolationstest**
    (CEO-Vorschlag): SSD an einen ANDEREN USB-Port umgesteckt, kompletter
    Wipe+Neuformatierung wiederholt — **identischer Fehler an identischer
    Stelle reproduziert.** Das schließt Kabel-/Port-Flackern aus (das würde
    zufällige Fehlerorte verursachen, nicht denselben Ort zweimal in Folge)
    und bestätigt einen echten, lokal begrenzten Hardware-Defekt (defekte
    NAND-Blöcke, vermutlich erschöpfter/beschädigter interner Ersatzbereich
    der SSD). `smartctl` konnte keine Diagnosedaten liefern (unbekannte USB-
    SATA-Brücke, VID:PID `048d:1234`, Modell "AL SSD"/"PSSD", unterstützt
    kein SAT-Passthrough auch nicht mit `-T permissive`).
18. **CEO-Entscheidung nach diesem Fund**: SSD wird NICHT mehr für aktive
    Docker-Daten verwendet — SD-Karte (64GB) übernimmt diese Rolle als
    Hauptspeicher. Die SSD soll nur noch als Backup-Ziel dienen. **Wichtiger
    offener Einwand von mir dazu**: eine Platte, die nachweislich frisch
    geschriebene Daten innerhalb von Sekunden korrumpiert, ist auch als
    reines Backup-Ziel nicht vertrauenswürdig — ein Backup, das man nicht
    verifizieren kann, ist trügerisch. Empfehlung fürs nächste Mal: falls
    diese SSD doch für Backups genutzt wird, IMMER mit Checksummen-
    Verifikation nach dem Schreiben arbeiten, nicht blind vertrauen.
19. **KRITISCHE SICHERHEITSNOTIZ (CEO, 24.07.2026)**: Es gibt eine DRITTE
    SSD im Besitz des CEO mit sehr wichtigen Daten, die **NIEMALS
    formatiert oder sonst wie destruktiv verändert werden darf** — noch
    keine identifizierenden Merkmale (UUID/Label/Seriennummer) bekannt, da
    sie bisher nicht am Pi angeschlossen war. **Verbindliche Regel für jede
    künftige Sitzung**: bevor IRGENDEIN destruktiver Datenträger-Befehl
    (`wipefs`, `mkfs`, `parted`, `dd` o.ä.) auf dem Pi ausgeführt wird,
    IMMER zuerst per UUID/Label eindeutig identifizieren welches Gerät das
    ist, NIEMALS nach Gerätenamen (`/dev/sdX`) blind vertrauen (siehe auch
    Punkt 17 - Gerätenamen verschieben sich je nach Bootmedium/Portreihenfolge),
    und explizit beim CEO nachfragen falls Zweifel bestehen, welche Platte
    gerade angeschlossen ist.

**Dritter Nachtrag, gleicher Tag: Hermes-Agent erfolgreich gebaut und
gestartet, Tailscale/SSH-Zugriff repariert, Feinkonfiguration begonnen.**

20. **Docker + Portainer auf der SD-Karte installiert** (offizielles
    Docker-Install-Skript, `usermod -aG docker`), sauber verifiziert
    (`docker run hello-world`). Portainer als Container deployt (Port 9443).
21. **Selektive Wiederherstellung aus dem Backup statt Vollrücksicherung**:
    nur `hermes-agent`-Repo + `.hermes`-Config aus dem `tar`-Archiv
    zurückgespielt (nicht die vollen 11GB inkl. Alt-Ballast). **Dabei echte
    stille Datenkorruption im Backup entdeckt**: 4 Dateien im
    `hermes-agent`-Repo (u.a. `contributors/emails/fanyu@moonshot.cn`)
    hatten nach dem Zurückspielen verfälschten Inhalt bei IDENTISCHER
    Dateigröße (`git diff` zeigte Binärmüll statt "FuryMartin") — der
    Ursprung liegt darin, dass das Backup noch lief, WÄHREND der Pi von der
    (später als hardwaredefekt identifizierten) SSD gebootet war; `tar`
    kopierte den bereits vorhandenen stillen Datenverfall unbemerkt mit
    (ein Lesefehler wäre aufgefallen, verfälschte-aber-lesbare Bytes nicht).
    **Sauber behoben** über Git selbst: `git fsck --full` bestätigte eine
    intakte Objekt-Datenbank, `git checkout -- .` stellte alle 4 Dateien aus
    dem korrekten Git-Store wieder her — Git-Repos sind damit gegen genau
    diese Art Backup-Korruption selbstheilend, andere (Nicht-Git-)Dateien
    aus dem Backup bleiben ein Restrisiko und wurden nur stichprobenartig
    (nicht vollständig) auf Lesbarkeit geprüft.
22. **Hermes-Docker-Build erfolgreich** (auf der sauberen SD-Karte, keine
    Korruption mehr) — Image `hermes-agent:latest`, 3,83GB, `docker compose
    up -d` startet `hermes` (Gateway) + `hermes-dashboard` sauber, s6-
    supervidiert, stabil (mehrfach über Minuten ohne Neustart geprüft).
    Das war das eigentliche Ziel seit dem 23.07.
23. **Tailscale-SSH-Rätsel gelöst: war nie ein Firewall-/Routing-Problem,
    sondern eine fehlerhafte Windows-WinHTTP-Proxy-Einstellung.** `iptables`
    auf dem Pi zeigte bereits akzeptierten Traffic auf `tailscale0`
    (326 Pakete durch die ACCEPT-Regel), `sshd` lauschte korrekt auf
    `0.0.0.0:22` — das Problem lag komplett auf der Windows-Seite. Ein
    `Test-NetConnection` in PowerShell (umgeht Proxy-Einstellungen)
    funktionierte sofort; `curl`/`ssh` mit `HTTPS_PROXY=`/`HTTP_PROXY=`
    (bzw. PowerShells Äquivalent) leer gesetzt liefen danach ebenfalls
    sauber durch. **Lehre**: bei "Tailscale ping funktioniert, aber TCP-
    Verbindungen (SSH/HTTPS) timen aus" zuerst lokale Windows-Proxy-
    Umgebungsvariablen prüfen/leeren, bevor man Firewall/ACLs auf der
    Gegenseite verdächtigt.
24. **`tailscale serve` ausprobiert, dann wieder verworfen** — technisch
    funktioniert der Reverse-Proxy (HTTPS auf Port 443 → `localhost:9119`),
    aber Hermes' Dashboard hat einen bewussten Host-Header-Schutz gegen
    DNS-Rebinding (GHSA-ppp5-vxwm-4cf7): bei Loopback-Bind werden NUR
    Loopback-Host-Header akzeptiert, der von `tailscale serve`
    durchgereichte Original-Hostname wird als "Invalid Host header"
    abgelehnt. Es gibt im Code keinen Mechanismus für eine Zusatz-
    Allowlist (nur loopback-only ODER 0.0.0.0 mit Auth-Pflicht). **Der vom
    Entwickler vorgesehene Weg ist der SSH-Tunnel**
    (`ssh -L 9119:localhost:9119 tiep@pi-ki-tiep.tailed32d1.ts.net`) — der
    erscheint dem Dashboard als Loopback-Verbindung und besteht den Host-
    Check automatisch. Funktioniert jetzt auch über Tailscale (nicht nur
    LAN), seit das Proxy-Problem (Punkt 23) behoben ist — echter
    Remote-Zugriff von unterwegs damit möglich.
25. **Tailscale-Hostname endgültig bereinigt**: alte tote SSD-Installation
    im Adminportal gelöscht, neue SD-Installation von `pi-ki-tiep-1` auf
    `pi-ki-tiep` umbenannt (zweistufig: `sudo tailscale set --hostname`
    ändert nur den selbstgemeldeten OS-Hostnamen, der tatsächliche
    Tailnet-DNS-Name muss zusätzlich im Adminportal umbenannt werden, sonst
    bleibt die `-1`-Endung bestehen).
26. **Deutsche Sprache für feste Systemtexte konfiguriert**
    (`display.language: "de"` in `~/.hermes/config.yaml`) — laut Code-
    Kommentar betrifft das NUR feste UI-Strings (Freigabe-Abfragen, ein
    paar Gateway-Befehlsantworten), NICHT die eigentlichen Agenten-
    Antworten (die passen sich als LLM ohnehin der Gesprächssprache an).
27. **Feinkonfiguration nach CEO-geteiltem Leitfaden begonnen** (Tina Huang,
    lonelyoctopus.com, "Wie man Hermes Agent richtig einrichtet"): deckt
    sich weitgehend mit dem 23.07.-Plan. Tier-4-Speicher (Second Brain)
    soll wie damals entschieden an AI-OS' EIGENES `00_Wissen/09_Wiki`
    andocken, nicht an ein separates Obsidian-Vault — technisch aber nicht
    trivial, da Hermes im Container auf dem Pi läuft, das Wiki aber auf dem
    Windows-PC liegt. Lösung: AI-OS' eigener MCP-Server (`search_knowledge`-
    Tool, Port 5001) statt Datei-Spiegelung — Hermes unterstützt MCP nativ.
    MCP-Server war nicht gestartet, gerade neu gestartet, Verbindungsaufbau
    zu Hermes noch im Gange (Fortsetzung folgt).

**Vierter Nachtrag, gleicher Tag (spätabends): Performance-Realitätscheck,
Provider-Fallback umgestellt, drei neue Skills + Cronjob live.**

28. **Echter Performance-Test lokaler Pi-Inferenz: zu langsam für
    Interaktivität.** `qwen2.5:3b` direkt auf dem Pi4 (CPU-only) gemessen:
    **~1,76 Tokens/Sekunde** (61 Tokens in 34,6s reiner Rechenzeit). CEO-
    Sorge dazu war berechtigt — für echtes Chatten unbrauchbar (100-200
    Tokens würden 1-2 Minuten dauern). **Root Cause der ursprünglichen
    24/7-Vision-Frage**: nicht die Pi-CPU als Orchestrator (die reicht für
    Hermes' Agent-Loop/Cron/Gateway locker), sondern reine LLM-Inferenz auf
    Pi-CPU ist der Flaschenhals.
29. **Architektur-Entscheidung: Hermes nutzt jetzt AI-OS' bestehenden
    LiteLLM-Gateway (Port 4000) statt eigener/lokaler Pi-Inferenz.**
    LiteLLM hat die Fallback-Kette (PC-Ollama → Cloudflare/OpenRouter/etc.)
    schon fertig gebaut — sinnvoller, Hermes daran andocken zu lassen als
    eine zweite Fallback-Logik in Hermes selbst nachzubauen. `~/.hermes/
    config.yaml` zeigt jetzt auf `http://100.124.54.34:4000/v1` (Modell
    `llama3`). End-to-End getestet: echte Antwort in 34s (inkl. Hermes-
    eigenem CLI-Start-Overhead), LiteLLM routete automatisch auf Cloudflare
    Workers AI.
30. **Drei Windows-Dienste mussten für Pi-Erreichbarkeit von `127.0.0.1`
    auf die Tailscale-Interface-IP (`100.124.54.34`) umgestellt werden** —
    gleiches Muster wie schon beim MCP-Server (Punkt 27): `OLLAMA_HOST`
    (User-Umgebungsvariable, `setx` — WICHTIG: eine bereits laufende
    PowerShell-Sitzung liest `setx`-Änderungen NICHT automatisch nach, `
    $env:VAR` zusätzlich in der aktuellen Sitzung setzen, bevor der neue
    Prozess gestartet wird), `litellm_gateway.py` (neue `LITELLM_BIND_HOST`-
    Variable, Code vorher hart auf `127.0.0.1` verdrahtet) und
    `agent_system.py` (neue `AGENT_BIND_HOST`-Variable, gleiche Änderung).
    **Lehre zum Hintergrund-Start auf Windows**: `Start-Process
    -WindowStyle Hidden` mit `-RedirectStandardOutput` lieferte wiederholt
    leere Logs und keine Portbindung (Ursache nicht abschließend geklärt) —
    zuverlässig funktionierte stattdessen `nohup ... &` über die Bash-Tool-
    Umgebung (Git Bash). **Zweite Lehre**: `netstat -ano | grep` lieferte in
    dieser Windows/Git-Bash-Kombination wiederholt falsche/leere Ergebnisse
    trotz tatsächlich lauschendem Port — `Get-NetTCPConnection` (PowerShell)
    bzw. direktes `curl` gegen den Port sind die zuverlässigeren Checks.
31. **Kritischer, selbst gefundener Konfigurationsfehler: Hermes lief die
    ganze Zeit mit FALSCHEN Einstellungen.** `sudo docker compose up`
    löste `~` in `docker-compose.yml` als `/root` statt `/home/tiep` auf —
    der Container nutzte `/root/.hermes` (von Hermes selbst automatisch mit
    Default-SOUL.md/Default-config.yaml befüllt), NICHT unsere sorgfältig
    vorbereiteten Dateien unter `/home/tiep/.hermes`. Gefunden beim
    Debuggen, warum eine neu angelegte Skill-Datei im Container nicht
    sichtbar war (Zeitstempel/Eigentümer im Container passten nicht zum
    Host-Verzeichnis). **Fix**: `docker compose` OHNE `sudo` ausführen (User
    ist bereits in der `docker`-Gruppe) — danach löst sich `~` korrekt auf.
    **Lehre**: bei Docker-Compose-Setups mit `~` im Volume-Pfad IMMER genau
    prüfen, als welcher User der Compose-Befehl tatsächlich läuft.
32. **Drei neue Hermes-Skills gebaut** (alle unter `~/.hermes/skills/`,
    sofort als "local"/"enabled" erkannt):
    - `ai-os-second-brain` — durchsucht `00_Wissen` per HTTP gegen den
      MCP-Server (`/mcp/knowledge/<query>`)
    - `ai-os-agent-team` — delegiert Aufgaben an die 10 lokalen AI-OS-
      Agenten (`/orchestrate`, `/execute` auf Port 5300)
    - `blog-research` — recherchiert täglich vuxuantiep.de + Web-Quellen,
      schreibt einen vollständigen deutschen Artikel-Entwurf, speichert ihn
      NUR als Entwurf (nie direkt ins vuxuantiep.de-Repo, CEO-Entscheidung)
33. **Neuer `/mcp/save-draft`-Endpunkt** in `mcp_server.py` ergänzt (POST
    `{title, content, source}` → schreibt Markdown mit Frontmatter nach
    `00_Wissen/03_Aktuelles/Blog-Entwuerfe/`, Dateiname aus Titel-Slug,
    doppelt gegen Path Traversal abgesichert). Live getestet, funktioniert.
34. **Täglicher Cronjob eingerichtet** (`hermes cron create '0 8 * * *' ...
    --skill blog-research --deliver origin`) — Scheduler bestätigt aktiv
    (Ticker-Heartbeat läuft), nächster Lauf 25.07.2026 08:00 UTC.
35. **CTO-Rolle/Discord-Slack-Integration**: CEO-Wunsch bestätigt (Hermes
    soll als CTO-Kontaktpunkt Aufträge über Discord/Slack entgegennehmen
    und ans Agententeam delegieren) — **bewusst vertagt**, weil das
    CEO-seitig eine Bot-App-Registrierung (Discord Developer Portal bzw.
    Slack API) mit eigenem Token braucht, die niemand für ihn übernehmen
    kann.

**Fünfter Nachtrag, gleicher Tag (Sitzungsende): Autostart dauerhaft
eingerichtet, Discord/Slack-Anforderungen geklärt, echtes Tool-Calling-
Problem NICHT gelöst, kritische Architektur-Dopplung entdeckt.**

36. **Windows-Hintergrunddienste dauerhaft per Aufgabenplanung eingerichtet**
    (überleben jetzt PC-Neustart): bestehende Aufgabe "AI-OS LiteLLM
    Gateway" wiederverwendet (Action auf `cmd.exe /c set
    LITELLM_BIND_HOST=... && pythonw.exe ...` umgestellt, da die reine
    `setx`-Registry-Variable von der bereits laufenden Sitzung nicht
    übernommen wurde), zwei neue Aufgaben "AI-OS MCP Server" und "AI-OS
    Agent System" nach demselben Muster angelegt (Trigger "Bei Anmeldung",
    `pythonw.exe`, 3× Neustart bei Fehler, 2min Abstand). **Echter Bug
    dabei gefunden und behoben**: beide Skripte prüften direkt beim Start
    `sys.stdout.encoding` — unter `pythonw.exe` (kein Konsolenfenster) ist
    `sys.stdout` aber `None`, das ließ beide Skripte sofort mit Exit-Code 1
    abstürzen. Fix: bei `sys.stdout is None` in eine Logdatei
    (`%TEMP%\ai_os_mcp_server.log` bzw. `..._agent_system.log`) umleiten
    statt auf echte Konsolen-Streams zu vertrauen. Alle vier Dienste (MCP,
    Agent-System, LiteLLM, Ollama) danach einzeln vom Pi aus verifiziert.
37. **Discord/Slack-Integrationsanforderungen dokumentiert** (CEO hat
    Accounts, aber noch keine Bot-Tokens): Discord braucht nur
    `DISCORD_BOT_TOKEN` (Developer Portal) + eigene User-ID; Slack braucht
    `SLACK_BOT_TOKEN` (xoxb-, mit 12 spezifischen Scopes) UND
    `SLACK_APP_TOKEN` (xapp-, Socket Mode, `connections:write`) UND
    aktivierte Event Subscriptions — deutlich aufwendiger. CEO hat das für
    eine künftige Sitzung vertagt (Token-Beschaffung ist CEO-Aktion).
38. **Tool-Calling-Debugging, mehrstufig, NICHT final gelöst.** Der
    CEO-Test im Dashboard (siehe Screenshot) zeigte: Hermes BEHAUPTET, die
    `ai-os-second-brain`-Skill genutzt zu haben, liefert aber komplett
    erfundene Informationen (Broki-AI als "Finanz-KI-Plattform" — falsch,
    tatsächlich eine Wiki-Browser-Extension). Ursachenkette, mehrfach
    korrigiert:
    - `llama3` (erstes Modell) hat laut Ollamas eigenen Metadaten NUR
      `"completion"`, kein `"tools"` — Modell kann grundsätzlich nicht
      tool-callen.
    - Umstieg auf `mistral`/`gemma4` (haben `"tools"`) half nicht sofort —
      **eigentliches Konfigurationsschema war falsch**: `providers:` als
      eigener Dict-Block (mein Entwurf) ist kein gültiges Hermes-Schema.
      Laut Doku muss ein eigener Endpunkt direkt unter `model:` stehen:
      `provider: custom`, `base_url:`, `api_key:` — keine separate
      `providers:`-Sektion.
    - Nach Korrektur: Anfragen an "mistral"/"llama3" über den LiteLLM-
      Gateway landeten (Antwort-Feld `model`) tatsächlich bei
      `cloudflare/@cf/meta/llama-3.1-8b-instruct` — LiteLLMs eigene
      Fallback-Kette (`workers-ai` vor `openrouter-free`/
      `huggingface-llama`) hat lokales PC-Ollama gar nicht direkt erreicht.
      Cloudflares Modell sagt selbst explizit "I'm not capable of using
      external tools".
    - Direkt gegen PC-Ollama (ohne LiteLLM-Umweg, `http://100.124.54.34:
      11434/v1`) getestet: `mistral` liefert bei einer echten
      Tool-Definition eine LEERE Antwort ohne `tool_calls`. `gemma4`
      dagegen liefert bei `tool_choice:"required"` auf API-Ebene einen
      ECHTEN, korrekten `tool_calls`-Response — das Modell selbst kann es
      also grundsätzlich.
    - Trotzdem: der volle Hermes-Agent-Lauf mit `gemma4` scheitert
      weiterhin — die finale Testantwort bestand aus dem Modell, das über
      seine EIGENEN System-Prompt-Regeln sinniert, statt den angeforderten
      Bash-Befehl auszuführen. **Root Cause bleibt ungeklärt** — vermutlich
      eine Inkompatibilität zwischen Hermes' System-Prompt-/Tool-Schema-
      Format und diesem lokalen Ollama-Modell, nicht mehr durch einfaches
      Ausprobieren lösbar.
    - `openrouter-free`-Modell in LiteLLMs Config ist zudem selbst
      veraltet/tot (404, "unavailable for free" — will man ohnehin mal
      beheben, unabhängig vom Tool-Calling-Thema).
39. **KRITISCHE ARCHITEKTUR-DOPPLUNG ENTDECKT, ungeklärt.** CEO zeigte
    einen Dashboard-Kachel-Screenshot: AI-OS hat bereits eine EIGENE
    "Hermes / AI Engineering Platform" (FastAPI-Backend, Port 8000,
    `backend/app/agents/hermes.py`, RAG+Qdrant+Multi-Agent-Fundament,
    eigene Chat-UI unter `/ui`). Dokument `docs/Hermes-Pi4-Tailscale-
    Setup.md` (Stand **10.07.2026**, Roadmap-Status "✅ umgesetzt")
    beschreibt EXAKT die heute gebaute Zielarchitektur (Hermes+Backend
    24/7 auf dem Pi, LLM-Aufrufe per Tailscale zum Laptop-Ollama) — nur
    mit dem AI-OS-EIGENEN, schlankeren Hermes, NICHT mit Nous Researchs
    Hermes Agent. **Das Dokument erwähnt sogar explizit**, dass man sich
    am 10.07. bewusst GEGEN das Docker-basierte "Hermes Desktop"-Sidecar-
    Produkt entschieden hatte, zugunsten der nativen Backend-Integration —
    genau das, was heute den ganzen Tag gebaut wurde. **Nicht geklärt**:
    ob der CEO das heute bewusst nochmal anders wollte (Nous Researchs
    Hermes Agent ist deutlich funktionsreicher: 77 Skills, Cron,
    Multi-Platform-Messaging, eigenes Dashboard) oder ob hier unbeabsichtigt
    Doppelarbeit entstanden ist. **Bewusst nicht heute Nacht entschieden**
    — braucht einen Vergleich beider Systeme mit frischem Kopf.

**Offen für nächstes Mal**: (1) **Architektur-Entscheidung**: AI-OS'
eigener nativer Hermes (Port 8000, bereits vorhanden laut Roadmap) vs.
heute installiertes Nous-Research-"Hermes Agent" (Pi, Docker) — beide,
eins ablösen, oder bewusst getrennte Rollen? (2) Tool-Calling-Problem bei
Nous-Research-Hermes weiter debuggen (Prompt-Format-Kompatibilität mit
lokalen Ollama-Modellen) — bis geklärt sind die drei neuen Skills technisch
nicht zuverlässig nutzbar, (3) Discord- ODER Slack-Bot-Token besorgen
(CEO-Aktion), (4) Vorstellungs-Text für Hermes (`user.md`) vom CEO selbst,
(5) ersten Blog-Research-Cronjob-Lauf morgen früh verifizieren (könnte am
Tool-Calling-Problem scheitern, siehe Punkt 2), (6) defekte SSD-Situation
klären (Garantie/RMA), (7) `openrouter-free`-Modell-Slug in
`litellm_config.yaml` ist veraltet, reparieren.

---

## 2026-07-23 (Tag 11) — Broki AI Backend: Ollama-Pivot, dann echter wllama-Bug endlich gelöst

CEO-Ausgangsfrage: "Chat Nachricht reagiert noch garnicht, bzw. LLM keinen
Rückmeldung?" — der Broki-Sidebar-Chat hatte seit Sessionbeginn NIE eine
echte LLM-Antwort geliefert. Zwei Runden, gegenläufige Ergebnisse:

1. **Pivot zu Ollama-HTTP.** Nach CEO-Stopp der WASM-Fehlersuche ("kostet zu
   viel Zeit für ein wackliges Ergebnis") neuer Motor in `llm-gateway.js`:
   simples `fetch()` gegen die im restlichen AI-OS eh laufende lokale Ollama-
   Instanz (Port 11434). Braucht `"http://127.0.0.1:11434/*"` in
   `host_permissions` (manifest.json). Echter Bug dabei: Ollama blockt
   standardmäßig JEDE POST-Anfrage mit `Origin: chrome-extension://...` per
   CORS (403) — ein GET-Ping auf `/api/tags` täuschte "erreichbar" vor, ohne
   dass der eigentliche `/api/chat`-Call je durchkam. Fix: `OLLAMA_ORIGINS`
   als persistente Windows-Umgebungsvariable auf die exakte Extension-ID
   gesetzt, Ollama neu gestartet — mit `curl -H "Origin: ..."` in Sekunden
   verifiziert statt eines langen Browser-Testzyklus. Chat lief damit zum
   ersten Mal Ende-zu-Ende durch.
2. **CEO-Nachfrage, zurecht:** "ich dachte es soll vollständig nur im Browser
   laufen ohne eigenen PC/Server?" — berechtigt: Ollama-HTTP braucht eine
   ZUSÄTZLICHE Installation neben der Extension, widerspricht dem
   "Trojanisches Pferd, einfach installieren"-Verkaufsargument. CEO-
   Entscheidung: erst den alten wllama-Bug (nie root-gecaust, nur
   deprioritisiert) richtig diagnostizieren, bevor auf einen Ollama-Bundle-
   Installer ausgewichen wird.
3. **Diagnose-Methode, die endlich funktionierte:** Playwright sieht
   Offscreen-Dokumente grundsätzlich nicht (bekannte Lücke). NEU entdeckt:
   `chrome.storage` ist im Offscreen-Dokument selbst AUCH `undefined`
   (eingeschränkte Extension-API-Teilmenge dort) — ein direkter Checkpoint-
   Versuch dort schlug sofort fehl. Lösung: Checkpoints per
   `chrome.runtime.sendMessage` an den Service Worker relayen (neuer Case
   `"wllama-checkpoint"` in `background.js`), der sie in `chrome.storage.local`
   schreibt — übersteht sowohl Playwrights Blindheit als auch einen
   möglichen Absturz des Offscreen-Prozesses. Zusätzlich
   `self.addEventListener("unhandledrejection", ...)` in `offscreen.js`
   ergänzt — DAS brachte den entscheidenden Fund.
4. **Echter Root Cause:** wllamas vendorte `utils.js` versucht JEDES Modell
   automatisch per `caches.open()`/`cache.put()` im Cache-Storage-API
   zwischenzuspeichern. Die Cache-API akzeptiert aber NUR http(s)-URLs als
   Schlüssel — `chrome-extension://`-URLs (so lädt die Extension ihre
   eigenen .gguf-Dateien) wirft sie ab: `"Failed to execute 'put' on
   'Cache': Request scheme 'chrome-extension' is unsupported"`. Der Fehler
   passiert in einem ungesicherten XHR-`onload`-Handler → das Lade-Promise
   resolved/rejected NIE → sah wie ein stummes Einfrieren aus (Ursache des
   nie root-gecausten `"[object ProgressEvent]"`-Bugs aus früheren Runden).
   Fix in `offscreen.js` (NICHT in der vendorten/gitignorten `utils.js`, die
   bei jedem `npm run build:vendor` überschrieben wird): `window.caches` per
   `Object.defineProperty` auf `undefined` setzen, BEVOR wllama importiert
   wird.
5. **Verifiziert, mehrfach reproduziert:** Modell-Laden (0.5B, ~490MB) in 5s
   ohne Fehler, echte Text-Generierung liefert echten Text, komplette
   Sidebar-UI-Chat-Flow (Datei-Anhang + Frage) läuft durch mit
   `Motor: wllama (qwen2.5-0.5b-instruct-q4_k_m.gguf)`.
6. **Zwei weitere echte Bugs nebenbei gefunden:** die 8GB-RAM-Modellstufe in
   `broki-config.js` verwies auf eine nie heruntergeladene 3B-Datei (jeder
   Nutzer mit ≥8GB RAM wäre stillschweigend auf Ollama/Cloud zurückgefallen);
   die 1.5B-Datei (~1,1GB) brachte im echten UI-Test den GESAMTEN Renderer-
   Prozess zum Absturz (echter Speicher-Crash). Beide vorläufig konservativ
   entschärft: alle Modellstufen zeigen jetzt auf das verifiziert stabile
   0.5B-Modell, Token-Deckel für wllama separat auf 200 gesenkt (volle 1024
   Ollama-Token sprengten sonst das 25s-Offscreen-Timeout).
7. **Motor-Reihenfolge wiederhergestellt:** Native → WebLLM → wllama (alle
   Zero-Install) → Ollama (Fallback, braucht Zusatzinstallation) → Cloud.
   Ursprüngliche Produktvision damit technisch bewiesen umsetzbar.

**Lehre für künftige MV3-Offscreen-Diagnosen**: wenn Playwright nichts sieht
UND chrome.storage im Offscreen-Kontext selbst nicht verfügbar ist, den
Service Worker als Relais nutzen — der hat volle API-Rechte und übersteht
Abstürze des Offscreen-Dokuments.

**Offen für nächstes Mal:** 1.5B-Modellstufe mit RAM-Profiling stabilisieren
statt dauerhaft auf 0.5B zu bleiben (aktuelle Antwortqualität schwach —
Modell rambelt teils über die Token-Grenze hinaus mit erfundenem Text).

---

## 2026-07-22 (Tag 10) — Broki AI: Sidebar-Redesign + echte Assistentin-Illustration als Logo

Ganztägige Design-Iteration der Sidebar (Details siehe `[[project-broki-ai]]`
Memory, hier nur die Kurzfassung fürs Journal): von generischem Blau-Grau-
Look über "Apple/Perplexity-Minimalismus" zu einer Optik mit den vom CEO
gelieferten, professionell illustrierten PNG-Charakteren (Assistentin-Figur)
als Standard-Logo, Farbpalette per `img.getpixel()` exakt aus dem Logo
gemessen (dunkles Anthrazit + Blau-Akzent) statt geraten. Header von 3
Balken auf Punkt+Hamburger-Menü reduziert, Eingabefeld zur mitwachsenden
Textarea mit Datei-Anhang (`+`) und Spracheingabe (🎤) ausgebaut, alle
sichtbaren Rahmen entfernt. Mehrere echte Bugs unterwegs gefunden und live
mit Playwright verifiziert (nicht nur Code geschrieben), u.a. ein CSS-
Spezifitäts-Bug bei den Feedback-Buttons und ein Menü-Positionierungsfehler.
Wichtige Produktvision festgehalten: Assistentin (Chat-Frontend) + "Junge"
(Hintergrund-Analyse-Agent) sind zwei Mitglieder eines künftigen Broki-
Agenten-Teams — nur die Assistentin ist bisher umgesetzt.

---

## 2026-07-21 (Tag 9, Fortsetzung 7) — Qualitätsoffensive KI-Fabrik: Cloud-Code-Modell + Claude-Code-Prototyp

CEO-Ziel: "wirklich produktiv fähige MVP Produkte liefern". Nach Vergleich von
Hermes-Agent (eigenes `backend/`-Projekt, aber selbst als "Vorstufe zu
LangGraph" dokumentiert — kein Fortschritt) und Eigent (github.com/eigent-ai,
real und aktiv, aber neue Integration mit unbekanntem Aufwand) zwei konkrete
Bausteine gebaut:

1. **LangGraph bevorzugt jetzt gezielt ein offenes Cloud-Code-Modell.** Neuer
   Parameter `bevorzugt_cloud` in `llm_router.py` (überspringt für einen
   einzelnen Aufruf lokale Engines, respektiert aber den globalen
   "lokal"-Datenschutz-Schalter als harte, nicht überschreibbare Grenze).
   `node_entwickeln` (LangGraph) und `_factory_build_prototype` (Dashboard)
   nutzen das jetzt mit `model="qwen2.5-coder"` → OpenRouters kostenlose
   Qwen3-Coder-Stufe. Stolperstein: ein alter `langgraph_engine.py`-Prozess von
   18:42 Uhr lief noch mit dem alten Code weiter — `/api/services/start`
   startet einen bereits laufenden Dienst nicht neu, musste ihn gezielt killen.
   Live verifiziert: Auftrag lief komplett durch, `entwicklung` + `prototyp`
   liefen auf "Cloudflare Workers AI" (OpenRouter-Freikontingent war gerade
   ausgelastet, System wechselte automatisch zum nächsten Cloud-Anbieter).
2. **Claude-Code-Prototyp als kostenpflichtiger Opt-in.** Vorher zwei echte
   Kostentests: triviale Aufgabe 22s/$0,15, echtes Kanban-Board aus dem
   Auftrags-Archiv (mit Playwright verifiziert, inkl. funktionierendem
   Personen-Filter) 74s/$0,31 — beide sauber, kein Fehlversuch, deutlich besser
   als der lokale Deep-Agent-Versuch vom selben Tag. Wichtiger Fund: `claude -p`
   braucht zwingend `--model claude-sonnet-5`, sonst Fehler "Fable 5 requires
   usage credits". CEO-Vorgabe hart umgesetzt: JEDE Nutzung braucht Vorwarnung +
   explizite Bestätigung (`confirm()`-Dialog mit echten Kostenzahlen), nie
   automatisch. Neuer Button "💎 Claude-Code-Prototyp bauen (kostenpflichtig)"
   neben dem kostenlosen Deep-Prototyp-Button. End-to-End verifiziert: $0,28,
   sauberes Ergebnis über neue Route ausgeliefert.

---

## 2026-07-21 (Tag 9, Fortsetzung 5) — Agent-Knowledge-Doku, RAM-Guard, Deep-Prototyp (Opt-in)

Drei CEO-Anliegen in einer Runde, alle live geprüft.

1. **"Wo sind Agenten-Fähigkeiten definiert, wie erweitern?"** — ausgelöst durch
   Screenshot mit leerer Kategorie "Agent-Knowledge" (0 Dateien). Antwort: 3
   getrennte Code-Stellen (`agent_system.py` 7 Kern-Agenten nur Freitext-Prompt +
   Modell, KEIN echtes Tool-Calling; `agents/agents.json` 3 Spezial-Microservices
   mit echtem `capabilities`-Array; `langgraph_engine.py` nochmal separate
   Knoten-Rollen). Dokumentiert in 4 neuen Dateien unter
   `06_Gedächtnis/Agent-Knowledge/` (README + 3 Gruppen-Seiten mit Datei:Zeile-
   Referenzen). Kategorie zeigt jetzt 4 statt 0 Dateien.
2. **RAM-Guard (neue CEO-Sicherheitsregel)**: RAM darf nie 91% erreichen. Neuer
   Hintergrund-Thread `_ram_guard_worker()` in `ai_os_dashboard.py` (Muster wie
   `_docker_autostart_worker`): ab 90% Warn-Banner (jeder Tab), ab 91%
   automatisches Stoppen entbehrlicher Dienste in fester Reihenfolge (Keycloak/
   SearXNG/Node-RED/OpenHands/Hermes/Business-Tools zuerst — nie Dashboard/
   Kern-Infrastruktur). `GET /api/ram-guard/status`, Live getestet (echte 77,2%
   korrekt angezeigt, kein Fehlalarm).
3. **Deep-Prototyp als Opt-in** (Fortsetzung von Fortsetzung 3, siehe unten):
   isolierter Test zuerst — `qwen2.5-coder` kann KEIN echtes Tool-Calling in
   dieser Ollama-Einrichtung, `qwen3.5:9b` funktioniert aber SEHR langsam
   (12,5 Min für eine triviale Ein-Datei-Aufgabe, 3 Fehlversuche des Modells bei
   den Tool-Parametern, bevor der 4. klappte). CEO entschied nach diesem Befund:
   Opt-in-Button statt Standard-Ersatz. Umgesetzt: `_factory_build_deep_prototype()`
   mit `deepagents`-Paket + `FilesystemBackend(virtual_mode=True)` (Pfad-Sandbox
   PFLICHT, sonst kein Schutz gegen `..`/absolute Pfade), bewusst OHNE
   Shell-`execute`-Tool. Neue Routen `POST /api/factory/orders/deep-prototype` +
   `GET /factory/prototype/<id>/deep/<pfad>`, neuer Button pro Auftrag in der
   KI-Fabrik-Karte mit Warn-Dialog vor dem Start. Live-Verifikation mit echtem
   Testauftrag lief zum Zeitpunkt dieses Journal-Eintrags noch (siehe Memory
   [[project_ki-fabrik-team-agenten]] für das nachgetragene Ergebnis).

---

## 2026-07-21 (Tag 9, Fortsetzung 3) — LangGraph: lokale Traces statt LangSmith

CEO-Frage: FastAPI für LangGraph schon eingebaut? Und da LangGraph keine eigene GUI
hat — lohnt sich LangSmith (volle Observability) oder eher "Deep Agents" (Open-
Source-Harness für Planung/Kontext/Multi-Agenten bei langfristigen Aufgaben)?

- **FastAPI**: war schon drin (`langgraph_engine.py` läuft komplett auf FastAPI +
  uvicorn, seit dem ursprünglichen Bau der Engine). Installiert bestätigt: fastapi
  0.139.0, uvicorn 0.49.0, langgraph 1.2.7.
- **LangSmith vs. Deep Agents — unterschiedliche Probleme, nicht dieselbe Frage:**
  LangSmith = Transparenz/Debugging on-top vom Bestehenden. Deep Agents = eine
  Fähigkeits-Erweiterung (Planung, Dateisystem, Sub-Agenten) für den Graphen selbst.
  Empfehlung gegeben: LangSmith NICHT einbinden (sendet Traces standardmäßig an
  smith.langchain.com — Cloud-Standard-Verhalten passt nicht zum Lokal-Grundsatz des
  AI-OS; selbst-hostbar nur im teuren Enterprise-Tier). Stattdessen: eigene, rein
  lokale Trace-Aufzeichnung gebaut (kein neuer Cloud-Dienst, kein Docker nötig).
  Deep Agents als separate, größere Entscheidung offen gelassen (siehe unten).
- **Umsetzung (lokale Traces):**
  `langgraph_engine.py`: `_graph_stream_traced()` als gemeinsame Basis für `/run`
  UND `/run-stream` (vorher zwei getrennte Implementierungen des Graph-Durchlaufs),
  schreibt jeden Knoten-Abschluss in `06_Gedächtnis/Memory/Short-Memory/
  langgraph_traces.jsonl` (Timestamp, Knoten, Provider, Auftrags-/Ergebnis-Vorschau),
  auf 500 Zeilen gedeckelt. Neuer Endpunkt `GET /traces`.
  `ai_os_dashboard.py`: Proxy-Route `/api/langgraph/traces`.
  `dashboard.html`, Tab 🔄 Automatisierung: neue Karte "🔍 LangGraph-Traces" (auf-/
  zuklappbar), zeigt die letzten Knoten-Ausführungen mit Vorschau-Text.
- **Verifikation:** echter Testauftrag durch `/run-stream` geschickt, `/traces`
  lieferte beide Knoten (planen, entwickeln) mit korrekter Vorschau und Zeitstempel,
  UI-Elemente im ausgelieferten HTML bestätigt.
- **Offener Punkt (bewusst nicht in diesem Schritt entschieden):** Deep Agents wäre
  eine größere Umbau-Entscheidung (ersetzt den simplen 3-Knoten-Graphen durch einen
  Harness mit Planung/Dateisystem/Sub-Agenten) und würde inhaltlich mit der bereits
  dokumentierten OpenHands-Lücke zusammenhängen (siehe [[ki-fabrik-team-agenten]]) —
  dem CEO als eigene, größere Entscheidung vorgelegt statt einfach mitgebaut.

---

## 2026-07-21 (Tag 9, Fortsetzung 2) — Wissensmodell-Grid: von reiner Zahl zu prüf-/löschbar

CEO: "Das Gedächtnis kann ich aktuell nicht prüfen bzw. beeinflüssen" — der Tab
🧠 Gedächtnis zeigte pro Kategorie (Business-Knowledge, Short-Memory, ...) nur eine
Dateianzahl, keine Möglichkeit, tatsächlich reinzuschauen oder etwas zu entfernen.

- Backend (`ai_os_dashboard.py`): drei neue Routen nach dem bereits etablierten
  Wiki-Docs-Muster (`/api/wiki-docs` + `/api/wiki-file/...`):
  `GET /api/knowledge/<cat_key>/files` (Dateiliste inkl. Größe/Änderungsdatum),
  `GET /api/knowledge-file/<cat_key>/<relpath>` (Datei anzeigen, `send_from_directory`),
  `POST /api/knowledge-file/delete` (Datei löschen). Pfadsicherheit über
  `_knowledge_resolve_file()`: `relpath` wird gegen den aufgelösten Kategorie-Ordner
  geprüft (`root in candidate.parents`), Traversal-Versuch mit `../../..` live
  getestet → korrekt mit 404 abgewiesen. `.gitkeep` ist explizit vom Löschen
  ausgeschlossen.
- Frontend: jede Karte im Wissensmodell-Grid ist jetzt klickbar, öffnet ein Panel
  darunter mit der echten Dateiliste (Icon/Name/Größe/Datum), "👁 Anzeigen" öffnet
  die Datei im neuen Tab, "🗑" löscht mit `confirm()`-Sicherheitsabfrage und lädt
  Liste + Kategorie-Zähler neu.
- **Bewusst NICHT gebaut**: Inline-Bearbeiten der Dateien direkt im Browser — zu
  riskant für strukturierte JSON-Dateien, die laufende Dienste aktiv lesen/schreiben
  (z.B. `factory_orders.json` unter Short-Memory, 207 KB, aktiv von der KI-Fabrik
  genutzt). Nur Anschauen + gezieltes Löschen, kein Überschreiben ohne Git-Historie.

**Verifikation:** Datei angelegt → gelistet → per Route inhaltlich angezeigt →
gelöscht → Liste danach leer (echter Round-Trip getestet, nicht nur Code gelesen).
Pfad-Traversal-Versuch und `.gitkeep`-Löschversuch beide korrekt abgewiesen.

---

## 2026-07-21 (Tag 9, Fortsetzung) — Produktion-Modul: Test-Umgebung / Live-Umgebung getrennt

CEO: das Produktion-Modul soll klar zwischen "nur lokal, MVP" und "schon produktiv
veröffentlicht" trennen — jedes neue Produkt UND jede neue Version soll künftig
immer zuerst durch die Test-Umgebung (Pilotierung), erst danach in die Live-Umgebung.

- `dashboard.html`, Tab 🏭 Produktion neu strukturiert in drei Bereiche: Hinweis-Box
  zur Ablauf-Regel oben, dann **🧪 Test-Umgebung** (nur lokal/MVP), **🚀 Live-Umgebung**
  (produktiv im Einsatz), **🧱 Bausteine** (wiederverwendbare Komponenten, unverändert).
- **Einordnung der bestehenden 5 Einträge (eigene Einschätzung, bitte prüfen):**
  - Live: **LeadPilot CRM** — bereits in echtem Einsatz fürs eigene IT-Freelancer-
    Geschäft (echte Angebote/Rechnungen laufen darüber).
  - Test: **AI Business Checker** (internes Recherche-Tool, kein Kundenprodukt),
    **DocuCheck Local** (nur über den lokalen AI-OS-Server erreichbar, keine echte
    öffentliche Domain), **KI-Avatar Pipeline-Board** (Pipeline selbst laut Doku noch
    im Aufbau), **Broki AI** (wartet laut Gate explizit auf CEO-Freigabe — dafür aus
    dem "Bausteine"-Bereich raus, wo es sachlich nicht hingehört, in Test verschoben).
- Rein UI-seitig umgesetzt (Karten sind statisches HTML, kein Backend-Registry nötig).
  Verifiziert: JS-Syntax-Check (`node --check`) + Dashboard neu gestartet, alle drei
  neuen Bereichsüberschriften im ausgelieferten HTML bestätigt.

---

## 2026-07-21 (Tag 9) — Prompt-Baukasten (RKZFE) + LangGraph als echter Team-Agent

CEO: zwei Aufträge. 1) Wissen aus `00_Wissen/04_Referenzen/Wiki/Prompt Grundlage Wissen/`
(Webinar-PDF, reines Bild-PDF ohne Textlayer) auswerten und daraus eine Prompt-Vorlage
im AI-OS bauen. 2) LangGraph und OpenHands sind als "Team-Agenten" für die
CEO-Ideen-Werkstatt eigentlich schon da, werden aber gar nicht richtig genutzt —
beheben.

1. **PDF-Auswertung ohne Textlayer:** `pypdf` lieferte für alle 20 Seiten "kein Text
   extrahierbar". `pdftoppm` (für das Read-Tool-eigene PDF-Rendering) war nicht
   installiert. Gelöst mit `pymupdf`/`fitz`, das bereits als Python-Lib vorhanden war —
   alle 20 Seiten bei 110 DPI zu PNG gerendert und einzeln gelesen. Kernrahmenwerk:
   **RKZFE** (Rolle/Kontext/Ziel/Format/Einschränkung) für einzelne Prompts, plus die
   Unterscheidung Prompt (einmalig) vs. Skill (gespeicherter Ablauf) vs. Preset/
   "Aufstellung" (strukturell erzwungene Agenten-Konfiguration) — Kernsatz der Quelle:
   *"Ein Prompt ist ein Versprechen, eine Berechtigung ist eine Tatsache."*
2. **Prompt-Baukasten gebaut** (`06_Gedächtnis/Prompt-Library/README.md` +
   `RKZFE-Vorlage.md` als Referenz, `/api/prompt-baukasten` in `ai_os_dashboard.py` als
   Backend, neue Karte im Tab 💡 CEO-Ideen): rohe, unstrukturierte Notiz rein → RKZFE-
   Prompt raus, nach dem "ALBERT"-Muster aus der Quelle. Direkt Ollama (kein Cloud-
   Fallback über den LLM-Router) — gleiche Privatsphäre-Regel wie `/api/rag-chat|`,
   da die Notiz interne/geschäftliche Details enthalten kann.
   - **Stolperstein:** llama3 hielt sich beim ersten Versuch nicht an den
     angeforderten JSON-Schlüssel (`einschränkung` statt `einschraenkung`) und ordnete
     Rolle/Format inhaltlich falsch zu (z.B. "Rolle: Kunde" statt "Rolle:
     Vertriebsmitarbeiter"). Behoben durch ein konkretes Few-Shot-Beispiel im
     System-Prompt (das exakte Kugellager-Beispiel aus der Quelle) + defensive
     Schlüssel-Normalisierung im Backend. Danach live mit zwei verschiedenen Notizen
     verifiziert (Kugellager-Beispiel + eine echte Broki-Pi-Sync-Testnotiz).
3. **LangGraph als echter Team-Agent statt Karteileiche:** `_process_factory_order()`
   in `ai_os_dashboard.py` hat die Planen→Entwickeln→Qualität-Schleife (inkl.
   Nachbesserungs-Schleife) komplett doppelt von Hand nachgebaut — obwohl
   `langgraph_engine.py` (Port 5500) genau diesen Zustandsgraphen bereits fertig und
   getestet bereitstellt, aber von der echten KI-Fabrik nie aufgerufen wurde.
   - Neuer Endpunkt `POST /run-stream` in `langgraph_engine.py`: NDJSON, ein Event pro
     abgeschlossenem Graph-Knoten (`GRAPH.stream(...)`), damit die Live-Status-
     Anzeige der KI-Fabrik (LEGO-Fabrik-Animation) ihre Schritt-für-Schritt-Optik
     behält, statt nur auf ein einziges Endergebnis zu warten.
   - `_factory_run_langgraph()` liest diesen Stream und spiegelt jeden Knoten
     (`planen`→analyse, `entwickeln`→entwicklung inkl. Prototyp-Neubau,
     `qualitaet`→qualität inkl. Rework-Erkennung) live in die Auftragsschritte.
   - Alte Inline-Logik bleibt als `_factory_run_inline_pipeline()` Fallback erhalten,
     falls die LangGraph-Engine (:5500) mal nicht läuft.
   - **OpenHands bewusst NICHT in diesem Schritt angebunden** (CEO-Entscheidung nach
     Rückfrage): der Prototyp-Schritt bleibt ein Ein-Schuss-LLM-Aufruf. Echtes
     OpenHands (autonomer Coding-Agent, Docker :3000) läuft normalerweise nur
     interaktiv über die GUI; die programmatische Ansteuerung über den neuen
     Agent-Server (Bild `ghcr.io/openhands/agent-server`) wäre ein eigener,
     unsicherer Rechercheaufwand — als offener Punkt vermerkt, nicht stillschweigend
     übersprungen.

**Verifikation:** `node --check` auf dem extrahierten Dashboard-JS, `py_compile` auf
beiden Python-Dateien, `/api/prompt-baukasten` zweimal live gegen echtes Ollama
getestet, `/run-stream` direkt gegen die laufende LangGraph-Engine getestet (liefert
genau 3 Events mit korrektem `path`/`engines`), und ein echter Fabrik-Testauftrag
(`ord_20260721_175836`) durchlief `annahme → analyse → entwicklung` sichtbar mit
Engine-Label `LangGraph :5500 · Ollama (lokal)` statt der alten Inline-Engine-Labels.

---

## 2026-07-18 (Tag 8i) — Broki auf vuxuantiep.de integriert + Sicherheit/Compliance

CEO: Broki-Präsentation auf der Hauptseite (ersetzt „Lego-AI"), Landingpage-Link,
Hell/Dunkel im Frontend, + Sicherheits-/Compliance-Anforderungen (Zero-Trust,
Signatur, Auditierbar, EU-AI-Act/NIS2/BSI/ISO).

1. **Website-Integration** (separates Repo `Github_Projekte/vuxuantiep.de`,
   TanStack/React, CEO gab „direkt im Repo bauen" frei):
   - `BrokiHeroCard` ersetzt die KI-Fabrik-Slideshow im Hero — Browser-Fenster-
     Mockup mit Broki-Sidebar + proaktivem Prüfhinweis (USt-IdNr §27a), zeigt den
     USP sofort. CTA „Broki entdecken" → /broki.
   - `/broki` Produktseite: Hero (vorhandener ParticleBackground) + 6 Vorteile +
     Cloud-Assistenten-Abgrenzung + Sicherheit&Compliance-Grid + CTA. Dreisprachig
     (t() DE/EN/VI), im Corporate-Design. Build ✓ (Route-Tree generiert).
   - Sauber committet (NUR Broki-Dateien — mein `git add -A src/` hatte erst die
     laufende Arbeit des Users mitgezogen → per reset --soft getrennt). NICHT
     gepusht (Live-Website, CEO deployt selbst).
   - **Positionierung:** kein Raspberry Pi/Tailscale im Verkaufstext (CEO: Pi =
     MVP-Homelab, im Verkauf optionales Zusatzpaket „Mini-KI-Server"). Als
     Feedback-Memory + Landingpage-Plan-Regel festgehalten.
2. **Sicherheits-/Compliance-Konzept** (`Sicherheit-Compliance-Konzept-Broki.md`):
   Was gebaut ist (ECDSA-Signatur, Zero-Trust-lokal, Rollen-Access, fail-closed,
   AES-Journal) + Auditierbarkeit (Quellen-Rückführung, Netzwerk-Beweis, geplantes
   signiertes Audit-Log) + regulatorische Ausrichtung (DSGVO by design, AI-Act
   begrenztes Risiko, NIS2 unterstützend, BSI/ISO = Ziel Phase 2, NICHT Jahr 1).
   Harte Ehrlichkeits-Regel: nie „zertifiziert" behaupten, nur „auditierbar/
   vorbereitet" — auf /broki bereits mit Fußnote umgesetzt.
3. Hell/Dunkel-Umschalter in Broki-Hero eingebaut + als Artifact veröffentlicht
   (live ansehbar), themen-adaptiver Partikel-Hintergrund.

Nächstes großes Paket: Broki-Frontend-Dashboard (MVP aus dem Mockup) — CEO-Wahl.

---

## 2026-07-18 (Tag 8h) — Broki: animierter Partikel-Hintergrund + Hero-Seite gebaut

CEO-Wunsch: Partikel-Netzwerk-Hintergrund wie itsupporthh.de, aber in Broki-Farben.
Deren Seite nutzt particles.js + jQuery (WordPress) → bewusst NICHT übernommen.

1. **Eigene Canvas-Komponente** `broki-landingpage/assets/broki-particles.js`:
   self-contained (keine Fremd-Lib → CSP-konform für MV3 + „keine Cloud"-treu),
   driftende Punkte + Distanz-Linien im Grün #00c758, dezente Maus-Anziehung.
   Performance: pausiert bei verstecktem Tab, `prefers-reduced-motion`,
   Partikel-Deckel 140, devicePixelRatio-aware — die CPU bleibt fürs LLM frei.
2. **Hero-Seite** `broki-landingpage/index.html` als erster echter Landingpage-
   Baustein im Corporate-Design (schwarz/grün, Inter + JetBrains Mono, grüne
   Wort-Highlights „bleibt."/„privat." wie vuxuantiep.de „skaliert."/„liefert.",
   Trust-Leiste, grüner Primär- + Ghost-Button, Terminal-Tech-Stack-Zeile).
   Headless-Screenshot geprüft: Animation sichtbar, Layout stimmig.
3. Design-System §5b um die Hintergrund-Signatur ergänzt. Fonts noch System-
   Fallback (Inter/JetBrains Mono für Produktion lokal vendorn).

---

## 2026-07-18 (Tag 8g) — Broki Design-System = Corporate Identity (vuxuantiep.de)

CEO: Broki soll aussehen wie vuxuantiep.de (einheitliche Marke). Echtes CSS der
Live-Website geholt und die Tokens extrahiert → `Broki-Design-System.md`:
- **Farben:** BG #0a0a0a/#000, Karten #0d0d0f, Border #27272a; Grün-Signatur
  #00c758 (primär) / #00d294 (mint) / #4ade80 (hell) / #00bb7f (teal).
- **Fonts:** Inter (Text) + JetBrains Mono (Code/Tech) — LOKAL vendorn, nie
  Google-CDN (sonst Widerspruch zur „keine Cloud"-Botschaft + Extension-CSP).
- **Signatur:** Terminal/Code-Ästhetik (//-Kommentare, grüner Status-Text),
  grün-cyaner Robot (gleiche Maskottchen-Familie wie Website-„LEGO AI-OS").
- **Wichtigste Änderung:** das Frontend-Mockup nutzt Lila #7c5cff → auf Grün
  #00c758 umstellen (Buttons, Aktiv-Zustände, Banner, Robot). Layout bleibt.
- Landingpage-Plan darauf verwiesen; Palette als mögliche gemeinsame brand.css
  für ALLE Marktprodukte vermerkt (Portfolio als „ein Haus").

---

## 2026-07-18 (Tag 8f) — Broki: Wettbewerbsanalyse + Priorisierung + Landingpage-Plan

CEO-Frage „ist Broki stärker als andere? → vollständig entwickeln + priorisieren"
+ Frontend-Mockup (`Broki Ai-Frontend.png`) + Landingpage planen.

1. **Wettbewerbsanalyse** (`Wettbewerbsanalyse-und-Priorisierung-Broki.md`,
   web-recherchiert): Kernbefund — in der DSGVO-Nische (Kanzleien/Praxen) ist
   Broki strukturell überlegen, weil die bequeme Konkurrenz (Merlin/Sider/Monica)
   dort rechtlich DISQUALIFIZIERT ist: UCL-Studie 2025 (DSGVO-Verstoß, Aufzeichnung
   im Privatmodus), Merlin exfiltrierte eine Steuer-ID aus IRS-Formular,
   Sider/TinaMind teilen Prompts+IP mit Trackern → „ungeeignet für Enterprise".
   Die lokalen Alternativen (WebLLM/WebML) sind nur Tech-Demos ohne Firmen-RAG.
   Ehrlich: für den Massenmarkt NICHT stärker (Setup-Hürde). → Fokus-Empfehlung,
   kein „Merlin-Killer für alle".
2. **Priorisierung/MVP-Roadmap** zum Mockup-Nordstern: MVP-0 (Dogfooding, fast
   fertig) → MVP-1 verkaufbar (Dashboard-Grundgerüst + Lizenz-Wächter) → MVP-2
   „das WOW" (proaktive Assistenz = einziges Feature, das keiner hat) → Ausbau →
   Vision (Hermes/Mesh, nur Pitch). Proaktive Assistenz bewusst NACH dem
   verkaufbaren Gerüst, aber VOR Nice-to-have.
3. **Landingpage-Plan** (`Landingpage-Plan-Broki.md`): konkretisiert die docx zu
   8 baubaren Sektionen. NEU ggü. docx: „Datenschutz-Schock"-Sektion + direkte
   Vergleichstabelle (Broki vs. Merlin/Sider vs. Copilot) als Konversionskern —
   mit seriösen Quellen (Abmahnrisiko beachtet). ~2–3 Tage für v1. Bauen erst
   nach Dogfooding (Gate-Auflage 2).

---

## 2026-07-18 (Tag 8e) — Broki-Businessplan 2. Erweiterung (IP-Schutz, Hermes, Mesh)

Plan von 118k → 133k gewachsen. Neue Inhalte eingearbeitet:

1. **IP-/Kopierschutz** (CEO-Kernfrage „wie schütze ich Broki vor Nachbau?"):
   4-stufige „Schutzburg" in `Architektur-Broki-Extension.md` §5c mit ROI-Ranking.
   Wichtigste Erkenntnis: der **Lizenz-Wächter (Chef-Schlüssel)** ist quasi
   geschenkt — er nutzt die BEREITS gebaute ECDSA-Signaturkette (nur ein
   zusätzliches, an die Firmen-Domain gebundenes Lizenz-Zertifikat, das UI/RAG
   freischaltet). Bester Schutz, ~1 Tag, v1-tauglich. Rest: Marke anmelden
   (billig), WASM-Obfuskation (erst bei Kunden), Mesh-Protokoll = eigentlicher USP.
2. **Neue Branchen** Hafen/Logistik + E-Commerce: super Usecases (Netzausfall-
   Umfeld), aber Großenterprise-Vertrieb → Phase-2-Narrativ, nicht Startmarkt.
3. **Hermes-Loop + Mesh-Schwarm** (autonome Workflows, serverlose Team-KI via
   WebRTC): als Ausbau-Ideen §5b + Gate klar als **Vision 2027/2028** markiert —
   Pitch-Deck-Material, NICHT Jahr-1-Kalkulation (Autonomie-Haftung).
4. Gate um 2 Auflagen erweitert (Kopierschutz früh, Vision sauber trennen),
   SKILL um IP-Schutz + Hermes/Mesh ergänzt. → alles ins RAG-Gedächtnis.

---

## 2026-07-18 (Tag 8d) — Pi-Gegenstück gebaut + 3-Wege-LLM-Schalter + Hell-Theme

CEO-Freigabe fürs Pi-Gegenstück erteilt → gebaut (Dogfooding aufs eigene 00_Wissen,
Gate-Auflage 1). Dazu 2 CEO-Wünsche: Cloud-Modus zum Rechner-Entlasten + helles UX-Theme.

**1. Broki Pi-Server** (`Produkt/broki-pi-server/`, eigenständig, Python):
- `sign_utils.py`: ECDSA-P256, **DER→P1363-Konvertierung** — der kritische Punkt,
  weil WebCrypto (crypto.subtle.verify) NUR das P1363-Rohformat (r||s, 64 Byte)
  akzeptiert, Python `cryptography` aber DER erzeugt. `test_signatur.py` beweist
  es E2E: Python signiert → Node/WebCrypto verifiziert echt=✓, manipuliert=✗.
- `index_builder.py`: 00_Wissen → Chunks → Embeddings via Ollama nomic (LOKAL,
  nie Cloud) → rollenbasierte Partitionen (mitarbeiter/admin) → signiert.
  Ergebnis: 74/75 Chunks, ~1,2 MB je Rolle, Public Key erzeugt.
- `pi_server.py` :8088: manifest + partitionen, pfadsicher, Live getestet
  (health ✓, 404 bei falscher Rolle ✓, 400 bei Pfad-Traversal/non-jsonl ✓).
- Public Key in `broki-extension/config/broki-config.js` eingetragen.
- Stolperstein: Windows-cp1252-Emoji-Crash im print → sys.stdout.reconfigure.

**2. LLM-Schalter jetzt 3-Wege** (`llm_router.py` + Dashboard): lokal / hybrid /
**cloud**. Cloud-Modus überspringt Ollama/LM Studio/LiteLLM → entlastet den
eigenen Rechner (Pi bleibt, ist remote). **Bewiesen:** Ollama läuft, aber
Cloud-Modus antwortet via Cloudflare Workers AI. UI: 3-Knopf-Schalter im Gateway-Tab.

**3. Hell/Dunkel-Theme** (Dashboard-UX): `[data-theme="light"]`-Variablen-Override
(inkl. neuer --bg-sidebar/--bg-topbar, damit auch Sidebar/Topbar mitschalten),
🌙/☀️-Toggle in der Sidebar-Fußzeile, localStorage-Persistenz, `?theme=`-Deep-Link.
Beide Themes per Screenshot geprüft — hell durchgängig konsistent.

**Broki-Teststatus (Antwort an CEO):** Pi-Server + Signatur-Kette fertig & bewiesen.
Für vollen Extension-Test fehlt clientseitig nur: `npm install` (vendor: WebLLM/
wllama — User baut das gerade) ODER Cloud-Modus mit Key; + basisUrl auf
127.0.0.1:8088 für lokalen Test. UI/Schalter/Tresor sind schon testbar.

---

## 2026-07-18 (Tag 8c) — Broki-Businessplan erweitert → Wissen aktualisiert

CEO hat den Businessplan erweitert (102k → 118k Z.) — enthält jetzt die Zahlen,
die bei der Erst-Gate-Prüfung fehlten. Eingearbeitet:

1. **Gate-Prüfung aktualisiert** (`wirtschaftlichkeit-broki-ai.md`): Erlösmodell
   ist jetzt belegt statt geraten — B2B SaaS-Light **5–10 €/Seat/M bei ~95 %
   Marge** (wiederkehrend = echter Fortschritt!), Setup 2.500–8.000 €, ROI
   „>380k €/Jahr @ 1.000 Nutzer" (als Pitch top, als Solo-Umsatz-Basis untauglich).
   Prüfer bleibt konservativ: Plan-Zahlen UNVALIDIERT → Basis-Szenario ≈ 13k €/
   Jahr 1 (vorher 10k). Neue Auflagen: Audit-Tool als GTM-Lead-Magnet, BSI erst
   Phase 2. Empfehlung unverändert GO_MIT_AUFLAGEN.
2. **Architektur-Plan** (`Architektur-Broki-Extension.md`, Abschnitt 5b): drei
   Ausbau-Ideen aus dem Plan eingeordnet — P2P-Vektor-Sync (WebRTC/Gossip),
   Zero-Trust-Partner-Partition, Auto-Learning — alle ausdrücklich Phase 2+
   (nicht v1). Wettbewerbs-Abgrenzung (vs. Copilot / WebLLM) für Pitch festgehalten.
3. **SKILL** ergänzt (Erlösmodell, GTM „Trojanisches Pferd", Zielmarkt-Phasen).
   → alles ins RAG-Gedächtnis.

---

## 2026-07-18 (Tag 8b) — Betrieb: Tunnel + LLM-Fallback + Datenschutz-Schalter

CEO meldete „ai-os.vuxuantiep.de läuft nicht" + „KI-Fallback muss autonom sein"
+ „00_Wissen NIE Cloud" + „Schalter Lokal/Cloud" + „wo sind scraper & broki?".

1. **Tunnel repariert:** cloudflared lief nicht (401 = nur Worker-Fallback).
   Kein Windows-Dienst → per Aufgabenplanung **„Cloudflare Tunnel AI-OS"**
   (AtLogOn, Restart×3) eingerichtet, altes VBS aus shell:startup entfernt
   (Duplikat). 4 Tunnel-Verbindungen ✓.
2. **LLM-Fallback autonom gemacht:** LiteLLM lief gar nicht + Kette war kaputt
   (HuggingFace-Credits leer, OpenRouter-:free 429). Fix: eigenen **Workers-AI**-
   Provider vorn in die Fallback-Kette (planbares Kontingent, eigener CF-Account;
   WORKERS_AI_*→CLOUDFLARE_* gemappt). **E2E bewiesen:** Ollama AN→llama3 lokal,
   Ollama AUS→cloudflare/llama-3.1-8b automatisch, Ollama wieder AN→llama3.
   LiteLLM-Autostart-Task + Dashboard-Dienst-Kachel.
3. **00_Wissen hart lokal:** knowledge_agent.py spricht Ollama eh DIREKT an
   (kein Router, keine Cloud) — als CEO-Regel im Code-Kopf zementiert; Schalter
   gilt dort NICHT.
4. **Datenschutz-Schalter (Lokal/Hybrid):** `llm_router.py` liest `llm_mode.json`;
   im Lokal-Modus werden LiteLLM+GitHub+OpenRouter+HuggingFace+Cloudflare
   übersprungen (nur Ollama/LM Studio/Pi = selbst-gehostet). Dashboard-API
   `/api/llm/mode` + UI-Schalter im KI-Gateway-Tab. **Bewiesen:** Lokal-Modus +
   Ollama aus → „kein Provider", NULL Cloud-Kontakt (statt heimlich Cloud).
5. **Bausteine sichtbar:** neue Sektion „🧱 Bausteine" im Produktion-Tab —
   Feed-Scraper (Test-Seite verlinkt) + Broki-Extension (mit Lade-Anleitung).
   Erklärt, warum sie nicht als „Dienst" auftauchen: Wasm-Komponente bzw.
   Browser-Extension = kein eigener Server.

Verifiziert: py_compile + node --check aufs Template-JS grün, Schalter-
Persistenz, Failover, Screenshot des Gateway-Tabs.

---

## 2026-07-18 (Tag 8) — Broki AI: Browser-Extension-Architektur gebaut

CEO-Auftrag (Senior-Architekt-Rolle): Manifest-V3-Extension „lokaler KI-Wiki-
Assistent" mit Tailscale/Pi-Sync. Vorher: die 2 Broki-docx gelesen — **Broki AI
ist die Produktisierung der Plattform** (Businessplan 102k Zeichen: Pi+Tailscale,
380k-€-Ersparnis-Story, Zielgruppe Kanzleien/Arztpraxen = unser Gate-Beachhead!).
Einordnung: `Produkt/broki-extension/` in Lokal-SML.

**Gebaut (11 Dateien, alle node --check-grün, Manifest JSON-valide):**
1. **tailscale-sync.js**: Alarm-basierter Sync (MV3: chrome.alarms statt Timer!)
   vom echten Tailnet (`pi-ki-tiep.tailed32d1.ts.net:8088`), rollenbasiert.
   Integrität: **ECDSA-P256 über SHA-256** statt nacktem Hash-Vergleich —
   wichtig verstanden: einen mitgelieferten Hash kann der Angreifer auf dem Pi
   selbst fälschen, die Signatur ohne privaten Firmenschlüssel nicht.
   Fail closed: Signaturfehler → Index GESPERRT (Flag + UI-Banner), Pi offline
   → alter Index bleibt (kein Sicherheitsfall). Atomare Übernahme.
2. **memory-manager.js**: L1 Exact (SHA-256 der Normalform, TTL 7 Tage) →
   L2 Semantic (Cosine ≥ 0.92, gedeckelt 500) → L3 RAG (Top-4). Rückschreiben
   nach LLM-Antwort — außer im Privat-Modus.
3. **llm-gateway.js**: window.ai (3 Namensraum-Varianten defensiv geprobt) →
   WebLLM (WebGPU) → wllama (CPU). `navigator.deviceMemory` → 3 Modellstufen
   (0.5B/1B/3B) als OOM-Schutz. Embedding vom Motor, Notfall: Hash-Trigramm.
4. **private-vault.js**: isPrivateMode in `chrome.storage.session` (= reiner
   RAM, Browser zu → weg) + SW-Map für Drag-and-Drop-Dokumente, Tab-Aufräumer.
5. **crash-rollback.js**: Heartbeat-Trick (onSuspend feuert bei echtem Crash
   NICHT → Flag bleibt „laeuft" = Crash erkannt), AES-GCM-Journal (ehrlich
   dokumentiert: at-rest-Schutz, nicht gegen Profil-Vollzugriff), Content-Script
   entprellt (1,5 s) + Wiederherstellung mit input-Event für Framework-Bindings.
6. Sidebar-UI (Chat, Tresor-Schalter, Sperr-Banner, Rollback-Dialog),
   Architektur-Diagramm (Pflicht-Regel) `Architektur-Broki-Extension.md`.

Offen (im Architektur-Plan dokumentiert): Pi-Gegenstück (Index-Builder +
Signaturdienst), vendor/-Befüllung, **eigene Gate-Prüfung für Broki als Produkt**
(Businessplan liegt ja schon — Kern-Umsetzung war expliziter CEO-Auftrag).

### Nachtrag: Gate-Prüfung Broki + Wissen ins Gedächtnis (SKILL + Indexer)

1. **Gate-Prüfung** (`wirtschaftlichkeit-broki-ai.md`): Businessplan-docx hat
   KEINE Preise (reine Technik-Recherche) → alle Zahlen als Annahmen-Spannen
   gekennzeichnet (Prüfer-Regel 1). Marktbedarf 7/10 (DSGVO-Kaufdruck +
   Copilot-FOMO; Referenzpreis ChatGPT Enterprise 30–60 €/Nutzer/M). Stärke:
   einziges Produkt mit **wiederkehrendem** Modell (Setup 2.500–8.000 € +
   Wartung 100–300 €/M). Basis ≈ 10.000 €/Jahr 1 bei 50–80 €/h; konservativ
   0 € Umsatz, aber internes Wiki-KI-Tool bleibt. → **GO_MIT_AUFLAGEN**:
   Dogfooding aufs eigene 00_Wissen ZUERST (max. 7 Tage), kein Vertrieb vor
   Referenz, SLA begrenzt, Nachprüfung M3. **Status WARTET_AUF_FREIGABE.**
2. **Wissen ins Gedächtnis:** `SKILL_Broki-Extension.md` (7 Kern-Patterns:
   MV3-Grundgesetz, Signatur-statt-Hash, fail closed, storage.session-Flüchtig-
   keit, Heartbeat-Crash-Trick, Motor-Adapter, Memory-Kaskade) nach
   `02_Fähigkeiten/Aktiv/`. **Indexer erweitert:** INDEX_QUELLEN + `02_Fähigkeiten`
   (8 saubere .md, vorher gezählt — kein Junk).
3. Pi-Gegenstück bewusst NICHT begonnen — wartet auf CEO-Freigabe (Auflage 1
   macht es zum Dogfooding-Baustein).

---

## 2026-07-17 (Tag 7) — Lead-Radar: Arbeitsort-Filter + Standort-Erkennung

Angefangenes Feature aus der Vortagssitzung fertiggebaut (lag uncommittet in
`app.py`: Funktionen existierten, waren aber nirgends angeschlossen; dazu ein
Tippfehler-Funktionsname `KEIN_STANDort_check` → sauber `ist_kein_standort`).

1. **Arbeitsort-Klassifizierung** je Radar-Treffer: 🏠 Remote / 🔀 Hybrid /
   🏢 Vor Ort / ❔ Unklar (Regex-Heuristik, Hybrid gewinnt vor Remote, weil
   „hybrid + remote möglich" sonst als Remote durchginge).
2. **Standort-Extraktion**: Klammer-Inhalt im Titel oder explizite Marker
   (`Location:`, `Standort`, `based in`). Gelernt: `in <Wort>` im Fließtext ist
   zu mehrdeutig („experience in Claude" → Standort „Claude" 🤦) — deshalb
   `in <Stadt>` nur noch im Titel + Ausschlussliste (Gender-Kürzel, Tech-Begriffe,
   Sprachen, Rollen). Iterativ verfeinert: 33 → 24 → 19 → 18 Standorte,
   am Ende alle 18 echte Städte (São Paulo, Mexico City, Los Angeles …).
3. **Einbau nach Rollenfilter-Muster**: Scan setzt `arbeitsort`/`standort`,
   `/api/radar` klassifiziert Alt-Treffer lazy nach + liefert `arbeitsorte`-Zähler,
   Filter kombinierbar (`?rolle=…&arbeitsort=…`). UI: zweite Chip-Reihe
   „Arbeitsorte", Treffer zeigen Ort-Badge + 📍 Stadt.
4. **Stolperstein Zombie-Prozess (wieder!)**: `netstat | grep LISTEN` findet auf
   deutschem Windows nichts — dort heißt es „ABHÖREN". Alter Prozess hat mit
   altem Regex nachklassifiziert und die Messung verfälscht. Merken:
   `grep ":5330 .*ABH"`.

Verifiziert: 7 synthetische Fälle ✓, 68 echte Treffer → 39 Remote / 2 Hybrid /
27 Unklar, 18 saubere Standorte ✓, Kombi-Filter ✓ (ki_automation+remote = 2),
node --check auf ausgeliefertem JS ✓, Dashboard-Proxy 200 ✓.

### Nachtrag: KI-Gedächtnis liest jetzt auch 10_Business (Indexer erweitert)

CEO-Frage „wo speichere ich Produktideen, damit die KI sie lernt?" deckte eine
Lücke auf: Der RAG-Indexer (`06_Gedächtnis/knowledge_agent.py`) las nur
`00_Wissen/` — dort liegen aber nur **8** .md-Dateien. Die gesamte
Produktplanung in `10_Business/` war fürs Gedächtnis unsichtbar.

1. **INDEX_QUELLEN** = `00_Wissen` + `10_Business` (Antwort auf die CEO-Frage:
   neue Produktidee → `10_Business/<Name>/` mit README + `Plannung/` +
   `wirtschaftlichkeit-<name>.md`, Material als .md → wandert automatisch ins RAG).
2. **INDEX_AUSSCHLUSS**: `01_Persönlich` (privat, CEO-Wunsch) + node_modules/
   venv/EspoCRM-10.0.2. Wichtig: ohne die Ausschlüsse wären **453 von 489**
   Dateien Fremd-Doku gewesen (EspoCRM-Handbuch 234, node_modules-READMEs 219) —
   erst zählen, dann indexieren!
3. Index neu aufgebaut: 36 Dateien → 210 Chunks (nomic-embed-text via Ollama).

Verifiziert per semantischer Suche: „Wie viel kann das IT Pipeline CRM
einbringen?" → 0.85 auf README + Konzept-Prüfung ✓, „SLM im Browser" → WebLLM-
Doku + neuer Lernpfad ✓, „Compliance KI-Avatar" → compliance-critic-agent ✓.

### Nachtrag: 10_Business komplett auf Standard-Struktur umgeräumt

CEO-Auftrag: alle Produktordner auf das Schema README / Plannung/ /
wirtschaftlichkeit-*.md / app/ bringen. Vorgehen: ERST Referenzen greppen,
DANN verschieben — `board/`, `research-agent/`, `Produkt/dokucheck-lokal`,
`content/videos`, `KI-Fabrik-Auftraege` werden von Dashboard/Agenten
referenziert und blieben deshalb unangetastet.

- **KI-Avatar:** „Konzept-KI Avatar" + 01_Usecases → `Plannung/` (Usecases als
  Unterordner), Gate-Doku auf Produktebene; leere Ordner TikTok/Youtube weg.
- **CEO-Dashboard:** Frontend/ceo-dashboard → `app/`, .glb + Chat-Export →
  `Plannung/`, README neu (Prototyp, internes Tool).
- **Client-Side Self-Evolving AI + Lokal-Private-LLM-App:** Plannung/ + README
  mit ⚠️ „Gate ausstehend" (beide haben noch keine Wirtschaftlichkeitsprüfung!).
- **Lokal-SML:** „Idee und Plannung" → `Plannung/`, PRD aus docs/ dazu.
- **Neu:** `10_Business/README.md` = Struktur-Konvention + Produkttabelle +
  Liste der NICHT verschiebbaren (referenzierten) Pfade.

Stolpersteine: Windows-Ordnersperren (Move-Item statt mv half; 1 leerer
Ordner „Konzept und Plannung" bleibt gesperrt zurück — bei Gelegenheit löschen).

### Nachtrag: „Client-Side Self-Evolving AI" in Lokal-SML eingegliedert

CEO-Frage: passt die docx (82k-Zeichen-Chat-Export über die „5 Technologien")
zu Lokal-SML-Webassembly-MultiMemory oder neues Projekt? **Analyse: gleiche
Nische, gleicher Stack** (WebLLM, WASM/WebGPU, Transformers.js-Embeddings,
IndexedDB/OPFS) — das Praxisbeispiel im Dokument IST quasi DokuCheck. Neu darin
nur: Agenten-Loop + Self-Evolving Memory (autonome Recherche erweitert eigenes
Gedächtnis) = **Stufe 2 der Plattform, kein neues Produkt.**

- Kernaussagen als `Plannung/Konzept-Self-Evolving-Agent.md` destilliert
  (3-Säulen-Architektur, 3 SLM-Qualitäts-Hebel: RAG/QLoRA/Agentic Loops,
  B2B-Argument, Roadmap-Synergie mit v0.3-Embeddings) → geht ins RAG-Gedächtnis.
- docx daneben gelegt, Produktordner „Client-Side Self-Evolving AI" aufgelöst
  (nur gesperrte leere Hülle bleibt), beide READMEs angepasst.

### Nachtrag: 10_Business zweigeteilt — 01_Marktprodukte / 02_Interne-Tools

CEO-Wunsch: interne Tools von Marktprodukten trennen, mit Nummerierung.
Diesmal eine echte Migration, weil referenzierte Service-Pfade umzogen:

1. `01_Marktprodukte/` = IT Pipeline System, KI-Avatar, Lokal-SML, LLM-App;
   `02_Interne-Tools/` = CEO-Dashboard. `KI-Fabrik-Auftraege/` + `content/`
   bewusst auf Root belassen (werden von Fabrik/Higgsfield-Agent beschrieben).
2. **Vorher LeadPilot-Prozess gekillt** (CWD sperrt sonst den Ordner) — trotzdem
   sperrten IT-Pipeline + KI-Avatar für `git mv`; PowerShell Move-Item schaffte
   es (KI-Avatar fiel auf Copy zurück, >2 min bei node_modules).
3. `ai_os_dashboard.py`: 7 Pfade angepasst (Service-Registry, PRODUCTS/dokucheck,
   Start-Hinweise). Wichtig gelernt: die `start`-Strings dort sind nur ANZEIGE —
   echte Starts laufen über `Popen([sys.executable, script_path])`.
4. Git-Renames für die PowerShell-Moves manuell: `git add -u` (Löschungen) +
   Loop über `--diff-filter=D` → neue Pfade einzeln adden. 94 Renames, 0 Waisen,
   Vendor-Check sauber (kein EspoCRM/node_modules gestaged).
5. Dashboard per Scheduled Task neu gestartet, LeadPilot vom neuen Pfad.

E2E verifiziert: Dashboard 200, LeadPilot direkt + via Proxy 200, DokuCheck-Proxy
200, **Board-Start über die Dashboard-API vom neuen Pfad** → :5310 health 200 ✓.
Memories (dokucheck/ki-avatar/leadpilot/wissens-einordnung) auf neue Pfade gesetzt.

### Nachtrag: Wassette v0.4.0 installiert (Wasm-Sandbox + MCP)

Microsofts Wassette (aus dem Self-Evolving-Agent-Konzept: sichere Wasm-Sandbox
für Agenten-Tools, deny-by-default-Permissions) installiert:

- winget hing beim Quellen-Update → **Release-Binary direkt** von GitHub
  (v0.4.0, `wassette_0.4.0_windows_amd64.zip`) nach `C:\Users\vuxua\Tools\wassette\`,
  User-PATH ergänzt (kein Admin nötig).
- Als MCP-Server für Claude Code registriert (User-Scope, stdio):
  `claude mcp add --scope user wassette -- ...\wassette.exe run` → ✔ Connected.
- Smoke-Test: `component list` (leer, frisch) ✓, `registry search time` findet
  OCI-Komponente `ghcr.io/microsoft/time-server-js` ✓.
- Nutzung: Komponenten aus OCI-Registries laden (`wassette component load ...`),
  Rechte per `wassette permission` steuern. Tools erscheinen in NEUEN
  Claude-Code-Sitzungen als MCP-Tools.

### Nachtrag: Bauplan Feed-Scraper-Wasm + Fusion LLM-App → Plattform

CEO-Auftrag: Mini-Scraper als Wasm-Komponente genau planen (Smartphone-
Endverbraucher zuerst, 3 SLM-Hebel nutzen) + prüfen, ob Lokal-Private-LLM-App
und Lokal-SML-Webassembly-MultiMemory fusionieren sollen.

1. **Fusions-Prüfung → JA:** gleiche Mission (souveräne lokale KI für
   Endverbraucher), gleiche Memory-Architektur, gleiche Modellklasse. Smartphone-
   first wird SCHON von der PWA bedient (zero-install); die native App (USP:
   Inferenz-Router zum Heim-Ollama) wird **Ausbaustufe 3** der Plattform statt
   eigenes Produkt → `Plannung/Native-App/` (Architektur-Plan + Expo-Skeleton).
   Ergebnis: ein Gate statt drei, ein Portfolio-Eintrag weniger.
2. **Bauplan** (`Plannung/Bauplan-Feed-Scraper-Wasm.md`): Usecase „Persönlicher
   Themen-Assistent" (Feeds statt Scraping — gleiche rechtliche Linie wie
   Lead-Radar), Architektur „eine Wasm-Komponente, zwei Laufzeiten" (Wassette
   desktop mit Feed-only-Netzrechten / jco-Transpile für die PWA), 3-Hebel-
   Mapping (RAG Phase 3, Agentic Loop Phase 4, QLoRA bewusst später),
   4 Phasen mit Kommandos, Risiken (CORS→Proxy-Fallback, fetch-Support,
   Speicherbudget, iOS-WebGPU).
3. **Phase 0 erledigt:** Toolchain verifiziert (Node 24.15, componentize-js
   0.21.0, jco 1.25.2) — Umsetzung ab Phase 1 wartet auf Gate-Freigabe.

### Nachtrag: FREIGABE + Architektur-Plan + Phase 1 GEBAUT ✅

CEO hat das Gate freigegeben (Status FREIGEGEBEN_2026-07-17) und als neue
Dauerregel einen **Architektur-Plan (Diagramm) für jeden Produktbau** verlangt
→ `Plannung/Architektur-Themen-Assistent.md` (Mermaid: Systemübersicht,
Sequenz des Loops, Modul-Tabelle, Erweiterungspunkte) + Feedback-Memory.

**Phase 1 umgesetzt und verifiziert:**
1. `Produkt/scraper-komponente/`: WIT-Interface (`fetch-feed(url) →
   result<list<feed-item>, string>`), JS mit Regex-RSS/Atom-Parser (kein
   DOMParser in StarlingMonkey!), componentize-js-Build auf Anhieb → 12,5-MB-Wasm.
2. Wassette-Load: Pfadformat-Falle — `file:///C:/...` wird abgelehnt,
   `file://C:/...` (zwei Slashes) funktioniert.
3. Policy: `permission grant network feed-scraper www.tagesschau.de` — NUR
   dieser Host.
4. **Test über `wassette serve --streamable-http` + MCP-JSON-RPC** (das CLI
   `tool invoke` löst Komponenten-Tools in v0.4.0 nicht auf — Session nötig):
   Tagesschau-Feed → saubere Items mit Titel/Link/Datum/Text ✓;
   **example.com → von der Sandbox verweigert** („fetch_https: host API
   error") ✓. Deny-by-default funktioniert in der Praxis.

Gelernt: Wasm-Komponente wirft JS-`throw` als result-err durch — sauberes
Fehler-Mapping ohne Extra-Code. Nächster Schritt: Phase 2 (jco transpile
für die PWA + CORS-Realitätstest).

### Nachtrag: Phase 2 ✅ — dieselbe Komponente läuft im Browser (DokuCheck-Testseite)

CEO-Frage „keine GUI? in DokuCheck einbauen?" → Phase 2 vorgezogen und gebaut:

1. jco-Transpile + **vendored** preview2-shims (Import-Map statt Bundler,
   CSP/offline-konform wie DokuCheck), Feed-Proxy `/feeds/<id>` im Dashboard
   (Whitelist, Fremd-IDs → 404), Testseite `scraper-test.html` mit Auto-Run-
   Parameter für Headless-Tests.
2. **Zwei echte Stolpersteine:** (a) WASI-HTTP-Shim braucht absolute URLs —
   relative Proxy-Pfade werfen URL-Constructor-Fehler; (b) danach trapte
   wasi-http komplett (C++ out_of_range in StarlingMonkey, Chrome-Konsole via
   `--enable-logging=stderr` war der Schlüssel). Statt Shim-Debugging:
   **Architektur-Entscheid** — Browser-Pfad = Seite fetcht (Browser/CORS = Netz-
   Sandbox), Wasm parst via neuem Export `parse-feed(xml)`; Desktop behält
   `fetch-feed` + Wassette-Policy. Kein Sicherheitsverlust, eine Codebasis.
3. E2E: Headless-Chrome mit `--virtual-time-budget` + `--dump-dom` →
   **„50 Items in 10 ms"**, echte Tagesschau-Artikel im DOM, Screenshot visuell
   geprüft; Desktop-Regression (test-scraper.py) weiter grün — Komponente
   exportiert jetzt 2 Tools (fetch-feed, parse-feed).
4. Wiederverwendung dokumentiert: CorporateLLM (Browser, parse-feed) und
   Research-Agent/AI-OS-Agenten (Wassette-MCP, fetch-feed) können die
   identische .wasm nutzen — im Architektur-Plan festgehalten.

### Nachtrag: Gate-Prüfung Themen-Assistent + Analyse Browser vs. Native

1. **Wirtschaftlichkeitsprüfung** (`wirtschaftlichkeit-themen-assistent.md`,
   Format des Prüfer-Agenten): Marktbedarf 6/10 (echte Lücke „lokal statt
   Cloud", aber erklärungsbedürftig + Reichweiten-abhängig). Ehrlich: als
   reines Endverbraucher-Produkt trägt es sich im Jahr 1 NICHT (Anlaufkurve
   M1–6 ≈ 0 €); belastbarer Geldweg = B2B-Done-for-you (1.500–5.000 €/Setup,
   LeadPilot-Muster). 0 € Cash, ~30 h Bau, Doppelnutzen mit DokuCheck v0.3.
   → **GO_MIT_AUFLAGEN** (max. 4 Bautage, Payment erst ab Trigger >500 Nutzer
   oder B2B-Anfrage, Demo-Video ab Phase 4, Nachprüfung M3).
   **Status WARTET_AUF_FREIGABE.**
1b. **Usecase-Analyse nachgereicht** (CEO-Wunsch, Branchen aus der docx bewertet):
   Medizin/Banken = technisch gleiche Plattform, aber für Solo-Einstieg
   blockiert (MDR/CE bzw. BaFin/Enterprise-Onboarding) → nur Marketing-Narrativ.
   Realistisch: **Kanzleien/Steuerberater als Beachhead** (DSGVO = Kaufgrund,
   DokuCheck-Basis existiert), dann Industrie-Wartung als KMU-Variante (M6+).
   Kern-Erkenntnis: jede Branchen-Variante = gleiche Codebasis, nur andere
   Feeds/Dokumente/Finetuning → das ist der Plattform-Hebel. Auflage 3 auf
   Zielbranche Kanzleien geschärft.
2. **Browser vs. Native** (`Plannung/Analyse-Browser-vs-Native.md`, CEO-Frage):
   Kernbefund — **Antwortqualität ist identisch** (gleiche Gewichte/Quantisierung,
   RAG + Loop sind Software); Unterschiede nur Tempo (WebGPU ≈ 80–90 % nativ,
   kein NPU-Zugriff) und Komfort (kein zuverlässiger Hintergrund-Sync im
   Browser). Für den Usecase verschmerzbar (Feeds laden beim Öffnen). PWA-
   Vorteile überwiegen klar (Link-Distribution, eine Codebase, 0 €, Datenschutz
   per F12 beweisbar > App-Vertrauen). **Native App zurückgestellt**, nur bei
   Triggern T1–T3; Inferenz-Router als mögliches PWA-Feature „Stufe 2.5".
`git add` bricht bei EINEM ungültigen Pfad KOMPLETT ab (fatal pathspec →
nichts gestaged, obwohl es so aussah). Vendor-Check vor Commit: kein
node_modules/EspoCRM/web-llm-chat im Staging ✓. Services nachher: LeadPilot
200 ✓, DokuCheck-Proxy 200 ✓.

---

## 2026-07-16 (Tag 6) — Research-Agent: Themen-Gruppen + Gewinnchancen · Dashboard-Feinschliff

1. **Themen-Gruppierung im Research-Agent** (CEO-Wunsch): 8 Kategorien
   (KI-Tools/Deepfakes, Finanz/Trading, Business/Coaching, Krypto, IT/Apps,
   Immobilien, Gesundheit, Sonstiges) mit Regex-Klassifizierung pro Fund
   (dreisprachig). Alt-Funde werden lazy nachklassifiziert (`_mit_kategorie`).
2. **Gewinnchancen pro Thema** nach Wirtschaftlichkeits-Prüfer-Logik: statisches
   `potenzial` 0–10 (RPM × Material × Konkurrenzlücke ÷ Rechtsrisiko) + RPM-Spanne
   + Klartext-Einschätzung, kombiniert mit der GEMESSENEN Nachfrage (Funde-Zahl
   aus den Scans). API `/api/themen`, UI: Themen-Karten mit Potenzialbalken
   (Ampelfarbe), Klick = Filter auf alle Funde-Listen.
   Erste echte Zahlen: KI-Tools 9/10 (28 Funde!), IT/Apps 6/10 (41), Finanz 8/10 (4).
   Interessant: „Sonstiges“ hat 50 Funde → Muster-Katalog später nachschärfen.
3. **Dashboard**: Tab „🛍️ Produkte“ → „🏭 Produktion“ umbenannt (Nav, Titel-Map,
   Überschrift), AI-Business-Checker-Karte an Position 1 (CEO-Priorität),
   Kartentext um Themen-Gruppen/Gewinnchancen ergänzt.
   Verifiziert per Struktur-Assertions (Reihenfolge, keine Dublette) + node --check.

### Nachtrag: LeadPilot CRM gebaut — Phase A des IT Pipeline Systems ✅

Nach CEO-Freigabe (16.07., GO_MIT_AUFLAGEN + Zusatz: portabel für AI-OS UND
Trace-AI OS, SaaS-UX, eigenes CRM, Lead-Radar) komplette Phase A umgesetzt:

**LeadPilot** (`IT Pipeline System inkl CRM/app/`, Flask :5330, self-contained):
1. **CRM-Kern:** Leads mit 6-Stufen-Pipeline (Kanban Drag&Drop), Verlaufs-Protokoll,
   Volltextsuche, Pipeline-Wert; Webhooks für Kontaktformular + Cal.com
   (BOOKING_CREATED) mit **Dedup per E-Mail** (gleiche Person → Verlaufs-Eintrag
   statt Dublette, Termin wird nachgetragen).
2. **F3 umgesetzt:** Mail 1 (Eingangsbestätigung) sofort bei JEDEM Lead;
   Mail 2 (Buchungs-Erinnerung) systemseitig auf **genau 1× pro Lead** begrenzt
   (Flag, kein Drip → §7 UWG). Ohne SMTP-Env landen Mails sichtbar im Postausgang.
3. **F2 umgesetzt:** Export je Lead (Art. 15), Hard-Delete inkl. Mails (Art. 17),
   Anonymisieren, Löschkonzept (verlorene Leads nach X Monaten, Dashboard-Banner
   + Aufräum-Button).
4. **Lead-Radar:** RemoteOK/WWR/Remotive + eigene Feeds, Keyword-Scoring mit
   **Wortgrenzen** (Bugfix: "ai" matchte in "maintain" — 156 Treffer vorher,
   64 saubere nachher), 1 Klick → Lead. Bewusst Projektbörsen statt
   Personendaten-Scraping (DSGVO/UWG, in README dokumentiert).
5. **SaaS-UI:** Sidebar-App (Dashboard-KPIs, Pipeline, Leads-Tabelle, Radar,
   Postausgang, Einstellungen mit Mail-Templates/Keywords/DSGVO-Frist).
6. **Portabilität:** keine Host-Imports, relative API-Pfade, `INSTALL.md` mit
   3 Varianten (standalone / AI-OS / Trace-AI OS inkl. Proxy-Snippet + Warnung
   vor der Werkzeug-Routen-Falle). EspoCRM bewusst NICHT genutzt (PHP+MySQL-
   Overhead), bleibt als Referenz liegen.

End-to-End verifiziert: Webhook→Lead→Mail1 ✓, Cal.com-Dedup+Termin ✓, Move ✓,
Export ✓, Anonymisieren ✓, Radar-Scan (64 Treffer, 0 Fehler) ✓, Übernahme ✓,
Config ✓, alles auch durch den Dashboard-Proxy `/produkte/it-pipeline/` ✓,
Regression der 3 anderen Produkte ✓.

### Nachtrag: Eigene Terminbuchung (Cal.com-Ersatz) + helles Corporate-Theme

CEO wollte weg von der Cal.com-Abhängigkeit → statt Fremdlösung (Cal.com
self-hosted = Node+DB, Easy!Appointments = PHP+MySQL) **Terminbuchung direkt in
LeadPilot eingebaut**:

1. **Slot-Engine:** konfigurierbar (Wochentage, von/bis, Slot-Dauer, Vorlauf-
   Stunden, Horizont-Tage), Kollisionsprüfung gegen gebuchte Lead-Termine,
   Doppelbuchung → 409. Deutsche Wochentags-Labels (strftime %a wäre englisch).
2. **Öffentliche Buchungsseite `/buchen`** (3 Schritte: Tag → Uhrzeit → Daten),
   hell/professionell, per iframe auf vuxuantiep.de einbettbar — Embed-Snippet
   wird in den Einstellungen generiert. Buchung → Lead (Quelle „buchung") +
   **Mail 3 Terminbestätigung** (neues Template mit {termin_text}).
3. **ICS-Kalender-Feed `/api/termine.ics`** — Kalender-Abo in Thunderbird/
   Outlook/Google statt externem Kalenderdienst. Dashboard zeigt „Nächste Termine".
4. **Helles Corporate-Theme** als Standard (CSS-Variablen, angelehnt an
   Trace-AI OS/CorporateLLM), Dunkel-Modus per Sidebar-Toggle (localStorage).
   Buchungsseite im gleichen Look.

End-to-End: /buchen 200 ✓, Tage/Slots ✓, Buchung ✓ (Mail 3 im Postausgang),
Doppelbuchung 409 ✓, ICS 1 VEVENT ✓, naechste_termine ✓, via Proxy ✓,
Screenshots (hell + Buchungsseite) visuell geprüft ✓.

### Nachtrag: LeadPilot → komplettes Freelancer-Betriebssystem (CEO-Ausbau)

Auf CEO-Wunsch massiv erweitert — LeadPilot ist jetzt CRM + Faktura + Zeiterfassung:

1. **Kundenverwaltung** (Neu/Bestand, Adresse für Rechnungen, individueller
   Stundensatz), „Als Kunde übernehmen"-Button im Lead-Modal (Dedup per E-Mail).
2. **Leistungskatalog** mit Seed aus echten Produkten beider Plattformen
   (DocuCheck, KI-Avatar-Pipeline, LeadPilot) + Dienstleistungen mit
   **Marktpreis-Spannen** (Orientierung, manuell gepflegt — beim Angebot-Erstellen
   wird die Spanne neben dem eigenen Preis angezeigt = „Marktpreise-Blick").
3. **Dokumente**: Angebot/Rechnung/Mahnung/Dienstvertrag mit Nummernkreisen je
   Typ+Jahr — Rechnungen im Format der eigenen Vorlage („2026-001", Aufbau aus
   `Plannung/Rechnungsvorlagen` per xlsx-Analyse extrahiert). A4-Druckansicht
   (`/dokument/<id>`, Browser-Druck → PDF) mit §14-UStG-Pflichtangaben,
   USt./Kleinunternehmer umschaltbar. Mahnwesen 3-stufig (Erinnerung → 1. → 2.
   Mahnung mit §288-BGB-Hinweis), Überfällig-Erkennung automatisch.
4. **Zeiterfassung** mit „Offene Zeiten → Rechnung" (Positionen je Tag,
   Leistungszeitraum automatisch, Zeiten werden als abgerechnet markiert).
5. **Dienstvertrag**: Generator (Muster mit Selbstständigkeits-Klauseln, AVV-
   Hinweis, Haftungsbegrenzung + Disclaimer) und **Prüfer** (Checklisten-Heuristik:
   10 Pflichtklauseln + 8 Risikosignale inkl. Scheinselbstständigkeit).
6. **Radar-Autoscan täglich 7 Uhr** (Hintergrund-Thread + Marker in radar.json,
   „Jetzt scannen" bleibt), Stunde konfigurierbar.

Verifiziert: 8-Schritte-E2E (Kunde → Katalog → Angebot A-2026-001 → Zeiten →
Rechnung 2026-001 → Mahnung M-2026-001 → Vertrag + Druck → Prüfung erkennt
Weisungsbindung/feste Arbeitszeiten → Lead→Kunde) + Rechnungs-Screenshot
gegen Vorlage abgeglichen. SMTP-Daten (IONOS) trägt CEO nach.

**Nachschlag: Radar-Rollenfilter** — 9 Aufgabenprofile (IT-Support, Sysadmin,
Application Manager, KI-Automation, KI-Berater, Cloud-Admin/DevOps, IT-Techniker,
Entwickler, Daten) als Regex-Klassifizierung mit Prioritätsreihenfolge,
Filter-Chips mit Trefferzahl im Radar, Alt-Treffer lazy nachklassifiziert.
Test: 66 Treffer → 32 Entwickler, 6 KI-Automation, 6 Cloud, 2 Support …

### Nachtrag: Konzept-Prüfung „IT Pipeline System inkl. CRM" (neues Produkt)

CEO hat neues Produkt eingebracht (`10_Business/IT Pipeline System inkl CRM/`):
Lead-Pipeline + CRM für IT-Freelancer, doppelt verwertbar (Eigennutzung +
Done-for-you-Verkauf à 2.000–5.000 €, siehe Recherche-Screenshots).

**Konzept-Prüfung** (`Plannung/Konzept-Pruefung.md`) — 3 harte Findings:
- **F1: HubSpot Free hat KEINE Workflow-Automatisierung** — Stufe 3 des Konzepts
  (Trigger-Mails „im CRM eingebaut, kein Zusatztool") stimmt im Free-Tier nicht.
  Empfehlung: self-hosted CRM + n8n (passt zur AI-OS-Philosophie, macht es erst
  zum echten Modul).
- **F2: DSGVO/UWG fehlt** (AV-Vertrag, §7 UWG bei Follow-up-Mails: keine Drip-Serien
  ohne Einwilligung, Löschkonzept).
- **F3: Linker Pfad verschenkt die sofortige Eingangsbestätigung** — die
  konversionsstärkste Automatisierung gehört in BEIDE Pfade.

**Wirtschaftlichkeitsprüfung** (Gate-Regel 4, `wirtschaftlichkeit-it-pipeline-crm.md`):
Anders als beim Checker ist der konservative Fall hier nicht negativ (eigenes
System bleibt immer übrig). Basis-Szenario ~6.000–12.000 €/Jahr (2–3 verkaufte
Setups + 1 Zusatzauftrag durch schnellere Reaktion), ~80–150 €/h.
→ **GO_MIT_AUFLAGEN**: Phase A (Eigenbau, max. 3 Tage, self-hosted, 0 € Cash)
sofort; Phase B (Produktisierung) erst nach 4 Wochen Echtbetrieb + Nutzen-Nachweis.
**Status: WARTET_AUF_FREIGABE.**

### Nachtrag: Positiv-Liste „Gelobte KI-Business" (CEO-Wunsch)

Separater grüner Bereich unten auf der Checker-Seite: KI-Business, die in den
Quellen **gelobt / als funktionierend** erwähnt werden — inkl. „Mehrfach erwähnt"-
Chips (Namen, die über ≥2 positive Funde auftauchen = Kandidaten für
„überraschend okay"-Videos).

- Erkennung bewusst konservativ: Lob-Muster DE/EN/VI („hat bei mir funktioniert",
  „got paid", „uy tín" …), **Fragen disqualifizieren** („Is X legit?" ist Suche,
  kein Lob), Warnsignal-Treffer schließen Positiv-Einstufung aus.
- Neue Reddit-Suchläufe für Erfolgsberichte (r/sidehustle, r/Entrepreneur),
  eigene Empfehlungsklasse `positiv` (umgeht den Scam-Score-Filter),
  API `/api/positiv` mit Namens-Aggregation (`extrahiere_namen` + Stopwörter).
- **Getestet per Integrationstest mit synthetischen Funden** (Reddit war nach
  4 Scans in 30 min komplett rate-limited): 2 Positive korrekt erkannt, Frage
  korrekt abgelehnt, „Jasper ×2" aggregiert, Store danach wiederhergestellt.
  Hinweis im UI: Positiv-Liste ist kein Gütesiegel — Dossier-Pflicht bleibt.

---

## 2026-07-15 (Tag 5) — Usecase 3: „AI Business Checker" geplant

### Was heute entstanden ist

Dritter Usecase fürs KI-Avatar-Produkt: **AI Business Checker** — YouTube-Kanal +
TikTok-Shorts, der „Geld verdienen mit KI"-Anbieter auf Seriosität prüft
(Warnung/Aufklärung, Animation statt Avatar).

1. **Plan** (`01_Usecases/usecase-ai-business-checker.md`): Kanal-Konzept mit
   4 wiederkehrenden Formaten, angepasste Pipeline (Research-Scan → Scoring →
   **Dossier** → Skript → Stimme → **Animation** → Edit → QA/Legal → Posting),
   Monetarisierung (bewusst KEINE Affiliates → Unabhängigkeit), 4-Phasen-Roadmap.
   Animation via Remotion-Templates = einzige bezahlte API (HeyGen) entfällt hier.
2. **Market-Research-Agent** (`Konzept-KI Avatar/market-research-agent.md`):
   Quellen-Prioritäten (amtlich > dokumentierend > Community), Warnsignal-Katalog
   W1–W8, JSON-Dossier-Format mit Beleg-Pflicht (URL + Zitat + Datum),
   Scoring-Rubrik, harte Verhaltensregeln (2-Quellen-Minimum, neutrale Sprache,
   Positivbefunde melden — Agent ist Rechercheur, kein Richter).
3. **Compliance-Critic-Agent → Check 7 „Äußerungsrecht"**: verbotene Begriffe
   ohne Urteil („Betrug") = Block, jede Tatsachenbehauptung muss dem Dossier
   zuordenbar sein, 2-Quellen-Minimum, Stellungnahme-Pflicht bei Deep-Dives
   (Verdachtsberichterstattung!). Neues Schema-Feld `aeusserungsrecht`.
4. **Board erweitert**: dritter Usecase mit eigenem Filter-Chip + Badge-Farbe,
   Label-Mapping von hartkodiertem Ternary auf `UC_LABEL`-Map umgestellt.

### Wichtigste Design-Entscheidung (gelernt)

Bei einem Prüf-/Warn-Kanal ist **Äußerungsrecht der härteste Blocker**, nicht
Plattform-Compliance: Eine falsche Tatsachenbehauptung über einen benannten
Anbieter = Abmahnung. Deshalb Dossier-Stufe als Pflicht-Input VOR dem Skript
(keine Behauptung ohne Beleg-Datensatz) statt Legal-Check erst am Ende.

### Nachtrag: Wirtschaftlichkeits-Gate als neue Pflicht-Regel

Neue CEO-Anweisung dauerhaft verankert: Jede neue Produktplanung enthält ab jetzt
einen **Wirtschaftlichkeits-Prüfer-Agenten**, und Umsetzung startet erst nach Freigabe.

1. **Agent-Prompt** (`10_Business/wirtschaftlichkeits-pruefer-agent.md`, wiederverwendbar
   für alle Produkte): Marktbedarf → Einnahmequellen-Inventar (mit Voraussetzungen +
   „fließt ab Monat X") → 3-Szenarien-Rechnung (P70/P50/P20 mit Anlaufkurve) →
   Kosten inkl. Arbeitszeit → Break-even → GO/GO_MIT_AUFLAGEN/PIVOT/NO_GO.
   Wichtigste Regeln: keine Zahl ohne Herkunft, €/Arbeitsstunde immer ausweisen
   (versteckte Selbstausbeutung!), Monat 1–6 bei Content ≈ 0 € ehrlich einplanen.
2. **Erste Anwendung** (`wirtschaftlichkeit-ai-business-checker.md`): Marktbedarf 7/10,
   5 Einnahmequellen (Affiliate bewusst ausgeschlossen), Basis-Szenario ~250–450 €/Mon.
   in Monat 12, Break-even Cash Monat ~9–10, ABER nur ~8–10 €/h — der echte Hebel ist
   die Pipeline-Wiederverwendung über alle 3 Usecases + Digitalprodukt in Jahr 2.
   → **GO_MIT_AUFLAGEN** (3-Monats-Meilenstein, 15h/Woche- und 500-€-Deckel),
   Status WARTET_AUF_FREIGABE.
3. **CLAUDE.md**: als Arbeitsregel 4 „Wirtschaftlichkeits-Gate" eingetragen
   (Secrets rückte auf 5), zusätzlich als Feedback-Memory gespeichert.

### Nachtrag 2: CEO-Freigabe erteilt → Phase 0 umgesetzt

**Freigabe 15.07.2026** (GO_MIT_AUFLAGEN dokumentiert), danach beide Phase-0-Bausteine gebaut:

1. **Market-Research-Agent v1** (`research-agent/app.py`, Flask :5320, im Dashboard
   als Dienst registriert): scannt Reddit + Verbraucherdienst-Blog + Watchlist
   Internet (optional SearXNG via env), bewertet gegen Warnsignal-Katalog W1–W8
   (Regex-Heuristik) + KI-Relevanz-Filter, dedupliziert, persistiert atomar.
   API: `/api/scan` (POST), `/api/funde?empfehlung=video_kandidat`, CLI `--scan`.
   **Erster Live-Scan: 104 Funde, 2 Video-Kandidaten** (Deepfake-Promi-Werbung),
   „Peak Momentum Erfahrungen" auf der Beobachtungsliste — das Format trägt.
2. **Remotion-Template-Set** (`animation/`): CheckerLong (16:9) + CheckerShort
   (9:16) als EIN datengetriebenes Template — Dossier-JSON rein, Video raus.
   Szenen: Intro → Warnsignal-Karten (Zitat + Quellenleiste) → animierter
   Risiko-Score (Ampelfarben) → Checklisten-Outro. KI-Label ab Sekunde 1 fest
   eingebaut (Art. 50). Dauer wächst via `calculateMetadata` automatisch mit
   der Warnsignal-Anzahl. **Test-Render: 14-s-Short komplett (420 Frames, 1,8 MB)**
   + 2 Preview-Frames visuell geprüft.

**Stolpersteine des Tages:**
- Reddits JSON-API liefert pauschal 403 (auch mit Browser-UA) — die **RSS-Endpunkte
  (`old.reddit.com/.../search.rss`) funktionieren**. Merke: bei Reddit-Scraping
  ohne OAuth immer RSS statt JSON. Zusätzlich ≥4 s Pause, sonst 429.
- Watchlist Internet: Feed liegt unter `/rss/`, nicht `/rss.xml`.
- Feed-Parser namespace-agnostisch bauen (`tag.split('}')[-1]`), damit RSS 2.0
  UND Atom (Reddit) mit demselben Code funktionieren.

### Nachtrag 3: Research-Agent global + eigene Quellen (CEO-Wunsch)

1. **Globale Quellen eingebaut** (Kanal-Ziel: weltweite Sichtbarkeit, DE + US + VN):
   FTC Consumer Alerts + FTC Consumer Protection News (USA), VnExpress Pháp
   luật/Số hóa + Tuổi Trẻ Pháp luật (Vietnam). Warnsignal-Muster jetzt
   dreisprachig DE/EN/VI („lừa đảo", „việc nhẹ lương cao", „đa cấp", „earn $X/day").
   Scan-Verteilung nach Umbau: 81 AT, 22 VN, 13 US, 14 Reddit ✓
2. **Eigene-Quellen-Feature**: Eingabe-Box auf der Startseite — URL rein,
   `erkenne_quelle()` prüft automatisch: direkter RSS/Atom-Feed? In der HTML-Seite
   verlinkter Feed (`<link type="application/rss+xml">`)? Sonst Seiten-Scan
   (sichtbarer Text, Inhalts-Hash in der Dedup-URL → geänderte Seite = neuer Fund).
   API: GET/POST/DELETE `/api/quellen`, Persistenz `data/custom_sources.json`.
   Getestet: WordPress-Blog → Feed autodetected ✓, ScamAdviser → Seiten-Scan ✓.

### Nachtrag 4: AI Business Checker im Dashboard sichtbar

Dritte Produktkarte im Produkte-Tab (🔎 AI Business Checker, Status-Pill +
Öffnen-Button). Dafür den ki-avatar-Proxy zu `PRODUKT_PROXIES` verallgemeinert
(Dict prod→Port, Dispatching weiter in `serve_produkt`): `/produkte/ai-checker/`
→ :5320. Status-Check im Frontend als Schleife über `PRODUCT_SERVICES` statt
Einzelfunktion. Proxy-Timeout 15→300 s, weil der Scan-Button über den Proxy
einen 1–2-Minuten-POST macht. Getestet: alle 3 Produkte via :5000 erreichbar,
Checker-Health über Proxy 200 ✓.

---

## 2026-07-14 (Tag 4) — KI-Avatar: Produktstart + Pipeline-Board (Port 5310)

### Was heute entstanden ist

Neues Business-Produkt **KI-Avatar** unter `10_Business/KI-Avatar/` gestartet
(2 Usecases: YouTube-Automation, TikTok-Shop) — inkl. Trello-artigem
**Pipeline-Board** als AI-OS-Erweiterung:

1. **Compliance-Critic-Agent überarbeitet** (`Konzept-KI Avatar/compliance-critic-agent.md`):
   - Batch-Schema um Felder ergänzt, die der Prüfkatalog referenzierte, aber nie bekam
     (`transcript`, `duration_seconds`, `daily_shoppable_count`, `channel_metadata`, `native_ai_label_set`)
   - Enum-Bug `youtube_short` vs. `youtube_shorts` gefixt
   - Explizite Status-Ableitungsregel (fail→BLOCKED, warning→APPROVED_WITH_WARNING)
   - Art. 50 EU-KI-VO plattformunabhängig gemacht (gilt ab 02.08.2026!)
   - False-Positive-Schutz: "Geld-zurück-Garantie" ≠ Heilsversprechen

2. **Pipeline-Board** (`board/app.py` + `templates/board.html`, Flask, Port 5310):
   - 8 Spalten = Pipeline-Stufen (Trend-Scan → … → Posting → Veröffentlicht)
   - Karten = Videos: Usecase, Plattform, Kanal, Compliance-Status, Notizen
   - Drag & Drop (HTML5, optimistisches Update mit Rollback bei API-Fehler)
   - Usecase-Filter-Chips, Farben wie im Architektur-Diagramm
     (türkis = selbst gehostet, koralle = externe API, grau = Ein-/Ausgabe)
   - REST-API: GET /api/board, POST/PUT/DELETE /api/cards, POST /api/cards/id/move
   - Persistenz: `board/data/board.json` (atomares Schreiben via tmp + os.replace)

### Was ich dabei gelernt/beachtet habe

- **LLM-Agent-Prompts brauchen ein vollständiges Eingabe-Schema:** Jede Prüfung im
  Prompt, für die kein Eingabefeld existiert, zwingt das Modell zum Raten. Regel:
  erst Felder definieren, dann Prüfungen darauf aufbauen — und für fehlende
  optionale Felder explizit `manual_review`/`n/a` vorschreiben statt Block.
- **Bekannte Stolpersteine vorab entschärft:** JS aus dem Template extrahiert und
  mit `node --check` geprüft (Dashboard-Lektion), `sys.stdout.reconfigure(utf-8)`
  gegen den Windows-Print-Bug, eigener Port 5310 statt 5000 (keine Zombie-Kollision).
- **Atomares JSON-Schreiben** (`tmp` + `os.replace`) verhindert kaputte board.json
  bei Absturz mitten im Schreiben.

### Verifikation

Server gestartet, komplette API durchgetestet: Health ✓, Board laden (8 Stufen,
Seed-Karten) ✓, Karte anlegen ✓, verschieben ✓, Compliance updaten ✓, ungültige
Stufe → 400 ✓, löschen ✓, Startseite HTTP 200 ✓, JS/Python-Syntax ✓.

### Nachtrag (gleicher Tag): Dashboard-Integration „Produkte"-Tab

Beide Produkte ins AI-OS-Dashboard eingruppiert:

1. **Neuer Nav-Tab „🛍️ Produkte“** (`templates/dashboard.html`) — ersetzt den
   einzelnen DocuCheck-Button. Panel mit Produktkarten (service-card-Stil):
   DocuCheck Local + KI-Avatar Pipeline-Board, je mit Beschreibung, Status-Pill
   und Öffnen-Button. Deep-Link `/#products` funktioniert über den bestehenden
   Hash-Mechanismus automatisch.
2. **Proxy `/produkte/ki-avatar/` → 127.0.0.1:5310** (`ai_os_dashboard.py`) —
   bewusst Proxy statt Direktlink auf `localhost:5310`: über Cloudflare-Tunnel
   und Tailscale ist nur Port 5000 exponiert; so ist das Board auch remote
   nutzbar. GET/POST/PUT/DELETE werden mit Body + Content-Type durchgereicht,
   bei Offline-Board kommt eine 503-Seite mit Startbefehl.
3. **Board auf relative API-Pfade umgestellt** (`board.html`: `api()` strippt
   führenden Slash) — dieselbe Datei funktioniert standalone (`/api/board`)
   und hinter dem Proxy (`/produkte/ki-avatar/api/board`). Der ⌂-AI-OS-Link
   zeigt hinter dem Proxy auf `/` statt hart auf `localhost:5000`.
4. **Dienst-Registrierung**: KI-Avatar Board als SERVICES-Eintrag (Port 5310,
   `health_path: /api/health`, Layer 10_Business) — erscheint im Dienste-Tab
   und ist von dort startbar; `app.py` liest jetzt `KIAVATAR_BOARD_PORT` aus.

**Gelernt (durch Test widerlegte Annahme!):** Ich hatte erwartet, dass Werkzeug
die spezifischere Route `/produkte/ki-avatar/<path>` vor `/produkte/<prod>/<path>`
matcht — tut es NICHT: die generische Route gewann, der Proxy bekam nie Requests
(Symptom: `{"error": "Unbekanntes Produkt"}` + 405 bei POST). Lösung: keine
konkurrierende Route, sondern Dispatching **innerhalb** von `serve_produkt`
(`if prod == "ki-avatar": return _kiavatar_proxy(...)`). Merksatz: Bei
überlappenden Flask-Routen nie auf Prioritätsregeln verlassen — selbst dispatchen.

**Zombie-Falle erneut bestätigt:** Auf Port 5000 lief noch ein `pythonw` von
GESTERN (13.07., PID 65672) und servierte alten Code, während der neue Server
scheinbar fehlerfrei startete (Windows erlaubt Doppel-Bind). Erst
`Get-NetTCPConnection -LocalPort 5000` + `Stop-Process` machte den Weg frei —
genau wie in der Memory-Notiz dokumentiert.

Außerdem: Ein Sub-Dienst hinter einem Pfad-Proxy darf im Frontend keine
absoluten Pfade (`/api/...`) verwenden, sonst landen die Requests am falschen
Server — deshalb nutzt das Board jetzt relative Pfade.

**End-to-End verifiziert:** Proxy-CRUD komplett (POST/MOVE/DELETE über
`/produkte/ki-avatar/api/...`) ✓, Board-Seite via Proxy HTTP 200 ✓, DocuCheck
weiterhin HTTP 200 ✓, Offline-Fall → 503-Hinweisseite mit Startbefehl ✓,
Produkte-Tab im Dashboard-HTML vorhanden ✓.

---

## 2026-07-12 (Tag 3) — DokuCheck Lokal v0.2: Browser-KI als erstes Produkt

### Was heute entstanden ist

| # | Arbeit | Ort |
|---|--------|-----|
| 1 | **DokuCheck Lokal v0.2** — Prototyp-Monolith zerlegt in saubere App (HTML/CSS/JS, kein Build-Toolchain) | `10_Business/Lokal-SML-Webassembly-MultiMemory/Produkt/dokucheck-lokal/` |
| 2 | **Vendoring statt CDN**: WebLLM 0.2.79, pdf.js 4.4.168, Tesseract.js 5.1.1 + Sprachdaten (deu/eng/vie) lokal eingecheckt | `.../vendor/` |
| 3 | **WebLLM in Web Worker** verschoben — UI bleibt während Inferenz responsiv | `worker.js` |
| 4 | **OCR-Modul** (Bild → Text, WASM, läuft ohne WebGPU) + 📷 Kamera-Aufnahme mobil | `ocr.js` |
| 5 | **Übersetzen** (Deutsch/Englisch/Vietnamesisch) über das geladene SLM — keine neue Bibliothek | `app.js` |
| 6 | **BM25-Retrieval** statt Keyword-Zählen + Map-Reduce-Zusammenfassung für lange Dokumente | `app.js` |
| 7 | **Multi-Memory-Panel** (IndexedDB): Episodic (Verlauf), Semantic (Dokumente), Procedural (Prüfroutinen), Tool (Modellwahl) | `memory/` |
| 8 | **PWA**: installierbar, App-Shell offline (Service Worker), Manifest + Icon | `sw.js`, `manifest.webmanifest` |
| 9 | **Dashboard-Integration**: Route `/produkte/<prod>/` + Nav-Button „🛡️ DokuCheck Lokal" | `ai_os_dashboard.py`, `templates/dashboard.html` |
| 10 | Wiki-Kopie → Redirect-Stub (eine Quelle der Wahrheit) | `00_Wissen/04_Referenzen/Wiki/dokucheck-lokal.html` |
| 11 | **Mehrsprachigkeit DE/EN/VI** — Umschalter in der Beweisleiste, komplette UI + KI-Prompts übersetzt (locker formuliert), Wahl wird in Tool Memory gemerkt | `i18n.js` (107 Schlüssel × 3 Sprachen), `index.html` (`data-i18n`), `app.js` |
| 12 | **Schritt-Führung** — „✓ bereit“-Badges an Schritt 1/2/3, Schritt 3 ausgegraut bis alles bereit ist, dann Anscrollen + Puls-Highlight + grüner Nächster-Schritt-Hinweis | `app.js` (`statusFlow()`), `index.html`, `styles.css` |
| 13 | **Scan-PDF-Rettung** — PDFs ohne Textebene (0 Zeichen extrahiert!) werden erkannt, Seiten als Canvas gerendert und automatisch per OCR gelesen; leere Extraktion wird nie mehr als „✓ fertig“ angezeigt | `app.js` (`ocrPdf()`), `ocr.js` (`ocrWorker` wiederverwendbar) |
| 14 | **Bugfix Übersetzen** — Modell plauderte auf Deutsch („Ich verstehe, dass du möchtest …") statt nach Vietnamesisch zu übersetzen; Übersetzungs-Prompt aus i18n herausgelöst und sprachunabhängig auf Englisch fixiert, Anweisung zusätzlich in der User-Nachricht wiederholt | `app.js` (`uebersetzen()`, `TRANS_ZIEL`), `i18n.js` (`prompt.transSys` entfernt) |
| 15 | **Bugfix falsche OCR-Warnung** — „Texterkennung war unvollständig" erschien auch bei sauberen Text-PDFs: Qualitätsheuristik lief auf JEDEM Dokument und `/(.)\1\1+/` schlug schon bei „…"/„---"/„www" an; jetzt nur noch für echten OCR-Text (`ausOcr`-Flag) + Regex nur Buchstaben 4x+ | `app.js` (`setzeDokument()`, `schaetzeOcrQualitaet()`) |
| 16 | **Auto-Load des Modells** — nach Seiten-Reload blieb Schritt 3 grau, bis man Schritt 1 manuell neu klickte, obwohl die Gewichte im Cache lagen; jetzt lädt das Modell automatisch, sobald ein Dokument bereit ist und `hasModelInCache` zutrifft | `app.js` (`autoLadeModell()`), `i18n.js` (`s1.autoLoad` ×3) |

### Lern-Highlights des Tages (mit Code)

**1. Worker-Fetches sind für den Hauptthread unsichtbar.** Das Signatur-Feature
(Netzwerk-Beweiszähler) wäre durch den Umzug der Engine in den Web Worker blind
geworden: `PerformanceObserver` sieht nur Requests des eigenen Kontexts. Lösung —
zweiter Observer **im Worker**, Meldung per `BroadcastChannel` (stört das
WebLLM-Message-Protokoll nicht, anders als eigene `postMessage`-Typen):

```js
// worker.js
const netChannel = new BroadcastChannel("dokucheck-net");
new PerformanceObserver(list => {
  for (const e of list.getEntries())
    if (e.initiatorType === "fetch") netChannel.postMessage({ kind: "net", url: e.name });
}).observe({ entryTypes: ["resource"] });
```

**2. Windows-Registry sabotiert ES-Module.** Flask/`mimetypes` liest Content-Types
aus der Registry — `.js` kommt dort oft als `text/plain`, und Browser verweigern
dann Module und Worker. Pflicht-Fix im Dashboard:

```python
import mimetypes
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("application/wasm", ".wasm")
```

**3. „Offline" ehrlich definieren.** WebLLM hat keinen WASM/CPU-Fallback (Kernels
sind WebGPU-only) und die Modellgewichte (0,8–2 GB) kommen zwingend einmalig von
HuggingFace. Der ehrliche Claim: *App-Shell + OCR 100 % lokal; Analyse nach
einmaligem Modell-Download offline.* Deshalb zeigt die Beweisleiste jetzt zwei
Zähler: „Modell-Download (einmalig)" vs. „Analyse-Anfragen: 0".

**4. Übersetzen ohne neue Abhängigkeit.** Statt einer Translation-Bibliothek
übersetzt das bereits geladene SLM abschnittsweise (Chunk für Chunk, gestreamt) —
ein System-Prompt genügt.

**5. i18n ohne Framework.** Ein flaches Schlüssel-Objekt pro Sprache + zwei
DOM-Attribute reichen: `data-i18n` (textContent) und `data-i18n-ph` (placeholder).
Der Kniff bei dynamischen Elementen: Das Ausgabefeld trägt anfangs `data-i18n`
für den Platzhalter — sobald eine echte Analyse drinsteht, wird das Attribut
per `removeAttribute` entfernt, sonst würde ein Sprachwechsel das Ergebnis
überschreiben. Gleiches Muster beim „Modell laden“→„Modell wechseln“-Button:
statt nur den Text zu setzen, wird das `data-i18n`-Attribut mit umgestellt.
Wichtig: Die Sprachwahl steuert auch die **Prompts** (`prompt.sys` etc.) —
so antwortet die KI in der UI-Sprache. Die BM25-Suchbegriffe des Risiko-Checks
bleiben dagegen mehrsprachig kombiniert, weil sie zum **Dokument** passen
müssen, nicht zur UI.

### Nachtrag 12.07. abends: DocuCheck-Reparatur nach Fremd-Edits

Ein anderer Agent (Agile Agent Canvas) hatte die App erweitert (Presets, Stepper,
Exporte, OCR-Vorverarbeitung, Umbenennung DokuCheck→DocuCheck) und dabei vier
Fehler eingebaut, die **Schritt 2 komplett lahmlegten**:

1. **`bm25Index` tokenisierte Chunk-Objekte statt `c.text`** → TypeError bei jedem
   Dokument-Upload („s.toLowerCase is not a function"). Der Killer-Bug.
2. **`procedural.js`: nicht geschlossener Blockkommentar in Zeile 1** verschluckte
   Import + alle 5 CRUD-Exports bis zum nächsten `*/` (Zeile 36) — syntaktisch
   gültig (!), daher von `node --check` unsichtbar. Routinen + „Prüfung:"-Preset tot.
3. **`semantic.js`: `return doc`** — Variable existiert nicht → jede Speicherung
   rejected nach dem Schreiben, Dokumentliste blieb leer.
4. **Preset-Modelle (Qwen2 0.5B, Phi 3.5 mini) fehlten im Modell-Dropdown** →
   Profilwahl lief ins Leere, falsches Modell wäre geladen worden.

Dazu repariert: OCR-Vorverarbeitung warf bei Canvas-Quellen (Scan-PDF-Fallback)
weg (`URL.createObjectURL(canvas)` ist illegal) + Object-URL-Leak + `\3`-Oktal-Regex.

**Lehre:** Ein offener Blockkommentar ist der fieseste „Syntaxfehler", weil er
keiner ist — Prüfung ab jetzt zusätzlich: erwartete Exports greppen, nicht nur
`node --check`.

### Nachtrag 12.07.: Übersetzen nach Vietnamesisch war kaputt

Symptom: Statt der Übersetzung kam deutsches Geplauder („Ich verstehe, dass du
möchtest, dass ich den Text vollständig übersetze …"). Ursache: Der
Übersetzungs-Prompt kam aus i18n und war damit in der **UI-Sprache** — ein
deutscher System-Prompt plus roher Text ohne Anweisung in der User-Nachricht
verleitet kleine Modelle dazu, auf Deutsch zu kommentieren statt zu übersetzen.

Fix in `uebersetzen()`: Prompt aus i18n herausgelöst und fest auf Englisch
(SLMs folgen englischen Instruktionen am zuverlässigsten), Zielsprache doppelt
benannt und die Anweisung in der User-Nachricht wiederholt:

```js
const TRANS_ZIEL = { de: "German (Deutsch)", en: "English", vi: "Vietnamese (Tiếng Việt)" };
// system: "You are a translation engine. Translate ... into Vietnamese (Tiếng Việt).
//          Reply with ONLY the translated text ..."
// user:   "Translate the following text into Vietnamese (Tiếng Việt). Output only the translation:\n\n" + chunk
```

**Lehre (korrigiert Highlight 5):** UI-Sprache darf die *Antwortsprache* steuern
(Zusammenfassen, Fragen) — aber nie einen Prompt, dessen Zielsprache der Nutzer
separat wählt. Task-Prompts für SLMs: englisch, Anweisung nah am Text wiederholen.

### Nachtrag 12.07.: v0.3 — Übersetzen ohne LLM (transformers.js + OPUS-MT)

Erkenntnis aus dem Übersetzungs-Bug: Reine Übersetzung ist keine LLM-Aufgabe.
Spezialisierte NMT-Modelle (OPUS-MT/MarianMT, ~45 MB int8 statt ~800 MB SLM)
übersetzen besser, schneller und ohne Geplauder — und laufen als ONNX/WASM
auf der **CPU**, brauchen also kein WebGPU.

**Architektur:**
- `trans-worker.js` — eigener Web Worker mit transformers.js 3.8.1 (gevendort
  inkl. 21-MB-ONNX-Runtime-WASM in `vendor/transformers/`), lazy eine
  `pipeline("translation", ...)` je Sprachpaar, Gewichte einmalig von
  HuggingFace → Browser-Cache (gleiche Beweis-Logik wie WebLLM-Downloads:
  eigener `PerformanceObserver` + BroadcastChannel, in app.js `netPhase="model"`).
- Sprachpaare: `Xenova/opus-mt-{de-en,en-de,en-vi,vi-en}` (auf HF verifiziert);
  **de↔vi existiert nicht** → Pivot über Englisch (de→en→vi).
- Quellsprache heuristisch: vietnamesische Diakritika sind eindeutig,
  Deutsch vs. Englisch per Stoppwort-Zählung.
- MarianMT verkraftet nur ~512 Tokens → Text absatzweise in Satzgruppen
  (~420 Zeichen) zerlegen, `absatzEnde`-Flag erhält die Absatzstruktur.

**UI-Konsequenz:** Übersetzen ist vom SLM entkoppelt — `runAktion(...,
brauchtEngine=false)`, `transBtn` nur noch an Dokument gebunden, Schritt 3
wird schon mit Dokument aktiv (nur Analyse-Buttons warten aufs Modell).
Damit funktioniert Übersetzen erstmals auch auf Geräten **ohne WebGPU**.

**Lehre:** Werkzeug nach Aufgabe wählen — ein 1B-Chat-SLM für Übersetzung
einzusetzen war v0.2-Pragmatismus („keine neue Bibliothek"); das dedizierte
Seq2Seq-Modell ist in jeder Dimension überlegen. Und: `.mjs`-MIME-Type war
im Dashboard zum Glück schon registriert — sonst wäre die ONNX-Runtime
(dynamischer Import von `ort-wasm-simd-threaded.jsep.mjs`) still gestorben.

### Stolpersteine
- `node --check` behandelt `.js` als CommonJS → für ES-Module-Check als `.mjs`-Kopie prüfen.
- Der cp1252-Print-Bug schlug wieder zu (Häkchen-Zeichen im Python-Check) → `PYTHONUTF8=1`.
- Flask-Teststart braucht >6 s (LLM-Router-Init) — nicht zu früh curlen.
- Auf dem Smartphone via LAN/Tailnet: Service Worker + WebGPU verlangen Secure Context —
  über `http://` (nicht localhost) läuft nur OCR; für volle Funktion HTTPS/Tunnel nötig.

---

## 2026-07-10 (Tag 2)

### Was heute entstanden ist

| # | Arbeit | Ort | Commit |
|---|--------|-----|--------|
| 1 | **Qdrant** als 2. Vector-Store (Phase 3b) | `backend/app/rag/qdrant_store.py` | `0ffc4a8` |
| 2 | **Lernguide** (Architektur-Diagramme, 8-Schritte-Bauplan) | `docs/AI-OS-Backend-Lernguide.html` | `cf2fa26` |
| 3 | **Hermes-Agent** — autonomer Mitarbeiter (learn/ask/work/status) | `backend/app/agents/hermes.py` | `b921941` |
| 4 | **Hermes Web-GUI** + Doppelklick-Start | `backend/app/static/hermes.html`, `backend/Hermes-Starten.bat` | `8d27f63` |
| 5 | **Hermes Desktop App** (v40.10.2) konfiguriert: Ollama-Anbindung, Auto-Routing, Deutsch | `~/.hermes/config.yaml`, `~/.hermes/SOUL.md`, `~/.hermes/skills/ai-os/` | — (außerhalb Repo) |
| 6 | **Lokale LLM-Fallbacks installiert**: LM Studio + Jan | `%LOCALAPPDATA%\Programs\{LM Studio, Jan}` | — |
| 7 | **Prompt-Board** (Trello-Stil, Modul 4 "Prompt Registry") | `backend/app/prompts/registry.py`, `/prompts` | siehe Git-Log |
| 8 | Pi-4B/Tailscale-Hosting-Anleitung | `docs/Hermes-Pi4-Tailscale-Setup.md` | `b921941` |

### Lern-Highlights des Tages (mit Code)

**1. Der Lohn des Interface-Schnitts (Qdrant).** Weil `RagService` nur den
`VectorStore`-**Protocol**-Vertrag kennt, brauchte die komplette Qdrant-Integration
**null Änderungen** an Services oder Routen — nur eine neue Klasse + 1 Zeile Verdrahtung:

```python
# vector_store.py — der Vertrag
class VectorStore(Protocol):
    def add_document(self, meta: DocumentMeta, chunks: list[ChunkRecord]) -> None: ...
    def search(self, query_embedding: list[float], top_k: int = 4) -> list[tuple[ChunkRecord, float]]: ...

# main.py — die einzige Stelle, die entscheidet (Composition Root)
def build_vector_store(settings: Settings) -> VectorStore:
    if settings.vector_backend == "qdrant":
        return QdrantVectorStore(settings.qdrant_url, settings.qdrant_collection)
    return JsonVectorStore(settings.data_dir / "vector_store.json")
```

Test-Trick: `QdrantClient(":memory:")` startet Qdrant im Prozess — die ganze
Test-Suite läuft per `@pytest.fixture(params=["json", "qdrant"])` gegen **beide**
Backends, ohne Server.

**2. Ein Agent, der aus eigener Arbeit lernt (Hermes).** `work()` ist der Kreislauf
Kontext holen → arbeiten → Ergebnis zurück in die Wissensbasis:

```python
async def work(self, briefing: str, top_k: int = 4) -> HermesWorkResult:
    sources = await self._rag.retrieve(briefing, top_k)      # 1. Kontext (nur Suche!)
    result = await self._pipeline.run(briefing_mit_kontext)  # 2. Planner→Developer→Reviewer
    await self._rag.ingest(journal_filename, journal, ...)   # 3. Journal → Wissensbasis
```

Wichtig dabei: `retrieve()` (Vektorsuche ohne LLM-Antwort) als eigene Methode
neben `query()` — sonst würde `work()` unnötig eine Antwort generieren.

**3. Frontmatter als Datenbank (Prompt-Board).** Das Trello-Board hat KEINE eigene
Datenbank — Status/Version/Tags leben als YAML-Frontmatter **in den Markdown-Dateien
selbst** (`04_Infrastruktur/Gateway/Prompts/*.md`). Das Board ist nur eine Sicht:

```markdown
---
title: CEO-Bild aus Dashboard entfernen
status: entwurf        # backlog | entwurf | test | freigegeben  ← Kanban-Spalte
version: 2             # erhöht sich automatisch bei Inhalts-Änderung
tags: [dashboard]
---
# Prompt-Inhalt wie gehabt ...
```

Vorteile: git-versionierbar, Obsidian-kompatibel, kein Lock-in. Alt-Dateien ohne
Frontmatter landen automatisch im Backlog und werden beim ersten Update migriert.

**4. Sicherheit bei Datei-APIs:** Der Registry-Pfad wird gegen Path-Escape geprüft
(`../../etc/passwd` → ValueError) — Pflicht, sobald ein API-Parameter zum Dateinamen wird.

**5. Hermes-App-Ökosystem:** Die Desktop-App (Nous Research) hat dieselbe
Skill-Struktur wie Claude Code. LLM-Routing = `fallback_providers`-Kette in
`~/.hermes/config.yaml` (verifiziert im Quellcode: `hermes_cli/fallback_config.py`),
Sprache = `display.language: "de"` (`agent/i18n.py`), Persona = `~/.hermes/SOUL.md`.
Kette jetzt: `llama3 → qwen3.5:9b → mistral → LM Studio (:1234) → Jan (:1337)`.

### Stolpersteine des Tages

- **Port-Zombie**: Alter uvicorn-Prozess hielt Port 8000 → neuer Server startete
  scheinbar, servierte aber 404. Deutsches Windows zeigt `ABHÖREN` statt
  `LISTENING` → `netstat`-Filter anpassen!
- **winget-Silent-Install von LM Studio schlägt fehl** (Exit 2, 3 Varianten
  probiert) → direkter Installer-Download von installers.lmstudio.ai + `/S` klappt.
- **`lms get <name>`** sucht nur "Staff Picks" — für beliebige Modelle die
  **volle HuggingFace-URL** übergeben.
- PocketPal AI / PalsHub / Locally AI sind Mobile-/Apple-Apps → auf Windows-PC
  nicht installierbar (PocketPal wäre was fürs Handy).

### Bedienung (Stand heute)

- **Hermes-Chat**: `backend/Hermes-Starten.bat` → http://localhost:8000/ui
- **Prompt-Board**: http://localhost:8000/prompts (Karten ziehen = Status ändern)
- **Swagger**: http://localhost:8000/docs
- **Hermes Desktop App**: Startmenü "Hermes" (Ollama llama3, deutsch, Auto-Fallback)

### Offene nächste Schritte

- [ ] Phase 4: LangGraph-Migration der Agent-Pipeline (QA-Schleife, Human Approval)
- [ ] Pi-Deployment nach `docs/Hermes-Pi4-Tailscale-Setup.md` (Schritte 2–5 per SSH)
- [ ] LiteLLM-Gateway dauerhaft betreiben → als Stufe 1 in Hermes-Fallback-Kette
- [ ] In Jan einmalig ein Modell laden + Local API Server aktivieren (Stufe 5 der Kette)
- [ ] Evaluation-Modul (Modul 5): RAG-Antworten protokollieren & bewerten

---

## 2026-07-09 (Tag 1)

### Was entstanden ist

**Das neue Backend** (`backend/`) nach dem 8-Phasen-Lernkonzept — Commit `85855f6`:
FastAPI + Pydantic v2 + asyncio, verwaltet mit uv, geprüft mit Ruff + MyPy strict
+ pytest (13 Tests). Funktionierend ab Tag 1: RAG-Pipeline (Upload → PDF/DOCX/TXT-Parsing
→ absatzbewusstes Chunking mit Überlappung → nomic-embed-text-Embeddings via Ollama
→ JSON-Vector-Store mit Kosinus-Suche → Antwort mit Quellen) und die
Agenten-Pipeline Planner → Developer → Reviewer.

### Lern-Highlights

**1. Dependency Injection ist DIE Kernidee der Architektur:**

```python
class RagService:
    def __init__(self, llm: LLMClient, store: VectorStore, ...):  # bekommt, erzeugt nicht
        self._llm = llm
```

Serverstart (`main.py` lifespan) steckt echte Teile zusammen; Tests stecken Fakes
hinein. Gleicher Code, andere Verkabelung → Tests ohne Netzwerk in 0,4 s.

**2. `typing.Protocol` statt Vererbung:** `FakeLLMClient` im Test erfüllt den
`LLMClient`-Vertrag ohne `import` der echten Klasse — strukturelle Typisierung.

**3. Deterministische Fake-Embeddings** (Wort-Hash-Histogramm) machen sogar die
semantische Suche testbar: gleiche Wörter → ähnliche Vektoren.

**4. Pydantic v2 an der Grenze:** `Field(min_length=1)`, `ge=1, le=20` — ungültige
Requests sterben als 422, bevor Logik läuft ("Parse, don't validate").

### Verifikation

End-to-End mit echtem Ollama getestet: Dokument hochgeladen, gefragt
"Auf welchem Port läuft der LiteLLM Gateway?" → korrekte Antwort mit Quelle (Score 0.66).

---

*Regel: Dieses Journal wird am Ende jedes Arbeitstages von Claude aktualisiert.*
*Zuletzt aktualisiert: 2026-07-16*
