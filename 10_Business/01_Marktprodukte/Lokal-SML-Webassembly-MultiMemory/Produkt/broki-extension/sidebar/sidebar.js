// =============================================================================
// Broki AI — Sidebar-UI: Chat, Tresor-Schalter, Sperr-Banner, Rollback-Dialog.
// Bewusst dünn: ALLE Logik lebt im Service Worker, die Sidebar redet nur
// über den Message-Bus (typ/nutzlast, siehe background.js).
// =============================================================================

const chat = document.getElementById("chat");
const banner = document.getElementById("banner");
const statusZeile = document.getElementById("status");
const privatCheckbox = document.getElementById("privat");
const themeToggle = document.getElementById("themeToggle");
const modeSelect = document.getElementById("modeSelect");

// 4-Säulen-Framework (Continuity/Resilience/Agility/Adaptability) — zeigt
// bewusst nur, was WIRKLICH läuft. Details: Plannung/Broki-4-Saeulen-Framework.md
const saeuleContinuity = document.getElementById("saeule-continuity");
const saeuleResilience = document.getElementById("saeule-resilience");
const saeuleAdaptability = document.getElementById("saeule-adaptability");

const sende = (msg) => chrome.runtime.sendMessage(msg);

function zeige(text, wer, meta) {
  const div = document.createElement("div");
  div.className = "msg" + (wer === "ich" ? " ich" : "");
  div.textContent = text;
  if (meta) {
    const m = document.createElement("div");
    m.className = "meta"; m.textContent = meta;
    div.appendChild(m);
  }
  chat.appendChild(div);
  div.scrollIntoView({ block: "end" });
}

// --- Design: Hell / Dunkel ------------------------------------------------------
function toggleTheme() {
  const aktuell = document.body.classList.contains("dark");
  const neu = !aktuell;
  document.body.classList.toggle("dark", neu);
  chrome.storage.local.set({ brokiTheme: neu ? "dark" : "light" });
}
themeToggle.addEventListener("click", toggleTheme);

(async () => {
  const { brokiTheme } = await chrome.storage.local.get("brokiTheme");
  if (brokiTheme === "dark") document.body.classList.add("dark");
})();

// --- KI-Modus: Lokal / Cloud ----------------------------------------------------
modeSelect.addEventListener("change", async () => {
  const modus = modeSelect.value; // "local" | "cloud"
  await chrome.storage.local.set({ brokiMode: modus });
  statusZeile.textContent = modus === "cloud"
    ? "Modus: Cloud-Fallback (nutzt lokale Modelle, bei Fehler automatisch Cloud)"
    : "Modus: Nur lokal (WebGPU / WASM)";
  // Gateway neu initialisieren lassen, damit es den Modus beim nächsten Prompt berücksichtigt.
  await sende({ typ: "mode-wechsel", modus });
});

(async () => {
  const { brokiMode } = await chrome.storage.local.get("brokiMode");
  if (brokiMode) modeSelect.value = brokiMode;
  statusZeile.textContent = (brokiMode === "cloud")
    ? "Modus: Cloud-Fallback (nutzt lokale Modelle, bei Fehler automatisch Cloud)"
    : "Modus: Nur lokal (WebGPU / WASM)";
})();

// --- Frage stellen --------------------------------------------------------------
document.getElementById("frageForm").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const feld = document.getElementById("frage");
  const frage = feld.value.trim();
  if (!frage) return;
  feld.value = "";
  zeige(frage, "ich");
  zeige("…", "broki");
  const platzhalter = chat.lastChild;
  const antwort = await sende({ typ: "frage", frage });
  platzhalter.remove();
  if (antwort?.ok) {
    const d = antwort.daten;
    zeige(d.antwort, "broki",
      `Quelle: ${d.quelle}` + (d.aehnlichkeit ? ` (${d.aehnlichkeit.toFixed(2)})` : "")
      + (d.motor ? ` · Motor: ${d.motor}` : ""));
    if (d.motor) saeuleContinuity.textContent = d.motor;
    else if (d.quelle?.startsWith("L1") || d.quelle?.startsWith("L2"))
      saeuleContinuity.textContent = "Aus Cache — kein Motor nötig";
  } else {
    zeige("⚠️ " + (antwort?.fehler || "Unbekannter Fehler"), "broki");
  }
});

// --- Tresor-Schalter -----------------------------------------------------------
function resilienceAktualisieren() {
  saeuleResilience.textContent = "Tresor: " + (privatCheckbox.checked ? "Aktiv (RAM-only)" : "Aus");
}
privatCheckbox.addEventListener("change", () => {
  sende({ typ: "privat-modus-setzen", aktiv: privatCheckbox.checked });
  resilienceAktualisieren();
});
resilienceAktualisieren();

// --- Push-Nachrichten vom Service Worker ---------------------------------------
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.typ === "index-gesperrt") {
    banner.style.display = "block";
    banner.textContent = "🚫 Wissens-Index gesperrt (Integritätsprüfung). IT informieren!";
  }
  if (msg.typ === "rollback-verfuegbar") {
    zeige(`🛟 Es gibt ${msg.anzahl} gesicherte Eingaben von vor dem Absturz `
        + `(${msg.seiten.join(", ")}). Wiederherstellen?`, "broki");
    const knopf = document.createElement("button");
    knopf.textContent = "🛟 Jetzt wiederherstellen";
    knopf.addEventListener("click", async () => {
      const daten = await sende({ typ: "rollback-lesen" });
      if (!daten?.ok) return;
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const resultat = await chrome.tabs.sendMessage(tab.id,
        { typ: "rollback-anwenden", eintraege: daten.daten });
      zeige(`✅ ${resultat?.wiederhergestellt ?? 0} Felder wiederhergestellt.`, "broki");
      await sende({ typ: "rollback-verwerfen" });
      knopf.remove();
    });
    chat.appendChild(knopf);
  }
});

// --- Statuszeile + Adaptability-Säule --------------------------------------------
(async () => {
  const s = await sende({ typ: "sync-status" });
  if (!s?.ok) return;
  const d = s.daten;
  if (d.indexGesperrt) {
    banner.style.display = "block";
    banner.textContent = "🚫 Index gesperrt: " + (d.indexSperrGrund || "");
    saeuleAdaptability.textContent = "Gesperrt (Signaturprüfung)";
    return;
  }
  statusZeile.textContent = d.indexVersion
    ? `Index ${d.indexVersion} · Rolle ${d.indexRolle} · Stand ${String(d.indexStand).slice(0, 16)}`
    : "Noch kein Wissens-Index — warte auf ersten Tailscale-Sync.";
  saeuleAdaptability.textContent = d.indexVersion
    ? `Index ${d.indexVersion} (${String(d.indexStand).slice(0, 10)})`
    : "Warte auf ersten Sync";
})();
