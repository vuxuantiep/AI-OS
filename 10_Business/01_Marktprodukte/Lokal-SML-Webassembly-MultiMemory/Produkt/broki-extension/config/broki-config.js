// =============================================================================
// Broki AI — zentrale Konfiguration
// Alles, was pro Firma/Deployment angepasst wird, liegt HIER — nirgendwo sonst.
// =============================================================================

export const BROKI_CONFIG = {
  // --- Tailscale / Raspberry Pi (Wissens-Verteiler) -------------------------
  // MagicDNS-Name des Pi im Tailnet. Traffic ist durch Tailscale (WireGuard)
  // bereits transportverschlüsselt — deshalb reicht http im Tailnet.
  pi: {
    // Ziel-Deployment: MagicDNS-Name des Pi im Tailnet (Traffic ist via
    // Tailscale/WireGuard verschlüsselt → http reicht).
    // LOKALER DOGFOODING-TEST: auf "http://127.0.0.1:8088" umstellen und die
    // host_permissions im manifest.json entsprechend ergänzen.
    basisUrl: "http://pi-ki-tiep.tailed32d1.ts.net:8088",
    // Endpunkte des broki-pi-server (Gegenstück):
    //   GET /index/manifest.json?rolle=<r> → { version, rolle, dateien:[{pfad,sha256,signatur,chunks}] }
    //   GET /index/<rolle>.jsonl           → JSON-Zeilen {chunkId, partition, text, vektor}
    manifestPfad: "/index/manifest.json",
    syncIntervallMinuten: 30
  },

  // --- Manipulationsschutz ---------------------------------------------------
  // Firmen-Public-Key (ECDSA P-256, SPKI, Base64). Der Pi signiert jedes
  // Index-Paket mit dem privaten Firmen-Schlüssel; die Extension verifiziert
  // VOR dem Entpacken. Erzeugt vom broki-pi-server (index_builder.py gibt den
  // passenden Public Key aus). Dieser Wert gehört zum Schlüssel in
  // broki-pi-server/keys/firma_privat.pem (Dogfooding-Instanz, Stand 18.07.2026):
  firmenPublicKeySpkiB64: "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEF1i+hiQuBFZdqI7dQ1rzGrqMc3xxPd6glnreigG3bauoj46ZHSEX/LXrd6GM0MQlRav5TmoHPR+7t/YQM0bCMA==",

  // --- Rollen (rollenbasierter RAG-Index) ------------------------------------
  // Die Rolle entscheidet, welche Index-Partitionen der Pi ausliefert.
  // Wird bei der Einrichtung gesetzt (Options-Seite), Default: "mitarbeiter".
  standardRolle: "mitarbeiter",

  // --- Firmen-Domains für den IT-Crash-Rollback ------------------------------
  // Nur auf diesen Domains protokolliert das Content-Script Formulareingaben.
  // MUSS mit content_scripts.matches im manifest.json übereinstimmen.
  rollbackDomains: ["firmen-domain.example"],

  // --- LLM-Gateway -----------------------------------------------------------
  llm: {
    // Motor 2 (CEO-Entscheidung 23.07.2026): lokales Ollama per HTTP statt
    // WebLLM/wllama im Browser - dieselbe Ollama-Instanz, die im restlichen
    // AI-OS schon zuverlaessig laeuft (Port 11434), bleibt trotzdem 100%
    // lokal (kein Cloud-Verstoss), aber ohne die WASM/Offscreen-Komplexitaet.
    ollama: { basisUrl: "http://127.0.0.1:11434", modell: "llama3" },
    // Modellwahl nach navigator.deviceMemory (GB, Chrome rundet auf 0.25–8).
    // OOM-Schutz: lieber ein kleineres Modell als ein abgestürzter Tab.
    // wllama/WebLLM sind seit 23.07.2026 wieder Motor 1/2 (Zero-Install),
    // Ollama nur noch Fallback (siehe llm-gateway.js).
    // ECHTER BUG gefunden 23.07.2026 (1): die 8GB-Stufe verwies auf
    // "qwen2.5-3b-instruct-q4_k_m.gguf" - eine Datei, die scripts/
    // download-models.js NIE heruntergeladen hat (nur 1.5B/0.5B sind im
    // Download-Skript gelistet).
    // ECHTER BUG gefunden 23.07.2026 (2): die 1.5B-Datei (~1,1GB) brachte im
    // echten Sidebar-UI-Test den GESAMTEN Renderer-Prozess zum Absturz
    // (Playwright: "Target page ... has been closed" - diesmal fuer die
    // SIDEBAR-Seite selbst, nicht nur das Offscreen-Dokument -> Indiz fuer
    // einen echten Speicher-Crash, nicht nur ein Test-Artefakt). Nur die
    // 0.5B-Datei (~490MB) ist bisher Ende-zu-Ende verifiziert stabil (Laden +
    // echte Text-Generierung, mehrfach reproduziert). Bis die 1.5B-Stufe
    // separat mit mehr Zeit/RAM-Profiling geprueft ist: ALLE Stufen zeigen
    // vorerst auf das verifiziert stabile 0.5B-Modell - lieber zuverlaessig
    // klein als riskant gross. TODO: 1.5B-Stufe reaktivieren, sobald die
    // Absturzursache verstanden/geloest ist.
    modellStufen: [
      { minGb: 8, webllm: "Qwen2.5-0.5B-Instruct-q4f16_1-MLC", wllamaGguf: "qwen2.5-0.5b-instruct-q4_k_m.gguf" },
      { minGb: 4, webllm: "Qwen2.5-0.5B-Instruct-q4f16_1-MLC", wllamaGguf: "qwen2.5-0.5b-instruct-q4_k_m.gguf" },
      { minGb: 0, webllm: "Qwen2.5-0.5B-Instruct-q4f16_1-MLC", wllamaGguf: "qwen2.5-0.5b-instruct-q4_k_m.gguf" }
    ],
    antwortTokensMax: 1024,
    // wllama laeuft einzelfaedig auf CPU in WASM (bewusst n_threads:1, um die
    // SharedArrayBuffer/Cross-Origin-Isolation-Komplexitaet des Multi-Thread-
    // Modus zu vermeiden) - spuerbar langsamer als Ollama/native. 1024 Token
    // liessen die Generierung ueber das 25s-Offscreen-Timeout laufen (echter
    // Fund 23.07.2026, Sidebar-UI-Test). Eigener, kleinerer Deckel nur fuer
    // wllama, damit Zero-Install-Antworten in akzeptabler Zeit fertig werden.
    wllamaAntwortTokensMax: 200,
    temperatur: 0.3
  },

  // --- Memory / Cache --------------------------------------------------------
  memory: {
    dbName: "broki",
    l1TtlStunden: 24 * 7,        // Exact-Match-Cache: 1 Woche
    l2SchwelleCosine: 0.92,      // Semantic Cache: ab dieser Ähnlichkeit "Treffer"
    l2MaxEintraege: 500,
    ragTopK: 4
  },

  // --- Cloud-Fallback (optional) ---------------------------------------------
  // Wenn der Rechner zu belastet ist oder kein lokaler Motor verfügbar ist,
  // kann auf einen OpenAI-kompatiblen Cloud-Endpoint gefallen werden.
  // WICHTIG: Cloud-Modus = Daten verlassen das Gerät! Nur für Test/Notbetrieb.
  cloud: {
    endpoint: "",                 // z.B. "https://api.openai.com/v1/chat/completions"
    apiKey: "",                   // API-Key des Cloud-Anbieters
    modell: "gpt-4o-mini"         // Fallback-Modell
  }
};
