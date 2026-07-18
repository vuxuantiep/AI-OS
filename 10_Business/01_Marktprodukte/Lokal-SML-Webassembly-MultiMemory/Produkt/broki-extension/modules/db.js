// =============================================================================
// Broki AI — schlanker IndexedDB-Wrapper (Promises statt Callback-Hölle)
// Eine DB "broki" mit vier Stores:
//   l1_exact    — Level 1: identische Fragen (Key = Normalform-Hash)
//   l2_semantic — Level 2: Frage-Embeddings + Antworten (Semantic Cache)
//   l3_rag      — Level 3: Wiki-Vektor-Partitionen vom Pi (rollenbasiert)
//   journal     — Crash-Rollback-Protokoll (verschlüsselt)
// =============================================================================

import { BROKI_CONFIG } from "../config/broki-config.js";

const DB_VERSION = 1;
let _db = null;

export function oeffneDb() {
  if (_db) return Promise.resolve(_db);
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(BROKI_CONFIG.memory.dbName, DB_VERSION);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains("l1_exact"))
        db.createObjectStore("l1_exact", { keyPath: "frageHash" });
      if (!db.objectStoreNames.contains("l2_semantic"))
        db.createObjectStore("l2_semantic", { keyPath: "id", autoIncrement: true });
      if (!db.objectStoreNames.contains("l3_rag")) {
        const s = db.createObjectStore("l3_rag", { keyPath: "chunkId" });
        s.createIndex("partition", "partition", { unique: false });
      }
      if (!db.objectStoreNames.contains("journal")) {
        const s = db.createObjectStore("journal", { keyPath: "id", autoIncrement: true });
        s.createIndex("seite", "seite", { unique: false });
      }
    };
    req.onsuccess = () => { _db = req.result; resolve(_db); };
    req.onerror = () => reject(req.error);
  });
}

/** Eine Transaktion als Promise — tx(store, "readonly", cb) */
export async function tx(storeName, modus, arbeit) {
  const db = await oeffneDb();
  return new Promise((resolve, reject) => {
    const t = db.transaction(storeName, modus);
    const store = t.objectStore(storeName);
    const ergebnis = arbeit(store);
    t.oncomplete = () => resolve(ergebnis?.result !== undefined ? ergebnis.result : ergebnis);
    t.onerror = () => reject(t.error);
  });
}

export const dbGet = (store, key) =>
  tx(store, "readonly", s => s.get(key)).then(r => r);
export const dbPut = (store, wert) =>
  tx(store, "readwrite", s => s.put(wert));
export const dbAlle = (store) =>
  tx(store, "readonly", s => s.getAll()).then(r => r);
export const dbLeeren = (store) =>
  tx(store, "readwrite", s => s.clear());
export const dbLoeschen = (store, key) =>
  tx(store, "readwrite", s => s.delete(key));
