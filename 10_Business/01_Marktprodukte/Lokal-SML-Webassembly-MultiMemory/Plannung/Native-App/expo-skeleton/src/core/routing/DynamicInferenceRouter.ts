// mobile-expo-architecture/src/core/routing/DynamicInferenceRouter.ts

/**
 * Definiert die möglichen Netzwerkumgebungen des Nutzers.
 */
export type NetworkEnvironment = 'HOME_WIFI' | 'MOBILE_NETWORK' | 'OFFLINE';

/**
 * Repräsentiert einen verfügbaren Inferenz-Weg (Lokal, Heim-Server, Cloud).
 */
export interface InferenceRoute {
  id: string;
  type: 'LOCAL_ON_DEVICE' | 'REMOTE_PRIVATE_SERVER' | 'REMOTE_CLOUD';
  modelName: string;
  
  /** 
   * Prüft asynchron, ob diese Route gerade erreichbar ist (z.B. Ping an Tailscale-IP). 
   */
  isAvailable: () => Promise<boolean>;
  
  /** 
   * Geschätzte Latenz in Millisekunden. Hilft dem Router bei der Auswahl.
   */
  latencyEstimateMs?: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface InferenceRequest {
  messages: ChatMessage[];
  temperature?: number;
  maxTokens?: number;
  
  /**
   * Wenn true, wird vor der Anfrage die lokale SQLite/Vektor-DB durchsucht
   * und der Kontext (RAG) automatisch in den System-Prompt injiziert.
   */
  useRag?: boolean; 
}

export interface InferenceResponse {
  text: string;
  routeUsed: InferenceRoute;
  metrics: {
    tokensPerSecond: number;
    timeToFirstTokenMs: number;
    totalLatencyMs: number;
  };
}

/**
 * Kern-Interface des "Unsichtbaren KI-Gateway-Routers".
 * Diese Klasse entscheidet im Hintergrund, wohin der Prompt geschickt wird.
 */
export interface IDynamicInferenceRouter {
  /**
   * Analysiert die aktuelle Netzwerkverbindung (Tailscale, Cloudflare, Offline)
   * und ermittelt die optimale Route basierend auf Verfügbarkeit und Geschwindigkeit.
   */
  determineOptimalRoute(): Promise<InferenceRoute>;

  /**
   * Führt den Prompt über die optimale Route aus.
   * Muss Fallbacks unterstützen: Wenn der Heim-Server während der Anfrage
   * abbricht, wird transparent auf 'LOCAL_ON_DEVICE' gewechselt.
   */
  executePrompt(request: InferenceRequest): Promise<InferenceResponse>;

  /**
   * Erzwingt eine spezifische Route (z.B. wenn der Nutzer absolute Privacy fordert
   * und ausschließlich das lokale Handy-Modell nutzen will).
   */
  forceRoute(routeType: InferenceRoute['type']): void;
}
