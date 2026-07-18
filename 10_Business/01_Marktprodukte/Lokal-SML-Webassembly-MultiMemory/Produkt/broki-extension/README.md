# 🤖 Broki AI — Browser-Extension (Manifest V3)

Lokaler KI-Wiki-Assistent: Firmen-Wiki + Berater, 100 % im Browser.
Sync vom Raspberry Pi über Tailscale, dreistufiges Gedächtnis, agnostisches
LLM-Gateway, privater Tresor, IT-Crash-Rollback.
**Architektur (Diagramme):** `../../Plannung/Architektur-Broki-Extension.md`
**Businessplan:** `../../Plannung/Businessplanung und Produkt Konzept der Broki AI.docx`

## Schnellstart

```bash
npm install
npm run build:vendor
npm run download:models
```

Danach Chrome/Edge → `chrome://extensions` → Entwicklermodus → **„Entpackt laden"**
→ diesen Ordner wählen. Sidebar öffnet per Klick aufs Icon.

## Was `npm run build:vendor` macht

Kopiert die Laufzeitdateien aus `node_modules` in `vendor/`:
- `vendor/webllm/` — WebLLM (WebGPU-Inferenz)
- `vendor/wllama/` — wllama (WebAssembly/CPU-Inferenz)
- `vendor/modelle/` — GGUF-Modelle (werden von `download:models` befüllt)

## Ohne Pi testen

`sync-jetzt` über die Sidebar-Konsole schicken → Status „offline" ist korrekt,
solange kein Pi antwortet; die Frage-Kaskade meldet dann sauber
„Noch kein Wissens-Index geladen". Signatur-/Sperrlogik lässt sich mit einem
lokalen Python-Server + absichtlich falscher Signatur durchspielen
(Erwartung: 🚫-Banner in der Sidebar, L3 verweigert).

## Cloud-Fallback testen

In `config/broki-config.js` eintragen:
```javascript
cloud: {
  endpoint: "https://api.openai.com/v1/chat/completions",
  apiKey: "DEIN_API_KEY",
  modell: "gpt-4o-mini"
}
```

Sidebar → Modus „☁️ Cloud" wählen → Frage stellen.

## Features

- 🧠 Dreistufiges Gedächtnis (L1 Exact → L2 Semantic → L3 RAG)
- 🔒 Privat-Modus (RAM-Sandbox, kein Sync, kein Persistenz)
- 🛟 Crash-Rollback (AES-GCM-Journal + Heartbeat-Erkennung)
- 🔐 Manipulationsschutz (ECDSA-P256 über SHA-256)
- 🎨 Hell/Dunkel-Modus
- 🖥️ Lokal / Cloud-Umschalter
