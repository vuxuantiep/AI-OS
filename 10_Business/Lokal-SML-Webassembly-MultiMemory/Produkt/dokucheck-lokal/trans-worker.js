/* DocuCheck Local — Übersetzungs-Worker (v0.3)
   Neuronale Übersetzung OHNE LLM: OPUS-MT (MarianMT) über transformers.js,
   ONNX-Runtime als WASM auf der CPU — läuft damit auch ohne WebGPU.
   Deutsch↔Vietnamesisch existiert nicht als direktes Modellpaar → Pivot
   über Englisch (de→en→vi bzw. vi→en→de).
   Die Modellgewichte (~45 MB je Paar, int8) kommen einmalig von HuggingFace
   und landen im Browser-Cache (Cache API) — danach offline nutzbar. */
import { pipeline, env } from "./vendor/transformers/transformers.min.js";

env.allowLocalModels = false; // sonst probiert die Lib erst unseren Origin (404-Rauschen)
env.backends.onnx.wasm.wasmPaths = new URL("./vendor/transformers/", self.location.href).href;

/* Netzwerk-Beweiszähler: Fetches im Worker sind für den Hauptthread
   unsichtbar → gleiches Muster wie worker.js (BroadcastChannel). */
const netChannel = new BroadcastChannel("docucheck-net");
new PerformanceObserver((list) => {
  for (const e of list.getEntries()) {
    if (e.initiatorType === "fetch") netChannel.postMessage({ kind: "net", url: e.name });
  }
}).observe({ entryTypes: ["resource"] });

const MODELLE = {
  "de-en": "Xenova/opus-mt-de-en",
  "en-de": "Xenova/opus-mt-en-de",
  "en-vi": "Xenova/opus-mt-en-vi",
  "vi-en": "Xenova/opus-mt-vi-en",
};

/* Route: direktes Paar, sonst Pivot über Englisch */
function route(quelle, ziel) {
  const direkt = quelle + "-" + ziel;
  if (MODELLE[direkt]) return [direkt];
  return [quelle + "-en", "en-" + ziel];
}

const pipelines = new Map();
async function holePipeline(paar, melde) {
  if (pipelines.has(paar)) return pipelines.get(paar);
  const p = await pipeline("translation", MODELLE[paar], {
    dtype: "q8",
    progress_callback: (d) => {
      if (d.status === "progress" && d.total) {
        melde({ typ: "lade", paar, datei: d.file, prozent: Math.round((d.loaded / d.total) * 100) });
      }
    },
  });
  pipelines.set(paar, p);
  return p;
}

/* MarianMT verkraftet nur ~512 Tokens pro Aufruf → Text absatzweise in
   Satzgruppen von max. ~420 Zeichen zerlegen. absatzEnde steuert, ob der
   Hauptthread danach einen Absatzumbruch oder nur ein Leerzeichen setzt. */
function zerlege(text, max = 420) {
  const gruppen = [];
  const absaetze = text.split(/\n+/).map((a) => a.trim()).filter(Boolean);
  for (const absatz of absaetze) {
    const saetze = absatz.match(/[^.!?]+[.!?]*\s*/g) || [absatz];
    let akt = "";
    const teile = [];
    for (const s of saetze) {
      if ((akt + s).length > max && akt) { teile.push(akt.trim()); akt = ""; }
      akt += s;
    }
    if (akt.trim()) teile.push(akt.trim());
    teile.forEach((t, i) => gruppen.push({ text: t, absatzEnde: i === teile.length - 1 }));
  }
  return gruppen;
}

let stoppFlag = false;

self.onmessage = async (ev) => {
  const m = ev.data || {};
  if (m.typ === "stopp") { stoppFlag = true; return; }
  if (m.typ !== "uebersetzen") return;
  stoppFlag = false;
  const melde = (msg) => self.postMessage(msg);
  try {
    const paare = route(m.quelle, m.ziel);
    for (const paar of paare) await holePipeline(paar, melde); // erst laden (mit Fortschritt) ...
    melde({ typ: "modelleBereit" });
    const gruppen = zerlege(m.text);                           // ... dann übersetzen
    for (let i = 0; i < gruppen.length; i++) {
      if (stoppFlag) { melde({ typ: "gestoppt" }); return; }
      let text = gruppen[i].text;
      for (const paar of paare) {
        const r = await pipelines.get(paar)(text);
        text = r[0].translation_text;
      }
      melde({ typ: "teil", i, n: gruppen.length, text, absatzEnde: gruppen[i].absatzEnde });
    }
    melde({ typ: "fertig" });
  } catch (err) {
    melde({ typ: "fehler", msg: (err && err.message) || String(err) });
  }
};
