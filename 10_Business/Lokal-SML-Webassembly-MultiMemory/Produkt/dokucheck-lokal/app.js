/* =========================================================
   DocuCheck Local v0.2 — Hauptmodul
   Architektur: UI (dieser Thread) + WebLLM-Engine im Web
   Worker (worker.js) + OCR im Tesseract-Worker (ocr.js).
   Mehrsprachig (DE/EN/VI) über i18n.js — die Sprachwahl
   steuert UI-Texte UND die Antwortsprache des Modells.
   Alle Bibliotheken lokal gevendort — die App-Shell macht
   keine externen Requests. Nur die Modellgewichte kommen
   beim ersten Laden von der HuggingFace-CDN und liegen
   danach im Browser-Cache.
   ========================================================= */
import * as webllm from "./vendor/web-llm/web-llm.js";
import * as pdfjs from "./vendor/pdfjs/pdf.min.mjs";
import { erkenneText, ocrWorker } from "./ocr.js";
import { t, setLang, initLang } from "./i18n.js";
import { sessionGet, sessionSet } from "./memory/db.js";
import * as episodic from "./memory/episodic.js";
import * as semantic from "./memory/semantic.js";
import * as procedural from "./memory/procedural.js";

pdfjs.GlobalWorkerOptions.workerSrc = new URL("./vendor/pdfjs/pdf.worker.min.mjs", import.meta.url).href;

const $ = (id) => document.getElementById(id);

/* ---------- Zustand (Working Memory der Sitzung) ---------- */
let engine = null;
let aktivesModell = "";
let docText = "";
let docName = "";
let chunks = [];
let bmIndex = null;
let generating = false;
let stopFlag = false;

/* ---------- DOM-Referenzen ---------- */
const netCount = $("netCount");
const netModel = $("netModel");
const netVerdict = $("netVerdict");
const gpuCard = $("gpuCard");
const loadProg = $("loadProg");
const loadStatus = $("loadStatus");
const loadBtn = $("loadBtn");
const presetSel = $("presetSel");
const modelSel = $("modelSel");
const fileMeta = $("fileMeta");
const ocrProg = $("ocrProg");
const ocrStatus = $("ocrStatus");
const safetyHint = $("safetyHint");

/* =========================================================
   Netzwerk-Beweis (Signatur-Feature)
   Phase "model": Downloads während des Modell-Ladens (einmalig, erwartet).
   Phase "watch": danach zählt jede EXTERNE Anfrage als Alarm.
   Worker-Fetches sieht der Hauptthread nicht — worker.js meldet
   sie deshalb per BroadcastChannel.
   ========================================================= */
let netPhase = "boot"; // boot → model → watch
let modelNet = 0;
let watchNet = 0;

function meldeNetz(url) {
  if (netPhase === "boot") return;
  if (netPhase === "model") {
    modelNet++;
    $("netModel").textContent = modelNet;
    return;
  }
  // watch: lokale Anfragen an die eigene App (gleicher Origin) sind kein Datenabfluss
  try {
    if (new URL(url, location.href).origin === location.origin) return;
  } catch { /* unparsebare URL → sicherheitshalber zählen */ }
  watchNet++;
  $("netCount").textContent = watchNet;
  const v = $("netVerdict");
  v.removeAttribute("data-i18n");
  v.innerHTML = '<span class="net-alert">' + t("proof.alert") + "</span>";
}

new BroadcastChannel("docucheck-net").onmessage = (e) => {
  if (e.data && e.data.kind === "net") meldeNetz(e.data.url);
};
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.initiatorType === "fetch" || entry.initiatorType === "xmlhttprequest") meldeNetz(entry.name);
  }
}).observe({ entryTypes: ["resource"] });

/* ---------- WebGPU-Erkennung ---------- */
const hatWebGPU = "gpu" in navigator;
function zeigeGpuBadge() {
  $("gpuInfo").innerHTML = hatWebGPU
    ? '<span class="badge-ok">' + t("gpu.okBadge") + "</span>"
    : '<span class="badge-warn">' + t("gpu.missingBadge") + "</span>";
}
if (!hatWebGPU) {
  $("gpuCard").hidden = false;
  $("loadBtn").disabled = true;
}

/* ---------- Schritt 1: Modell laden (im Web Worker) ---------- */
async function zeigeCacheStatus() {
  try {
    const imCache = await webllm.hasModelInCache($("modelSel").value);
    if (imCache) $("loadStatus").innerHTML = '<span class="badge-ok">' + t("s1.cached") + "</span>";
    else if (!engine) $("loadStatus").textContent = "";
  } catch { /* Cache-API nicht verfügbar (z. B. file://) */ }
}

/* =========================================================
   Modell-Presets: Profil → Modell + Inferenz-Parameter
   ========================================================= */
