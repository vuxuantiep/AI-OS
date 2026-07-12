/* DocuCheck Local — Service Worker (PWA)
   Cacht die komplette App-Shell inkl. gevendorter Bibliotheken,
   damit die App installierbar ist und offline startet.
   Die Modellgewichte verwaltet WebLLM selbst über die Cache API —
   Cross-Origin-Anfragen werden hier bewusst NICHT angefasst. */
const CACHE = "docucheck-v0.2.4";

const APP_SHELL = [
  "./",
  "./index.html",
  "./styles.css",
  "./app.js",
  "./i18n.js",
  "./worker.js",
  "./ocr.js",
  "./icon.svg",
  "./manifest.webmanifest",
  "./memory/db.js",
  "./memory/episodic.js",
  "./memory/semantic.js",
  "./memory/procedural.js",
  "./vendor/web-llm/web-llm.js",
  "./vendor/pdfjs/pdf.min.mjs",
  "./vendor/pdfjs/pdf.worker.min.mjs",
  "./vendor/tesseract/tesseract.esm.min.js",
  "./vendor/tesseract/worker.min.js",
  "./vendor/tesseract/core/tesseract-core-simd-lstm.wasm.js",
  "./vendor/tesseract/core/tesseract-core-lstm.wasm.js",
  "./vendor/tessdata/deu.traineddata.gz",
  "./vendor/tessdata/eng.traineddata.gz",
  "./vendor/tessdata/vie.traineddata.gz",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  // Nur eigene, lesende Anfragen bedienen — Modell-Downloads etc. durchreichen
  if (event.request.method !== "GET" || url.origin !== self.location.origin) return;
  event.respondWith(
    caches.match(event.request, { ignoreSearch: true }).then((hit) => {
      if (hit) return hit;
      return fetch(event.request).then((resp) => {
        if (resp.ok) {
          const kopie = resp.clone();
          caches.open(CACHE).then((cache) => cache.put(event.request, kopie));
        }
        return resp;
      });
    })
  );
});
