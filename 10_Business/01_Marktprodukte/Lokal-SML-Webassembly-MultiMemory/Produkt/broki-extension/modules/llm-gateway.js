// =============================================================================
// Broki AI — Agnostisches LLM-Gateway („der austauschbare Muskel")
//
// Motor-Rangfolge (erster verfügbarer gewinnt) — Zero-Install zuerst, wieder
// hergestellt am 23.07.2026 (siehe unten):
//   1. Native On-Device-KI des Browsers  (Prompt API: window.ai / LanguageModel
//      — Edge liefert Phi, Chrome Gemini Nano; 0 MB Download, sofort da)
//   2. WebLLM   (WebGPU; Llama-3/Qwen als MLC-Pakete — schnellster Fallback)
//   3. wllama   (WebAssembly/CPU; läuft praktisch überall, GGUF-Format;
//      > 2 GB-Modelle müssten gesharded werden → vermeiden wir durch die
//      deviceMemory-Stufen von vornherein)
//   4. Ollama per HTTP (nur wenn 1-3 nicht verfügbar/fehlgeschlagen sind)
//      — braucht eine ZUSÄTZLICHE lokale Installation neben der Extension,
//      bleibt aber 100% lokal. Reine Notlösung/Power-User-Option, NICHT der
//      Standardweg — das würde das "nur Extension installieren"-Verkaufs-
//      argument (Kanzleien/Praxen) untergraben (siehe project-broki-ai Memory,
//      CEO-Nachfrage 23.07.: "ich dachte es soll vollständig nur im Browser
//      laufen ohne eigenen PC/Server").
//   5. Cloud (nur im expliziten Cloud-Modus)
//
// OOM-Schutz: VOR jeder Motor-Initialisierung wird navigator.deviceMemory
// gelesen und die Modellgröße daran ausgerichtet — ein eingefrorener Tab
// ist der schnellste Weg, Nutzer zu verlieren.
//
// HISTORIE (23.07.2026): wllama war zwischenzeitlich als "unzuverlässig"
// hinter Ollama einsortiert, weil ein mysteriöser "[object ProgressEvent]"-
// Fehler beim Modell-Laden nie root-gecaust werden konnte. Root Cause dann
// doch gefunden (chrome.storage-Checkpoint-Diagnose in offscreen.js): wllamas
// vendorte utils.js versucht jedes Modell per Cache-Storage-API zu cachen,
// die aber nur http(s)-URLs akzeptiert - chrome-extension://-URLs (so lädt
// die Extension ihre eigenen .gguf-Dateien) wirft sie ab, der Fehler hing in
// einem ungesicherten XHR-Handler fest und ließ das Lade-Promise nie
// resolven. Fix in offscreen.js: window.caches im Offscreen-Kontext
// deaktivieren, bevor wllama importiert wird. Damit ist wllama jetzt
// nachweislich funktionsfähig (Modell-Laden + echte Text-Generierung
// verifiziert) und wieder Motor 1 der lokalen WASM-Kette.
// =============================================================================

import { BROKI_CONFIG } from "../config/broki-config.js";

export class LLMGateway {
  constructor() {
    this.cfg = BROKI_CONFIG.llm;
    this.motor = null;        // { name, generate(prompt), embed(text)? }
    this.motorName = "keiner";
    this._initPromise = null;
    this.modus = "local";     // "local" | "cloud"
  }

  /** Modus umschalten: „local" = nur lokale Motoren, „cloud" = lokale Motoren
   *  zuerst, bei Fehler automatisch auf Cloud-API fallen. */
  setModus(modus) {
    this.modus = modus === "cloud" ? "cloud" : "local";
    console.log("[Broki/LLM] Modus gewechselt auf:", this.modus);
  }

  // ---------------------------------------------------------------------------
  // Geräte-Erkennung
  // ---------------------------------------------------------------------------

  /** RAM-Klasse des Geräts (GB). Chrome liefert 0.25–8 (gerundet, gedeckelt) —
   *  reicht völlig, um zwischen 0.5B-, 1B- und 3B-Modellen zu entscheiden. */
  static geraeteRamGb() {
    return (typeof navigator !== "undefined" && navigator.deviceMemory) || 2;
  }

  /** Passende Modellstufe zum RAM — verhindert Out-of-Memory-Abstürze. */
  modellStufe() {
    const gb = LLMGateway.geraeteRamGb();
    return this.cfg.modellStufen.find(s => gb >= s.minGb)
        || this.cfg.modellStufen.at(-1);
  }

  static async webgpuVerfuegbar() {
    try {
      if (!("gpu" in navigator)) return false;
      return (await navigator.gpu.requestAdapter()) !== null;
    } catch { return false; }
  }

