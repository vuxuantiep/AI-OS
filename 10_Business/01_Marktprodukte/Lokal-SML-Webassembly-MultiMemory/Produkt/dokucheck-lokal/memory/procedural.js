/* Procedural + Skill Memory — DocuCheck Local Prüfroutinen
   (wiederverwendbare Prompt-Vorlagen, CRUD + JSON-Export/Import). */
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

/* Startpaket beim ersten Öffnen — zeigt sofort, was Routinen sind.
   Die ersten vier Namen müssen zu den Werten des "Prüfung:"-Dropdowns
   in Schritt 3 (index.html, #presetSelUse) passen. */
const DEFAULTS = [
  {
    name: "Vollprüfung (Vertrag)",
    prompt: "Du bist ein Vertragsprüfer für deutsche Verbraucherverträge. Du ersetzt keine Rechtsberatung, sollst aber Risiken, Kosten, Fristen und Kündigungsbedingungen strukturiert markieren. Analysiere den folgenden Vertragstext und gib die Antwort in vier Sektionen:\n\nZusammenfassung (maximal 10 Sätze)\nFristen (Liste mit Datum und Ereignis)\nKosten & Gebühren (Liste mit Betrag und Bedingung)\nKündigung & Verlängerung (Beschreibung der Mindestlaufzeit, Kündigungsfrist und automatischer Verlängerung).\n\nWenn Textstellen unklar sind oder durch OCR Fehler enthalten, markiere sie mit „UNKLAR“ und erfinde nichts hinzu.",
  },
  {
    name: "Mietvertrag (privat)",
    prompt: "Prüfe diesen Mietvertrag auf folgende Punkte:\n1. Kautionshöhe und Verwendung\n2. Kündigungsfristen (Mieter/Vermieter)\n3. Betriebskosten und deren Aufschlüsselung\n4. Schönheitsreparaturen\n5. Haustier-Klausel\nZitiere die relevanten Stellen. Markiere ungewöhnliche oder nachteilige Klauseln mit „UNKLAR“.",
  },
  {
    name: "Mobilfunkvertrag",
    prompt: "Prüfe diesen Mobilfunkvertrag auf folgende Punkte:\n1. Grundgebühr und Laufzeit\n2. Datenvolumen und Drosselung\n3. Kündigungsfrist und automatische Verlängerung\n4. Kosten für Sonderrufnummern, Roaming, Service\n5. Widerrufsrecht\nZitiere die relevanten Stellen. Markiere versteckte Kosten mit „UNKLAR“.",
  },
  {
    name: "Versicherungsbedingungen",
    prompt: "Prüfe diese Versicherungsbedingungen auf folgende Punkte:\n1. Versicherte Risiken und Ausschlüsse\n2. Selbstbeteiligung\n3. Kündigungsfrist und automatische Verlängerung\n4. Leistungsausschlüsse (z. B. bei grober Fahrlässigkeit)\n5. Beitragsanpassungen\nZitiere die relevanten Stellen. Markiere unklare Ausschlüsse mit „UNKLAR“.",
  },
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
