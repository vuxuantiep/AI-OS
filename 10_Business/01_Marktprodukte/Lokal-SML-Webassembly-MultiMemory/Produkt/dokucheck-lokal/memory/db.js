/* DocuCheck Local — IndexedDB-Wrapper (vanilla, ohne Bibliothek).
   DB "docucheck", Stores:
     dokumente : {id, name, zeichen, ts, text, chunks[]}   → Semantic Memory
     chunks    : reserviert für v0.3 (Embeddings je Chunk)  → RAG Memory
     analysen  : {id, ts, docName, aktion, frage, modell, antwort} → Episodic Memory
     routinen  : {id, name, prompt, ts}                     → Procedural/Skill Memory
     session   : {key, value}                               → Working/Tool Memory */

const DB_NAME = "docucheck";
const DB_VERSION = 1;
let dbPromise = null;

export function openDB() {
  if (dbPromise) return dbPromise;
  dbPromise = new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains("dokumente")) {
        db.createObjectStore("dokumente", { keyPath: "id", autoIncrement: true });
      }
      if (!db.objectStoreNames.contains("chunks")) {
        const s = db.createObjectStore("chunks", { keyPath: "id", autoIncrement: true });
        s.createIndex("docId", "docId");
      }
      if (!db.objectStoreNames.contains("analysen")) {
        db.createObjectStore("analysen", { keyPath: "id", autoIncrement: true });
      }
      if (!db.objectStoreNames.contains("routinen")) {
        db.createObjectStore("routinen", { keyPath: "id", autoIncrement: true });
      }
      if (!db.objectStoreNames.contains("session")) {
        db.createObjectStore("session", { keyPath: "key" });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
  return dbPromise;
}

function txDone(tx) {
  return new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.onabort = () => reject(tx.error);
  });
}

export async function dbPut(store, value) {
  const db = await openDB();
  const tx = db.transaction(store, "readwrite");
  const req = tx.objectStore(store).put(value);
  await txDone(tx);
  return req.result; // Schlüssel (bei autoIncrement die neue id)
}

export async function dbGet(store, key) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const req = db.transaction(store).objectStore(store).get(key);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export async function dbGetAll(store) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const req = db.transaction(store).objectStore(store).getAll();
    req.onsuccess = () => resolve(req.result || []);
    req.onerror = () => reject(req.error);
  });
}

export async function dbDelete(store, key) {
  const db = await openDB();
  const tx = db.transaction(store, "readwrite");
  tx.objectStore(store).delete(key);
  await txDone(tx);
}

/* Working/Tool Memory: einfache Key-Value-Ablage */
export async function sessionSet(key, value) {
  await dbPut("session", { key, value });
}

export async function sessionGet(key) {
  const row = await dbGet("session", key);
  return row ? row.value : undefined;
}
