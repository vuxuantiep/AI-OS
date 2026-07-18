#!/usr/bin/env python3
"""Broki Pi — Index-Builder: baut aus dem Firmen-Wiki den signierten,
rollenbasierten RAG-Vektorindex, den die Browser-Extension über Tailscale lädt.

Ablauf:
  1. Markdown-Dateien der Wissensquelle einlesen (Default: AI-OS 00_Wissen).
  2. In Absatz-Chunks schneiden.
  3. Embeddings LOKAL über Ollama (nomic-embed-text) erzeugen — KEINE Cloud
     (gleiche Regel wie der AI-OS-RAG: Firmenwissen verlässt das Gerät nie).
  4. Chunks je nach Rolle in Partitionen aufteilen.
  5. Jede Partition als JSON-Zeilen-Paket ECDSA-signieren.
  6. manifest.json je Rolle schreiben (Version, Dateien, Signaturen).

Aufruf:  python index_builder.py            # baut alle Rollen
         python index_builder.py --quelle <pfad>
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from sign_utils import schluessel_erzeugen, signiere

HIER = Path(__file__).parent
AI_OS_ROOT = Path(os.environ.get("AI_OS_ROOT", HIER.parents[5]))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
EMBED_MODEL = "nomic-embed-text"
DATA_DIR = HIER / "index_data"          # hier landen die auslieferbaren Pakete
KEYS_DIR = HIER / "keys"                # firma_privat.pem (NICHT versioniert!)

# Rollen → welche Unterordner der Quelle sie sehen dürfen (rollenbasierter RAG).
# "mitarbeiter" = das offizielle Wiki; "admin" = alles inkl. interner Notizen.
ROLLEN = {
    "mitarbeiter": ["00_Übersicht", "02_Fähigkeiten", "03_Aktuelles", "04_Referenzen"],
    "admin": None,   # None = keine Einschränkung (alle .md der Quelle)
}
AUSSCHLUSS = {"01_Persönlich", "node_modules", "__pycache__", ".git"}


def embed(text: str) -> list:
    payload = json.dumps({"model": EMBED_MODEL, "prompt": text}).encode()
    req = urllib.request.Request(f"{OLLAMA_URL}/api/embeddings", data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["embedding"]


def chunk_text(text: str, max_chars=1200):
    text = text.strip()
    if len(text) <= max_chars:
        return [text] if text else []
    chunks, cur = [], ""
    for absatz in text.split("\n\n"):
        if len(cur) + len(absatz) + 2 <= max_chars:
            cur = (cur + "\n\n" + absatz) if cur else absatz
        else:
            if cur:
                chunks.append(cur)
            cur = absatz[:max_chars]
    if cur:
        chunks.append(cur)
    return chunks


def sammle_dateien(quelle: Path, erlaubte_ordner):
    for pfad in quelle.rglob("*.md"):
        if AUSSCHLUSS.intersection(pfad.parts):
            continue
        if erlaubte_ordner is not None:
            rel = pfad.relative_to(quelle)
            if not rel.parts or rel.parts[0] not in erlaubte_ordner:
                continue
        yield pfad


def baue_rolle(rolle: str, quelle: Path, privat, version: str):
    erlaubte = ROLLEN[rolle]
    chunks = []
    for pfad in sammle_dateien(quelle, erlaubte):
        try:
            inhalt = pfad.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = str(pfad.relative_to(quelle))
        for i, stueck in enumerate(chunk_text(inhalt)):
            chunks.append({
                "chunkId": f"{rel}#c{i}",
                "partition": rolle,
                "text": stueck,
                "vektor": embed(stueck),
            })
    # Partition als JSON-Zeilen serialisieren (ein Chunk pro Zeile)
    paket = "\n".join(json.dumps(c, ensure_ascii=False) for c in chunks).encode("utf-8")
    datei = f"{rolle}.jsonl"
    (DATA_DIR / datei).write_bytes(paket)
    eintrag = {
        "pfad": f"/index/{datei}",
        "sha256": hashlib.sha256(paket).hexdigest(),
        "signatur": signiere(privat, paket),
        "chunks": len(chunks),
    }
    print(f"  Rolle '{rolle}': {len(chunks)} Chunks, {len(paket)//1024} KB, signiert.")
    return eintrag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quelle", default=str(AI_OS_ROOT / "00_Wissen"),
                    help="Wurzel des Firmen-Wikis (Default: AI-OS 00_Wissen)")
    args = ap.parse_args()
    quelle = Path(args.quelle)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    privat, pub_b64 = schluessel_erzeugen(KEYS_DIR)
    # Version = Hash über Quelle-Mtimes → ändert sich nur bei echten Änderungen
    stamp = hashlib.sha256(
        "".join(sorted(str(p) + str(p.stat().st_mtime)
                       for p in quelle.rglob("*.md"))).encode()).hexdigest()[:12]

    print(f"📚 Baue Broki-Index aus {quelle} (Version {stamp})")
    manifeste = {}
    for rolle in ROLLEN:
        eintrag = baue_rolle(rolle, quelle, privat, stamp)
        manifeste[rolle] = {"version": stamp, "rolle": rolle, "dateien": [eintrag]}
        (DATA_DIR / f"manifest_{rolle}.json").write_text(
            json.dumps(manifeste[rolle], ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n✅ Fertig. Öffentlicher Firmen-Schlüssel (in broki-config.js eintragen):")
    print(f"   firmenPublicKeySpkiB64: \"{pub_b64}\"")
    (DATA_DIR / "public_key.txt").write_text(pub_b64, encoding="utf-8")


if __name__ == "__main__":
    main()
