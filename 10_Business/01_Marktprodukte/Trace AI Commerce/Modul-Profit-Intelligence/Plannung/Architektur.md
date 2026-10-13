# Architektur — Profit-Intelligence (Stand 13.10.2026, Konzept)

> Pflicht-Diagramm (CEO-Anweisung 17.07.2026). Bei jeder Änderung mitpflegen.

## Komponenten

```mermaid
flowchart LR
    subgraph Quellen["Datenquellen (nur zulässige)"]
        CSV[CSV-Import]
        MAN[Manuelle Recherche<br/>Lieferantenangebote]
        SPAPI[Amazon SP-API<br/>Phase 4]
        TT[TikTok Shop Partner-API<br/>später]
    end

    subgraph AIOS["AI-OS (Bestand)"]
        NR[Node-RED / Scheduler]
        subgraph BE["backend/ FastAPI :8000 — Modul profit_intelligence"]
            DISC[Discovery<br/>Dubletten]
            MR[Market Research<br/>Quelle + Alter je Zahl]
            PE[Profit Engine<br/>Decimal, deterministisch]
            RC[Risk & Compliance<br/>harte Ausschlussregeln]
            DA[Decision Assistant<br/>Bericht + Datenlücken]
        end
        DB[(DB: products, listings,<br/>observations, supplier_offers,<br/>cost_profiles, profit_runs,<br/>purchase_decisions, audit_events)]
        LLM[LiteLLM :4000]
        DASH[Dashboard :5000<br/>Tab Profit-Intelligence]
    end

    CEO((CEO-Freigabe))

    CSV --> DISC
    MAN --> DISC
    SPAPI -.-> MR
    TT -.-> MR
    NR --> DISC
    DISC --> MR --> PE --> RC --> DA
    DA --> LLM
    DISC & MR & PE & RC & DA --> DB
    DB --> DASH
    DASH --> CEO
    CEO -->|Entscheidung unveränderlich| DB
```

## Entscheidungsablauf

```mermaid
flowchart TD
    A[Produkt erfassen] --> B{Quelle & Nutzungsrecht ok?}
    B -- Nein --> X[Verwerfen]
    B -- Ja --> C{Daten ausreichend?}
    C -- Nein --> D[Lücken markieren<br/>manuelle Recherche anfordern] --> C
    C -- Ja --> E[Markt & Preis analysieren]
    E --> F[Kosten + 3 Szenarien berechnen]
    F --> G{Harte Ausschlussregel?<br/>Stress-DB < 0, Marke gesperrt,<br/>Compliance unbekannt}
    G -- Ja --> X2[Ablehnen / sperren]
    G -- Nein --> H[Risiko + Datenqualität bewerten]
    H --> I[Produktbericht]
    I --> J{Menschliche Freigabe}
    J -- Nein --> K[Beobachten / ablehnen]
    J -- Ja --> L[Menge + Begründung dokumentieren]
    L --> M[Ist-Verkäufe zurückführen] --> F
```

## Grenzen (Sicherheit)

- Keine Bestellungen, keine Schreibzugriffe aufs Verkäuferkonto im MVP.
- Secrets nur in zentraler `.env` / `01_Verbindungen/APIs/Geheimnisse/`.
- Externe Texte = Daten, nie Anweisungen an den LLM.
- Veraltete/fehlende Daten blockieren die Vorlage zur Freigabe.
