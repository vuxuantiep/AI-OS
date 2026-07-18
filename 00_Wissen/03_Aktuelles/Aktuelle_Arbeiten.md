# 📋 Aktuelle Arbeiten — Arbeitsjournal

> Tägliche Dokumentation der kompletten Arbeit am AI-OS (von Claude geführt).
> Zweck: Überblick behalten + aus dem Code lernen. Neuester Tag oben.
> Details zur Architektur: [[../../docs/AI-Engineering-Roadmap|Roadmap]] · Lernguide: `docs/AI-OS-Backend-Lernguide.html`

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
