#!/usr/bin/env python3
"""Broki Pi — Signatur-Werkzeuge (ECDSA P-256, WebCrypto-kompatibel).

KRITISCHES DETAIL: Der Browser prüft die Signatur mit
    crypto.subtle.verify({name:"ECDSA", hash:"SHA-256"}, key, sig, data)
und erwartet die Signatur im IEEE-P1363-Format (r||s, je 32 Byte = 64 Byte roh).
Pythons `cryptography` erzeugt aber DER-kodierte Signaturen. Ohne Umwandlung
schlägt die Browser-Verifikation IMMER fehl. Deshalb konvertieren wir hier
DER → P1363. Der Public Key wird als SPKI/DER (Base64) exportiert — genau das
Format, das crypto.subtle.importKey("spki", …) erwartet.
"""
import base64
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils as asym_utils


def schluessel_erzeugen(ziel_dir: Path):
    """Erzeugt ein ECDSA-P256-Schlüsselpaar. Privat bleibt auf dem Pi,
    Public (SPKI/Base64) wandert in broki-config.js der Extension."""
    ziel_dir.mkdir(parents=True, exist_ok=True)
    privat_pfad = ziel_dir / "firma_privat.pem"
    if privat_pfad.exists():
        privat = serialization.load_pem_private_key(privat_pfad.read_bytes(), password=None)
    else:
        privat = ec.generate_private_key(ec.SECP256R1())
        privat_pfad.write_bytes(privat.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()))
    pub_spki_b64 = base64.b64encode(privat.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo)).decode()
    return privat, pub_spki_b64


def lade_privat(ziel_dir: Path):
    return serialization.load_pem_private_key(
        (ziel_dir / "firma_privat.pem").read_bytes(), password=None)


def signiere(privat, daten: bytes) -> str:
    """ECDSA-Signatur über SHA-256(daten), zurück als Base64 im P1363-Format
    (r||s, 64 Byte) — direkt von crypto.subtle.verify im Browser prüfbar."""
    der = privat.sign(daten, ec.ECDSA(hashes.SHA256()))
    r, s = asym_utils.decode_dss_signature(der)
    p1363 = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    return base64.b64encode(p1363).decode()


def verifiziere_lokal(privat, daten: bytes, signatur_b64: str) -> bool:
    """Gegenprobe rein in Python (P1363 → DER → verify). Der echte Beweis der
    Browser-Kompatibilität läuft zusätzlich über test_signatur (WebCrypto)."""
    roh = base64.b64decode(signatur_b64)
    r = int.from_bytes(roh[:32], "big")
    s = int.from_bytes(roh[32:], "big")
    der = asym_utils.encode_dss_signature(r, s)
    try:
        privat.public_key().verify(der, daten, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False
