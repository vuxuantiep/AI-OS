# -*- coding: utf-8 -*-
"""
Markt-Radar für LeadPilot — Lead-Generator + Marktrecherche (regional & global).

Quellen (alle öffentlich, KEINE Personendaten — nur Ausschreibungen, Stellen-
und Projektangebote von Organisationen bzw. Branchen-Zählungen):
- Arbeitsagentur Jobsuche (pc/v6): regionale Stellen = Bedarfssignal, plus
  Angebotsart "Selbständigkeit" = Freelance-/Auftragsangebote
- service.bund.de RSS: öffentliche Ausschreibungen Bund/Land/Kommune
- TED (EU-Amtsblatt, API v3): IT-Ausschreibungen mit Leistungsort Deutschland
- Arbeitnow: deutsche/remote Tech-Stellen
- (bestehend in app.py) RemoteOK / WeWorkRemotely / Remotive = global remote
- OpenStreetMap Overpass: Anzahl Praxen/Pflegedienste/Kanzleien/… je Region
  (Marktgröße, nur gezählt — keine Einzeldatensätze gespeichert)

Bewertung: gewichtete Zielsegmente (Healthcare-IT > IAM/Öffentlich/KI > KMU-
Branchen) + Regionsbonus + Typbonus (Ausschreibung/Freelance > Stelle).
Ausschluss: Praktikum/Werkstudent/Ausbildung/Minijob.

Rein stdlib, keine Host-Imports (Portabilitäts-Anforderung von LeadPilot).
"""
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

USER_AGENT = "LeadPilot-Marktradar/1.0 (+https://vuxuantiep.de)"

# --- Zielprofil ------------------------------------------------------------------
# Gewicht = wie wertvoll ein Treffer in diesem Segment für das Kombi-Modell ist.
SEGMENTE = [
    {"key": "healthcare_it", "name": "🏥 Healthcare-IT (KIS/PVS)", "gewicht": 4, "muster": [
        r"krankenhausinformationssystem", r"\bkis\b", r"\bpvs\b", r"praxisverwaltung", r"\bhl7\b", r"\bfhir\b",
        r"\borbis\b", r"\bnavis\b", r"imedone", r"\bmedico\b", r"dedalus", r"\bcgm\b", r"turbomed", r"meierhofer",
        r"telematik", r"\bti[- ]?(anbindung|konnektor)", r"konnektor", r"\bepa\b", r"\bkim\b", r"\bkhzg\b",
        r"klinik", r"krankenhaus", r"universitätsklinik", r"uniklinik", r"\bpacs\b", r"\blis\b", r"dicom",
        r"medizininformati", r"e-?health", r"gesundheitswesen", r"healthcare", r"hospital", r"\bmvz\b"]},
    {"key": "iam", "name": "🔐 IAM / Berechtigungen", "gewicht": 3, "muster": [
        r"\bentra\b", r"azure ad", r"active directory", r"\biam\b", r"identity", r"identitäts", r"berechtigungs",
        r"rollenkonzept", r"zugriffs(rechte|steuerung)", r"\bsso\b", r"single sign", r"keycloak", r"\bldap\b"]},
    {"key": "oeffentlich", "name": "🏛 Öffentlicher Sektor / eAkte", "gewicht": 3, "muster": [
        r"e-?akte", r"\bdms\b", r"behörde", r"(stadt|landes|kommunal|bundes)verwaltung", r"öffentliche verwaltung",
        r"\bozg\b", r"kommunal|kommune",r"landesamt", r"ministerium",
        r"dataport", r"öffentliche[nr]? (auftrag|sektor|dienst)", r"\bitzbund\b", r"public sector"]},
    {"key": "ki_automation", "name": "🤖 KI-Automatisierung", "gewicht": 3, "muster": [
        r"\bki\b", r"künstliche intelligenz", r"\bai\b", r"\bllm\b", r"\brag\b", r"power automate", r"\bn8n\b",
        r"automatisier", r"automation", r"chatbot", r"copilot", r"machine learning", r"prozessautomati",
        r"\brpa\b", r"workflow[- ]?automati"]},
    {"key": "integration", "name": "🔌 Integration / Schnittstellen", "gewicht": 3, "muster": [
        r"schnittstelle", r"\bapi\b", r"integration", r"middleware", r"\besb\b", r"kommunikationsserver",
        r"\borchestra\b", r"\bmirth\b", r"migration"]},
    {"key": "kmu_branchen", "name": "🏪 KMU-Zielbranchen", "gewicht": 2, "muster": [
        r"arztpraxis", r"\bpraxis\b", r"zahnarzt", r"physiotherap", r"pflegedienst", r"ambulante pflege",
        r"pflegeeinrichtung", r"steuerberat", r"kanzlei", r"\bdatev\b", r"handwerk", r"online[- ]?shop",
        r"e-?commerce", r"shopify", r"woocommerce", r"apotheke"]},
    {"key": "it_betrieb", "name": "🖥 IT-Betrieb / Support", "gewicht": 1, "muster": [
        r"system ?administrator", r"sysadmin", r"it[- ]?support", r"service ?desk", r"help ?desk",
        r"anwendungsbetreu", r"application (manager|support)", r"\bm365\b", r"microsoft 365", r"intune",
        r"netzwerk", r"windows server", r"backup", r"it[- ]?sicherheit", r"security"]},
]
SEGMENT_NAMEN = {s["key"]: s["name"] for s in SEGMENTE}

