# ⚖️ Analyse: Browser/PWA vs. Native App — reicht der Browser ohne Qualitätsverlust?

> Erstellt 17.07.2026 auf CEO-Frage: „Ist alles im Webbrowser nicht viel besser
> als eine Native App (plattformunabhängig, leichter) — solange die Qualität
> nicht leidet?" Verwandt: [[Bauplan-Feed-Scraper-Wasm]], `Native-App/ARCHITECTURE_PLAN.md`

## Kernantwort zuerst

**Die ANTWORT-Qualität ist im Browser identisch zur nativen App** — und das ist
der entscheidende Punkt: Die Qualität einer lokalen KI hängt an
(a) den Modellgewichten + Quantisierung, (b) dem RAG-Kontext, (c) dem Agenten-Loop.
Alle drei sind im Browser exakt gleich umsetzbar wie nativ (WebLLM lädt dieselben
q4f16-Gewichte, die auch llama.cpp nutzen würde; Embeddings + Loop sind Software).
**Was sich unterscheidet, ist nicht Qualität, sondern Geschwindigkeit und Komfort.**

## Ehrlicher Vergleich

| Kriterium | Browser/PWA | Native App | Gewicht für unseren Usecase |
|---|---|---|---|
| **Antwortqualität** (gleiche Gewichte/RAG/Loop) | ✅ identisch | ✅ identisch | — entscheidend, kein Unterschied |
| Inferenz-Tempo GPU | ✅ WebGPU ≈ 80–90 % von nativ (MLC-Benchmarks; ANNAHME: Größenordnung, geräteabhängig) | ✅ 100 % | 1B-Modell: Differenz kaum spürbar |
| **NPU-Zugriff** (Apple ANE, Snapdragon) | ❌ nicht aus dem Browser (WebNN unreif) | ✅ via CoreML/NNAPI | erst relevant ab ~3B+-Modellen mobil |
| Hintergrund-Updates (Feeds nachts ziehen) | ⚠️ nur bei geöffneter App; Periodic Background Sync nur Chrome/Android, unzuverlässig | ✅ zuverlässig | Workaround: Update beim Öffnen (Feeds laden in Sekunden) |
| Push-Benachrichtigungen | ⚠️ möglich (iOS erst ab 16.4, PWA muss installiert sein) | ✅ voll | für v1 nicht nötig |
| Speicher-Persistenz | ⚠️ IndexedDB kann bei Platzmangel geräumt werden → `navigator.storage.persist()` Pflicht | ✅ stabil | mitigierbar |
| iOS-Realität | ⚠️ WebGPU ab iOS 18; davor nur OCR/BM25-Fallback | ✅ ab iOS 15 | Zielgruppe mit aktuellen Geräten ok |
| **Distribution** | ✅ Link teilen = installiert; sofortige Updates | ❌ Store-Review, 15–30 % Gebühr auf In-App-Käufe | riesiger PWA-Vorteil für uns (keine Reichweite → jede Hürde tödlich) |
| Codebasen/Wartung | ✅ eine (läuft auch auf Desktop!) | ❌ zweite Codebase (Expo mildert, bleibt Aufwand) | Ein-Personen-Betrieb → schwer wiegend |
| Kosten | ✅ 0 € | ❌ Apple Dev 99 $/Jahr + Play 25 $ + Review-Zeit | passt zur 0-€-Cash-Strategie |
| Datenschutz-Story | ✅ „F12 → Netzwerk = Beweis" (DokuCheck-Beweisleiste!) | ⚠️ Nutzer muss App vertrauen | PWA-Story ist sogar STÄRKER |

## Fazit

**Browser-first ist für dieses Produkt objektiv die bessere Wahl** — nicht nur
„leichter", sondern strategisch: Die einzige echte Schwäche (kein Hintergrund-
Update) ist für den Themen-Assistenten verschmerzbar (Feeds laden beim Öffnen in
Sekunden), und die Datenschutz-Beweisbarkeit ist im Browser sogar stärker.
Qualitätsverlust bei den Antworten: **keiner** — die 3 SLM-Hebel (RAG, Loop,
später QLoRA-Modelle) wirken im Browser genauso.

**Native App (Stufe 3) wird ZURÜCKGESTELLT und nur bei konkreten Triggern gebaut:**
- **T1:** Nutzer verlangen nachweislich Hintergrund-Sync/Push (Feedback-Tickets)
- **T2:** Bedarf an Modellen >3B mobil → NPU-Zugriff nötig
- **T3:** App-Store-Präsenz wird als Vertriebskanal gebraucht (B2B-Kunde verlangt es)

Der Inferenz-Router (USP des Native-App-Plans, Heim-Ollama via Tailscale) ist
übrigens NICHT app-exklusiv: er lässt sich als optionales Feature auch in der
PWA umsetzen (fetch auf Tailnet-HTTPS-Endpunkt) — Kandidat für Stufe 2.5.
