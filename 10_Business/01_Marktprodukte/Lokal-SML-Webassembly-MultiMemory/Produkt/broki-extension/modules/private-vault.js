// =============================================================================
// Broki AI — Privater Tresor (isPrivateMode, Opt-Out)
//
// Grundsatz: Der Schalter lebt in chrome.storage.session — dieser Speicher
// existiert NUR im RAM des laufenden Browsers und wird beim Schließen
// automatisch und restlos verworfen. Genau das gewünschte Verhalten:
// nichts vom Privat-Modus überlebt die Sitzung.
//
// Wirkung bei isPrivateMode === true:
//   • Tailscale-Sync wird blockiert (kein Netz-Kontakt zum Pi)
//   • Memory-Level 1/2 speichern nichts (antwortMerken wird übersprungen)
//   • Crash-Rollback protokolliert nichts
//   • Drag-and-Drop-Dokumente leben nur in dieser RAM-Session-Map
// =============================================================================

export class PrivateVault {
  constructor() {
    // Flüchtige Dokumente (Drag-and-Drop im Privat-Modus): NUR im RAM des
    // Service Workers. Wird der SW beendet oder der Modus verlassen → weg.
    this._ramDokumente = new Map();
  }

  static async istAktiv() {
    return (await chrome.storage.session.get("isPrivateMode")).isPrivateMode === true;
  }

  /** Schaltet den Privat-Modus um und räumt beim Verlassen den RAM auf. */
  async setzen(aktiv) {
    await chrome.storage.session.set({ isPrivateMode: aktiv === true });
    if (!aktiv) this._ramDokumente.clear();
    // UI informieren (Sidebar zeigt den Tresor-Status als Badge).
    chrome.runtime.sendMessage({ typ: "privat-modus", aktiv: aktiv === true })
      .catch(() => {});
    console.log("[Broki/Tresor] Privat-Modus:", aktiv ? "AN (RAM-Sandbox)" : "aus");
  }

  /** Nimmt ein Drag-and-Drop-Dokument flüchtig auf (nur Privat-Modus).
   *  tabId als Schlüsselteil: Schließt der Nutzer den Tab, räumt
   *  vergissTab() alles zu diesem Tab weg. */
  ablegen(tabId, name, text) {
    const key = `${tabId}::${name}`;
    this._ramDokumente.set(key, { text, zeit: Date.now() });
    return key;
  }

  lesen(tabId) {
    const treffer = [];
    for (const [key, wert] of this._ramDokumente) {
      if (key.startsWith(tabId + "::")) treffer.push({ name: key.split("::")[1], ...wert });
    }
    return treffer;
  }

  /** Tab zu → zugehörige RAM-Dokumente restlos vergessen
   *  (wird von background.js an chrome.tabs.onRemoved gehängt). */
  vergissTab(tabId) {
    for (const key of [...this._ramDokumente.keys()]) {
      if (key.startsWith(tabId + "::")) this._ramDokumente.delete(key);
    }
  }
}
