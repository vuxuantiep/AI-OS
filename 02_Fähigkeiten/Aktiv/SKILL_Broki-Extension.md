# SKILL: Broki-Extension entwickeln & betreiben

#skill #broki #webassembly #manifest-v3

> Destilliertes Arbeitswissen aus dem Bau (18.07.2026). Referenzen:
> Code `10_Business/01_Marktprodukte/Lokal-SML-Webassembly-MultiMemory/Produkt/broki-extension/`,
> Diagramme [[Architektur-Broki-Extension]], Gate [[wirtschaftlichkeit-broki-ai]].

## Was Broki ist (1 Satz)

Manifest-V3-Extension: Firmen-Wiki-KI 100 % im Browser — Index kommt signiert
vom Raspberry Pi übers Tailscale-Netz, Antworten aus dreistufigem lokalem
Gedächtnis + austauschbarem LLM-Motor.

## Die 7 Kern-Patterns (das eigentliche Gelernte)

1. **MV3-Grundgesetz:** Service Worker kann jederzeit schlafen → `chrome.alarms`
   statt Timer, Zustand in `chrome.storage`/IndexedDB, Message-Handler gibt
   `true` zurück für asynchrone Antworten.
2. **Integrität = Signatur, nicht Hash:** ECDSA-P256 über SHA-256 gegen
   gepinnten Firmen-Public-Key (WebCrypto `subtle.verify`). Ein nackter Hash
   wäre wertlos — den fälscht der Angreifer auf dem Pi einfach mit.
3. **Fail closed mit Augenmaß:** Signaturfehler → Index sperren (Flag +
   UI-Banner). Pi offline → KEIN Sicherheitsfall, alter Index bleibt gültig.
   Index-Übernahme atomar: erst wenn alle Partitionen verifiziert sind.
4. **Flüchtigkeit per Design:** `chrome.storage.session` lebt nur im RAM des
   laufenden Browsers → perfekt für Privat-Modus-Flag; Drag-and-Drop-Dokumente
   in einer SW-Map, aufgeräumt via `tabs.onRemoved`.
5. **Crash-Erkennung per Heartbeat:** `runtime.onSuspend` feuert bei echtem
   Absturz NICHT — Flag „laeuft" beim nächsten Start = Crash erkannt. Journal
   AES-GCM-verschlüsselt (at-rest-Schutz, ehrlich dokumentiert).
6. **Motor-Agnostik (Adapter):** Rangfolge window.ai (3 Namensraum-Varianten
   proben!) → WebLLM (WebGPU) → wllama (WASM/CPU). Vor Init:
   `navigator.deviceMemory` → Modellstufe (0.5B/1B/3B) = OOM-Schutz.
7. **Memory-Kaskade:** L1 = SHA-256 der normalisierten Frage (0 ms), L2 =
   Cosine ≥ 0.92 auf Frage-Embeddings (gedeckelt), L3 = Top-4 RAG-Chunks.
   Rückschreiben nach Antwort — NIE im Privat-Modus.

## Entwickeln & Testen

- Laden: `chrome://extensions` → Entwicklermodus → „Entpackt laden".
- Syntax-Gate vor jedem Commit: alle Module als `.mjs`-Kopie durch
  `node --check`; `manifest.json` durch JSON-Parser.
- Ohne Pi testen: Sync liefert sauber „offline"; Sperr-Logik mit lokalem
  Server + absichtlich falscher Signatur provozieren (Erwartung: 🚫-Banner).
- Schlüssel: `openssl ecparam -name prime256v1` (privat → NUR Pi),
  SPKI-Base64 des Public Key → `config/broki-config.js`.

## Offene Bausteine

Pi-Gegenstück (Index-Builder + Signaturdienst, API in der Produkt-README
spezifiziert) · vendor/-Befüllung (WebLLM, wllama, GGUF) · Dogfooding aufs
eigene 00_Wissen (Gate-Auflage 1).
