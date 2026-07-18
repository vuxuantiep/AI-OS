// =============================================================================
// Broki AI — Agnostisches LLM-Gateway („der austauschbare Muskel")
//
// Motor-Rangfolge (erster verfügbarer gewinnt):
//   1. Native On-Device-KI des Browsers  (Prompt API: window.ai / LanguageModel
//      — Edge liefert Phi, Chrome Gemini Nano; 0 MB Download, sofort da)
//   2. WebLLM   (WebGPU; Llama-3/Qwen als MLC-Pakete — schnellster Fallback)
//   3. wllama   (WebAssembly/CPU-Multi-Threading; läuft praktisch überall,
//      GGUF-Format; > 2 GB-Modelle müssten gesharded werden → vermeiden wir
//      durch die deviceMemory-Stufen von vornherein)
//
// OOM-Schutz: VOR jeder Motor-Initialisierung wird navigator.deviceMemory
// gelesen und die Modellgröße daran ausgerichtet — ein eingefrorener Tab
// ist der schnellste Weg, Nutzer zu verlieren.
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
    if (await LLMGateway.webgpuVerfuegbar()) {
      try {
        const { CreateMLCEngine } = await import("../vendor/webllm/index.js");
        const engine = await CreateMLCEngine(stufe.webllm);
        this.motor = {
          name: `webllm (${stufe.webllm})`,
          generate: async (prompt) => {
            const r = await engine.chat.completions.create({
              messages: [{ role: "user", content: prompt }],
              max_tokens: this.cfg.antwortTokensMax,
              temperature: this.cfg.temperatur
            });
            return r.choices[0].message.content;
          }
        };
        this.motorName = this.motor.name;
        console.log("[Broki/LLM] Motor: WebLLM,", stufe.webllm);
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
      const { Wllama } = await import("../vendor/wllama/index.js");
      const wllama = new Wllama({
        "single-thread/wllama.wasm": "../vendor/wllama/single-thread/wllama.wasm",
        "multi-thread/wllama.wasm": "../vendor/wllama/multi-thread/wllama.wasm"
      });
      await wllama.loadModelFromUrl(
        chrome.runtime.getURL("vendor/modelle/" + stufe.wllamaGguf),
        { n_ctx: 4096 });
      this.motor = {
        name: `wllama (${stufe.wllamaGguf})`,
        generate: (prompt) => wllama.createCompletion(prompt, {
          nPredict: this.cfg.antwortTokensMax,
          sampling: { temp: this.cfg.temperatur }
        }),
        embed: (text) => wllama.createEmbedding(text)
      };
      this.motorName = this.motor.name;
      console.log("[Broki/LLM] Motor: wllama (CPU),", stufe.wllamaGguf);
      return this.motorName;
    } catch (e) {
      console.warn("[Broki/LLM] wllama-Start fehlgeschlagen:", e.message);
      if (this.modus === "cloud") {
        const name = await this._initCloud();
        if (name) return name;
      }
    }

    // --- Motor 4: Cloud-Fallback (nur wenn Modus=cloud) ----------------------
    if (this.modus === "cloud") {
      const name = await this._initCloud();
      if (name) return name;
    }

    throw new Error("Kein KI-Motor verfügbar (weder native API, WebGPU noch WASM).");
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
