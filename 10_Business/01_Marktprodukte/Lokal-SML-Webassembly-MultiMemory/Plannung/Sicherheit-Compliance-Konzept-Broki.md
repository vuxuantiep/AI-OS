# 🔐 Broki AI — Sicherheits- & Compliance-Konzept

> Erstellt 18.07.2026 (CEO-Anforderung: Zero-Trust, Access Control, Signatur/
> Private Key, Auditierbarkeit, EU AI Act, NIS2, BSI-/ISO-Zertifizierung).
> Verwandt: [[Architektur-Broki-Extension]] (§4 Sicherheits-Entscheidungen, §5c IP-Schutz),
> [[wirtschaftlichkeit-broki-ai]]. Ehrlichkeits-Regel: Zertifizierungen sind ZIEL,
> nicht abgeschlossen — nie als „zertifiziert" darstellen, nur „auditierbar/vorbereitet".

## 1. Sicherheits-Säulen (was schon gebaut ist)

| Säule | Umsetzung | Status |
|---|---|---|
| **Integrität (Signatur/Private Key)** | ECDSA-P256 über SHA-256; jedes Wissenspaket signiert, Extension verifiziert vor dem Entpacken (`sign_utils.py` / `crypto-utils.js`). Private Key bleibt beim Kunden. | ✅ gebaut + E2E bewiesen |
| **Zero-Trust-Datenhaltung** | 100 % lokal im Browser (IndexedDB); keine Daten verlassen das Gerät. „Kein Vertrauen nötig, weil nichts rausgeht." | ✅ Kernarchitektur |
| **Access Control (rollenbasiert)** | Pi-Index partitioniert nach Rolle (mitarbeiter/admin/…); Zero-Trust-Partner erhalten nur gefilterten Wissensteil, nie System-Zugang. | ✅ Rollen im Index-Builder, Partner = Ausbau |
| **Manipulationsschutz** | Signaturfehler → Index sofort gesperrt (fail closed, Data-Poisoning-Schutz). | ✅ gebaut |
| **Vertraulichkeit lokal** | AES-GCM für das Crash-Rollback-Journal (at rest). | ✅ gebaut |
| **Kopierschutz** | Lizenz-Wächter (signiertes, domain-gebundenes Zertifikat schaltet UI/RAG frei). | 🔜 v1 (nutzt Signaturkette) |

## 2. Auditierbarkeit (Anforderung: prüfbar für Revision/Betriebsrat)

- **Nachvollziehbarkeit:** Antworten nennen ihre Quelle (Chunk-ID/Dokument) —
  jede KI-Aussage ist auf ein Wiki-Dokument rückführbar (kein Blackbox-Halluzinieren).
- **Prüfbares Datenschutz-Versprechen:** Netzwerk-Beweisleiste (wie DokuCheck) —
  in der Browser-Netzwerk-Konsole ist sichtbar, dass nichts nach außen geht.
- **Audit-Log (zu bauen):** optionales lokales, signiertes Ereignis-Log
  (Index-Sync, Lizenz-Prüfung, Rollen-Wechsel) für IT-Revision — append-only,
  ohne Inhalts-Daten (nur Metadaten). → Backlog v1.1.
- **Betriebsrat-Konformität:** keine Prompt-/Nutzer-Übermittlung, keine
  Leistungskontrolle — Konformitätserklärung als PDF (Landingpage-Asset).

## 3. Regulatorische Ausrichtung (ZIEL, in Vorbereitung)

| Rahmen | Broki-Bezug | Realistische Einordnung |
|---|---|---|
| **DSGVO** | lokal, keine Verarbeitung durch uns, AVV minimal (wir sehen keine Kundendaten) | erfüllbar by design — stärkstes Argument |
| **EU AI Act** | Broki = begrenztes Risiko (Assistenz, kein High-Risk-Automatismus); Transparenzpflichten (KI-Kennzeichnung, Quellen) erfüllt | ausrichtbar; Klassifizierung dokumentieren |
| **NIS2** | „auditierbar" — Broki reduziert Angriffsfläche (keine Cloud-Exfiltration); relevant für Betreiber, nicht für Broki selbst als Produkt | unterstützend, nicht Broki-Pflicht |
| **BSI-Grundschutz** | Sicherheitskonzept an BSI-Bausteinen ausrichten (Krypto, Zugriff, Protokollierung) | Ziel, mehrmonatig, Phase 2 |
| **ISO 27001** | ISMS-Vorbereitung; für Solo-Anbieter teuer/langwierig | Ziel Phase 2/Enterprise, NICHT Jahr 1 |

## 4. Ehrlichkeits-/Marketing-Regeln (Prüfer)

1. **Nie „zertifiziert" behaupten**, solange kein Zertifikat vorliegt — nur
   „auditierbar", „ausgerichtet an", „vorbereitet für". (Auf /broki bereits so umgesetzt
   + Fußnote.) Abmahn- und Haftungsschutz.
2. **Zertifizierung = Kostenfaktor** (BSI/ISO 4-/5-stellig, Monate) → erst wenn
   zahlende Kunden es verlangen (Enterprise Phase 2), nicht in die Startkalkulation.
3. **Vertrauens-Anker, kein Feature-Wettlauf:** Der Verkaufswert ist „lokal =
   kein Datenabfluss" (technisch beweisbar), nicht ein Stapel Siegel.

## 5. Backlog (abgeleitete Bau-Aufgaben)

- [ ] Lizenz-Wächter (v1) — signiertes Firmen-Lizenz-Zertifikat schaltet UI/RAG frei.
- [ ] Signiertes lokales Audit-Log (append-only, Metadaten) — v1.1.
- [ ] EU-AI-Act-Risikoklassifizierung + Transparenz-Doku (1 Seite) — vor Verkauf.
- [ ] Betriebsrat-Konformitätserklärung (PDF, rechtlich prüfen) — Landingpage-Asset.
- [ ] BSI-/ISO-Vorbereitung als Enterprise-Phase-2-Paket (nicht Jahr 1).
