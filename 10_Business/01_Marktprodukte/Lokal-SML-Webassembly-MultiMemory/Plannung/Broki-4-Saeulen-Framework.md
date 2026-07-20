# Broki AI — 4-Säulen-Framework („Adaptive Resilience Strategy")

*Stand: 19.07.2026 · Strategisches Framework für Produktarchitektur und Roadmap-Priorisierung.*

## Das Konzept

Vier Fähigkeiten, die zusammen einem System sowohl absolute Stabilität als auch
extreme Flexibilität verleihen:

```
                  ┌─────────────────────────────────────────┐
                  │       ADAPTIVE RESILIENCE STRATEGY       │
                  └────────────────────┬────────────────────┘
          ┌────────────────────────────┼────────────────────────────┐
          ▼                            ▼                            ▼
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│    CONTINUITY    │         │    RESILIENCE    │         │     AGILITY      │
│  (Überleben)     │         │  (Widerstand)    │         │ (Geschwindigkeit)│
└─────────┬────────┘         └─────────┬────────┘         └─────────┬────────┘
          │                            │                            │
          └────────────────────────────┼────────────────────────────┘
                                       ▼
                             ┌──────────────────┐
                             │   ADAPTABILITY   │
                             │  (Evolution)     │
                             └──────────────────┘
```

- **Continuity** sichert das Jetzt — die KI ist immer verfügbar.
- **Resilience** schützt vor dem Unerwarteten — Angriffe, Fehlbedienung, Datenleck.
- **Agility** bewegt das System im Hier und Jetzt — Kontextwechsel in Echtzeit.
- **Adaptability** verändert das System für die Zukunft — lernt aus Nutzung.

## Mapping auf Broki AI — Ist-Stand vs. Roadmap

Ehrlich geführt (Prinzip aus dem Sicherheits-Konzept: nie mehr behaupten als
gebaut). Stand 19.07.2026, Code in `Produkt/broki-extension/`.

### 1. Continuity — größtenteils GEBAUT ✅
| Feature | Status | Wo im Code |
|---|---|---|
| Multi-LLM-Fallback (native → WebLLM → wllama → Cloud) | ✅ gebaut | `modules/llm-gateway.js` |
| deviceMemory-Stufen (OOM-Schutz statt Absturz) | ✅ gebaut | `llm-gateway.js::modellStufe()` |
| Crash-Rollback (Formulareingaben überleben Absturz) | ✅ gebaut | `modules/crash-rollback.js` |
| Offline-Cache für wiederkehrende Antworten (L1/L2) | ✅ gebaut | `modules/memory-manager.js` |

### 2. Resilience — TEILWEISE, Kernstück offen ⚠️
| Feature | Status | Wo im Code |
|---|---|---|
| Signaturprüfung des RAG-Index (ECDSA, fail-closed) | ✅ gebaut | `modules/tailscale-sync.js` |
| Privat-Modus / RAM-Tresor (keine Persistenz) | ✅ gebaut | `modules/private-vault.js` |
| **Prompt-Injection-Schutz** (Indirect Injection über Webseiten filtern) | ❌ Roadmap | — |
| **Data-Leakage-Guard** (PII/Passwort/Kreditkarte automatisch maskieren, bevor Prompt den Browser Richtung LLM verlässt) | ❌ Roadmap | — |

→ Nächster sinnvoller Baustein für dieses Framework: Data-Leakage-Guard, weil
er das stärkste Vertrauensargument für Kanzleien/Praxen ist (Mandantendaten-Schutz
auch bei Cloud-Fallback-Modus).

### 3. Agility — NICHT gebaut ❌
| Feature | Status | Wo im Code |
|---|---|---|
| Dynamic Prompting (erkennt Website-Typ, wechselt Modus: Code/CRM/Vertrieb) | ❌ Roadmap | — |
| Micro-UI via Shadow-DOM (UI direkt in Ziel-Webseite einblenden) | ❌ Roadmap | — |

→ Aktuell läuft Broki NUR als Side Panel (`sidebar/sidebar.html`), nicht als
In-Page-Overlay. Das Content-Script (`content/content-script.js`) beobachtet
nur Formularfelder für Rollback — erkennt noch keinen Seiten-/Aufgabentyp.
Voraussetzung für die Landingpage-Aussage „proaktiver Agent, der im
Hintergrund mitarbeitet": genau dieser Baustein.

### 4. Adaptability — Fundament gebaut, Lernschleife offen ⚠️
| Feature | Status | Wo im Code |
|---|---|---|
| 3-Stufen-Gedächtnis wird mit Nutzung schneller (L1/L2-Cache wächst) | ✅ gebaut | `modules/memory-manager.js` |
| **Hermes-Lernschleife** (User-Korrektur → gespeicherte Regel, RLHF im Kleinen) | ❌ Roadmap | — |
| **RAG-on-the-fly** (Wiki-Rescan bei Richtlinien-Änderung, ohne Neu-Training) | ❌ Roadmap (Tailscale-Sync liefert aktuell nur periodische Voll-Updates vom Pi, kein Live-Scan) | `modules/tailscale-sync.js` |

## Priorisierung (Vorschlag)

1. **Resilience: Data-Leakage-Guard** — stärkstes Vertrauensargument, technisch
   überschaubar (Regex/Heuristik-Filter vor `gateway.antworten()`).
2. **Adaptability: Hermes-Lernschleife (Explizites Feedback)** — kleinste
   Ausbaustufe des im Businessplan beschriebenen Hermes-Patterns, direkt an
   `memory-manager.js` andockbar.
3. **Agility: Website-Typ-Erkennung** — Voraussetzung für „proaktiver Agent"-
   Versprechen der Landingpage; braucht Content-Script-Erweiterung (Heuristik
   auf Domain/DOM-Struktur, kein neues Berechtigungsproblem).
4. **Agility: Shadow-DOM Micro-UI** — größter UI-Umbau, danach.
5. **Resilience: Prompt-Injection-Schutz** — technisch anspruchsvoller
   (Absicherung gegen indirekte Injektion aus Seiteninhalt), eher Phase 2.

## Verwandt

- `SKILL_Broki-Extension.md` (02_Fähigkeiten/Aktiv) — Arbeitswissen zur Extension
- `Sicherheit-Compliance-Konzept-Broki.md` — Zero-Trust/DSGVO-Rahmen, in den
  Resilience-Bausteine einzuordnen sind
- Landingpage-Sektion „Hermes-Pattern" (`Produkt/broki-landingpage/index.html`)
  verspricht bereits explizites/implizites Feedback + lokales Fine-Tuning —
  Priorität 2 oben ist der erste Schritt, das Versprechen einzulösen