REGION_MUSTER = re.compile(
    r"rostock|hamburg|schwerin|wismar|stralsund|greifswald|güstrow|neubrandenburg|mecklenburg|vorpommern"
    r"|lübeck|kiel|schleswig|norderstedt|pinneberg|\bmv\b", re.I)
AUSSCHLUSS = re.compile(r"praktikum|praktikant|werkstudent|ausbildung zum|ausbildung als|azubi|minijob"
                        r"|internship|\bintern\b|working student|duales studium"
                        r"|sales|vertrieb|account (executive|manager)|marketing|recruit|business development", re.I)
# Ausschreibungen müssen IT-Bezug haben (sonst landet "Neubau Klinik, Putzarbeiten" im Radar)
IT_PFLICHT = re.compile(r"software|\bit[- ]|\bedv\b|informations(technik|system|sicherheit)|digital|daten"
                        r"|netzwerk|server|cloud|lizenz|hardware|schnittstelle|\bki\b|\bkis\b|\bpvs\b"
                        r"|rechenzentrum|\bm365\b|microsoft|telematik|e-?akte|\bdms\b|portal|anwendung|plattform", re.I)
# Stellen/Projekte: IT-Rolle muss im Titel bzw. Beruf erkennbar sein (sonst kommen über die
# KIS-Suche auch Pflege-/MFA-Stellen derselben Klinik rein)
IT_ROLLE = re.compile(r"software|\bit[- ]|\bedv\b|informati|developer|engineer|entwickl|administrator|\bai\b|\bki\b"
                      r"|devops|programm|daten|\bdata\b|cloud|netzwerk|system(techn|admin|betreu|engineer|integr)"
                      r"|\bkis\b|\bpvs\b|consultant|berater|architekt|architect|digital|security|it-sicherheit"
                      r"|integration|schnittstelle|it-support|anwendungsbetreu|application|identity|\biam\b"
                      r"|fhir|hl7", re.I)
BAU_AUSSCHLUSS = re.compile(r"bauarbeit|neubau|umbau|putz|dach|heizung|sanitär|wärme|abwasser|maler|tiefbau"
                            r"|gerüst|fenster|reinigung|catering|wäsche|elektrische leitungen|gebäudeautomation"
                            r"|lüftung|aufzug|möbel|fahrzeug|lebensmittel|garten|landschaft", re.I)
MIN_SCORE_STANDARD = 8

TYP_LABELS = {"ausschreibung": "📜 Ausschreibung", "freelance": "💼 Projekt/Freelance",
              "bedarfssignal": "📈 Stelle (Bedarfssignal)"}
TYP_BONUS = {"ausschreibung": 3, "freelance": 3, "bedarfssignal": 0}