const PRESETS = {
  schnell:   { modell: "Qwen2-0.5B-Instruct-q4f16_1-MLC", temperature: 0.3, max_tokens: 500, repetition_penalty: 1.1 },
  standard:  { modell: "Llama-3.2-1B-Instruct-q4f16_1-MLC", temperature: 0.25, max_tokens: 800, repetition_penalty: 1.15 },
  praezise:  { modell: "Llama-3.2-3B-Instruct-q4f16_1-MLC", temperature: 0.2, max_tokens: 1200, repetition_penalty: 1.2 },
  experimental: { modell: "Phi-3.5-mini-instruct-q4f16_1-MLC", temperature: 0.2, max_tokens: 1000, repetition_penalty: 1.1 },
};

function wendePresetAn(name) {
  const p = PRESETS[name] || PRESETS.standard;
  $("modelSel").value = p.modell;
  sessionSet("modell", p.modell);
  sessionSet("preset", name);
  zeigeCacheStatus();
}

$("presetSel").addEventListener("change", () => wendePresetAn($("presetSel").value));
$("modelSel").addEventListener("change", () => {
  sessionSet("modell", $("modelSel").value);
  zeigeCacheStatus();
});

/* ---------- Schritt 1: Modell laden (im Web Worker) ---------- */
async function ladeModell() {
  const modell = $("modelSel").value;
  $("loadBtn").disabled = true;
  $("loadProg").hidden = false;
  netPhase = "model";
  try {
    if (!hatWebGPU) {
      throw new Error(t("err.webgpu"));
    }
    engine = await webllm.CreateWebWorkerMLCEngine(
      new Worker(new URL("./worker.js", import.meta.url), { type: "module" }),
      modell,
      {
        initProgressCallback: (p) => {
          $("loadProg").value = p.progress ?? 0;
          $("loadStatus").textContent = p.text ?? "";
        },
      }
    );
    aktivesModell = modell;
    netPhase = "watch";
    $("loadStatus").innerHTML = '<span class="badge-ok">' + t("s1.ready") + "</span>";
    $("loadBtn").disabled = false;
    $("loadBtn").setAttribute("data-i18n", "s1.switchBtn");
    $("loadBtn").textContent = t("s1.switchBtn");
    updateReady();
  } catch (err) {
    netPhase = "boot";
    const msg = err && err.message ? err.message : String(err);
    if (msg.toLowerCase().includes("webgpu") || msg.toLowerCase().includes("gpu")) {
      $("loadStatus").innerHTML = '<span class="badge-warn">' + t("err.webgpu") + "</span>";
    } else {
      $("loadStatus").innerHTML = '<span class="badge-warn">' + t("s1.error") + " " + msg + "</span>";
    }
    $("loadBtn").disabled = false;
  }
}
$("loadBtn").addEventListener("click", ladeModell);

/* Modell automatisch initialisieren, sobald ein Dokument bereit ist und die
   Gewichte bereits im Browser-Cache liegen (kein Download nötig). Ohne das
   bleibt Schritt 3 nach jedem Seiten-Reload grau, bis man Schritt 1 erneut
   anklickt — aus Nutzersicht "startet Schritt 3 nicht". */
let autoLadeVersucht = false;
async function autoLadeModell() {
  if (autoLadeVersucht || engine || !hatWebGPU || $("loadBtn").disabled) return;
  autoLadeVersucht = true;
  try {
    if (await webllm.hasModelInCache($("modelSel").value)) {
      $("loadStatus").textContent = t("s1.autoLoad");
      ladeModell();
    }
  } catch { /* Cache-API nicht verfügbar (z. B. file://) — manuell laden */ }
}

