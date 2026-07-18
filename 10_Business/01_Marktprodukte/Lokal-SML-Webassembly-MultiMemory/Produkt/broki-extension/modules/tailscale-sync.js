// =============================================================================
// Broki AI — Tailscale-Sync & Manipulationsschutz
//
// Holt periodisch den rollenbasierten RAG-Vektorindex vom Raspberry Pi über
// das Tailscale-Netz (MagicDNS). Transportverschlüsselung übernimmt Tailscale
// (WireGuard) — dieses Modul kümmert sich um DATENINTEGRITÄT:
// jedes Paket wird per ECDSA-über-SHA-256 gegen den Firmen-Public-Key
// verifiziert. Schlägt das fehl → lokaler Index wird SOFORT gesperrt
// (fail closed: lieber keine Antwort als eine vergiftete Antwort).
// =============================================================================

import { BROKI_CONFIG } from "../config/broki-config.js";
import { verifiziereSignatur, sha256Hex } from "./crypto-utils.js";
import { dbPut, dbLeeren } from "./db.js";

export class TailscaleSync {
  constructor() {
    this.cfg = BROKI_CONFIG.pi;
    this.publicKey = BROKI_CONFIG.firmenPublicKeySpkiB64;
  }

  /** Registriert den periodischen Sync (MV3: chrome.alarms statt setInterval —
   *  der Service Worker darf jederzeit schlafen gelegt werden). */
  static registriereAlarm() {
    chrome.alarms.create("broki-sync", {
      periodInMinutes: BROKI_CONFIG.pi.syncIntervallMinuten,
      delayInMinutes: 1
    });
  }

  /** Ist der lokale Index gesperrt? (nach fehlgeschlagener Signaturprüfung) */
  static async istGesperrt() {
    return (await chrome.storage.local.get("indexGesperrt")).indexGesperrt === true;
  }

  async _sperren(grund) {
    console.error("[Broki/Sync] INDEX GESPERRT:", grund);
    await chrome.storage.local.set({
      indexGesperrt: true,
      indexSperrGrund: grund,
      indexSperrZeit: new Date().toISOString()
    });
    // Der ganzen Extension Bescheid geben (Sidebar zeigt Warnbanner).
    chrome.runtime.sendMessage({ typ: "index-gesperrt", grund }).catch(() => {});
  }

  async _entsperren() {
    await chrome.storage.local.set({ indexGesperrt: false, indexSperrGrund: null });
  }

  /**
   * Ein kompletter Sync-Lauf:
   * 1. Manifest vom Pi holen (Version, Rolle, Dateiliste, Signaturen)
   * 2. Nur bei neuer Version weitermachen (Bandbreite sparen)
   * 3. Jede Partition laden → Signatur verifizieren → erst DANN übernehmen
   * Im Privat-Modus wird gar nicht erst synchronisiert (siehe private-vault).
   */
  async sync() {
    const { isPrivateMode } = await chrome.storage.session.get("isPrivateMode");
    if (isPrivateMode) {
      console.log("[Broki/Sync] Privat-Modus aktiv — Sync übersprungen.");
      return { status: "privat-modus" };
    }

    const rolle = (await chrome.storage.local.get("rolle")).rolle
      || BROKI_CONFIG.standardRolle;

    let manifest;
    try {
      const resp = await fetch(this.cfg.basisUrl + this.cfg.manifestPfad
        + "?rolle=" + encodeURIComponent(rolle), { cache: "no-store" });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      manifest = await resp.json();
    } catch (e) {
      // Pi nicht erreichbar (Laptop unterwegs, Tailscale aus) ist KEIN
      // Sicherheitsfall — alter Index bleibt nutzbar, nächster Alarm probiert es.
      console.warn("[Broki/Sync] Pi nicht erreichbar:", e.message);
      return { status: "offline" };
    }

    const lokaleVersion = (await chrome.storage.local.get("indexVersion")).indexVersion;
    if (manifest.version === lokaleVersion && !(await TailscaleSync.istGesperrt())) {
      return { status: "aktuell", version: lokaleVersion };
    }

    // --- Partitionen laden und verifizieren ---------------------------------
    const neueChunks = [];
    for (const datei of manifest.dateien) {
      let paket;
      try {
        const resp = await fetch(this.cfg.basisUrl + datei.pfad, { cache: "no-store" });
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        paket = await resp.arrayBuffer();
      } catch (e) {
        console.warn("[Broki/Sync] Abbruch, Partition fehlt:", datei.pfad, e.message);
        return { status: "unvollstaendig" };  // alter Index bleibt gültig
      }

      // >>> Kern des Manipulationsschutzes <<<
      const ok = await verifiziereSignatur(paket, datei.signatur, this.publicKey);
      if (!ok) {
        await this._sperren(
          `Signaturprüfung fehlgeschlagen für ${datei.pfad} `
          + `(SHA-256: ${await sha256Hex(paket)})`);
        return { status: "gesperrt" };
      }

      // Paketformat: JSON-Zeilen { chunkId, partition, text, vektor:[…] }
      const zeilen = new TextDecoder().decode(paket).trim().split("\n");
      for (const zeile of zeilen) neueChunks.push(JSON.parse(zeile));
    }

    // --- Atomar übernehmen: erst wenn ALLE Partitionen verifiziert sind ------
    await dbLeeren("l3_rag");
    for (const chunk of neueChunks) await dbPut("l3_rag", chunk);
    await chrome.storage.local.set({
      indexVersion: manifest.version,
      indexRolle: rolle,
      indexStand: new Date().toISOString()
    });
    await this._entsperren();

    console.log(`[Broki/Sync] Index ${manifest.version} übernommen `
      + `(${neueChunks.length} Chunks, Rolle: ${rolle}).`);
    return { status: "aktualisiert", version: manifest.version, chunks: neueChunks.length };
  }
}
