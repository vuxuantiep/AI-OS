import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");

const vendorDir = path.join(root, "vendor");

// =============================================================================
// 1. WebLLM nach vendor/webllm/ kopieren
// =============================================================================
// Stand 22.07.2026: @mlc-ai/web-llm liefert den Build inzwischen unter lib/,
// nicht mehr dist/ (Paket-Layout hat sich geändert, echter Breaking-Change
// gegenüber der urspruenglich dokumentierten ^0.2.78-Struktur).
const webllmSrc = path.join(root, "node_modules", "@mlc-ai", "web-llm", "lib");
const webllmDst = path.join(vendorDir, "webllm");

if (!fs.existsSync(webllmSrc)) {
  console.error("[build-vendor] @mlc-ai/web-llm/lib nicht gefunden. Hast du npm install ausgeführt?");
  process.exit(1);
}

fs.rmSync(webllmDst, { recursive: true, force: true });
fs.cpSync(webllmSrc, webllmDst, { recursive: true });
console.log("[build-vendor] WebLLM kopiert → vendor/webllm/");

// =============================================================================
// 2. wllama nach vendor/wllama/ kopieren
// =============================================================================
// Stand 22.07.2026: @wllama/wllama ist bei npm inzwischen bei Major 3.x, die
// alte ^0.8.3-Version existiert im Registry nicht mehr (404). Auf 1.0.0
// gepinnt (siehe package.json) - dessen Build liegt unter esm/, nicht dist/.
const wllamaSrc = path.join(root, "node_modules", "@wllama", "wllama", "esm");
const wllamaDst = path.join(vendorDir, "wllama");

if (!fs.existsSync(wllamaSrc)) {
  console.error("[build-vendor] @wllama/wllama/esm nicht gefunden. Hast du npm install ausgeführt?");
  process.exit(1);
}

fs.rmSync(wllamaDst, { recursive: true, force: true });
fs.cpSync(wllamaSrc, wllamaDst, { recursive: true });
console.log("[build-vendor] wllama kopiert → vendor/wllama/");

// =============================================================================
// 3. models/-Ordner sicherstellen
// =============================================================================
const modelsDir = path.join(vendorDir, "modelle");
if (!fs.existsSync(modelsDir)) fs.mkdirSync(modelsDir, { recursive: true });

const readme = path.join(modelsDir, "README.md");
if (!fs.existsSync(readme)) {
  fs.writeFileSync(readme, `# GGUF-Modelle\n\nDieser Ordner wird von scripts/download-models.js befüllt.\nModelle:\n- qwen2.5-1.5b-instruct-q4_k_m.gguf\n- qwen2.5-0.5b-instruct-q4_k_m.gguf\n`);
  console.log("[build-vendor] models/-Ordner vorbereitet");
}

console.log("[build-vendor] Fertig. Führe danach npm run download:models aus, um GGUF-Dateien zu holen.");
