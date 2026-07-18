// =============================================================================
// Broki AI — Content-Script (läuft NUR auf den Firmen-Domains aus dem Manifest)
//
// Aufgabe 1: Formular-/Textzustände beobachten und an den Service Worker
//            melden (IT-Crash-Rollback). Entprellt, damit nicht jeder
//            Tastendruck eine Nachricht erzeugt.
// Aufgabe 2: Nach einem Crash die Wiederherstellung ausführen, wenn die
//            Sidebar sie anfordert (Message "rollback-anwenden").
// =============================================================================

(() => {
  const ENTPRELL_MS = 1500;
  const timer = new Map();

  /** Stabile Feld-Kennung: id > name > DOM-Pfad (Fallback). */
  function feldId(el) {
    if (el.id) return "#" + el.id;
    if (el.name) return "[name=" + el.name + "]";
    const pfad = [];
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      pfad.unshift(n.tagName + ":" + [...(n.parentElement?.children || [])].indexOf(n));
    }
    return pfad.join(">");
  }

  function melden(el) {
    const wert = el.isContentEditable ? el.innerText : el.value;
    if (!wert || wert.length < 3) return;      // Leeres/Winziges lohnt nicht
    chrome.runtime.sendMessage({
      typ: "feld-zustand",
      seite: location.origin + location.pathname,
      feldId: feldId(el),
      wert
    }).catch(() => {});                        // SW schläft? Nächster Input trifft ihn.
  }

  // Ein Listener für alles Tippbare — input feuert auch bei contenteditable.
  document.addEventListener("input", (ev) => {
    const el = ev.target;
    const tippbar = el.matches?.("input[type=text], input:not([type]), textarea")
      || el.isContentEditable;
    if (!tippbar) return;
    const id = feldId(el);
    clearTimeout(timer.get(id));
    timer.set(id, setTimeout(() => melden(el), ENTPRELL_MS));
  }, true);

  // --- Wiederherstellung: Sidebar schickt die entschlüsselten Feldwerte ------
  chrome.runtime.onMessage.addListener((msg, _sender, sendeAntwort) => {
    if (msg.typ !== "rollback-anwenden") return;
    let getroffen = 0;
    for (const eintrag of msg.eintraege) {
      if (!eintrag.seite.startsWith(location.origin)) continue;
      let el = null;
      try {
        el = eintrag.feldId.startsWith("#") || eintrag.feldId.startsWith("[")
          ? document.querySelector(eintrag.feldId.startsWith("#")
              ? eintrag.feldId : "input" + eintrag.feldId + ", textarea" + eintrag.feldId)
          : null;
      } catch { /* ungültiger Selektor → überspringen */ }
      if (!el) continue;
      if (el.isContentEditable) el.innerText = eintrag.wert;
      else el.value = eintrag.wert;
      el.dispatchEvent(new Event("input", { bubbles: true }));  // Framework-Bindings wecken
      getroffen++;
    }
    sendeAntwort({ ok: true, wiederhergestellt: getroffen });
  });
})();
