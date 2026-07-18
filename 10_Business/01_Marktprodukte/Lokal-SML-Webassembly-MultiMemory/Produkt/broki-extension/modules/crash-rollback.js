// =============================================================================
// Broki AI — IT-Crash-Rollback („die Lebensversicherung")
//
// Das Content-Script meldet Formular-/Textzustände der Firmen-Domain an den
// Service Worker. Hier werden sie AES-GCM-verschlüsselt in der IndexedDB
// mitprotokolliert (Store "journal"). Nach einem Absturz (Browser, Rechner,
// IT-System) erkennt der nächste Start den "unsauberen" Vorlauf über ein
// Heartbeat-Flag und bietet der UI die Wiederherstellung an.
// =============================================================================

import { holeOderErzeugeJournalSchluessel, verschluesseln, entschluesseln }
  from "./crypto-utils.js";
import { dbPut, dbAlle, dbLeeren } from "./db.js";
import { PrivateVault } from "./private-vault.js";

export class CrashRollback {
  constructor() {
    this._key = null;
    this._entprellt = new Map();   // pro Seite+Feld max. 1 Schreiber je 2 s
  }

  async _schluessel() {
    if (!this._key) this._key = await holeOderErzeugeJournalSchluessel();
    return this._key;
  }

  // ---------------------------------------------------------------------------
  // Heartbeat: "sauber beendet?"-Erkennung.
  //  • Beim SW-Start: stand das Flag noch auf "läuft" → letzter Lauf endete
  //    NICHT sauber → Journal prüfen und ggf. Wiederherstellung anbieten.
  //  • chrome.runtime.onSuspend setzt das Flag auf "sauber beendet".
  // ---------------------------------------------------------------------------
  async startPruefung() {
    const { heartbeat } = await chrome.storage.local.get("heartbeat");
    const unsauber = heartbeat === "laeuft";
    await chrome.storage.local.set({ heartbeat: "laeuft" });

    if (!unsauber) return { wiederherstellbar: false };

    const eintraege = await this.alleEintraege();
    if (eintraege.length === 0) return { wiederherstellbar: false };

    console.warn(`[Broki/Rollback] Unsauberer Vorlauf erkannt — `
      + `${eintraege.length} gesicherte Feld-Zustände gefunden.`);
    return { wiederherstellbar: true, anzahl: eintraege.length,
             seiten: [...new Set(eintraege.map(e => e.seite))] };
  }

  static sauberBeenden() {
    // onSuspend ist "best effort" — genau deshalb funktioniert die Erkennung:
    // bei einem echten Crash feuert es NICHT und das Flag bleibt auf "laeuft".
    chrome.runtime.onSuspend.addListener(() => {
      chrome.storage.local.set({ heartbeat: "sauber" });
    });
  }

  // ---------------------------------------------------------------------------
  // Protokollieren (vom Content-Script via Message-Passing aufgerufen)
  // ---------------------------------------------------------------------------
  async protokolliere({ seite, feldId, wert }) {
    if (await PrivateVault.istAktiv()) return;          // Tresor: nichts loggen
    const entprellKey = seite + "::" + feldId;
    const jetzt = Date.now();
    if ((this._entprellt.get(entprellKey) || 0) > jetzt - 2000) return;
    this._entprellt.set(entprellKey, jetzt);

    const key = await this._schluessel();
    await dbPut("journal", {
      id: entprellKey,                       // pro Feld nur der LETZTE Zustand
      seite, feldId, zeit: jetzt,
      daten: await verschluesseln(key, wert)
    });
  }

  async alleEintraege() {
    const key = await this._schluessel();
    const roh = await dbAlle("journal");
    const klar = [];
    for (const e of roh) {
      try {
        klar.push({ seite: e.seite, feldId: e.feldId, zeit: e.zeit,
                    wert: await entschluesseln(key, e.daten) });
      } catch { /* einzelner kaputter Eintrag blockiert nicht den Rest */ }
    }
    return klar;
  }

  /** Nutzer hat wiederhergestellt oder verworfen → Journal leeren. */
  async verwerfen() { await dbLeeren("journal"); }
}
