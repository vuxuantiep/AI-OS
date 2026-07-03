# AI Factory V3 — Finale Architektur 🏭

> **Datum:** 27.06.2026
> **Status:** ✅ Aktiv (Abgelöst: AI-OS V2)

---

## 🧠 Der grosse Architekturwechsel

**Von tool-zentriert → rollenbasiert.**

In V2 wurde die Architektur um einzelne Tools herum geplant (LiteLLM, LangGraph, Qdrant, etc.).  
In **V3 planen wir um Rollen herum**. KI-Modelle wie Claude Code, OpenHands, GLM 5.2 oder GPT-5.5 sind austauschbare "Mitarbeiter", die einer klar definierten Rolle zugewiesen werden.

**Vorteile:**
- ✅ Anbieterunabhängigkeit
- ✅ Bessere Wartbarkeit
- ✅ Klare Verantwortlichkeiten
- ✅ Einfacheres Onboarding neuer Modelle

---

## 🏛️ Die 4 Layer

### 1. 👑 AI MANAGEMENT (`management/`)

Die Führungsebene der AI Factory.

| Rolle | Verantwortung |
|-------|--------------|
| **CEO** | Strategie, Vision, Roadmap, Priorisierung |
| **CTO** | Technologie-Entscheidungen, Architektur, Tech-Stack |
| **Project Manager** | Sprint-Planung, Aufgabenverteilung, Meilensteine |
| **Auditor** | Qualitätsaudits, Compliance, Architektur-Reviews |

### 2. 🤖 AGENT ORGANIZATION (`agents/`)

Spezialisierte KI-Rollen, die Aufgaben ausführen.

| Rolle | Verantwortung |
|-------|--------------|
| **Developer** | Code-Generierung, Code-Reviews, Refactoring |
| **Research** | Technologierecherche, Machbarkeitsstudien |
| **Marketing** | Content-Erstellung, SEO, Social Media |
| **Security** | Pentesting, Threat Modeling, Sicherheitsaudits |
| **QA** | Testautomatisierung, E2E-Tests, Qualitätssicherung |
| **Memory** | Wissensmanagement, Embeddings, Vektorsuche |
| **DevOps** | CI/CD, Deployment, Monitoring, Infrastruktur |

### 3. 🏭 AI FACTORY OS (`platform/`)

Die technische Plattform, auf der die Rollen operieren.

| Komponente | Zweck |
|------------|-------|
| **LiteLLM** | LLM-Gateway & Provider-Routing |
| **LangGraph** | Workflow-Orchestrierung & Agenten-Graphen |
| **FastAPI** | REST-API-Server |
| **MCP** | Model Context Protocol (Tool-Integration) |
| **Qdrant** | Vektor-Datenbank für semantische Suche |
| **Postgres** | Relationale Datenbank |
| **MinIO** | S3-kompatibler Object Storage |
| **Redis** | Cache & Message Queue |
| **Tailscale** | Sicheres Networking (VPN/Mesh) |
| **Docker** | Containerisierung |
| **Cloudflare** | DNS, CDN, Workers |
| **Terraform** | Infrastructure as Code |

### 4. 📦 BUSINESS PROJECTS (`projects/`)

Konkrete Geschäftsanwendungen, die auf der Factory aufbauen.

| Projekt | Beschreibung |
|---------|-------------|
| **YouTube Factory** | Automatisierte YouTube-Kanal-Produktion |
| **AIVO GEO** | Geodaten-basierte KI-Anwendung |
| **Trade Research** | Marktforschung & Handelsanalyse |
| **Corporate LLM** | Massgeschneiderte LLM-Lösung für Unternehmen |
| **Playground** | Experimentierumgebung für neue Ideen |

---

## 📁 Verzeichnisstruktur (Übersicht)

```
ai-factory/
├── management/          👑 Strategie & Führung
├── agents/              🤖 Spezialisierte KI-Rollen
├── platform/            🏭 Infrastruktur & Services
├── projects/            📦 Geschäftsanwendungen
├── docs/                📚 Dokumentation & Architektur
├── config/              ⚙️ Konfigurationen
├── knowledge/           🧠 Wissensdatenbank
├── monitoring/          📊 Observability
├── scripts/             🔧 Automatisierung
├── tests/               🧪 Tests
├── templates/           📋 Vorlagen
└── archive/             🗄️ Historische Versionen
```

---

## 📜 Versionsgeschichte

| Version | Beschreibung | Datei |
|---------|-------------|-------|
| V2 | Tool-zentrierte Architektur (AI-OS) | `AI-OS-V2.png` |
| V3-0 | Erster rollenbasierter Entwurf | `AI-OS-V3-0.png` |
| V3-1 | Verfeinerte rollenbasierte Architektur | `Verzeichnis-struktur.png` |
| **V3** 🏆 | **Finale rollenbasierte Architektur** | `AI-OS-V3.png` + diese Beschreibung |
