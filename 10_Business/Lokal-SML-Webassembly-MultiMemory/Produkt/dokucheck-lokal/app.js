/* =========================================================
   DokuCheck Lokal v0.2 — Hauptmodul
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
import { erkenneText } from "./ocr.js";
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

new BroadcastChannel("dokucheck-net").onmessage = (e) => {
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

$("modelSel").addEventListener("change", () => {
  sessionSet("modell", $("modelSel").value); // Tool Memory: Modellwahl merken
  zeigeCacheStatus();
});

$("loadBtn").addEventListener("click", async () => {
  const modell = $("modelSel").value;
  $("loadBtn").disabled = true;
  $("loadProg").hidden = false;
  netPhase = "model";
  try {
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
    // data-i18n mit umstellen, damit ein Sprachwechsel den Text nicht zurücksetzt
    $("loadBtn").setAttribute("data-i18n", "s1.switchBtn");
    $("loadBtn").textContent = t("s1.switchBtn");
    updateReady();
  } catch (err) {
    netPhase = "boot";
    $("loadStatus").innerHTML = '<span class="badge-warn">' + t("s1.error") + " " + err.message + "</span>";
    $("loadBtn").disabled = false;
  }
});

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
      setzeDokument(file.name, text);
    } else {
      setzeDokument(file.name, await file.text());
    }
  } catch (err) {
    $("fileMeta").textContent = t("file.error") + " " + err.message;
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
    $("ocrStatus").innerHTML = '<span class="badge-ok">' + t("ocr.done") + "</span>";
    $("ocrText").hidden = false;
    $("ocrText").textContent = text;
    setzeDokument(file.name || "Foto", text);
  } catch (err) {
    $("ocrProg").hidden = true;
    $("ocrStatus").innerHTML = '<span class="badge-warn">' + t("ocr.error") + " " + err.message + "</span>";
  }
}

function setzeDokument(name, text, ausSpeicher = false) {
  docText = text.replace(/\s{3,}/g, " ").trim();
  docName = name;
  chunks = makeChunks(docText, 1400);
  bmIndex = bm25Index(chunks);
  $("fileMeta").textContent = `✓ ${name} · ${docText.length.toLocaleString("de-DE")} ${t("file.chars")} · ${chunks.length} ${t("file.sections")}`;
  updateReady();
  if (!ausSpeicher && docText.length > 0) {
    // Semantic Memory: Dokument + Chunks persistieren
    semantic.saveDokument(name, docText, chunks).then(renderDokumente).catch(() => {});
  }
}

/* Chunking mit Überlappung */
function makeChunks(text, size) {
  const out = [];
  for (let i = 0; i < text.length; i += size - 200) out.push(text.slice(i, i + size));
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
    const toks = tokenisiere(c);
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
  return idx.map((i) => chunks[i]).join("\n---\n");
}

function updateReady() {
  const ready = engine && docText.length > 0 && !generating;
  ["sumBtn", "riskBtn", "transBtn", "qBtn", "qInput"].forEach((id) => ($(id).disabled = !ready));
  document.querySelectorAll("[data-routine-run]").forEach((b) => (b.disabled = !ready));
}

/* =========================================================
   Schritt 3: Generierung (Streaming aus dem Worker)
   System- und Aufgaben-Prompts kommen aus i18n.js —
   die gewählte Sprache bestimmt die Antwortsprache.
   ========================================================= */
async function generate(messages, { onDelta, maxTokens = 700, temperature = 0.3 } = {}) {
  const stream = await engine.chat.completions.create({
    stream: true, messages, temperature, max_tokens: maxTokens,
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
  // Ab jetzt zeigt #output Ergebnisse — Sprachwechsel darf sie nicht überschreiben
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
    $("output").textContent = t("err.prefix") + " " + err.message;
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
    if (len + c.length > maxZeichen && aktuelle.length) {
      gruppen.push(aktuelle.join("\n"));
      aktuelle = []; len = 0;
    }
    aktuelle.push(c); len += c.length;
  }
  if (aktuelle.length) gruppen.push(aktuelle.join("\n"));
  return gruppen;
}

function zusammenfassen() {
  runAktion(t("action.sum"), null, async () => {
    const sys = { role: "system", content: t("prompt.sys") };
    if (chunks.length <= 4) {
      return generate([
        sys,
        { role: "user", content: t("prompt.sumShort", { doc: chunks.join("\n---\n") }) },
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
      { role: "system", content: t("prompt.sys") },
      { role: "user", content: t("prompt.risk", { doc: ctx }) },
    ], { onDelta: (_, text) => ($("output").textContent = text) });
  });
}

/* --- Übersetzen: Abschnitt für Abschnitt über das SLM --- */
const MAX_UEBERSETZUNG = 6;
function uebersetzen() {
  const zielCode = $("transLang").value;         // de | en | vi
  const zielName = t("lang." + zielCode);        // Sprachname in der UI-Sprache
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
        { role: "system", content: t("prompt.transSys", { ziel: zielName }) },
        { role: "user", content: teile[i] },
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
      miniBtn(t("mem.delete"), async () => { await semantic.deleteDokument(d.id); renderDokumente(); }, "btn mini danger")
    );
    liste.append(li);
  }
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
  a.download = "dokucheck-routinen.json";
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
  renderAnalysen();
  renderDokumente();
  renderRoutinen();
});

/* =========================================================
   Initialisierung
   ========================================================= */
(async function init() {
  await initLang(); // Sprache zuerst — alles danach rendert bereits übersetzt

  // Tool Memory: gemerkte Modellwahl wiederherstellen
  try {
    const gemerkt = await sessionGet("modell");
    if (gemerkt && [...$("modelSel").options].some((o) => o.value === gemerkt)) {
      $("modelSel").value = gemerkt;
    }
  } catch { /* IndexedDB nicht verfügbar */ }
  zeigeGpuBadge();
  zeigeCacheStatus();

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
