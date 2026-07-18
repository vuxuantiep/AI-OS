# 🤖 Broki AI — Browser-Extension (Manifest V3)

Lokaler KI-Wiki-Assistent: Firmen-Wiki + Berater, 100 % im Browser.
Sync vom Raspberry Pi über Tailscale, dreistufiges Gedächtnis, agnostisches
LLM-Gateway, privater Tresor, IT-Crash-Rollback.
**Architektur (Diagramme):** `../../Plannung/Architektur-Broki-Extension.md`
**Businessplan:** `../../Plannung/Businessplanung und Produkt Konzept der Broki AI.docx`

## Einrichten (Entwicklung)

1. **Firmenschlüssel erzeugen** (auf einer vertrauenswürdigen Maschine):
   ```bash
   openssl ecparam -name prime256v1 -genkey -noout -out firma.key      # bleibt auf dem Pi!
   openssl ec -in firma.key -pubout -outform DER | base64 -w0          # → in broki-config.js
   ```
2. `config/broki-config.js`: Public Key eintragen, Pi-URL prüfen
   (Standard: `http://pi-ki-tiep.tailed32d1.ts.net:8088`), Firmen-Domains setzen
   (auch in `manifest.json` unter `content_scripts.matches`).
3. **Vendor befüllen** (noch offen, siehe Architektur-Plan Punkt 6):
   `vendor/webllm/` (npm `@mlc-ai/web-llm`), `vendor/wllama/` (npm `@wllama/wllama`),
   `vendor/modelle/` (GGUF, z. B. qwen2.5-1.5b-instruct-q4_k_m).
4. Chrome/Edge → `chrome://extensions` → Entwicklermodus → **„Entpackt laden"**
   → diesen Ordner wählen. Sidebar öffnet per Klick aufs Icon.

## Pi-Gegenstück (eigenes Arbeitspaket)

Der Pi liefert unter `:8088`:
- `GET /index/manifest.json?rolle=<r>` → `{ version, dateien: [{pfad, signatur}] }`
- `GET /index/<partition>.bin` → JSON-Zeilen `{chunkId, partition, text, vektor}`
Signatur: ECDSA-P256 über SHA-256 des Pakets, mit `firma.key`.

## Testen ohne Pi

`sync-jetzt` über die Sidebar-Konsole schicken → Status „offline" ist korrekt,
solange kein Pi antwortet; die Frage-Kaskade meldet dann sauber
„Noch kein Wissens-Index geladen". Signatur-/Sperrlogik lässt sich mit einem
lokalen Python-Server + absichtlich falscher Signatur durchspielen
(Erwartung: 🚫-Banner in der Sidebar, L3 verweigert).
