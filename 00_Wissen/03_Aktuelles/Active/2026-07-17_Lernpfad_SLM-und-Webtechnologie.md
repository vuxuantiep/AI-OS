# 🎓 Lernpfad: Webtechnologie & SLM (Small Language Models)

#wichtig #lernen #slm #webtechnologie

> Lern-Hub für das Thema. Rohmaterial liegt im Wiki, die destillierten Erkenntnisse
> kommen HIER rein — nur diese Markdown-Notiz landet im RAG-Gedächtnis der KI-Fabrik.

## 📎 Rohmaterial (Wiki)

- [[Aktuelle-Arten von MEMORY in COGNITIVE AGENTS und SLM und WEBASSEMBLY.pdf]]
  (liegt in `00_Wissen/04_Referenzen/Wiki/`)
- Weitere PDFs/Videos/Screenshots → ebenfalls nach `00_Wissen/04_Referenzen/Wiki/` legen
  und hier verlinken.

## 🧠 Kernkonzepte (beim Lesen füllen)

### Memory-Arten in Cognitive Agents
<!-- Short-Term / Long-Term / Episodic / Semantic / Procedural — Definition + je 1 Beispiel aus dem eigenen AI-OS -->

### SLM (Small Language Models)
<!-- Was zählt als SLM? Kandidaten für lokalen Einsatz (Ollama/Pi)? Abgrenzung zu LLM -->

### WebAssembly / Browser-KI
<!-- WASM-Runtime für Modelle im Browser — Bezug: DokuCheck Lokal nutzt WebLLM 0.2.79 -->

## 🔗 Bezug zum eigenen AI-OS

- Memory-Schichten-Modell existiert schon: `06_Gedächtnis/` (Short/Long/Episodic — Struktur da, Inhalte leer)
- Browser-SLM in Produktion: [[project_dokucheck-lokal|DokuCheck Lokal]] (WebLLM im Browser)
- Lokale SLMs: Ollama-Modelle (deepseek-coder 776 MB = kleinstes) + geplantes miniLLM auf dem Pi

## ❓ Offene Fragen

- Welche Memory-Art fehlt unserem Agent-System am meisten?
- Lohnt ein SLM auf dem Pi für einen konkreten Agenten-Task?

## ✅ Gelernt / Erledigt

- [ ] PDF durcharbeiten, Kernkonzepte oben füllen
- [ ] 1 Experiment ableiten (z. B. Episodic Memory für einen Agenten)