# --- Arbeitsagentur-Suchen (editierbar über config "radar_ba_suchen") ------------
BA_SUCHEN_STANDARD = [
    # Regional: lokale Bedarfssignale (Praxen, Kliniken, KMU in MV/HH)
    {"was": "Krankenhausinformationssystem", "wo": "Hamburg", "umkreis": 100},
    {"was": "Krankenhausinformationssystem", "wo": "Rostock", "umkreis": 150},
    {"was": "Anwendungsbetreuer", "wo": "Rostock", "umkreis": 100},
    {"was": "Systemadministrator", "wo": "Rostock", "umkreis": 50},
    {"was": "IT-Support", "wo": "Rostock", "umkreis": 50},
    {"was": "Digitalisierung", "wo": "Rostock", "umkreis": 80},
    {"was": "Entra ID", "wo": "Hamburg", "umkreis": 50},
    {"was": "Power Automate", "wo": "Hamburg", "umkreis": 50},
    # Bundesweit: Spezialthemen (oft Homeoffice/Remote möglich)
    {"was": "HL7"}, {"was": "FHIR"}, {"was": "Berechtigungskonzept"}, {"was": "Medizininformatik"},
    # Selbständigkeit = Auftrags-/Freelance-Angebote
    {"was": "IT", "angebotsart": 2}, {"was": "Software", "angebotsart": 2}, {"was": "KI", "angebotsart": 2},
]

TED_CPV = "72000000 48000000 72200000 72500000 72600000 72300000"


def _get(url, headers=None, timeout=20, data=None):
    h = {"User-Agent": USER_AGENT}
    h.update(headers or {})
    req = urllib.request.Request(url, headers=h, data=data)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "ignore")


def _clean(s, n=1500):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
          .replace("&#252;", "ü").replace("&#228;", "ä").replace("&#246;", "ö").replace("&#220;", "Ü")
          .replace("&#196;", "Ä").replace("&#214;", "Ö").replace("&#223;", "ß"))
    return re.sub(r"\s+", " ", s).strip()[:n]


# --- Bewertung -------------------------------------------------------------------

def bewerte(item, extra_keywords=(), min_score=MIN_SCORE_STANDARD):
    """Setzt segmente, keywords, region, score. Gibt False zurück, wenn irrelevant."""
    text = (item.get("titel", "") + " " + item.get("text", "") + " " + item.get("firma", "")).lower()
    if AUSSCHLUSS.search(item.get("titel", "")):
        return False
    if item.get("typ") == "ausschreibung" and (BAU_AUSSCHLUSS.search(item.get("titel", ""))
                                              or not IT_PFLICHT.search(text)):
        return False
    if item.get("typ") != "ausschreibung" and not IT_ROLLE.search(item.get("titel", "") + " " + item.get("text", "")[:200]):
        return False
    segmente, kws, score = [], [], 0
    for s in SEGMENTE:
        hits = sorted({m.group(0).strip() for p in s["muster"] for m in [re.search(p, text)] if m})
        if hits:
            segmente.append(s["key"])
            kws += hits[:4]
            # Grundgewicht + 1 je weiterem Treffer (max +2) — Titeltreffer zählen doppelt
            titel_hit = any(re.search(p, item.get("titel", "").lower()) for p in s["muster"])
            score += s["gewicht"] + min(len(hits) - 1, 2) + (s["gewicht"] if titel_hit else 0)
    for k in extra_keywords:
        if re.search(r"(?<![a-z0-9])" + re.escape(k.lower()) + r"(?![a-z0-9])", text) and k.lower() not in kws:
            kws.append(k.lower())
            score += 1
    if not segmente and not kws:
        return False
    regional = bool(REGION_MUSTER.search(text + " " + item.get("standort", "")))
    score += 4 if regional else 0
    score += TYP_BONUS.get(item.get("typ", "bedarfssignal"), 0)
    # Kombi-Bonus: Healthcare + (IAM | Integration | KI) = genau das Wunschprofil
    if "healthcare_it" in segmente and {"iam", "integration", "ki_automation"} & set(segmente):
        score += 3
    if score < min_score:
        return False
    item["segmente"] = segmente
    item["keywords"] = kws[:10]
    item["region"] = "regional" if regional else "global"
    item["score"] = score
    return True


# --- Quellen ---------------------------------------------------------------------

