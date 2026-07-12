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
      const { data } = await worker.recognize(src);
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
