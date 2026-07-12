/* DokuCheck Lokal — OCR-Modul (Tesseract.js 5.1.1, lokal gevendort).
   Läuft als WebAssembly auf jedem Gerät — braucht KEIN WebGPU.
   Alle Pfade absolut aufgelöst, damit die Fetches im Tesseract-Worker
   unabhängig vom Serverpfad (z. B. /produkte/dokucheck/) funktionieren. */
import Tesseract from "./vendor/tesseract/tesseract.esm.min.js";

const BASE = new URL(".", import.meta.url);
const PFADE = {
  workerPath: new URL("vendor/tesseract/worker.min.js", BASE).href,
  corePath: new URL("vendor/tesseract/core", BASE).href,
  langPath: new URL("vendor/tessdata", BASE).href,
  gzip: true,
};

/* imageSource: File/Blob/URL. sprachen z. B. "deu+eng" oder "vie".
   onProgress bekommt {status, progress} von Tesseract. */
export async function erkenneText(imageSource, sprachen = "deu+eng", onProgress) {
  const worker = await Tesseract.createWorker(sprachen.split("+"), 1, {
    ...PFADE,
    logger: (m) => onProgress?.(m),
  });
  try {
    const { data } = await worker.recognize(imageSource);
    return (data.text || "").trim();
  } finally {
    // Speicher sofort freigeben — wichtig auf Smartphones
    await worker.terminate();
  }
}
