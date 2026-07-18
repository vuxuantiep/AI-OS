# wllama

Dieser Ordner wird von `npm run build:vendor` befüllt.

Enthält die Laufzeitdateien aus `node_modules/@wllama/wllama/dist/`:
- `index.js`
- `single-thread/wllama.wasm`
- `multi-thread/wllama.wasm`

## Befüllen

```bash
npm install
npm run build:vendor
```

## Manuell

```bash
xcopy /E /I node_modules\@wllama\wllama\dist vendor\wllama\
```
