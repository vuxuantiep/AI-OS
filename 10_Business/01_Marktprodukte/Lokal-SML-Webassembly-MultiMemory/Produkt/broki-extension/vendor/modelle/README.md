# GGUF-Modelle

Dieser Ordner wird von `npm run download:models` befüllt.

## Vorhandene Modelle

- `qwen2.5-1.5b-instruct-q4_k_m.gguf` — ~1,1 GB (empfohlen für 4 GB+ RAM)
- `qwen2.5-0.5b-instruct-q4_k_m.gguf` — ~500 MB (für 2 GB RAM)

## Herunterladen

```bash
npm run download:models
```

Oder manuell von HuggingFace:
- https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
- https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF

Die Dateien müssen genau so heißen wie in `broki-config.js` konfiguriert:
```javascript
{ minGb: 4, webllm: "Llama-3.2-1B-Instruct-q4f16_1-MLC", wllamaGguf: "qwen2.5-1.5b-instruct-q4_k_m.gguf" }
{ minGb: 0, webllm: "Qwen2.5-0.5B-Instruct-q4f16_1-MLC", wllamaGguf: "qwen2.5-0.5b-instruct-q4_k_m.gguf" }
```

## Hinweis

Diese Dateien sind **groß** (500 MB – 1,1 GB). Sie werden von Git LFS ignoriert,
sofern konfiguriert. Für den produktiven Einsatz solltest du Git LFS verwenden
oder die Modelle separat verteilen.
