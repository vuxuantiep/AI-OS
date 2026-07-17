# Usecase 2: TikTok-Shop

## Ziel
Shoppable KI-Avatar-Videos, die Produkte aus dem TikTok-Shop bewerben
(z. B. Lernkarten-Sets zu "Deutsch Dễ Hiểu"). Monetarisierung über
Shop-Provision und Affiliate-Links.

## Unterschiede zur YouTube-Pipeline

| Punkt | TikTok-Shop-Besonderheit |
|---|---|
| Skript | Produkt-Hook in den ersten 3 Sekunden, Call-to-Action auf Shop-Link |
| Caption | Werbekennzeichnung ("Werbung"/"Anzeige") **in den ersten drei Zeilen** — Pflicht bei jedem Produktlink (§5a UWG) |
| QA-Check | zusätzlich: `daily_shoppable_count` ≤ 30/Tag, sonst Block + auf morgen verschieben |
| Posting | natives TikTok-KI-Label setzen (`native_ai_label_set: true` an QA übergeben) |

## Harte Regeln (aus Compliance-Critic-Agent)
1. Kein Video ohne sichtbares KI-Wasserzeichen (`avatar_disclosure_flag`)
2. Kein Produktlink ohne Werbekennzeichnung in den ersten 3 Caption-Zeilen
3. Keine Ergebnis-Versprechen ("garantiert fließend in 7 Tagen")
4. Max. 30 shoppable Videos/Tag pro Kanal

## KPIs (Start)
- 3–5 shoppable Videos/Tag, Conversion pro Video tracken
- Wiederholungsrate < 70 % gegenüber den letzten 3 Videos (Reichweiten-Schutz)

#ki-avatar #tiktok-shop
