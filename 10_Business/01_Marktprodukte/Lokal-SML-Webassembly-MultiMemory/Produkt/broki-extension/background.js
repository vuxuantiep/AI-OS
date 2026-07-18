// =============================================================================
// Broki AI — Service Worker (Manifest V3): der Orchestrator
//
// Verdrahtet alle Module und ist die EINZIGE Stelle mit Message-Bus-Logik.
// MV3-Regel Nr. 1: Der Service Worker kann jederzeit schlafen gelegt werden —
// deshalb: chrome.alarms statt Timer, Zustand in storage/IndexedDB statt
// in globalen Variablen (Ausnahme: bewusst flüchtiger RAM des Privat-Tresors).
// =============================================================================

import { TailscaleSync } from "./modules/tailscale-sync.js";
import { MemoryManager } from "./modules/memory-manager.js";
import { LLMGateway } from "./modules/llm-gateway.js";
import { PrivateVault } from "./modules/private-vault.js";
import { CrashRollback } from "./modules/crash-rollback.js";

const sync = new TailscaleSync();
const gateway = new LLMGateway();
const memory = new MemoryManager((text) => gateway.embed(text));
const tresor = new PrivateVault();
const rollback = new CrashRollback();

// --- Lebenszyklus -------------------------------------------------------------

chrome.runtime.onInstalled.addListener(() => {
  TailscaleSync.registriereAlarm();
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});
});

// Crash-Erkennung: läuft bei JEDEM Start des Service Workers.
CrashRollback.sauberBeenden();
rollback.startPruefung().then(status => {
  if (status.wiederherstellbar) {
    // UI benachrichtigen — die Sidebar zeigt den Wiederherstellen-Dialog.
    chrome.runtime.sendMessage({ typ: "rollback-verfuegbar", ...status }).catch(() => {});
  }
});

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === "broki-sync") await sync.sync();
});

// Tab zu → flüchtige Tresor-Dokumente dieses Tabs restlos vergessen.
chrome.tabs.onRemoved.addListener((tabId) => tresor.vergissTab(tabId));

// --- Message-Bus (Sidebar + Content-Scripts) ----------------------------------
// Konvention: { typ: "...", ...nutzlast } → Antwort { ok, daten | fehler }

chrome.runtime.onMessage.addListener((msg, sender, sendeAntwort) => {
  (async () => {
    switch (msg.typ) {

      // ---- Modus wechseln (Lokal / Cloud) ------------------------------------
      case "mode-wechsel":
        gateway.setModus(msg.modus);
        return { ok: true, modus: gateway.modus };

      // ---- Kern: Frage beantworten (L1 → L2 → L3 → LLM) --------------------
      case "frage": {
        const privat = await PrivateVault.istAktiv();
        const stufe = await memory.frageAbrufen(msg.frage);

        // Cache-Treffer (L1/L2) oder Fehlerzustand → direkt zurück.
        if (stufe.antwort) return { ok: true, daten: stufe };
        if (stufe.fehler) return { ok: false, fehler: stufe.fehler, quelle: stufe.quelle };

        // Privat-Modus: flüchtige RAM-Dokumente des Tabs in den Kontext mischen.
        let kontext = stufe.kontext;
        if (privat && sender.tab) {
          const ramDocs = tresor.lesen(sender.tab.id);
          kontext = [
            ...ramDocs.map((d, i) => ({ chunkId: "RAM:" + d.name, text: d.text, sim: 1 })),
            ...kontext
          ];
        }

        const antwort = await gateway.antworten(msg.frage, kontext);
        const belege = kontext.map(c => c.chunkId);
        await memory.antwortMerken({
          frageHash: stufe.frageHash, frageVektor: stufe.frageVektor,
          antwort, belege, privatModus: privat
        });
        return { ok: true, daten: { quelle: privat ? "L3-rag (privat)" : "L3-rag",
                                    antwort, belege, motor: gateway.motorName } };
      }

      // ---- Tresor ----------------------------------------------------------
      case "privat-modus-setzen":
        await tresor.setzen(msg.aktiv);
        return { ok: true };
      case "privat-dokument": {
        if (!(await PrivateVault.istAktiv()))
          return { ok: false, fehler: "Privat-Modus ist aus — Dokument nicht angenommen." };
        tresor.ablegen(sender.tab?.id ?? -1, msg.name, msg.text);
        return { ok: true };
      }

      // ---- Sync ------------------------------------------------------------
      case "sync-jetzt":
        return { ok: true, daten: await sync.sync() };
      case "sync-status": {
        const s = await chrome.storage.local.get(
          ["indexVersion", "indexStand", "indexRolle", "indexGesperrt", "indexSperrGrund"]);
        return { ok: true, daten: s };
      }

      // ---- Crash-Rollback --------------------------------------------------
      case "feld-zustand":                    // vom Content-Script
        await rollback.protokolliere(msg);
        return { ok: true };
      case "rollback-lesen":
        return { ok: true, daten: await rollback.alleEintraege() };
      case "rollback-verwerfen":
        await rollback.verwerfen();
        return { ok: true };

      default:
        return { ok: false, fehler: "Unbekannter Nachrichtentyp: " + msg.typ };
    }
  })().then(sendeAntwort)
     .catch(e => sendeAntwort({ ok: false, fehler: String(e?.message || e) }));
  return true;   // asynchrone Antwort — Kanal offen halten (MV3-Pflicht)
});
