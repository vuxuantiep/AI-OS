/* DokuCheck Lokal — WebLLM-Engine im Web Worker (WebLLM 0.2.79, lokal gevendort).
   Netzwerk-Requests dieses Workers erscheinen NICHT in der Performance-Timeline
   des Hauptthreads — deshalb meldet ein eigener Observer sie per BroadcastChannel
   an die Beweis-Leiste der UI. */
import { WebWorkerMLCEngineHandler } from "./vendor/web-llm/web-llm.js";

const netChannel = new BroadcastChannel("dokucheck-net");
const netObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.initiatorType === "fetch" || entry.initiatorType === "xmlhttprequest") {
      netChannel.postMessage({ kind: "net", url: entry.name });
    }
  }
});
netObserver.observe({ entryTypes: ["resource"] });

const handler = new WebWorkerMLCEngineHandler();
onmessage = (msg) => handler.onmessage(msg);
