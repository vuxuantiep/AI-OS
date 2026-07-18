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
    // Modellwahl nach navigator.deviceMemory (GB, Chrome rundet auf 0.25–8).
    // OOM-Schutz: lieber ein kleineres Modell als ein abgestürzter Tab.
    modellStufen: [
      { minGb: 8, webllm: "Llama-3.2-3B-Instruct-q4f16_1-MLC", wllamaGguf: "qwen2.5-3b-instruct-q4_k_m.gguf" },
      { minGb: 4, webllm: "Llama-3.2-1B-Instruct-q4f16_1-MLC", wllamaGguf: "qwen2.5-1.5b-instruct-q4_k_m.gguf" },
      { minGb: 0, webllm: "Qwen2.5-0.5B-Instruct-q4f16_1-MLC", wllamaGguf: "qwen2.5-0.5b-instruct-q4_k_m.gguf" }
    ],
    antwortTokensMax: 1024,
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
