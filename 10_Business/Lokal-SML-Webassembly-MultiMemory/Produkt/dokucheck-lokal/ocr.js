/* DocuCheck Local — OCR-Modul (Tesseract.js 5.1.1, lokal gevendort).
   Läuft als WebAssembly auf jedem Gerät — braucht KEIN WebGPU.
   Alle Pfade absolut aufgelöst, damit die Fetches im Tesseract-Worker
   unabhängig vom Serverpfad (z. B. /produkte/docucheck/) funktionieren. */
import Tesseract from "./vendor/tesseract/tesseract.esm.min.js";

const BASE = new URL(".", import.meta.url);
const PFADE = {
  workerPath: new URL("vendor/tesseract/worker.min.js", BASE).href,
  corePath: new URL("vendor/tesseract/core", BASE).href,
  langPath: new URL("vendor/tessdata", BASE).href,
  gzip: true,
};

export function schaetzeOcrQualitaet(text) {
  if (!text || text.length < 15) return { schlecht: true, grund: "zu kurz" };
  const woerter = text.split(/[\s\n]+/).filter((w) => w.length > 1);
  if (!woerter.length) return { schlecht: true, grund: "keine wörter" };
  const nurFragmente = woerter.filter((w) => w.length <= 2).length;
  const anteil = nurFragmente / woerter.length;
  const kuerzel = /(.)\1\1+/;
  const vieleSonderzeichen = (text.match(/[^a-zA-ZäöüÄÖÜß0-9\s.,!?;:'"()\[\]{}<>/\\@#$%^&*_+=~`|·\-–—\n\r\tàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸšŠžŽřŘčČćĆżŻłŁőŐűŰ]/gu) || []).length;
  if (anteil > 0.6 || vieleSonderzeichen > text.length * 0.15 || kuerzel.test(text)) {
    return { schlecht: true, grund: "fragmente" };
  }
  return { schlecht: false };
}

/* ---------- Bildvorverarbeitung (Canvas): Kontrast + Binarisierung ----------
   Verbessert die Erkennung bei Fotos/Scans. Akzeptiert Image-Quellen
   (File/Blob/URL) UND fertige Canvas-Elemente (PDF-OCR-Fallback). */
function bearbeiteCanvas(quelle, breite, hoehe, { contrast, brightness, binarize, threshold }) {
  const canvas = document.createElement("canvas");
  canvas.width = breite;
  canvas.height = hoehe;
  const ctx = canvas.getContext("2d");
  if (typeof ctx.filter !== "undefined") {
    ctx.filter = `contrast(${contrast}) brightness(${brightness})`;
  }
  ctx.drawImage(quelle, 0, 0);
  if (binarize) {
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const d = imageData.data;
    for (let i = 0; i < d.length; i += 4) {
      const gray = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
      const val = gray > threshold ? 255 : 0;
      d[i] = d[i + 1] = d[i + 2] = val;
    }
    ctx.putImageData(imageData, 0, 0);
  }
  return canvas;
}

function preprocessImage(source, { contrast = 1.4, brightness = 1.1, binarize = true, threshold = 160 } = {}) {
  const optionen = { contrast, brightness, binarize, threshold };
  // Canvas (z. B. gerenderte PDF-Seite) direkt verarbeiten — kein Image-Umweg
  if (typeof HTMLCanvasElement !== "undefined" && source instanceof HTMLCanvasElement) {
    return Promise.resolve(bearbeiteCanvas(source, source.width, source.height, optionen));
  }
  return new Promise((resolve, reject) => {
    const img = new Image();
    const objUrl = typeof source === "string" ? null : URL.createObjectURL(source);
    const aufraeumen = () => { if (objUrl) URL.revokeObjectURL(objUrl); };
    img.onload = () => {
      try {
        resolve(bearbeiteCanvas(img, img.naturalWidth, img.naturalHeight, optionen));
      } catch (e) {
        reject(new Error("Bildvorverarbeitung fehlgeschlagen: " + e.message));
      } finally {
        aufraeumen();
      }
    };
    img.onerror = () => { aufraeumen(); reject(new Error("Bild konnte nicht geladen werden")); };
    img.src = objUrl || source;
  });
}

/* Wiederverwendbarer OCR-Worker — für mehrere Erkennungen (z. B. alle
   Seiten eines gescannten PDFs) lohnt sich EIN Worker statt je einer. */
export async function ocrWorker(sprachen = "deu+eng", onProgress) {
  const worker = await Tesseract.createWorker(sprachen.split("+"), 1, {
    ...PFADE,
    logger: (m) => onProgress?.(m),
  });
  return {
    /* src: File/Blob/Canvas/URL */
    erkennen: async (src) => {
      let canvas;
      try {
        canvas = await preprocessImage(src);
      } catch {
        canvas = src instanceof HTMLCanvasElement ? src : undefined;
      }
      const { data } = await worker.recognize(canvas || src);
      return (data.text || "").trim();
    },
    beenden: () => worker.terminate(),
  };
}

/* Bequem-Variante für ein einzelnes Bild. */
export async function erkenneText(imageSource, sprachen = "deu+eng", onProgress) {
  const w = await ocrWorker(sprachen, onProgress);
  try {
    return await w.erkennen(imageSource);
  } finally {
    // Speicher sofort freigeben — wichtig auf Smartphones
    await w.beenden();
  }
}
