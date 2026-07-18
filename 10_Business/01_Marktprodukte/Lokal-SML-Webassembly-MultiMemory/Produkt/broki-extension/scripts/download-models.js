import https from "https";
import http from "http";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const modelsDir = path.resolve(root, "vendor", "modelle");

const MODELS = [
  {
    id: "qwen2.5-1.5b-instruct-q4_k_m",
    url: "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
    sizeMB: 1100
  },
  {
    id: "qwen2.5-0.5b-instruct-q4_k_m",
    url: "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf",
    sizeMB: 500
  }
];

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith("https") ? https : http;
    const req = client.get(url, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        return download(res.headers.location, dest).then(resolve, reject);
      }
      if (res.statusCode !== 200) {
        return reject(new Error(`HTTP ${res.statusCode} für ${url}`));
      }
      const file = fs.createWriteStream(dest);
      res.pipe(file);
      file.on("finish", () => file.close(() => resolve(dest)));
    });
    req.on("error", reject);
  });
}

async function main() {
  if (!fs.existsSync(modelsDir)) fs.mkdirSync(modelsDir, { recursive: true });

  for (const m of MODELS) {
    const dest = path.join(modelsDir, m.id + ".gguf");
    if (fs.existsSync(dest)) {
      console.log(`[download-models] ${m.id} bereits vorhanden, überspringe.`);
      continue;
    }
    console.log(`[download-models] Lade ${m.id} (~${m.sizeMB} MB) ...`);
    try {
      await download(m.url, dest);
      console.log(`[download-models] ${m.id} gespeichert unter ${dest}`);
    } catch (e) {
      console.error(`[download-models] Fehler bei ${m.id}:`, e.message);
    }
  }
}

main();
