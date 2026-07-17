/* Episodic Memory — DocuCheck Local Analyse-Verlauf */
import { dbPut, dbGetAll, dbDelete } from "./db.js";

export async function saveAnalyse({ docName, aktion, frage, modell, antwort }) {
  return dbPut("analysen", {
    ts: Date.now(),
    docName,
    aktion,
    frage: frage || null,
    modell,
    antwort,
  });
}

export async function listAnalysen(limit = 15) {
  const all = await dbGetAll("analysen");
  all.sort((a, b) => b.ts - a.ts);
  return all.slice(0, limit);
}

export async function deleteAnalyse(id) {
  await dbDelete("analysen", id);
}
