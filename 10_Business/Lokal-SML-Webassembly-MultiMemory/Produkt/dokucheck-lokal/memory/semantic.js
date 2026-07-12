/* Semantic + RAG Memory — Dokumente samt Chunks persistieren.
   Chunks liegen v0.2 im Dokument-Datensatz; der separate "chunks"-Store
   ist für v0.3 reserviert (Embeddings je Chunk). */
import { dbPut, dbGet, dbGetAll, dbDelete } from "./db.js";

export async function saveDokument(name, text, chunks) {
  // Gleichnamiges Dokument ersetzen (eine Quelle der Wahrheit pro Name)
  const alle = await dbGetAll("dokumente");
  const alt = alle.find((d) => d.name === name);
  if (alt) await dbDelete("dokumente", alt.id);
  return dbPut("dokumente", {
    ...(alt ? { id: alt.id } : {}),
    name,
    zeichen: text.length,
    ts: Date.now(),
    text,
    chunks,
  });
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
  await dbDelete("dokumente", id);
}
