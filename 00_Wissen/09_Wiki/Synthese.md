# Synthese

*Diese Seite fasst die wichtigsten, seitenübergreifenden Erkenntnisse aus
`Themen/` und `Entitäten/` zusammen. Wird von der KI beim Ingest gepflegt.*

## Second Brain (Meta)

Das System, das diese Seite selbst ermöglicht, ist im Second-Brain-Vault
dokumentiert: [[Second-Brain-System]]. Erster echter Ingest-Testlauf
(21.07.2026, Aufgabe 9 des Implementierungsplans) — dabei ein offener
Konflikt zwischen ursprünglicher Spezifikation (kein 3D-Globus im MVP) und
späterer, expliziter User-Entscheidung gefunden und markiert statt selbst
aufgelöst (siehe Konflikt-Abschnitt in [[Second-Brain-System]]).

## Broki AI / lokale Browser-KI (23.07.2026)

Erster Ingest aus den Broki-AI-Backend-Sessions: [[Broki-AI]] (Produkt-
Entität), [[Lokale-LLM-Motoren-Browser]] und [[MV3-Offscreen-Dokumente-Debugging]]
(generisches technisches Wissen, projektübergreifend nutzbar). Wichtigster
Fund: ein tagelang unerklärlicher wllama-Bug ("[object ProgressEvent]") war
tatsächlich ein Cache-Storage-API-Konflikt mit `chrome-extension://`-URLs —
gefunden erst, nachdem Browser-Automatisierung (sieht Offscreen-Dokumente
nie) UND direktes In-Context-Logging (chrome.storage dort selbst
`undefined`) beide versagten und stattdessen der Service Worker als Relais
für Diagnose-Checkpoints genutzt wurde. Zweiter Fund: Ollama blockt
Extension-Requests standardmäßig per CORS, ein einfacher Reachability-Ping
täuscht fälschlich Erreichbarkeit vor. Beide Funde sind über Broki hinaus
relevant für jedes künftige AI-OS-Projekt mit lokaler Browser-KI oder
MV3-Extensions.
