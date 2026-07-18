# WebLLM

Dieser Ordner wird von `npm run build:vendor` befüllt.

Enthält die Laufzeitdateien aus `node_modules/@mlc-ai/web-llm/dist/`:
- `webllm.mjs` (oder `index.js`)
- Worker/WASM-Dateien

## Befüllen

```bash
npm install
npm run build:vendor
```

## Manuell

```bash
xcopy /E /I node_modules\@mlc-ai\web-llm\dist vendor\webllm\
```