/* ---------- Schritt 2: Dokument einlesen (lokal) ---------- */
const drop = $("drop");
const fileInput = $("fileInput");
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("over"); });
drop.addEventListener("dragleave", () => drop.classList.remove("over"));
drop.addEventListener("drop", (e) => {
  e.preventDefault();
  drop.classList.remove("over");
  if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener("change", () => fileInput.files[0] && handleFile(fileInput.files[0]));
$("cameraInput").addEventListener("change", () => $("cameraInput").files[0] && handleFile($("cameraInput").files[0]));

async function handleFile(file) {
  $("fileMeta").textContent = t("file.reading") + " " + file.name + " …";
  try {
    if (file.size > 100 * 1024 * 1024) {
      throw new Error(t("s2.fileTooBig"));
    }
    const name = file.name.toLowerCase();
    if (file.type.startsWith("image/") || /\.(png|jpe?g|webp|bmp|gif)$/.test(name)) {
      await handleBild(file);
      return;
    }
    if (name.endsWith(".pdf")) {
      const buf = await file.arrayBuffer();
      const pdf = await pdfjs.getDocument({ data: buf }).promise;
      let text = "";
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const tc = await page.getTextContent();
        text += tc.items.map((it) => it.str).join(" ") + "\n";
      }
      let ausOcr = false;
      if (text.replace(/\s+/g, "").length < 20) {
        text = await ocrPdf(pdf);
        ausOcr = true;
      }
      setzeDokument(file.name, text, false, ausOcr);
    } else {
      setzeDokument(file.name, await file.text());
    }
  } catch (err) {
    const msg = err && err.message ? err.message : String(err);
    $("fileMeta").innerHTML = '<span class="badge-warn">' + t("s2.error") + " " + msg + "</span>";
  }
}

/* OCR-Fallback für gescannte PDFs: Seiten als Canvas rendern und lesen.
   EIN Tesseract-Worker für alle Seiten (Init ist teuer). */
const MAX_OCR_SEITEN = 10;
async function ocrPdf(pdf) {
  const n = Math.min(pdf.numPages, MAX_OCR_SEITEN);
  $("fileMeta").textContent = t("pdf.scanned");
  const w = await ocrWorker($("ocrLang").value);
  try {
    let text = "";
    for (let i = 1; i <= n; i++) {
      $("fileMeta").textContent = t("pdf.scanned") + " " + t("pdf.ocrPage", { i, n });
      const page = await pdf.getPage(i);
      const vp = page.getViewport({ scale: 2 });
      const canvas = document.createElement("canvas");
      canvas.width = vp.width;
      canvas.height = vp.height;
      await page.render({ canvasContext: canvas.getContext("2d"), viewport: vp }).promise;
      text += (await w.erkennen(canvas)) + "\n";
    }
    if (pdf.numPages > n) text += "\n" + t("pdf.limited", { n });
    return text;
  } finally {
    await w.beenden();
  }
}

/* OCR-Pfad: Bild → Text (WASM, läuft ohne WebGPU) */
async function handleBild(file) {
  $("ocrPreview").hidden = false;
  $("ocrImage").src = URL.createObjectURL(file);
  $("ocrText").hidden = true;
  $("ocrProg").hidden = false;
  $("ocrProg").value = 0;
  $("fileMeta").textContent = "";
  const sprachen = $("ocrLang").value;
  try {
    const text = await erkenneText(file, sprachen, (m) => {
      if (m.status === "recognizing text") {
        $("ocrProg").value = m.progress ?? 0;
        $("ocrStatus").textContent = t("ocr.running") + " " + Math.round((m.progress ?? 0) * 100) + " %";
      } else {
        $("ocrStatus").textContent = m.status || "";
      }
    });
    $("ocrProg").hidden = true;
    if (!text) {
      $("ocrStatus").innerHTML = '<span class="badge-warn">' + t("ocr.none") + "</span>";
      return;
    }
    const qualitaet = schaetzeOcrQualitaet(text);
    if (qualitaet.schlecht) {
      $("ocrStatus").innerHTML = '<span class="badge-warn">' + t("ocr.badQuality") + "</span>";
    } else {
      $("ocrStatus").innerHTML = '<span class="badge-ok">' + t("ocr.done") + "</span>";
    }
    $("ocrText").hidden = false;
    $("ocrText").textContent = text;
    setzeDokument(file.name || "Foto", text, false, true);
  } catch (err) {
    $("ocrProg").hidden = true;
    const msg = err && err.message ? err.message : String(err);
    if (msg.toLowerCase().includes("model") && msg.toLowerCase().includes("image")) {
      $("ocrStatus").innerHTML = '<span class="badge-warn">' + t("ocr.error") + " Das Bildformat wird nicht unterstützt. Versuche ein JPEG oder ein schärferes Foto.</span>";
    } else if (msg.toLowerCase().includes("tesseract") || msg.toLowerCase().includes("worker")) {
      $("ocrStatus").innerHTML = '<span class="badge-warn">' + t("ocr.workerFailed") + "</span>";
    } else {
      $("ocrStatus").innerHTML = '<span class="badge-warn">' + t("ocr.error") + " " + msg + "</span>";
    }
  }
}

function schaetzeOcrQualitaet(text) {
  if (!text || text.length < 15) return { schlecht: true, grund: "zu kurz" };
  const woerter = text.split(/[\s\n]+/).filter((w) => w.length > 1);
  if (!woerter.length) return { schlecht: true, grund: "keine wörter" };
  const nurFragmente = woerter.filter((w) => w.length <= 2).length;
  const anteil = nurFragmente / woerter.length;
  // Nur Buchstaben 4x+ in Folge zählen als OCR-Artefakt — "..." , "---", "www"
  // oder "Schifffahrt" (3x f) kommen in sauberen Dokumenten legitim vor
  const kuerzel = /(\p{L})\1{3,}/u;
  const vieleSonderzeichen = (text.match(/[^a-zA-ZäöüÄÖÜß0-9\s.,!?;:'"()\[\]{}<>/\\@#$%^&*_+=~`|·\-–—\n\r\tàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸšŠžŽřŘčČćĆżŻłŁőŐűŰ]/gu) || []).length;
  if (anteil > 0.6 || vieleSonderzeichen > text.length * 0.15 || kuerzel.test(text)) {
    return { schlecht: true, grund: "fragmente" };
  }
  return { schlecht: false };
}

function setzeDokument(name, text, ausSpeicher = false, ausOcr = false) {
  const bereinigt = text.replace(/\s{3,}/g, " ").trim();
  if (bereinigt.length < 20) {
    docText = "";
    docName = "";
    chunks = [];
    bmIndex = null;
    $("fileMeta").innerHTML = '<span class="badge-warn">' + t("pdf.noText") + "</span>";
    updateReady();
    return;
  }
  docText = bereinigt;
  docName = name;
  chunks = makeChunks(docText, 1400);
  bmIndex = bm25Index(chunks);
  const meta = `✓ ${name} · ${docText.length.toLocaleString("de-DE")} ${t("file.chars")} · ${chunks.length} ${t("file.sections")}`;
  // Qualitätswarnung NUR für OCR-Text — Text aus einer PDF-Textebene oder
  // Textdatei ist verlustfrei, die Heuristik würde dort falschen Alarm schlagen
  if (ausOcr && !ausSpeicher && schaetzeOcrQualitaet(bereinigt).schlecht) {
    // Warnung ZUSÄTZLICH zur Meta-Zeile — nicht von ihr überschreiben lassen
    $("fileMeta").innerHTML = meta + '<br><span class="badge-warn">' + t("s2.ocrBad") + "</span>";
  } else {
    $("fileMeta").textContent = meta;
  }
  updateReady();
  if (!ausSpeicher) {
    semantic.saveDokument(name, docText, chunks).then(renderDokumente).catch(() => {});
  }
}

/* Chunking mit Überlappung und Metadaten */
function makeChunks(text, size = 1400) {
  const out = [];
  let i = 0;
  let reihe = 0;
  while (i < text.length) {
    const slice = text.slice(i, i + size);
    out.push({ text: slice, reihe: ++reihe, start: i, end: i + slice.length });
    i += size - 200;
  }
  return out;
}

/* =========================================================
   BM25-Retrieval (statt naivem Keyword-Zählen)
   ========================================================= */
const STOPP = new Set(("der die das ein eine einer eines einem einen und oder aber auch nicht kein keine ist sind war waren " +
  "wird werden wurde wurden hat haben hatte hatten sich mit von zur zum im in am an auf für bei aus nach über unter vor " +
  "dass wenn weil als wie noch nur schon sehr kann können muss müssen soll sollen darf dürfen des dem den es er sie wir " +
  "ihr ich du man dies diese dieser dieses alle allen aller beim vom durch gegen ohne bis seit sowie bzw etwa je pro " +
  "the and for with this that from are was were been have has had not you your").split(" "));

function tokenisiere(s) {
  return s.toLowerCase().replace(/ß/g, "ss")
    .split(/[^\p{L}\p{N}]+/u)
    .filter((w) => w.length > 2 && !STOPP.has(w));
}

function bm25Index(chunkListe) {
  const docs = chunkListe.map((c) => {
    const toks = tokenisiere(c.text);
    const tf = new Map();
    for (const t of toks) tf.set(t, (tf.get(t) || 0) + 1);
    return { len: toks.length, tf };
  });
  const df = new Map();
  for (const d of docs) for (const t of d.tf.keys()) df.set(t, (df.get(t) || 0) + 1);
  const avgdl = docs.reduce((s, d) => s + d.len, 0) / Math.max(docs.length, 1);
  return { docs, df, avgdl, n: docs.length };
}

function bm25TopK(frage, k = 3) {
  if (!bmIndex) return [];
  const K1 = 1.5, B = 0.75;
  const terme = new Set(tokenisiere(frage));
  const scores = [];
  bmIndex.docs.forEach((d, i) => {
    let s = 0;
    for (const term of terme) {
      const f = d.tf.get(term);
      if (!f) continue;
      const dfT = bmIndex.df.get(term) || 0;
      const idf = Math.log(1 + (bmIndex.n - dfT + 0.5) / (dfT + 0.5));
      s += idf * (f * (K1 + 1)) / (f + K1 * (1 - B + (B * d.len) / bmIndex.avgdl));
    }
    if (s > 0) scores.push({ i, s });
  });
  scores.sort((a, b) => b.s - a.s);
  return scores.slice(0, k).map((x) => x.i);
}

/* Kontext für eine Frage/Anweisung: BM25-Treffer, sortiert nach Dokumentreihenfolge */
function kontextFuer(frage, k = 4, mitAnfang = false) {
  let idx = bm25TopK(frage, k);
  if (mitAnfang && !idx.includes(0)) idx.push(0);
  if (idx.length === 0) idx = chunks.slice(0, k).map((_, i) => i); // Fallback: Anfang
  idx.sort((a, b) => a - b);
  return idx.map((i) => chunks[i]?.text || "").join("\n---\n");
}

function updateReady() {
  const ready = engine && docText.length > 0 && !generating;
  ["sumBtn", "riskBtn", "transBtn", "qBtn", "qInput"].forEach((id) => ($(id).disabled = !ready));
  document.querySelectorAll("[data-routine-run]").forEach((b) => (b.disabled = !ready));
  const presetReady = ready && $("presetSelUse").value;
  $("presetRunBtn").disabled = !presetReady;
  updateStepStatus();
}

/* ---------- Schrittbalken / Fortschrittsanzeige ---------- */
let warKomplett = false;
function setStepProgress(step) {
  const bar = $("stepBar");
  if (!bar) return;
  const pct = step === 1 ? 33 : step === 2 ? 66 : step === 3 ? 100 : 0;
  bar.style.width = pct + "%";
  bar.textContent = pct > 0 ? pct + "%" : "";
}

function updateStepStatus() {
  const modellOk = !!engine;
  const docOk = docText.length > 0;
  $("step1Status").textContent = modellOk ? t("step.ready") : "";
  $("step2Status").textContent = docOk ? t("s2.ready") : "";
  const komplett = modellOk && docOk;
  $("step3Status").textContent = komplett ? t("step.ready") : "";
  $("sec3").classList.toggle("section-off", !komplett);
  setStepProgress(komplett ? 3 : docOk ? 2 : modellOk ? 1 : 0);
  const hint = $("nextHint");
  if (docOk && !modellOk) {
    hint.hidden = false;
    hint.textContent = t("hint.needModel");
    autoLadeModell();
  } else if (komplett) {
    hint.hidden = false;
    hint.textContent = t("hint.goStep3");
  } else {
    hint.hidden = true;
  }
  if (safetyHint) {
    safetyHint.hidden = !komplett;
  }
  if (komplett && !warKomplett) {
    warKomplett = true;
    const sec = $("sec3");
    sec.scrollIntoView({ behavior: "smooth", block: "center" });
    sec.classList.add("section-pulse");
    setTimeout(() => sec.classList.remove("section-pulse"), 2600);
  }
  if (!komplett) warKomplett = false;
}

/* =========================================================
   Schritt 3: Generierung (Streaming aus dem Worker)
   System- und Aufgaben-Prompts kommen aus i18n.js —
   die gewählte Sprache bestimmt die Antwortsprache.
   ========================================================= */
async function generate(messages, { onDelta, maxTokens, temperature } = {}) {
  const preset = PRESETS[$("presetSel")?.value] || PRESETS.standard;
  const temp = temperature ?? preset.temperature;
  const max = maxTokens ?? preset.max_tokens;
  const stream = await engine.chat.completions.create({
    stream: true, messages, temperature: temp, max_tokens: max,
  });
  let text = "";
  for await (const part of stream) {
    if (stopFlag) {
      try { engine.interruptGenerate(); } catch { /* optional */ }
      break;
    }
    const delta = part.choices[0]?.delta?.content ?? "";
    text += delta;
    if (onDelta) onDelta(delta, text);
  }
  return text;
}

/* Rahmen für jede Aktion: Sperren, Stopp-Knopf, Episodic Memory */
async function runAktion(aktion, frage, arbeit) {
  if (generating || !engine || !docText) return;
  generating = true;
  stopFlag = false;
  $("stopBtn").hidden = false;
  $("output").removeAttribute("data-i18n");
  $("output").textContent = "";
  updateReady();
  try {
    const antwort = await arbeit();
    if (antwort && antwort.trim()) {
      await episodic.saveAnalyse({ docName, aktion, frage, modell: aktivesModell, antwort });
      renderAnalysen();
    }
  } catch (err) {
    const msg = err && err.message ? err.message : String(err);
    if (msg.toLowerCase().includes("webgpu") || msg.toLowerCase().includes("gpu")) {
      $("output").textContent = t("err.webgpu") + " " + t("err.reload");
    } else if (msg.toLowerCase().includes("tesseract") || msg.toLowerCase().includes("worker")) {
      $("output").textContent = t("err.tesseract") + " " + t("err.reload");
    } else if (msg.toLowerCase().includes("memory") || msg.toLowerCase().includes("allocation")) {
      $("output").textContent = t("err.memory");
    } else {
      $("output").textContent = t("err.prefix") + " " + msg;
    }
  } finally {
    generating = false;
    $("stopBtn").hidden = true;
    updateReady();
  }
}

$("stopBtn").addEventListener("click", () => { stopFlag = true; });

/* --- Zusammenfassen: Map-Reduce-Light für lange Dokumente --- */
const MAX_GRUPPEN = 6;
function gruppiereChunks(maxZeichen = 4200) {
  const gruppen = [];
  let aktuelle = [];
  let len = 0;
  for (const c of chunks) {
    if (len + c.text.length > maxZeichen && aktuelle.length) {
      gruppen.push(aktuelle.map(x => x.text).join("\n---\n"));
      aktuelle = []; len = 0;
    }
    aktuelle.push(c); len += c.text.length;
  }
  if (aktuelle.length) gruppen.push(aktuelle.map(x => x.text).join("\n---\n"));
  return gruppen;
}

function zusammenfassen() {
  runAktion(t("action.sum"), null, async () => {
    const sys = { role: "system", content: t("prompt.sys") };
    if (chunks.length <= 4) {
      return generate([
        sys,
        { role: "user", content: t("prompt.sumShort", { doc: chunks.map(c => c.text).join("\n---\n") }) },
      ], { onDelta: (_, text) => ($("output").textContent = text) });
    }
    // Map: Stichpunkte je Abschnittsgruppe
    let gruppen = gruppiereChunks();
    let hinweis = "";
    if (gruppen.length > MAX_GRUPPEN) {
      hinweis = "\n\n" + t("note.sumLong", { max: MAX_GRUPPEN, n: gruppen.length });
      gruppen = gruppen.slice(0, MAX_GRUPPEN);
    }
    const stichpunkte = [];
    for (let i = 0; i < gruppen.length; i++) {
      if (stopFlag) return "";
      $("output").textContent = t("status.sumPart", { i: i + 1, n: gruppen.length });
      const teil = await generate([
        sys,
        { role: "user", content: t("prompt.sumMap", { teil: gruppen[i] }) },
      ], { maxTokens: 250, temperature: 0.2 });
      stichpunkte.push(teil);
    }
    if (stopFlag) return "";
    // Reduce: finale Synthese, gestreamt
    const final = await generate([
      sys,
      { role: "user", content: t("prompt.sumReduce", { punkte: stichpunkte.join("\n\n") }) },
    ], { onDelta: (_, text) => ($("output").textContent = text) });
    $("output").textContent = final + hinweis;
    return final + hinweis;
  });
}

/* --- Risiko-Check: BM25 mit festen Risiko-Suchbegriffen ---
   Suchbegriffe mehrsprachig, damit sie zum DOKUMENT passen (nicht zur UI-Sprache). */
const RISIKO_QUERY = "Frist Termin Kündigung Widerruf Kosten Gebühren Zahlung Vertragsstrafe Haftung Verlängerung " +
  "deadline termination notice withdrawal cost fee payment penalty liability renewal " +
  "thời hạn chấm dứt hủy chi phí thanh toán phạt trách nhiệm gia hạn";

function risikoCheck() {
  runAktion(t("action.risk"), null, async () => {
    const ctx = kontextFuer(RISIKO_QUERY, 5, true);
    return generate([
      { role: "system", content: t("prompt.sysVertrag") },
      { role: "user", content: t("prompt.risk", { doc: ctx }) },
    ], { onDelta: (_, text) => ($("output").textContent = text) });
  });
}

/* --- Übersetzen: Abschnitt für Abschnitt über das SLM ---
   Prompt bewusst NICHT aus i18n: Er muss unabhängig von der UI-Sprache sein.
   Kleine Modelle folgen englischen Anweisungen am zuverlässigsten — mit
   deutschem System-Prompt kommentieren sie auf Deutsch statt zu übersetzen.
   Zielsprache doppelt benannt (englisch + nativ), Anweisung zusätzlich in
   der User-Nachricht wiederholt. */
const MAX_UEBERSETZUNG = 6;
const TRANS_ZIEL = {
  de: "German (Deutsch)",
  en: "English",
  vi: "Vietnamese (Tiếng Việt)",
};
function uebersetzen() {
  const zielCode = $("transLang").value;         // de | en | vi
  const zielName = t("lang." + zielCode);        // Sprachname in der UI-Sprache (nur Anzeige)
  const ziel = TRANS_ZIEL[zielCode] || zielCode;
  runAktion(t("action.trans"), zielName, async () => {
    let teile = chunks;
    let hinweis = "";
    if (teile.length > MAX_UEBERSETZUNG) {
      hinweis = "\n\n" + t("note.transLong", { max: MAX_UEBERSETZUNG, n: teile.length });
      teile = teile.slice(0, MAX_UEBERSETZUNG);
    }
    let gesamt = "";
    for (let i = 0; i < teile.length; i++) {
      if (stopFlag) break;
      const teil = await generate([
        { role: "system", content: "You are a translation engine. Translate the user's text into " + ziel + ". Reply with ONLY the translated text in " + ziel + " — no comments, no explanations, no preamble." },
        { role: "user", content: "Translate the following text into " + ziel + ". Output only the translation:\n\n" + teile[i].text },
      ], {
        maxTokens: 900, temperature: 0.2,
        onDelta: (_, text) => ($("output").textContent = gesamt ? gesamt + "\n\n" + text : text),
      });
      gesamt += (gesamt ? "\n\n" : "") + teil;
      $("output").textContent = gesamt;
    }
    $("output").textContent = gesamt + hinweis;
    return gesamt + hinweis;
  });
}

/* --- Freie Frage: BM25 Top-3 --- */
function frageStellen() {
  const q = $("qInput").value.trim();
  if (!q) return;
  runAktion(t("action.q"), q, async () => {
    const ctx = kontextFuer(q, 3);
    return generate([
      { role: "system", content: t("prompt.sys") },
      { role: "user", content: t("prompt.q", { ctx, frage: q }) },
    ], { onDelta: (_, text) => ($("output").textContent = text) });
  });
}

/* --- Prüfroutine ausführen (Procedural/Skill Memory) --- */
function routineAusfuehren(routine) {
  runAktion(t("action.routine") + " " + routine.name, routine.prompt, async () => {
    const ctx = kontextFuer(routine.prompt, 4, true);
    return generate([
      { role: "system", content: t("prompt.sys") },
      { role: "user", content: t("prompt.routine", { anweisung: routine.prompt, doc: ctx }) },
    ], { onDelta: (_, text) => ($("output").textContent = text) });
  });
}

$("sumBtn").addEventListener("click", zusammenfassen);
$("riskBtn").addEventListener("click", risikoCheck);
$("transBtn").addEventListener("click", uebersetzen);
$("qBtn").addEventListener("click", frageStellen);
$("qInput").addEventListener("keydown", (e) => e.key === "Enter" && frageStellen());

$("presetRunBtn").addEventListener("click", async () => {
  const name = $("presetSelUse").value;
  if (!name) return;
  const routinen = await procedural.listRoutinen();
  const r = routinen.find((x) => x.name === name);
  if (r) routineAusfuehren(r);
});

/* =========================================================
   Gedächtnis-Panel (Episodic / Semantic / Procedural)
   ========================================================= */
const datum = (ts) => new Date(ts).toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" });

function liEintrag(titel, sub) {
  const li = document.createElement("li");
  const t2 = document.createElement("div");
  t2.className = "mem-title";
  t2.textContent = titel;
  const s = document.createElement("div");
  s.className = "mem-sub";
  s.textContent = sub;
  const a = document.createElement("div");
  a.className = "mem-actions";
  li.append(t2, s, a);
  return { li, actions: a };
}

function miniBtn(text, onClick, klasse = "btn mini") {
  const b = document.createElement("button");
  b.type = "button";
  b.className = klasse;
  b.textContent = text;
  b.addEventListener("click", onClick);
  return b;
}

function leererEintrag(liste, key) {
  const li = document.createElement("li");
  li.className = "mem-empty";
  li.textContent = t(key);
  liste.append(li);
}

async function renderAnalysen() {
  const liste = $("memAnalysen");
  const eintraege = await episodic.listAnalysen();
  liste.innerHTML = "";
  if (!eintraege.length) return leererEintrag(liste, "mem.emptyAnalysen");
  for (const e of eintraege) {
    const { li, actions } = liEintrag(`${e.aktion} — ${e.docName}`, `${datum(e.ts)} · ${e.modell}`);
    actions.append(
      miniBtn(t("mem.show"), () => {
        $("output").removeAttribute("data-i18n");
        $("output").textContent = e.antwort;
        $("output").scrollIntoView({ behavior: "smooth", block: "nearest" });
      }),
      miniBtn(t("mem.export"), () => exportAnalyse(e), "btn mini ghost"),
      miniBtn(t("mem.delete"), async () => { await episodic.deleteAnalyse(e.id); renderAnalysen(); }, "btn mini danger")
    );
    liste.append(li);
  }
}

async function renderDokumente() {
  const liste = $("memDokumente");
  const docs = await semantic.listDokumente();
  liste.innerHTML = "";
  if (!docs.length) return leererEintrag(liste, "mem.emptyDokumente");
  for (const d of docs) {
    const { li, actions } = liEintrag(d.name, `${datum(d.ts)} · ${d.zeichen.toLocaleString("de-DE")} ${t("file.chars")}`);
    actions.append(
      miniBtn(t("mem.open"), async () => {
        const voll = await semantic.loadDokument(d.id);
        if (voll) {
          setzeDokument(voll.name, voll.text, true);
          $("fileMeta").textContent += " · " + t("file.fromMemory");
        }
      }),
      miniBtn(t("mem.export"), () => exportDokument(d), "btn mini ghost"),
      miniBtn(t("mem.delete"), async () => { await semantic.deleteDokument(d.id); renderDokumente(); }, "btn mini danger")
    );
    liste.append(li);
  }
}

/* ---------- Export-Funktionen (Markdown, HTML, JSON) ---------- */
function downloadBlob(content, filename, mime) {
  const blob = new Blob([content], { type: mime });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function exportAnalyse(e) {
  const md = `# Analyse: ${e.aktion} — ${e.docName}\n\n**Datum:** ${datum(e.ts)}\n**Modell:** ${e.modell}\n\n${e.antwort}`;
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>Analyse</title><style>body{font-family:sans-serif;max-width:800px;margin:2rem auto;padding:0 1rem;white-space:pre-wrap}</style></head><body><h1>Analyse: ${e.aktion} — ${e.docName}</h1><p><strong>Datum:</strong> ${datum(e.ts)}<br><strong>Modell:</strong> ${e.modell}</p><hr><div>${e.antwort.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}</div></body></html>`;
  const json = JSON.stringify({ version: "0.3", typ: "analyse", id: e.id, docName: e.docName, aktion: e.aktion, datum: e.ts, modell: e.modell, antwort: e.antwort }, null, 2);
  downloadBlob(md, `analyse-${e.id}.md`, "text/markdown");
  downloadBlob(html, `analyse-${e.id}.html`, "text/html");
  downloadBlob(json, `analyse-${e.id}.json`, "application/json");
}

async function exportDokument(d) {
  const voll = await semantic.loadDokument(d.id);
  if (!voll) return;
  const md = `# Dokument: ${d.name}\n\n**Erstellt:** ${datum(d.ts)}\n**Zeichen:** ${d.zeichen}\n\n${voll.text}`;
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>${d.name}</title><style>body{font-family:sans-serif;max-width:800px;margin:2rem auto;padding:0 1rem;white-space:pre-wrap}</style></head><body><h1>${d.name}</h1><p><strong>Erstellt:</strong> ${datum(d.ts)}<br><strong>Zeichen:</strong> ${d.zeichen}</p><hr><div>${voll.text.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}</div></body></html>`;
  const json = JSON.stringify({ version: "0.3", typ: "dokument", id: d.id, name: d.name, datum: d.ts, zeichen: d.zeichen, text: voll.text }, null, 2);
  downloadBlob(md, `dokument-${d.id}.md`, "text/markdown");
  downloadBlob(html, `dokument-${d.id}.html`, "text/html");
  downloadBlob(json, `dokument-${d.id}.json`, "application/json");
}

async function renderRoutinen() {
  const liste = $("memRoutinen");
  const routinen = await procedural.listRoutinen();
  liste.innerHTML = "";
  if (!routinen.length) return leererEintrag(liste, "mem.emptyRoutinen");
  for (const r of routinen) {
    const { li, actions } = liEintrag(r.name, r.prompt.slice(0, 70) + (r.prompt.length > 70 ? "…" : ""));
    const runBtn = miniBtn(t("mem.run"), () => routineAusfuehren(r));
    runBtn.setAttribute("data-routine-run", "1");
    runBtn.disabled = !(engine && docText && !generating);
    actions.append(
      runBtn,
      miniBtn(t("mem.edit"), () => {
        $("routineName").value = r.name;
        $("routinePrompt").value = r.prompt;
        $("routineName").dataset.editId = r.id;
      }, "btn mini ghost"),
      miniBtn(t("mem.delete"), async () => { await procedural.deleteRoutine(r.id); renderRoutinen(); }, "btn mini danger")
    );
    liste.append(li);
  }
}

$("routineSaveBtn").addEventListener("click", async () => {
  const name = $("routineName").value.trim();
  const prompt = $("routinePrompt").value.trim();
  if (!name || !prompt) return;
  const editId = $("routineName").dataset.editId;
  await procedural.saveRoutine({ ...(editId ? { id: Number(editId) } : {}), name, prompt });
  $("routineName").value = "";
  $("routinePrompt").value = "";
  delete $("routineName").dataset.editId;
  renderRoutinen();
});

$("routineExportBtn").addEventListener("click", async () => {
  const json = await procedural.exportRoutinenJSON();
  const blob = new Blob([json], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "docucheck-routinen.json";
  a.click();
  URL.revokeObjectURL(a.href);
});

$("routineImportInput").addEventListener("change", async () => {
  const file = $("routineImportInput").files[0];
  if (!file) return;
  try {
    const n = await procedural.importRoutinenJSON(await file.text());
    $("routineImportInput").value = "";
    renderRoutinen();
    alert(n + " " + t("mem.imported"));
  } catch (err) {
    alert(t("mem.importFailed") + " " + err.message);
  }
});

/* =========================================================
   Sprachumschalter: UI-Texte live tauschen, Listen neu rendern
   ========================================================= */
document.querySelectorAll(".lang-btn").forEach((btn) => {
  btn.addEventListener("click", () => setLang(btn.dataset.lang));
});
document.addEventListener("langchange", () => {
  zeigeGpuBadge();
  updateStepStatus();
  renderAnalysen();
  renderDokumente();
  renderRoutinen();
});

/* =========================================================
   Initialisierung
   ========================================================= */
(async function init() {
  await initLang(); // Sprache zuerst — alles danach rendert bereits übersetzt

  // Tool Memory: gemerkte Modellwahl und Preset wiederherstellen
  try {
    const gemerkt = await sessionGet("modell");
    if (gemerkt && [...$("modelSel").options].some((o) => o.value === gemerkt)) {
      $("modelSel").value = gemerkt;
    }
    const preset = await sessionGet("preset");
    if (preset && PRESETS[preset]) {
      $("presetSel").value = preset;
      wendePresetAn(preset);
    }
  } catch { /* IndexedDB nicht verfügbar */ }
  zeigeGpuBadge();
  zeigeCacheStatus();

  // Auto-Load wenn Modell bereits im Browser-Cache liegt
  try {
    const imCache = await webllm.hasModelInCache($("modelSel").value);
    if (imCache && hatWebGPU) {
      await ladeModell();
    }
  } catch { /* Cache-API nicht verfügbar */ }

  try {
    await procedural.ensureDefaults();
  } catch { /* z. B. Private Mode */ }
  renderRoutinen();
  renderAnalysen();
  renderDokumente();

  // PWA: Service Worker registrieren (App-Shell offline, installierbar)
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js").catch(() => { /* z. B. file:// */ });
  }
})();
