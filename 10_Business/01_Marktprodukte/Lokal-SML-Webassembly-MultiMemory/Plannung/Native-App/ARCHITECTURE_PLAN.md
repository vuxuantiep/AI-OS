# Architektur-Plan: Souveränes ChatGPT-Local (React Native / Expo)

Dieses Dokument beschreibt die Architektur für die mobile Gateway-App, die als "Brücke" zwischen lokaler On-Device-Inferenz, privaten Heim-Servern (Tailscale/Cloudflare) und Cloud-APIs dient.

## 1. Lokale Inferenz (On-Device)
Damit die App komplett offline oder im Flugmodus funktioniert, binden wir kleine Modelle (wie Google Gemma 2B oder Llama 3 3B) direkt ein.
*   **Technologie:** In React Native / Expo nutzen wir Wrapper wie `react-native-llama` (welches auf `llama.cpp` basiert) oder die offiziellen SDKs von MLC Chat, um direkt auf die NPU/GPU des Smartphones (Apple Neural Engine oder Qualcomm Hexagon) zuzugreifen.
*   **Vorteil:** Die Daten verlassen das Smartphone niemals. Akkuverbrauch wird durch Hardware-Beschleunigung (Metal auf iOS, Vulkan auf Android) optimiert.
*   **Ordnerstruktur:** Die Logik liegt unter `/src/core/llm/LocalModelProvider.ts`.

## 2. Der Dynamische Inferenz-Router (Tailscale / Cloudflare Tunnel)
Das Kernstück (USP) der App. Der Nutzer tippt auf "Senden", und die App entscheidet millisekundenschnell, wo der Prompt verarbeitet wird.
*   **Ablauf:** 
    1. Der `NetworkMonitor` prüft, ob eine W-LAN oder Mobilfunk-Verbindung besteht.
    2. Die App pingt über eine private Tailscale-IP (z.B. `100.x.x.x`) oder einen Cloudflare Tunnel Endpoint den heimischen Ollama-Server an.
    3. Antwortet der Server schnell (< 200ms), wird der Prompt dorthin geroutet.
    4. Ist der Server offline (oder dauert es zu lange), schaltet der Router sofort auf `LOCAL_ON_DEVICE` um.
*   **Zero-Friction-Setup:** Über einen QR-Code aus dem Trace AI-OS Web-Dashboard scannt die App einmalig die Tailscale-IPs und API-Keys ab und speichert sie verschlüsselt im SecureStorage des Smartphones.
*   **Ordnerstruktur:** Definiert im Interface `/src/core/routing/DynamicInferenceRouter.ts`.

## 3. Lokales RAG & Gedächtnis (SQLite / Vector DB)
Um echten Kontext zu bieten, ohne Privatsphäre aufzugeben, muss das Gedächtnis (Retrieval-Augmented Generation) lokal bleiben.
*   **Speicherung:** Alle Chats, importierten PDFs und Notizen werden lokal in einer SQLite-Datenbank (z.B. `expo-sqlite`) gespeichert.
*   **Vektorisierung:** Wir nutzen ein leichtgewichtiges, lokales Embedding-Modell (z.B. `MiniLM` kompiliert für mobile Endgeräte), um Vektoren aus Texten zu generieren.
*   **Vector Search:** Vektoren können mit Bibliotheken wie `sqlite-vss` oder reiner Vektor-Mathematik in JavaScript/C++ direkt in der App durchsucht werden. Wenn eine Frage gestellt wird, lädt die App den relevanten Kontext lokal aus der DB und hängt ihn (als RAG) an den Prompt an – egal ob dieser dann an den lokalen oder entfernten Server geschickt wird.
*   **Ordnerstruktur:** Die Datenbank- und Embedding-Logik befindet sich unter `/src/core/storage/` und `/src/core/rag/`.

## Vorgeschlagene Expo-Ordnerstruktur

\`\`\`text
/mobile-expo-architecture
├── App.tsx                    # Haupteinstiegspunkt der Expo-App
├── app.json                   # Expo Konfiguration
├── babel.config.js
├── src/
│   ├── core/                  # Herzstück der App (Inferenz & Logik)
│   │   ├── llm/               # Schnittstellen zu Llama.cpp / Ollama / OpenAI
│   │   │   ├── LocalModelProvider.ts
│   │   │   └── RemoteModelProvider.ts
│   │   ├── routing/           # Der unsichtbare Gateway-Router
│   │   │   ├── DynamicInferenceRouter.ts  <-- (Erstellt)
│   │   │   └── NetworkMonitor.ts
│   │   ├── rag/               # Retrieval-Augmented Generation (Embeddings)
│   │   │   ├── EmbeddingGenerator.ts
│   │   │   └── VectorSearch.ts
│   │   └── storage/           # Expo SQLite, SecureStore für API-Keys
│   │       ├── DatabaseProvider.ts
│   │       └── KeyManager.ts
│   ├── ui/                    # UI-Komponenten (React Native / NativeWind)
│   │   ├── screens/           # ChatScreen, SettingsScreen, QRScannerScreen
│   │   └── components/        # ChatBubble, MicrophoneButton, ModelStatusIndicator
│   └── hooks/                 # React Hooks für Audio-Recording & DB-Zustand
│       └── useInferenceRouter.ts
\`\`\`
