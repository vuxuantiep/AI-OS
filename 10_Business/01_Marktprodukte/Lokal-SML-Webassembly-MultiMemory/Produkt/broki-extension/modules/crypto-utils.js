// =============================================================================
// Broki AI — Krypto-Werkzeuge (Web Crypto API, keine Fremdbibliothek)
// SHA-256-Digest, ECDSA-Signaturprüfung (Index-Integrität) und AES-GCM
// (Verschlüsselung des Crash-Rollback-Journals "at rest" in der IndexedDB).
// =============================================================================

/** Base64 → ArrayBuffer (für SPKI-Key und Signaturen aus dem Manifest). */
export function b64ZuBuffer(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes.buffer;
}

/** SHA-256-Digest eines Buffers, als Hex-String (für Logs/Vergleiche). */
export async function sha256Hex(buffer) {
  const digest = await crypto.subtle.digest("SHA-256", buffer);
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, "0")).join("");
}

/**
 * Prüft die Signatur eines Index-Pakets gegen den Firmen-Public-Key.
 * Verfahren: ECDSA P-256 über das SHA-256-Digest der Daten — d. h. der Pi
 * signiert mit dem privaten Firmenschlüssel, hier wird NUR verifiziert.
 * (Ein reiner SHA-256-Vergleich ohne Signatur würde Manipulation auf dem Pi
 * nicht erkennen — der Angreifer könnte den Hash einfach mitliefern.)
 *
 * @param {ArrayBuffer} daten      das heruntergeladene Paket
 * @param {string} signaturB64     Signatur aus dem Manifest (Base64)
 * @param {string} publicKeySpkiB64 Firmen-Public-Key (SPKI, Base64)
 * @returns {Promise<boolean>}
 */
export async function verifiziereSignatur(daten, signaturB64, publicKeySpkiB64) {
  try {
    const key = await crypto.subtle.importKey(
      "spki", b64ZuBuffer(publicKeySpkiB64),
      { name: "ECDSA", namedCurve: "P-256" },
      false, ["verify"]
    );
    return await crypto.subtle.verify(
      { name: "ECDSA", hash: "SHA-256" },
      key, b64ZuBuffer(signaturB64), daten
    );
  } catch (e) {
    // Kaputter Key / kaputte Signatur = NICHT verifiziert (fail closed).
    console.error("[Broki/Krypto] Signaturprüfung technisch fehlgeschlagen:", e);
    return false;
  }
}

// --- AES-GCM für das Rollback-Journal ----------------------------------------
// Der Schlüssel wird einmalig erzeugt und in chrome.storage.local abgelegt.
// Ehrliche Einordnung: Das schützt die Daten "at rest" in der IndexedDB
// (z. B. Backup-Kopien, neugierige Tools) — NICHT gegen einen Angreifer mit
// vollem Zugriff auf dasselbe Browser-Profil. Für den Zweck (Crash-Schutz
// interner Formulardaten) ist das das richtige, ehrliche Schutzniveau.

export async function holeOderErzeugeJournalSchluessel() {
  const gespeichert = (await chrome.storage.local.get("journalKeyJwk")).journalKeyJwk;
  if (gespeichert) {
    return crypto.subtle.importKey("jwk", gespeichert,
      { name: "AES-GCM" }, false, ["encrypt", "decrypt"]);
  }
  const key = await crypto.subtle.generateKey(
    { name: "AES-GCM", length: 256 }, true, ["encrypt", "decrypt"]);
  await chrome.storage.local.set({ journalKeyJwk: await crypto.subtle.exportKey("jwk", key) });
  return crypto.subtle.importKey("jwk",
    await crypto.subtle.exportKey("jwk", key),
    { name: "AES-GCM" }, false, ["encrypt", "decrypt"]);
}

export async function verschluesseln(key, text) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const chiffrat = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv }, key, new TextEncoder().encode(text));
  return { iv: [...iv], chiffrat: [...new Uint8Array(chiffrat)] };
}

export async function entschluesseln(key, eintrag) {
  const klar = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: new Uint8Array(eintrag.iv) },
    key, new Uint8Array(eintrag.chiffrat));
  return new TextDecoder().decode(klar);
}
