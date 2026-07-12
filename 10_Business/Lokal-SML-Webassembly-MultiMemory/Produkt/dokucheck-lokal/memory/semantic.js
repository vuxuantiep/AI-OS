/* Semantic + RAG Memory — DocuCheck Local Dokumente + Chunks.
   Chunks ({text, reihe, start, end}) liegen im Dokument-Datensatz UND
   separat im "chunks"-Store (Basis für v0.3-Embeddings je Chunk). */
import { dbPut, dbGet, dbGetAll, dbDelete, openDB } from "./db.js";

async function loescheChunksVonDoc(docId) {
  const db = await openDB();
  const tx = db.transaction("chunks", "readwrite");
  const store = tx.objectStore("chunks");
  const alte = await new Promise((resolve) => {
    const req = store.index("docId").getAll(docId);
    req.onsuccess = () => resolve(req.result || []);
    req.onerror = () => resolve([]);
  });
  for (const c of alte) store.delete(c.id);
  await new Promise((resolve, reject) => {
    tx.oncomplete = resolve;
    tx.onerror = () => reject(tx.error);
  });
}

export async function saveDokument(name, text, chunks) {
  // Gleichnamiges Dokument ersetzen (eine Quelle der Wahrheit pro Name)
  const alle = await dbGetAll("dokumente");
  const alt = alle.find((d) => d.name === name);
  if (alt) {
    await loescheChunksVonDoc(alt.id);
    await dbDelete("dokumente", alt.id);
  }
  const docId = await dbPut("dokumente", {
    ...(alt ? { id: alt.id } : {}),
    name,
    zeichen: text.length,
    ts: Date.now(),
    text,
    chunks,
  });

  // Chunks separat speichern für RAG-Light (v0.3+ Embeddings)
  if (chunks && chunks.length) {
    const db = await openDB();
    const tx = db.transaction("chunks", "readwrite");
    const store = tx.objectStore("chunks");
    for (let i = 0; i < chunks.length; i++) {
      const { text: chunkText, reihe, start, end } = chunks[i];
      store.put({
        docId,
        text: chunkText,
        reihe: reihe || i + 1,
        start,
        end,
        ts: Date.now(),
      });
    }
    await new Promise((resolve, reject) => {
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error);
    });
  }

  return docId;
}

export async function listDokumente() {
  const all = await dbGetAll("dokumente");
  all.sort((a, b) => b.ts - a.ts);
  // Ohne Volltext zurückgeben — die Liste soll leicht bleiben
  return all.map(({ id, name, zeichen, ts }) => ({ id, name, zeichen, ts }));
}

export async function loadDokument(id) {
  return dbGet("dokumente", id);
}

export async function deleteDokument(id) {
  await loescheChunksVonDoc(id);
  await dbDelete("dokumente", id);
}