def quelle_arbeitsagentur(suchen, tage=14):
    items = []
    base = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"
    for s in suchen:
        params = {"was": s["was"], "size": s.get("size", 25), "veroeffentlichtseit": tage}
        if s.get("wo"):
            params["wo"] = s["wo"]
            params["umkreis"] = s.get("umkreis", 50)
        if s.get("angebotsart"):
            params["angebotsart"] = s["angebotsart"]
        d = json.loads(_get(base + "?" + urllib.parse.urlencode(params),
                            {"X-API-Key": "jobboerse-jobsuche"}))
        for e in d.get("ergebnisliste", []):
            ref = e.get("referenznummer", "")
            orte = [l.get("adresse", {}) for l in e.get("stellenlokationen", [])]
            ort = ", ".join(sorted({o.get("ort", "") for o in orte if o.get("ort")}))[:60]
            selbst = e.get("stellenangebotsart") == "SELBSTAENDIGKEIT"
            items.append({
                "titel": e.get("stellenangebotsTitel", "")[:250],
                "url": "https://www.arbeitsagentur.de/jobsuche/jobdetail/" + urllib.parse.quote(ref),
                "text": " ".join([e.get("hauptberuf", ""), " ".join(e.get("alleBerufe", []))]),
                "firma": e.get("firma", ""),
                "standort": ort,
                "datum": e.get("datumErsteVeroeffentlichung", "")[:10],
                "typ": "freelance" if selbst else "bedarfssignal",
                "arbeitsort": "remote" if e.get("homeofficemoeglich") else ("vor_ort" if ort else "unbekannt"),
                "suche": s["was"] + (" @" + s["wo"] if s.get("wo") else " (bundesweit)"),
            })
        time.sleep(0.3)  # höflich bleiben
    return items


def quelle_bund():
    xml = _get("https://www.service.bund.de/Content/Globals/Functions/RSSFeed/RSSGenerator_Ausschreibungen.xml")
    items = []
    for m in re.finditer(r"<item>(.*?)</item>", xml, re.S):
        block = m.group(1)

        def tag(t):
            r = re.search(r"<%s>(.*?)</%s>" % (t, t), block, re.S)
            return _clean(r.group(1).replace("<![CDATA[", "").replace("]]>", "")) if r else ""
        items.append({"titel": tag("title")[:250], "url": tag("link"), "text": tag("description"),
                      "datum": tag("pubDate")[:16], "typ": "ausschreibung", "arbeitsort": "unbekannt"})
    return items


def quelle_ted(tage=21):
    seit = (datetime.now() - timedelta(days=tage)).strftime("%Y%m%d")
    body = json.dumps({
        "query": f"classification-cpv IN ({TED_CPV}) AND place-of-performance IN (DEU) "
                 f"AND publication-date>={seit} SORT BY publication-date DESC",
        "fields": ["notice-title", "publication-number", "buyer-name", "buyer-city", "publication-date"],
        "limit": 100}).encode()
    d = json.loads(_get("https://api.ted.europa.eu/v3/notices/search",
                        {"Content-Type": "application/json"}, timeout=40, data=body))
    items = []
    for n in d.get("notices", []):
        titel = n.get("notice-title", {})
        titel = titel.get("deu") or titel.get("eng") or next(iter(titel.values()), "")
        titel = re.sub(r"^Deutschland\s*[–-]\s*", "", titel)
        kaeufer = n.get("buyer-name", {})
        kaeufer = (kaeufer.get("deu") or kaeufer.get("eng") or [""])[0] if isinstance(kaeufer, dict) else ""
        stadt = n.get("buyer-city", {})
        stadt = (stadt.get("deu") or next(iter(stadt.values()), [""]))[0] if isinstance(stadt, dict) and stadt else ""
        nr = n.get("publication-number", "")
        items.append({"titel": titel[:250], "url": f"https://ted.europa.eu/de/notice/-/detail/{nr}",
                      "text": "", "firma": kaeufer, "standort": stadt,
                      "datum": n.get("publication-date", "")[:10], "typ": "ausschreibung",
                      "arbeitsort": "unbekannt"})
    return items


