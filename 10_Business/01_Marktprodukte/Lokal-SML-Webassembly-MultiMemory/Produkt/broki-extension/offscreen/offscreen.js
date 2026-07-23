// =============================================================================
// Broki AI — Offscreen-Dokument: DOM-Kontext für WebLLM/wllama
//
// GRUND (gefunden 22.07.2026, echter Bug): dynamisches import() ist in einem
// Service Worker per HTML-Spec verboten ("import() is disallowed on
// ServiceWorkerGlobalScope") — background.js versuchte genau das, deshalb
// schlugen WebLLM UND wllama IMMER fehl, unabhängig davon ob die vendor-
// Dateien vorhanden/korrekt waren. Ein Offscreen-Dokument ist eine normale
// (unsichtbare) Seite mit DOM — dort ist import() erlaubt. Das ist Chromes
// offiziell empfohlenes Muster für genau diesen Fall (WebGPU/WASM-Arbeit,
// die im Service Worker nicht laufen darf).
//
// Kommunikation: background.js (LLMGateway) schickt Nachrichten mit
// { target: "offscreen", typ: "..." } über den normalen Message-Bus; nur
// dieses Dokument reagiert darauf (background.js ignoriert sie explizit).
// =============================================================================

let webllmEngine = null;
let wllamaInstanz = null;

// ECHTER ROOT-CAUSE-FUND (23.07.2026, per chrome.storage-Checkpoint diagnostiziert,
// siehe project-broki-ai Memory): wllamas vendorte utils.js (_loadBinaryResource)
// versucht JEDE geladene Modell-URL automatisch per `caches.open()`/`cache.put()`
// im Cache-Storage-API zwischenzuspeichern. Die Cache-API akzeptiert aber NUR
// http(s)-URLs als Schluessel - chrome-extension://-URLs (so laedt die Extension
// ihre eigenen .gguf-Dateien) wirft sie mit "Request scheme 'chrome-extension'
// is unsupported" ab. Der Fehler passiert in einem ungesicherten XHR-onload-
// Handler -> das eigentliche Lade-Promise resolved/rejected NIE, das sah wie ein
// stummes Einfrieren aus (Ursache des seit Sessionbeginn nie root-gecausten
// "[object ProgressEvent]"-Bugs). Fix HIER (nicht in der vendorten, gitignorten
// utils.js - die wird bei jedem `npm run build:vendor` ueberschrieben): window.caches
// im Offscreen-Dokument deaktivieren, BEVOR wllama importiert wird, damit dessen
// eigener Cache-Zweig (`if (window.caches)`) gar nicht erst betreten wird.
try {
  Object.defineProperty(self, "caches", { value: undefined, configurable: true });
} catch { /* nicht ueberschreibbar -> Bug bleibt bestehen, kein Absturz */ }

async function webllmInit(modell) {
  const { CreateMLCEngine } = await import("../vendor/webllm/index.js");
  webllmEngine = await CreateMLCEngine(modell);
}

async function webllmGenerate(prompt, maxTokens, temperatur) {
  const r = await webllmEngine.chat.completions.create({
    messages: [{ role: "user", content: prompt }],
    max_tokens: maxTokens,
    temperature: temperatur
  });
  return r.choices[0].message.content;
}

function serialisiereFehler(e) {
  if (e instanceof ProgressEvent) {
    const t = e.target;
    return `ProgressEvent(type=${e.type}, target=${t?.constructor?.name}` +
      (t && "status" in t ? `, status=${t.status}` : "") +
      (t && "responseURL" in t ? `, url=${t.responseURL}` : "") +
      (t && "statusText" in t ? `, statusText=${t.statusText}` : "") + ")";
  }
  return String(e?.message || e);
}

