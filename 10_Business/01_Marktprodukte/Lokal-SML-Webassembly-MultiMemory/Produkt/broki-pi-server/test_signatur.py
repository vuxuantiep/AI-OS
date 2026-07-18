#!/usr/bin/env python3
"""E2E-Beweis: Eine Python-signierte Partition wird mit crypto.subtle.verify
(dieselbe WebCrypto-API wie in der Broki-Extension) über Node verifiziert.
Das beweist, dass das P1363-Signaturformat und der SPKI-Public-Key browser-
kompatibel sind — der häufigste Stolperstein bei ECDSA über Sprachgrenzen.
"""
import base64
import json
import subprocess
import tempfile
from pathlib import Path

from sign_utils import schluessel_erzeugen, signiere, verifiziere_lokal

HIER = Path(__file__).parent

NODE_VERIFY = r"""
const fs = require('fs');
const { subtle } = require('crypto').webcrypto;
const inp = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const b64ToBuf = b64 => Uint8Array.from(Buffer.from(b64, 'base64'));
(async () => {
  const key = await subtle.importKey('spki', b64ToBuf(inp.pub),
    { name: 'ECDSA', namedCurve: 'P-256' }, false, ['verify']);
  const ok = await subtle.verify({ name: 'ECDSA', hash: 'SHA-256' },
    key, b64ToBuf(inp.sig), b64ToBuf(inp.data));
  const okManipuliert = await subtle.verify({ name: 'ECDSA', hash: 'SHA-256' },
    key, b64ToBuf(inp.sig), b64ToBuf(inp.dataManipuliert));
  console.log(JSON.stringify({ echt: ok, manipuliert: okManipuliert }));
})();
"""


def main():
    with tempfile.TemporaryDirectory() as tmp:
        privat, pub_b64 = schluessel_erzeugen(Path(tmp))
        daten = b'{"chunkId":"test#c0","text":"Broki Wiki-Eintrag","vektor":[0.1,0.2]}'
        sig = signiere(privat, daten)

        assert verifiziere_lokal(privat, daten, sig), "Python-Gegenprobe fehlgeschlagen"
        print("✅ Python-Gegenprobe: Signatur gültig.")

        manipuliert = daten.replace(b"Wiki-Eintrag", b"GEFAELSCHT!!")
        eingabe = {
            "pub": pub_b64,
            "sig": sig,
            "data": base64.b64encode(daten).decode(),
            "dataManipuliert": base64.b64encode(manipuliert).decode(),
        }
        inp = Path(tmp) / "inp.json"
        inp.write_text(json.dumps(eingabe))
        skript = Path(tmp) / "verify.js"
        skript.write_text(NODE_VERIFY)

        out = subprocess.run(["node", str(skript), str(inp)],
                             capture_output=True, text=True, timeout=30)
        if out.returncode != 0:
            print("❌ Node-Fehler:", out.stderr[:300])
            return 1
        res = json.loads(out.stdout)
        print(f"🌐 WebCrypto (wie im Browser): echt={res['echt']}, "
              f"manipuliert={res['manipuliert']}")
        if res["echt"] and not res["manipuliert"]:
            print("🎉 BEWEIS ERBRACHT: Browser akzeptiert die Pi-Signatur und "
                  "lehnt manipulierte Daten ab.")
            return 0
        print("❌ Format NICHT browser-kompatibel!")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