def quelle_arbeitnow():
    d = json.loads(_get("https://www.arbeitnow.com/api/job-board-api"))
    items = []
    for j in d.get("data", []):
        items.append({"titel": j.get("title", "")[:250], "url": j.get("url", ""),
                      "text": _clean(j.get("description", "")) + " " + " ".join(j.get("tags", [])),
                      "firma": j.get("company_name", ""), "standort": j.get("location", "")[:60],
                      "datum": datetime.fromtimestamp(j.get("created_at", 0)).strftime("%Y-%m-%d"),
                      "typ": "freelance" if re.search(r"freelance|freiberuf",
                                                     " ".join(j.get("job_types", [])), re.I) else "bedarfssignal",
                      "arbeitsort": "remote" if j.get("remote") else "unbekannt"})
    return items


QUELLEN = [
    ("Arbeitsagentur", "regional", lambda cfg: quelle_arbeitsagentur(cfg.get("radar_ba_suchen") or BA_SUCHEN_STANDARD)),
    ("service.bund.de", "ausschreibung", lambda cfg: quelle_bund()),
    ("TED (EU)", "ausschreibung", lambda cfg: quelle_ted()),
    ("Arbeitnow", "global", lambda cfg: quelle_arbeitnow()),
]


# --- Branchen-Marktgröße (OpenStreetMap) -----------------------------------------
# Hinweis: OSM ist unvollständig — Zahlen sind Untergrenzen, gut für den Vergleich
# zwischen Branchen/Regionen, nicht als absolute Marktgröße.
OSM_KATEGORIEN = [
    ("arztpraxis", "Arztpraxen", '["amenity"="doctors"]'),
    ("zahnarzt", "Zahnärzte", '["amenity"="dentist"]'),
    ("physio", "Physiotherapie", '["healthcare"="physiotherapist"]'),
    ("pflege", "Pflegedienste/-heime", '["amenity"="social_facility"]["social_facility"~"nursing_home|outreach|assisted_living"]'),
    ("apotheke", "Apotheken", '["amenity"="pharmacy"]'),
    ("steuerberater", "Steuerberater", '["office"="tax_advisor"]'),
    ("anwalt", "Anwaltskanzleien", '["office"="lawyer"]'),
    ("handwerk", "Handwerksbetriebe", '["craft"]'),
]
# Öffentliche Overpass-Spiegel sind oft überlastet (500/504) — der Reihe nach probieren
OVERPASS = ["https://overpass-api.de/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter"]

# Experten-Einschätzung je Branche (Stand 10/2026). 1–5. Treiber = warum die
# IT-Abhängigkeit wächst. Wird mit OSM-Anzahl + Stellen-Signal zum Chancen-Score.
BRANCHEN_PROFIL = {
    "pflege": {"abhaengigkeit_trend": 5, "zahlungsbereitschaft": 3, "it_reife_luecke": 5, "wettbewerb_gering": 4,
               "treiber": "TI-Anbindungspflicht seit 07/2025, KIM/ePA, digitale Pflegedoku + Abrechnung, Fachkräftemangel → Automatisierung"},
    "arztpraxis": {"abhaengigkeit_trend": 5, "zahlungsbereitschaft": 4, "it_reife_luecke": 3, "wettbewerb_gering": 3,
                   "treiber": "TI/eRezept/ePA/eAU Pflicht, KBV-IT-Sicherheitsrichtlinie, PVS-Wechsel, KI-Doku/Telefonassistenz"},
    "zahnarzt": {"abhaengigkeit_trend": 4, "zahlungsbereitschaft": 5, "it_reife_luecke": 3, "wettbewerb_gering": 3,
                 "treiber": "TI-Pflicht, digitales Röntgen/DVT (große Datenmengen, Backup), KZBV-Sicherheitsrichtlinie"},
    "physio": {"abhaengigkeit_trend": 4, "zahlungsbereitschaft": 2, "it_reife_luecke": 5, "wettbewerb_gering": 4,
               "treiber": "TI-Anbindung Heilmittelerbringer, eVerordnung, Terminorganisation/Online-Buchung"},
    "apotheke": {"abhaengigkeit_trend": 5, "zahlungsbereitschaft": 4, "it_reife_luecke": 2, "wettbewerb_gering": 2,
                 "treiber": "eRezept komplett digital, aber Warenwirtschafts-Anbieter liefern IT meist mit"},
    "steuerberater": {"abhaengigkeit_trend": 5, "zahlungsbereitschaft": 4, "it_reife_luecke": 2, "wettbewerb_gering": 2,
                      "treiber": "DATEV-Cloud, beSt-Postfach, E-Rechnung 2025–2028, KI-Belegverarbeitung — DATEV-Systempartner sind starke Konkurrenz"},
    "anwalt": {"abhaengigkeit_trend": 4, "zahlungsbereitschaft": 4, "it_reife_luecke": 3, "wettbewerb_gering": 3,
               "treiber": "beA-Pflicht, eAkte der Justiz, KI-Recherche/Schriftsatz — hoher Datenschutzanspruch (Produkt-Chance lokale KI)"},
    "handwerk": {"abhaengigkeit_trend": 3, "zahlungsbereitschaft": 2, "it_reife_luecke": 5, "wettbewerb_gering": 4,
                 "treiber": "E-Rechnung, Handwerkersoftware, Online-Terminierung — wächst, aber kleines IT-Budget"},
}


