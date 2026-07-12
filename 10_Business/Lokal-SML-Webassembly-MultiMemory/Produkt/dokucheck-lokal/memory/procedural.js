/* Procedural + Skill Memory — wiederverwendbare Prüfroutinen (Prompt-Vorlagen). */
import { dbPut, dbGetAll, dbDelete } from "./db.js";

export async function listRoutinen() {
  const all = await dbGetAll("routinen");
  all.sort((a, b) => a.name.localeCompare(b.name, "de"));
  return all;
}

export async function saveRoutine({ id, name, prompt }) {
  return dbPut("routinen", { ...(id ? { id } : {}), name, prompt, ts: Date.now() });
}

export async function deleteRoutine(id) {
  await dbDelete("routinen", id);
}

export async function exportRoutinenJSON() {
  const all = await listRoutinen();
  return JSON.stringify(all.map(({ name, prompt }) => ({ name, prompt })), null, 2);
}

export async function importRoutinenJSON(text) {
  const daten = JSON.parse(text);
  if (!Array.isArray(daten)) throw new Error("Erwartet wird ein JSON-Array aus {name, prompt}.");
  let n = 0;
  for (const r of daten) {
    if (r && typeof r.name === "string" && typeof r.prompt === "string") {
      await saveRoutine({ name: r.name, prompt: r.prompt });
      n++;
    }
  }
  return n;
}

/* Startpaket beim ersten Öffnen — zeigt sofort, was Routinen sind. */
const DEFAULTS = [
  {
    name: "Fristen-Check",
    prompt: "Liste alle Fristen, Termine und Stichtage aus dem Dokument auf. Nenne zu jeder Frist die Textstelle und was passiert, wenn sie verpasst wird.",
  },
  {
    name: "Kündigungs-Check",
    prompt: "Prüfe alle Regelungen zu Kündigung und Widerruf: Fristen, Form (schriftlich?), automatische Verlängerungen. Zitiere die relevanten Stellen.",
  },
  {
    name: "Kosten-Check",
    prompt: "Liste alle Kosten, Gebühren, Zahlungspflichten und mögliche Preiserhöhungen auf. Markiere versteckte oder ungewöhnliche Kostenklauseln.",
  },
];

export async function ensureDefaults() {
  const all = await dbGetAll("routinen");
  if (all.length > 0) return;
  for (const r of DEFAULTS) await saveRoutine(r);
}
