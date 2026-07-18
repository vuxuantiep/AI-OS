// =============================================================================
// Broki AI — Dreistufige Memory-Logik (alles in der Browser-IndexedDB)
//
//   Level 1 (Exact Match):    identische Frage → Antwort in ~0 ms aus Cache
//   Level 2 (Semantic Cache): ähnliche Frage (Cosine ≥ Schwelle) → Cache-Antwort
//   Level 3 (Local RAG):      Top-K aus den Wiki-Vektoren, die der
//                             Tailscale-Sync vom Pi geladen hat
//
// Wichtig: Level 1/2 speichern NIE im Privat-Modus (siehe private-vault) und
// Level 3 verweigert die Arbeit, wenn der Index gesperrt wurde (Sync-Modul).
// =============================================================================

import { BROKI_CONFIG } from "../config/broki-config.js";
import { sha256Hex } from "./crypto-utils.js";
import { dbGet, dbPut, dbAlle, dbLoeschen } from "./db.js";
import { TailscaleSync } from "./tailscale-sync.js";

export class MemoryManager {
  /**
   * @param {(text: string) => Promise<number[]>} embedFn — liefert das
   *   Embedding einer Frage. Kommt vom LLM-Gateway (wllama-Embedding-Modell
   *   oder WebLLM), damit Memory und Motor dieselbe Vektorwelt teilen.
   */
  constructor(embedFn) {
    this.embed = embedFn;
    this.cfg = BROKI_CONFIG.memory;
  }

  /** Normalform der Frage: Groß/klein, Satzzeichen, Mehrfach-Leerzeichen weg —
   *  „Wie beantrage ich Urlaub?" und „wie beantrage ich urlaub" sind EIN Key. */
  static normalisiere(frage) {
    return frage.toLowerCase()
      .replace(/[^\p{L}\p{N}\s]/gu, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  static cosine(a, b) {
    let dot = 0, na = 0, nb = 0;
    for (let i = 0; i < a.length; i++) { dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
    const nenner = Math.sqrt(na) * Math.sqrt(nb);
    return nenner === 0 ? 0 : dot / nenner;
  }

  // ---------------------------------------------------------------------------
  // ABFRAGE-KASKADE: L1 → L2 → L3. Gibt entweder eine fertige Cache-Antwort
  // zurück ODER den RAG-Kontext, mit dem das LLM-Gateway antworten soll.
  // ---------------------------------------------------------------------------
  async frageAbrufen(frage) {
    const hash = await sha256Hex(new TextEncoder().encode(MemoryManager.normalisiere(frage)));

    // --- Level 1: Exact Match (0 ms) ----------------------------------------
    const l1 = await dbGet("l1_exact", hash);
    if (l1 && this._nochGueltig(l1)) {
      return { quelle: "L1-exact", antwort: l1.antwort, belege: l1.belege };
    }

    // --- Level 2: Semantic Cache --------------------------------------------
    const vektor = await this.embed(frage);
    const cacheEintraege = await dbAlle("l2_semantic");
    let bester = null;
    for (const e of cacheEintraege) {
      if (!this._nochGueltig(e)) continue;
      const sim = MemoryManager.cosine(vektor, e.vektor);
      if (sim >= this.cfg.l2SchwelleCosine && (!bester || sim > bester.sim)) {
        bester = { ...e, sim };
      }
    }
    if (bester) {
      return { quelle: "L2-semantic", antwort: bester.antwort,
               belege: bester.belege, aehnlichkeit: bester.sim };
    }

    // --- Level 3: Local RAG (Wiki-Vektoren vom Pi) --------------------------
    if (await TailscaleSync.istGesperrt()) {
      return { quelle: "gesperrt",
               fehler: "Der Wissens-Index ist gesperrt (Signaturprüfung "
                     + "fehlgeschlagen). Bitte IT informieren." };
    }
    const chunks = await dbAlle("l3_rag");
    if (chunks.length === 0) {
      return { quelle: "leer", fehler: "Noch kein Wissens-Index geladen "
             + "(erster Tailscale-Sync steht aus?)." };
    }
    const bewertet = chunks
      .map(c => ({ ...c, sim: MemoryManager.cosine(vektor, c.vektor) }))
      .sort((a, b) => b.sim - a.sim)
      .slice(0, this.cfg.ragTopK);

    return {
      quelle: "L3-rag",
      kontext: bewertet.map(c => ({ text: c.text, chunkId: c.chunkId, sim: c.sim })),
      frageHash: hash,
      frageVektor: vektor
    };
  }

  // ---------------------------------------------------------------------------
  // NACH der LLM-Antwort: Ergebnis in L1 + L2 zurückschreiben, damit die
  // nächste (gleiche/ähnliche) Frage ohne Inferenz beantwortet wird.
  // privatModus=true → NICHTS speichern (flüchtige Sitzung).
  // ---------------------------------------------------------------------------
  async antwortMerken({ frageHash, frageVektor, antwort, belege, privatModus }) {
    if (privatModus) return;
    const jetzt = Date.now();
    await dbPut("l1_exact", { frageHash, antwort, belege, zeit: jetzt });
    await dbPut("l2_semantic", { vektor: frageVektor, antwort, belege, zeit: jetzt });
    await this._l2Deckeln();
  }

  _nochGueltig(eintrag) {
    return (Date.now() - eintrag.zeit) < this.cfg.l1TtlStunden * 3600 * 1000;
  }

  /** L2 klein halten: älteste Einträge raus, sobald das Limit reißt. */
  async _l2Deckeln() {
    const alle = await dbAlle("l2_semantic");
    if (alle.length <= this.cfg.l2MaxEintraege) return;
    const zuLoeschen = alle.sort((a, b) => a.zeit - b.zeit)
      .slice(0, alle.length - this.cfg.l2MaxEintraege);
    for (const e of zuLoeschen) await dbLoeschen("l2_semantic", e.id);
  }
}