def _overpass_count(region, filt):
    # admin_level 4 = Stadtstaat (Hamburg), 6 = kreisfreie Stadt (Rostock) — keine Ortsteile/Namensvettern
    q = (f'[out:json][timeout:60];area["name"="{region}"]["boundary"="administrative"]'
         f'["admin_level"~"^(4|6)$"]->.a;(nwr(area.a){filt};);out count;')
    letzter = None
    for url in OVERPASS:  # eine Runde — bei Ausfall lieber später erneut (Fehlversuch-Sperre in app.py)
        try:
            d = json.loads(_get(url, timeout=60, data=urllib.parse.urlencode({"data": q}).encode()))
            counts = [int(e["tags"].get("total", 0)) for e in d.get("elements", []) if e.get("type") == "count"]
            if counts:
                return counts[0]
            letzter = "leere Antwort"
        except Exception as e:  # nächsten Spiegel probieren
            letzter = type(e).__name__
        time.sleep(2)
    raise RuntimeError(f"Overpass nicht erreichbar ({letzter})")


def osm_zaehlen(region):
    """Zählt Zielbranchen in einer Stadt/Region. Eine Abfrage je Branche — eine Sammel-
    abfrage ist für große Gebiete (Hamburg) zu schwer und läuft auf den Spiegeln in 504."""
    return {k: _overpass_count(region, f) for k, _, f in OSM_KATEGORIEN}


def branchen_analyse(osm, signale):
    """osm: {region: {kat: anzahl}}, signale: {kat: anzahl Radar-Treffer mit Branchenbezug}."""
    zeilen = []
    for key, name, _ in OSM_KATEGORIEN:
        p = BRANCHEN_PROFIL.get(key, {})
        anzahl = {r: (osm.get(r) or {}).get(key) for r in osm}
        gesamt = sum(v or 0 for v in anzahl.values())
        # Marktgröße 1–5 (log-artig), Rest aus Profil
        groesse = 1 if gesamt < 20 else 2 if gesamt < 60 else 3 if gesamt < 150 else 4 if gesamt < 400 else 5
        teil = [p.get("abhaengigkeit_trend", 3), p.get("zahlungsbereitschaft", 3), p.get("it_reife_luecke", 3),
                p.get("wettbewerb_gering", 3), groesse]
        chancen = round(sum(w * v for w, v in zip([0.3, 0.2, 0.2, 0.15, 0.15], teil)) * 20)
        zeilen.append({"key": key, "name": name, "anzahl": anzahl, "gesamt": gesamt,
                       "signale": signale.get(key, 0), "chancen_score": chancen,
                       "treiber": p.get("treiber", ""),
                       "bewertung": {"Abhängigkeit↑": teil[0], "Zahlungsbereitschaft": teil[1],
                                     "IT-Reife-Lücke": teil[2], "wenig Wettbewerb": teil[3], "Marktgröße": teil[4]}})
    zeilen.sort(key=lambda z: -z["chancen_score"])
    return zeilen