// DIAGNOSE (23.07.2026): Offscreen-Dokumente haben KEINEN chrome.storage-
// Zugriff (empirisch verifiziert: chrome.storage ist hier `undefined`,
// eingeschraenkte API-Teilmenge fuer Offscreen-Kontexte) - deshalb schickt
// dieser Checkpoint stattdessen eine Nachricht an den Service Worker
// (background.js, Case "wllama-checkpoint"), der sie persistiert. Bewusst
// NICHT auf die sendMessage-Antwort gewartet (fire-and-forget), damit ein
// haengender/gecrashter Message-Bus den eigentlichen Ladevorgang nicht
// verzoegert. Ueberlebt einen Absturz des Offscreen-Prozesses, weil der
// letzte erreichte Schritt unabhaengig vom (dann toten) Kontext ausgelesen
// werden kann.
function checkpoint(schritt, extra) {
  chrome.runtime.sendMessage({
    typ: "wllama-checkpoint",
    daten: { schritt, zeit: new Date().toISOString(), ...extra }
  }).catch(() => {});
}

async function wllamaInit(ggufDateiname) {
  await checkpoint("start", { gguf: ggufDateiname });
  const { Wllama } = await import("../vendor/wllama/index.js");
  await checkpoint("import-ok");
  let wllamaTmp;
  try {
    wllamaTmp = new Wllama({
      "single-thread/wllama.wasm": chrome.runtime.getURL("vendor/wllama/single-thread/wllama.wasm")
    });
    await checkpoint("konstruktor-ok");
  } catch (e) {
    await checkpoint("konstruktor-fehler", { fehler: serialisiereFehler(e) });
    throw new Error("KONSTRUKTOR: " + serialisiereFehler(e));
  }
  const modelUrl = chrome.runtime.getURL("vendor/modelle/" + ggufDateiname);
  try {
    await checkpoint("vor-loadmodel", { url: modelUrl });
    await wllamaTmp.loadModelFromUrl(modelUrl, { n_ctx: 4096, n_threads: 1 });
    await checkpoint("loadmodel-ok");
  } catch (e) {
    await checkpoint("loadmodel-fehler", { fehler: serialisiereFehler(e) });
    throw new Error("LOADMODEL(" + modelUrl + "): " + serialisiereFehler(e));
  }
  wllamaInstanz = wllamaTmp;
}

self.addEventListener("error", (e) => {
  checkpoint("window-error", { message: e.message, filename: e.filename, lineno: e.lineno });
});
self.addEventListener("unhandledrejection", (e) => {
  checkpoint("unhandled-rejection", { reason: serialisiereFehler(e.reason) });
});

async function wllamaGenerate(prompt, maxTokens, temperatur) {
  return wllamaInstanz.createCompletion(prompt, {
    nPredict: maxTokens, sampling: { temp: temperatur }
  });
}

async function wllamaEmbed(text) {
  return wllamaInstanz.createEmbeddings(text);
}

chrome.runtime.onMessage.addListener((msg, sender, sendeAntwort) => {
  if (msg.target !== "offscreen") return false;   // nicht für uns — ignorieren
  (async () => {
    switch (msg.typ) {
      case "test-storage":
        try {
          await chrome.storage.local.set({ x: 1 });
          return { ok: true, chromeStorageVorhanden: typeof chrome?.storage, chromeStorageLocalVorhanden: typeof chrome?.storage?.local };
        } catch (e) {
          return { ok: false, fehler: String(e?.message || e), chromeVorhanden: typeof chrome, chromeStorageVorhanden: typeof chrome?.storage };
        }
      case "webllm-init":
        await webllmInit(msg.modell);
        return { ok: true };
      case "webllm-generate":
        return { ok: true, text: await webllmGenerate(msg.prompt, msg.maxTokens, msg.temperatur) };
      case "wllama-init":
        await wllamaInit(msg.gguf);
        return { ok: true };
      case "wllama-generate":
        return { ok: true, text: await wllamaGenerate(msg.prompt, msg.maxTokens, msg.temperatur) };
      case "wllama-embed":
        return { ok: true, vektor: await wllamaEmbed(msg.text) };
      default:
        return { ok: false, fehler: "Offscreen: unbekannter Typ " + msg.typ };
    }
  })().then(sendeAntwort)
     .catch(e => sendeAntwort({ ok: false, fehler: String(e?.message || e) }));
  return true;   // asynchrone Antwort
});