  /** Native Prompt API finden — Namensraum variiert je Browser-Generation
   *  (window.ai.languageModel, self.ai, globales LanguageModel). */
  static _nativeApi() {
    const g = globalThis;
    if (g.LanguageModel?.create) return { create: o => g.LanguageModel.create(o) };
    if (g.ai?.languageModel?.create) return { create: o => g.ai.languageModel.create(o) };
    if (g.window?.ai?.languageModel?.create)
      return { create: o => g.window.ai.languageModel.create(o) };
    return null;
  }

  // ---------------------------------------------------------------------------
  // Initialisierung: probiert die Motoren in Rangfolge durch.
  // Mehrfachaufrufe teilen sich EIN Init (Promise-Memoisierung).
  // ---------------------------------------------------------------------------
  init() {
    if (!this._initPromise) this._initPromise = this._init();
    return this._initPromise;
  }

  async _init() {
    const stufe = this.modellStufe();

    // --- Motor 1: native On-Device-KI ---------------------------------------
    const nativ = LLMGateway._nativeApi();
    if (nativ) {
      try {
        const session = await nativ.create({
          temperature: this.cfg.temperatur, topK: 3
        });
        this.motor = {
          name: "native (window.ai)",
          generate: (prompt) => session.prompt(prompt)
        };
        this.motorName = this.motor.name;
        console.log("[Broki/LLM] Motor: native Prompt API.");
        return this.motorName;
      } catch (e) {
        console.warn("[Broki/LLM] Native API vorhanden, aber nicht bereit:", e.message);
      }
    }

    // --- Motor 2: WebLLM (nur mit WebGPU) -----------------------------------
    // WICHTIG (gefunden 22.07.2026, echter Bug): dynamisches import() ist im
    // Service Worker per HTML-Spec verboten ("import() is disallowed on
    // ServiceWorkerGlobalScope") - background.js LÄUFT als Service Worker,
    // ein direktes `await import("../vendor/webllm/index.js")` HIER schlägt
    // deshalb IMMER fehl, unabhängig davon ob die vendor-Datei existiert.
    // Fix: die eigentliche WebLLM/wllama-Arbeit läuft in einem Offscreen-
    // Dokument (normale, unsichtbare Seite MIT DOM - dort ist import()
    // erlaubt), angesprochen über den Message-Bus. Siehe offscreen/offscreen.js.
    if (await LLMGateway.webgpuVerfuegbar()) {
      try {
        await this._ensureOffscreen();
        const init = await this._offscreenSend({ typ: "webllm-init", modell: stufe.webllm });
        if (!init?.ok) throw new Error(init?.fehler || "webllm-init fehlgeschlagen");
        this.motor = {
          name: `webllm (${stufe.webllm})`,
          generate: async (prompt) => {
            const r = await this._offscreenSend({
              typ: "webllm-generate", prompt,
              maxTokens: this.cfg.antwortTokensMax, temperatur: this.cfg.temperatur
            });
            if (!r?.ok) throw new Error(r?.fehler || "webllm-generate fehlgeschlagen");
            return r.text;
          }
        };
        this.motorName = this.motor.name;
        console.log("[Broki/LLM] Motor: WebLLM (offscreen),", stufe.webllm);
        return this.motorName;
      } catch (e) {
        console.warn("[Broki/LLM] WebLLM-Start fehlgeschlagen:", e.message);
        if (this.modus === "cloud") {
          const name = await this._initCloud();
          if (name) return name;
        }
      }
    }

    // --- Motor 3: wllama (CPU, läuft praktisch überall) ----------------------
    try {
      await this._ensureOffscreen();
      const init = await this._offscreenSend({ typ: "wllama-init", gguf: stufe.wllamaGguf });
      if (!init?.ok) throw new Error(init?.fehler || "wllama-init fehlgeschlagen");
      this.motor = {
        name: `wllama (${stufe.wllamaGguf})`,
        generate: async (prompt) => {
          // Eigener, kleinerer Token-Deckel (siehe broki-config.js) - wllama
          // laeuft einzelfaedig auf CPU, mit vollen 1024 Token (Ollama-Mass)
          // ueberschritt die Generierung sonst jedes Offscreen-Timeout.
          const r = await this._offscreenSend({
            typ: "wllama-generate", prompt,
            maxTokens: this.cfg.wllamaAntwortTokensMax, temperatur: this.cfg.temperatur
          }, 90000);
          if (!r?.ok) throw new Error(r?.fehler || "wllama-generate fehlgeschlagen");
          return r.text;
        },
        embed: async (text) => {
          const r = await this._offscreenSend({ typ: "wllama-embed", text });
          if (!r?.ok) throw new Error(r?.fehler || "wllama-embed fehlgeschlagen");
          return r.vektor;
        }
      };
      this.motorName = this.motor.name;
      console.log("[Broki/LLM] Motor: wllama (offscreen, CPU),", stufe.wllamaGguf);
      return this.motorName;
    } catch (e) {
      console.warn("[Broki/LLM] wllama-Start fehlgeschlagen:", e.message);
      if (this.modus === "cloud") {
        const name = await this._initCloud();
        if (name) return name;
      }
    }

    // --- Motor 4: lokales Ollama per HTTP (nur wenn 1-3 fehlschlagen) --------
    // Notloesung/Power-User-Option: braucht eine ZUSAETZLICHE lokale
    // Installation neben der Extension (Ollama muss separat laufen), bleibt
    // aber 100% lokal. Bewusst NICHT der Standardweg (siehe Kommentar am
    // Dateianfang) - nur relevant, falls Motor 1-3 alle fehlschlagen.
    try {
      const basisUrl = this.cfg.ollama.basisUrl;
      const modell = this.cfg.ollama.modell;
      const pingResp = await fetch(basisUrl + "/api/tags", { signal: AbortSignal.timeout(2000) });
      if (!pingResp.ok) throw new Error("Ollama antwortet nicht (HTTP " + pingResp.status + ")");
      this.motor = {
        name: `ollama (${modell})`,
        generate: async (prompt) => {
          const r = await fetch(basisUrl + "/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              model: modell,
              messages: [{ role: "user", content: prompt }],
              stream: false,
              keep_alive: "3m",
              options: { temperature: this.cfg.temperatur, num_predict: this.cfg.antwortTokensMax }
            })
          });
          if (!r.ok) throw new Error("Ollama-Chat HTTP " + r.status);
          const daten = await r.json();
          return daten.message?.content || "(keine Antwort)";
        }
        // Bewusst KEIN embed() hier: "llama3" ist ein Chat-, kein Embedding-
        // Modell (Ollama antwortete mit HTTP 403 auf /api/embeddings). Die
        // äußere embed()-Methode faellt automatisch auf hashEmbedding()
        // zurueck, wenn der Motor kein eigenes embed anbietet.
      };
      this.motorName = this.motor.name;
      console.log("[Broki/LLM] Motor: Ollama (lokal HTTP, Fallback),", modell);
      return this.motorName;
    } catch (e) {
      console.warn("[Broki/LLM] Ollama nicht erreichbar:", e.message);
    }

    // --- Motor 5: Cloud-Fallback (nur wenn Modus=cloud) ----------------------
    if (this.modus === "cloud") {
      const name = await this._initCloud();
      if (name) return name;
    }

    throw new Error("Kein KI-Motor verfügbar (weder native API, WebGPU noch WASM).");
  }

  /** Offscreen-Dokument erzeugen, falls noch keins existiert (Mehrfachaufrufe
   *  teilen sich EIN Dokument - offscreen erlaubt max. 1 pro Extension). */
  async _ensureOffscreen() {
    LLMGateway._log("ensureOffscreen: pruefe hasDocument()");
    if (await chrome.offscreen.hasDocument()) {
      LLMGateway._log("ensureOffscreen: existiert bereits");
      return;
    }
    LLMGateway._log("ensureOffscreen: erzeuge neues Dokument");
    await chrome.offscreen.createDocument({
      url: "offscreen/offscreen.html",
      reasons: ["WORKERS"],
      justification: "WebGPU/WASM-LLM-Inferenz (WebLLM/wllama) braucht einen "
        + "DOM-Kontext mit import() - im Service Worker laut HTML-Spec verboten."
    });
    LLMGateway._log("ensureOffscreen: erzeugt");
  }

  /** Nachricht an das Offscreen-Dokument, adressiert per target:"offscreen"
   *  (background.js ignoriert diese Nachrichten explizit, siehe dort).
   *  CEO-Befund 23.07.2026: Chat blieb bei fehlgeschlagener/nie antwortender
   *  Offscreen-Antwort UNBEGRENZT bei "…" haengen - kein Fehler, keine
   *  Rueckmeldung. Fix: harter Timeout, damit der Nutzer IMMER innerhalb
   *  weniger Sekunden entweder eine Antwort oder einen klaren Fehler sieht. */
  _offscreenSend(msg, timeoutMs = 25000) {
    LLMGateway._log("offscreenSend: sende " + msg.typ);
    const timeout = new Promise((_, rej) =>
      setTimeout(() => rej(new Error(`Offscreen-Antwort-Timeout (${timeoutMs / 1000}s) fuer ` + msg.typ)), timeoutMs));
    return Promise.race([
      chrome.runtime.sendMessage({ target: "offscreen", ...msg }),
      timeout
    ]).then(r => { LLMGateway._log("offscreenSend: Antwort fuer " + msg.typ + " erhalten"); return r; },
            e => { LLMGateway._log("offscreenSend: FEHLER bei " + msg.typ + ": " + e.message); throw e; });
  }

  /** Diagnose-Protokoll (CEO-Befund 23.07.2026: Playwright sieht das
   *  Offscreen-Dokument nicht als eigene Seite - Konsolen-Ausgaben von dort
   *  waren nie sichtbar. Dieses Log im Service-Worker-Kontext ist dagegen
   *  jederzeit per chrome.runtime.getContexts / manuellem Abruf einsehbar. */
  static _log(text) {
    const eintrag = new Date().toISOString() + " " + text;
    (globalThis.brokiDebugLog ||= []).push(eintrag);
    console.log("[Broki/Debug]", eintrag);
  }

  /** Cloud-Fallback: OpenAI-kompatibler Endpoint (z.B. eigener Server,
   *  Azure OpenAI, OpenRouter, etc.). Konfiguration in broki-config.js. */
  async _initCloud() {
    const url = BROKI_CONFIG.cloud?.endpoint;
    const key = BROKI_CONFIG.cloud?.apiKey;
    const modell = BROKI_CONFIG.cloud?.modell || "gpt-4o-mini";
    if (!url || !key) {
      console.warn("[Broki/LLM] Cloud-Modus aktiv, aber keine URL/Key in broki-config.js konfiguriert.");
      return null;
    }
    try {
      this.motor = {
        name: `cloud (${modell})`,
        generate: async (prompt) => {
          const r = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json", "Authorization": `Bearer ${key}` },
            body: JSON.stringify({
              model: modell,
              messages: [{ role: "user", content: prompt }],
              max_tokens: this.cfg.antwortTokensMax,
              temperature: this.cfg.temperatur
            })
          });
          if (!r.ok) throw new Error("Cloud-API HTTP " + r.status);
          const data = await r.json();
          return data.choices?.[0]?.message?.content || "(keine Antwort)";
        },
        embed: async (text) => {
          const r = await fetch(url.replace("/chat/completions", "/embeddings"), {
            method: "POST",
            headers: { "Content-Type": "application/json", "Authorization": `Bearer ${key}` },
            body: JSON.stringify({ model: modell, input: text })
          });
          if (!r.ok) throw new Error("Cloud-Embedding HTTP " + r.status);
          const data = await r.json();
          return data.data?.[0]?.embedding || LLMGateway.hashEmbedding(text);
        }
      };
      this.motorName = this.motor.name;
      console.log("[Broki/LLM] Motor: Cloud-Fallback,", modell);
      return this.motorName;
    } catch (e) {
      console.error("[Broki/LLM] Cloud-Fallback fehlgeschlagen:", e.message);
      return null;
    }
  }

  // ---------------------------------------------------------------------------
  // Öffentliche API
  // ---------------------------------------------------------------------------

  /** RAG-Antwort: strikt auf den gelieferten Wiki-Kontext beschränkt. */
  async antworten(frage, kontextChunks) {
    await this.init();
    const kontext = kontextChunks
      .map((c, i) => `[Quelle ${i + 1} · ${c.chunkId}]\n${c.text}`)
      .join("\n\n");
    const prompt =
`Du bist Broki, der interne Wiki-Assistent. Beantworte die Frage AUSSCHLIESSLICH
mit den folgenden Auszügen aus dem Firmen-Wiki. Steht die Antwort nicht im
Kontext, sage ehrlich: "Dazu steht nichts im Wiki." Nenne am Ende die Quellen.

KONTEXT:
${kontext}

FRAGE: ${frage}

ANTWORT (deutsch, präzise):`;
    return this.motor.generate(prompt);
  }

  /** Embedding für Memory-Level 2/3. Fällt der Motor ohne Embedding-Fähigkeit
   *  aus der Reihe (native API), nutzt Broki ein deterministisches
   *  Hash-Feature-Embedding als Notlösung — schwächer, aber funktional. */
  async embed(text) {
    await this.init();
    if (this.motor.embed) return this.motor.embed(text);
    return LLMGateway.hashEmbedding(text);
  }

  /** Notlösungs-Embedding: 256-dim Bag-of-Hashed-Trigrams (deterministisch,
   *  sprachunabhängig, ~gut genug für Exact-nahe Umformulierungen). */
  static hashEmbedding(text, dim = 256) {
    const v = new Array(dim).fill(0);
    const t = " " + text.toLowerCase().replace(/\s+/g, " ") + " ";
    for (let i = 0; i < t.length - 2; i++) {
      let h = 2166136261;
      for (let j = i; j < i + 3; j++) { h ^= t.charCodeAt(j); h = Math.imul(h, 16777619); }
      v[Math.abs(h) % dim] += 1;
    }
    return v;
  }
}