BRANCHEN_SIGNAL_MUSTER = {
    "arztpraxis": r"arztpraxis|\bpraxis\b|\bmvz\b|\bpvs\b|turbomed", "zahnarzt": r"zahnarzt|dental",
    "physio": r"physiotherap|heilmittel", "pflege": r"pflege", "apotheke": r"apothek",
    "steuerberater": r"steuerberat|\bdatev\b", "anwalt": r"kanzlei|rechtsanw|\bbea\b",
    "handwerk": r"handwerk",
}


def markt_report(log, tage=30):
    """Aggregiert das Markt-Log (alle je gefundenen relevanten Treffer)."""
    grenze = (datetime.now() - timedelta(days=tage)).isoformat()
    rel = [e for e in log if e.get("t", "") >= grenze]
    seg, kw, quelle, typ, region, branchen, wochen = {}, {}, {}, {}, {}, {}, {}
    for e in rel:
        for s in e.get("s", []):
            seg[s] = seg.get(s, 0) + 1
        for k in e.get("k", []):
            kw[k] = kw.get(k, 0) + 1
        quelle[e.get("q", "?")] = quelle.get(e.get("q", "?"), 0) + 1
        typ[e.get("y", "?")] = typ.get(e.get("y", "?"), 0) + 1
        region[e.get("r", "?")] = region.get(e.get("r", "?"), 0) + 1
        for b, m in BRANCHEN_SIGNAL_MUSTER.items():
            if re.search(m, e.get("x", "")):
                branchen[b] = branchen.get(b, 0) + 1
        w = e.get("t", "")[:10]
        if w:
            wk = datetime.fromisoformat(w).strftime("%G-KW%V")
            wochen.setdefault(wk, {})
            for s in e.get("s", []):
                wochen[wk][s] = wochen[wk].get(s, 0) + 1

    def top(d, n=15):
        return [{"key": k, "anzahl": v} for k, v in sorted(d.items(), key=lambda x: -x[1])[:n]]
    return {"zeitraum_tage": tage, "anzahl": len(rel),
            "segmente": [{"key": k, "name": SEGMENT_NAMEN.get(k, k), "anzahl": v}
                         for k, v in sorted(seg.items(), key=lambda x: -x[1])],
            "keywords": top(kw, 25), "quellen": top(quelle), "typen": top(typ), "regionen": top(region),
            "branchen_signale": branchen, "wochen": dict(sorted(wochen.items())),
            "produkt_ideen": produkt_ideen(seg, kw)}


def produkt_ideen(seg, kw):
    """Leitet aus wiederkehrender Nachfrage Produkt-Hypothesen ab (für das Wirtschaftlichkeits-Gate)."""
    ideen = []
    if seg.get("healthcare_it", 0) >= 5 and (seg.get("integration", 0) or kw.get("hl7") or kw.get("fhir")):
        ideen.append({"titel": "HL7/FHIR-Schnittstellen-Monitor für Kliniken/MVZ",
                      "warum": "Häufige Nachfrage nach KIS-Schnittstellen-Know-how → Monitoring-/Mapping-Tool als Produkt"})
    if seg.get("iam", 0) >= 5:
        ideen.append({"titel": "Berechtigungs-Audit-Report (Entra ID/AD) als Festpreis-Paket",
                      "warum": "IAM-Nachfrage stabil → standardisierter Audit mit Skript + Report"})
    if seg.get("ki_automation", 0) >= 5 and seg.get("kmu_branchen", 0) >= 2:
        ideen.append({"titel": "KI-Empfang/Telefonassistent für Praxen & Pflegedienste",
                      "warum": "KI-Nachfrage trifft KMU-Branchen → lokales, DSGVO-konformes KI-Produkt"})
    if seg.get("oeffentlich", 0) >= 5:
        ideen.append({"titel": "eAkte-/DMS-Einführungsbegleitung (Kommunen) als Paket",
                      "warum": "Viele öffentliche Ausschreibungen → Teilnahme als Subunternehmer/Bietergemeinschaft"})
    if seg.get("kmu_branchen", 0) >= 3:
        ideen.append({"titel": "IT-Wartungsvertrag 'Praxis-Sorglos' (Monatspauschale)",
                      "warum": "Wiederkehrende KMU-Nachfrage → planbarer Monatsumsatz statt Einzelstunden"})
    return ideen
