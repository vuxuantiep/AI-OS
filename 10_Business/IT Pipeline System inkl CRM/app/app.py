# -*- coding: utf-8 -*-
"""
LeadPilot — IT Pipeline CRM (self-contained AI-OS-/Trace-AI-OS-Modul).

Eigenes schlankes CRM für IT-Freelancer-Leads + Lead-Radar:
- Lead-Erfassung: Webhooks (Kontaktformular, Cal.com), manuell, Radar-Übernahme
- Pipeline: Neu -> Qualifiziert -> Erstgespräch -> Angebot -> Gewonnen/Verloren
- F3: sofortige Eingangsbestätigung bei JEDEM Lead (Mail 1) + genau EINE
  Buchungs-Erinnerung (Mail 2, UWG-konform kein Drip)
- F2: DSGVO — Export je Lead (Art. 15), Löschen (Art. 17), Anonymisierung
  verlorener Leads nach konfigurierbarer Frist, Verlaufs-Protokoll
- Lead-Radar: scannt öffentliche Projektbörsen-Feeds nach relevanten Projekten
  (Keyword-Scoring), eigene Quellen ergänzbar

Portabel: KEINE Abhängigkeit zur Host-Plattform. Kopieren + `python app.py`
genügt (siehe INSTALL.md). Persistenz: JSON-Dateien unter data/.

Start:  python app.py     ->  http://localhost:5330
"""
import json
import os
import re
import smtplib
import sys
import threading
import time
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.mime.text import MIMEText

from flask import Flask, jsonify, render_template, request

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

PORT = int(os.environ.get("LEADPILOT_PORT", "5330"))
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

STUFEN = [
    {"id": "neu", "titel": "Neu"},
    {"id": "qualifiziert", "titel": "Qualifiziert"},
    {"id": "erstgespraech", "titel": "Erstgespräch"},
    {"id": "angebot", "titel": "Angebot"},
    {"id": "gewonnen", "titel": "Gewonnen"},
    {"id": "verloren", "titel": "Verloren"},
]
STUFEN_IDS = {s["id"] for s in STUFEN}

DEFAULT_CONFIG = {
    "absender_name": "Tiep Vu Xuan — IT Services",
    # Eigener Buchungslink (die eingebaute Terminbuchung unter /buchen) —
    # kann auf die öffentliche URL der Website zeigen, sobald eingebettet
    "booking_link": "http://localhost:5330/buchen",
    # Eingebaute Terminbuchung (Cal.com-Ersatz, keine Fremdabhängigkeit)
    "buchung_aktiv": True,
    "buchung_wochentage": [0, 1, 2, 3, 4],   # Mo–Fr (0 = Montag)
    "buchung_von": "09:00",
    "buchung_bis": "17:00",
    "buchung_slot_minuten": 30,
    "buchung_vorlauf_stunden": 24,
    "buchung_horizont_tage": 14,
    "mail3_betreff": "Terminbestätigung: {termin_text}",
    "mail3_text": ("Hallo {name},\n\nIhr Gesprächstermin ist bestätigt:\n\n"
                   "  📅 {termin_text} (30 Minuten)\n\n"
                   "Falls der Termin nicht passt, antworten Sie einfach auf diese "
                   "E-Mail.\n\nViele Grüße\n{absender}"),
    # Firmendaten für Angebote/Rechnungen (§14 UStG Pflichtangaben!)
    # Aufbau nach eigener Vorlage (Plannung/Rechnungsvorlagen)
    "firma_name": "Tiep Vu Xuan — IT Services",
    "firma_adresse": "Musterstraße X\n12345 Musterstadt",
    "firma_inhaber": "Tiep Vu Xuan",
    "firma_telefon": "",
    "firma_email": "",
    "firma_website": "https://vuxuantiep.de",
    "steuernummer": "",
    "ust_id": "",
    "iban": "",
    "bic": "",
    "bank": "",
    "kleinunternehmer": False,  # Vorlage weist USt aus; True = §19 UStG Hinweis
    "ust_prozent": 19,
    "zahlungsziel_tage": 14,
    "stundensatz_standard": 85,
    "radar_autoscan_stunde": 7,  # täglicher Auto-Scan (zusätzlich zum Button)
    "erinnerung_aktiv": True,
    "erinnerung_nach_tagen": 3,
    "dsgvo_loeschfrist_monate": 6,
    "radar_keywords": ["python", "flask", "react", "ki", "ai", "automation",
                       "crm", "dashboard", "chatbot", "rag", "llm", "n8n"],
    "radar_quellen_eigene": [],
    "mail1_betreff": "Ihre Anfrage ist angekommen — nächste Schritte",
    "mail1_text": ("Hallo {name},\n\nvielen Dank für Ihre Anfrage ({projektart}). "
                   "Ich melde mich innerhalb von 24 Stunden persönlich.\n\n"
                   "Noch schneller geht es, wenn Sie sich direkt einen Termin aussuchen: "
                   "{booking_link}\n\nViele Grüße\n{absender}"),
    "mail2_betreff": "Kurze Erinnerung: Ihr Wunschtermin",
    "mail2_text": ("Hallo {name},\n\nfalls es untergegangen ist: Für Ihre Anfrage "
                   "({projektart}) können Sie sich hier direkt einen Gesprächstermin "
                   "sichern: {booking_link}\n\nDies ist die einzige automatische "
                   "Erinnerung — danach melde ich mich nur noch persönlich.\n\n"
                   "Viele Grüße\n{absender}"),
}

RADAR_QUELLEN = [
    {"name": "RemoteOK Dev", "typ": "feed", "url": "https://remoteok.com/remote-dev-jobs.rss"},
    {"name": "WeWorkRemotely Programming", "typ": "feed",
     "url": "https://weworkremotely.com/categories/remote-programming-jobs.rss"},
    {"name": "Remotive Software-Dev", "typ": "remotive",
     "url": "https://remotive.com/api/remote-jobs?category=software-dev&limit=50"},
]

app = Flask(__name__)


# --- Persistenz-Helfer ---------------------------------------------------------

def _now():
    return datetime.now().isoformat(timespec="seconds")


def _pfad(name):
    return os.path.join(DATA_DIR, name)


def lade(name, default):
    p = _pfad(name)
    if not os.path.exists(p):
        return default
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def speichere(name, daten):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = _pfad(name) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _pfad(name))


def lade_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(lade("config.json", {}))
    return cfg


def lade_leads():
    return lade("leads.json", [])


def finde_lead(leads, lead_id):
    return next((l for l in leads if l["id"] == lead_id), None)


def protokoll(lead, text):
    lead.setdefault("verlauf", []).append({"zeit": _now(), "text": text})
    lead["aktualisiert"] = _now()


# --- Mail-System (F3): sofortige Bestätigung + genau EINE Erinnerung -----------

def smtp_konfiguriert():
    return bool(os.environ.get("SMTP_HOST") and os.environ.get("SMTP_FROM"))


def sende_mail(an, betreff, text, lead_id, typ):
    """Sendet sofort wenn SMTP konfiguriert, sonst in den Postausgang (sichtbar).
    So funktioniert F3 auch ohne Mail-Server-Setup — nichts geht verloren."""
    outbox = lade("outbox.json", [])
    eintrag = {"id": str(uuid.uuid4()), "an": an, "betreff": betreff, "text": text,
               "lead_id": lead_id, "typ": typ, "zeit": _now(), "status": "wartet_smtp",
               "fehler": ""}
    if smtp_konfiguriert():
        try:
            msg = MIMEText(text, "plain", "utf-8")
            msg["Subject"] = betreff
            msg["From"] = os.environ["SMTP_FROM"]
            msg["To"] = an
            host = os.environ["SMTP_HOST"]
            port = int(os.environ.get("SMTP_PORT", "587"))
            with smtplib.SMTP(host, port, timeout=15) as s:
                s.starttls()
                if os.environ.get("SMTP_USER"):
                    s.login(os.environ["SMTP_USER"], os.environ.get("SMTP_PASS", ""))
                s.send_message(msg)
            eintrag["status"] = "gesendet"
        except Exception as e:
            eintrag["status"] = "fehler"
            eintrag["fehler"] = f"{type(e).__name__}: {e}"[:200]
    outbox.insert(0, eintrag)
    speichere("outbox.json", outbox[:500])
    return eintrag["status"]


def _mail_vars(cfg, lead):
    return {"name": lead.get("name") or "und Guten Tag",
            "projektart": lead.get("projektart") or "Ihr Projekt",
            "booking_link": cfg["booking_link"], "absender": cfg["absender_name"]}


def sende_bestaetigung(cfg, lead):
    if not lead.get("email"):
        return
    v = _mail_vars(cfg, lead)
    status = sende_mail(lead["email"], cfg["mail1_betreff"].format(**v),
                        cfg["mail1_text"].format(**v), lead["id"], "bestaetigung")
    protokoll(lead, f"Mail 1 (Eingangsbestätigung): {status}")


def termin_text(iso):
    """'2026-07-20T10:00' -> '20.07.2026, 10:00 Uhr'"""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", ""))
        return dt.strftime("%d.%m.%Y, %H:%M Uhr")
    except ValueError:
        return iso


def sende_terminbestaetigung(cfg, lead):
    if not lead.get("email"):
        return
    v = _mail_vars(cfg, lead)
    v["termin_text"] = termin_text(lead.get("termin", ""))
    status = sende_mail(lead["email"], cfg["mail3_betreff"].format(**v),
                        cfg["mail3_text"].format(**v), lead["id"], "terminbestaetigung")
    protokoll(lead, f"Mail 3 (Terminbestätigung): {status}")


def pruefe_erinnerungen():
    """Mail 2: genau EINE automatische Buchungs-Erinnerung pro Lead (UWG!).
    Nur für Formular-Leads ohne Termin, die noch in 'neu' stehen."""
    cfg = lade_config()
    if not cfg["erinnerung_aktiv"]:
        return 0
    leads = lade_leads()
    grenze = datetime.now() - timedelta(days=int(cfg["erinnerung_nach_tagen"]))
    gesendet = 0
    for lead in leads:
        if (lead["stufe"] == "neu" and lead["quelle"] == "formular"
                and lead.get("email") and not lead.get("termin")
                and not lead.get("erinnerung_gesendet")
                and not lead.get("anonymisiert")
                and datetime.fromisoformat(lead["erstellt"]) < grenze):
            v = _mail_vars(cfg, lead)
            status = sende_mail(lead["email"], cfg["mail2_betreff"].format(**v),
                                cfg["mail2_text"].format(**v), lead["id"], "erinnerung")
            lead["erinnerung_gesendet"] = True  # hart: nie eine zweite (kein Drip)
            protokoll(lead, f"Mail 2 (einmalige Erinnerung): {status}")
            gesendet += 1
    if gesendet:
        speichere("leads.json", leads)
    return gesendet


# --- Lead-Kern ------------------------------------------------------------------

def neuer_lead(daten, quelle, mail_typ="bestaetigung"):
    """Legt Lead an ODER hängt an bestehenden offenen Lead an (Dedup per E-Mail)."""
    leads = lade_leads()
    cfg = lade_config()
    email = (daten.get("email") or "").strip().lower()
    if email:
        offen = next((l for l in leads if l.get("email", "").lower() == email
                      and l["stufe"] not in ("gewonnen", "verloren")
                      and not l.get("anonymisiert")), None)
        if offen:
            protokoll(offen, f"Weitere Anfrage über {quelle}: "
                             f"{(daten.get('nachricht') or daten.get('projektart') or '')[:200]}")
            if daten.get("termin"):
                offen["termin"] = daten["termin"]
                protokoll(offen, f"Termin gebucht: {daten['termin']}")
                if mail_typ == "termin":
                    sende_terminbestaetigung(cfg, offen)
            speichere("leads.json", leads)
            return offen, False
    lead = {
        "id": str(uuid.uuid4()),
        "name": (daten.get("name") or "").strip()[:120],
        "email": email[:200],
        "telefon": (daten.get("telefon") or "").strip()[:60],
        "firma": (daten.get("firma") or "").strip()[:120],
        "projektart": (daten.get("projektart") or "").strip()[:200],
        "nachricht": (daten.get("nachricht") or "").strip()[:3000],
        "quelle": quelle,
        "stufe": "neu",
        "termin": daten.get("termin", ""),
        "wert_eur": daten.get("wert_eur", 0),
        "erinnerung_gesendet": False,
        "anonymisiert": False,
        "erstellt": _now(),
        "aktualisiert": _now(),
        "verlauf": [{"zeit": _now(), "text": f"Lead angelegt (Quelle: {quelle})"}],
    }
    leads.insert(0, lead)
    if mail_typ == "termin":
        sende_terminbestaetigung(cfg, lead)
    else:
        sende_bestaetigung(cfg, lead)  # F3: in JEDEM Pfad, sofort
    speichere("leads.json", leads)
    return lead, True


# --- DSGVO (F2) -------------------------------------------------------------------

def dsgvo_faellige(leads, cfg):
    grenze = datetime.now() - timedelta(days=30 * int(cfg["dsgvo_loeschfrist_monate"]))
    return [l for l in leads if l["stufe"] == "verloren" and not l.get("anonymisiert")
            and datetime.fromisoformat(l["aktualisiert"]) < grenze]


def anonymisiere(lead):
    lead.update({"name": "— anonymisiert —", "email": "", "telefon": "",
                 "firma": "", "nachricht": "", "anonymisiert": True})
    lead["verlauf"] = [{"zeit": _now(), "text": "Personenbezogene Daten gemäß Löschkonzept entfernt"}]
    lead["aktualisiert"] = _now()


# --- Eingebaute Terminbuchung (Cal.com-Ersatz, keine Fremdabhängigkeit) -------------

def belegte_slots():
    """Alle künftig gebuchten Termine (ISO 'YYYY-MM-DDTHH:MM') aus den Leads."""
    belegt = set()
    for l in lade_leads():
        t = (l.get("termin") or "").replace("Z", "")[:16]
        if t and l["stufe"] != "verloren" and not l.get("anonymisiert"):
            belegt.add(t)
    return belegt


def slots_fuer_tag(cfg, tag):
    """Freie Slots für ein Datum (date-Objekt) nach Konfiguration."""
    if tag.weekday() not in cfg["buchung_wochentage"]:
        return []
    von_h, von_m = map(int, cfg["buchung_von"].split(":"))
    bis_h, bis_m = map(int, cfg["buchung_bis"].split(":"))
    schritt = int(cfg["buchung_slot_minuten"])
    fruehestens = datetime.now() + timedelta(hours=int(cfg["buchung_vorlauf_stunden"]))
    belegt = belegte_slots()
    slots = []
    t = datetime(tag.year, tag.month, tag.day, von_h, von_m)
    ende = datetime(tag.year, tag.month, tag.day, bis_h, bis_m)
    while t + timedelta(minutes=schritt) <= ende:
        iso = t.strftime("%Y-%m-%dT%H:%M")
        if t >= fruehestens and iso not in belegt:
            slots.append(iso)
        t += timedelta(minutes=schritt)
    return slots


@app.route("/buchen")
def buchen_seite():
    return render_template("buchen.html")


@app.route("/api/buchungen/tage")
def api_buchung_tage():
    cfg = lade_config()
    if not cfg["buchung_aktiv"]:
        return jsonify({"aktiv": False, "tage": []})
    tage = []
    heute = datetime.now().date()
    for i in range(int(cfg["buchung_horizont_tage"]) + 1):
        tag = heute + timedelta(days=i)
        anzahl = len(slots_fuer_tag(cfg, tag))
        if anzahl:
            wt = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"][tag.weekday()]
            tage.append({"datum": tag.isoformat(), "frei": anzahl,
                         "label": wt + tag.strftime(" %d.%m.")})
    return jsonify({"aktiv": True, "tage": tage,
                    "slot_minuten": cfg["buchung_slot_minuten"]})


@app.route("/api/buchungen/slots")
def api_buchung_slots():
    cfg = lade_config()
    try:
        tag = datetime.fromisoformat(request.args.get("tag", "")).date()
    except ValueError:
        return jsonify({"error": "Ungültiges Datum"}), 400
    return jsonify({"slots": slots_fuer_tag(cfg, tag)})


@app.route("/api/buchungen", methods=["POST"])
def api_buchung_anlegen():
    cfg = lade_config()
    if not cfg["buchung_aktiv"]:
        return jsonify({"error": "Buchung derzeit deaktiviert"}), 403
    d = request.get_json(silent=True) or {}
    slot = (d.get("slot") or "")[:16]
    email = (d.get("email") or "").strip()
    if not (slot and email and d.get("name")):
        return jsonify({"error": "Name, E-Mail und Termin sind Pflicht"}), 400
    try:
        slot_dt = datetime.fromisoformat(slot)
    except ValueError:
        return jsonify({"error": "Ungültiger Termin"}), 400
    # Slot muss zu den Regeln passen UND noch frei sein (Kollisionsprüfung)
    if slot not in slots_fuer_tag(cfg, slot_dt.date()):
        return jsonify({"error": "Dieser Termin ist nicht (mehr) verfügbar — bitte anderen wählen"}), 409
    lead, neu = neuer_lead({
        "name": d.get("name"), "email": email,
        "projektart": (d.get("thema") or "Erstgespräch (30 min)"),
        "nachricht": (d.get("nachricht") or "")[:2000],
        "termin": slot,
    }, "buchung", mail_typ="termin")
    return jsonify({"ok": True, "lead_id": lead["id"], "termin": slot,
                    "termin_text": termin_text(slot)}), 201


@app.route("/api/termine.ics")
def api_termine_ics():
    """ICS-Feed aller gebuchten Termine — in Thunderbird/Outlook/Google Kalender
    als Kalender-Abo einbinden (kein externer Kalenderdienst nötig)."""
    cfg = lade_config()
    dauer = int(cfg["buchung_slot_minuten"])
    zeilen = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//LeadPilot//Termine//DE",
              "X-WR-CALNAME:LeadPilot Termine"]
    for l in lade_leads():
        t = (l.get("termin") or "").replace("Z", "")[:16]
        if not t or l.get("anonymisiert"):
            continue
        try:
            start = datetime.fromisoformat(t)
        except ValueError:
            continue
        ende = start + timedelta(minutes=dauer)
        zeilen += ["BEGIN:VEVENT",
                   f"UID:{l['id']}@leadpilot",
                   f"DTSTART:{start.strftime('%Y%m%dT%H%M%S')}",
                   f"DTEND:{ende.strftime('%Y%m%dT%H%M%S')}",
                   f"SUMMARY:Erstgespräch: {l.get('name', '')}",
                   f"DESCRIPTION:{(l.get('projektart') or '')} — {(l.get('email') or '')}",
                   "END:VEVENT"]
    zeilen.append("END:VCALENDAR")
    from flask import Response
    return Response("\r\n".join(zeilen), content_type="text/calendar; charset=utf-8")


# --- Lead-Radar --------------------------------------------------------------------

def _http_get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "ignore")


def _feed_items(xml_text):
    items = []
    root = ET.fromstring(xml_text)
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        d = {c.tag.split("}")[-1]: (c.text or "").strip() for c in el}
        link = d.get("link", "")
        if not link:
            for c in el:
                if c.tag.split("}")[-1] == "link" and c.get("href"):
                    link = c.get("href")
        items.append({"titel": d.get("title", "")[:250], "url": link,
                      "text": re.sub(r"<[^>]+>", " ", d.get("description", "") or d.get("summary", ""))[:1500],
                      "datum": (d.get("pubDate") or d.get("updated") or "")[:30]})
    return items


def radar_scan():
    cfg = lade_config()
    radar = lade("radar.json", {"seen": [], "treffer": [], "letzter_scan": None})
    seen = set(radar["seen"])
    keywords = [k.lower() for k in cfg["radar_keywords"]]
    fehler, neue = [], []
    quellen = RADAR_QUELLEN + [{"name": q.get("name", "eigene"), "typ": "feed", "url": q["url"]}
                               for q in cfg.get("radar_quellen_eigene", []) if q.get("url")]
    for q in quellen:
        try:
            if q["typ"] == "remotive":
                jobs = json.loads(_http_get(q["url"])).get("jobs", [])
                items = [{"titel": j.get("title", "")[:250], "url": j.get("url", ""),
                          "text": re.sub(r"<[^>]+>", " ", j.get("description", ""))[:1500],
                          "datum": j.get("publication_date", "")[:10]} for j in jobs]
            else:
                items = _feed_items(_http_get(q["url"]))
            for it in items:
                if not it["url"] or it["url"] in seen:
                    continue
                seen.add(it["url"])
                text = (it["titel"] + " " + it["text"]).lower()
                # Wortgrenzen statt Substring — sonst matcht "ai" in "maintain"
                treffer_kw = [k for k in keywords
                              if re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", text)]
                if not treffer_kw:
                    continue
                it["quelle"] = q["name"]
                it["keywords"] = treffer_kw
                it["score"] = len(treffer_kw)
                it["gefunden_am"] = _now()
                it["id"] = str(uuid.uuid4())
                neue.append(it)
        except Exception as e:
            fehler.append(f"{q['name']}: {type(e).__name__}")
    neue.sort(key=lambda x: -x["score"])
    radar["seen"] = list(seen)[-8000:]
    radar["treffer"] = (neue + radar["treffer"])[:300]
    radar["letzter_scan"] = _now()
    speichere("radar.json", radar)
    return {"neue_treffer": len(neue), "fehler": fehler}


# --- Kunden & Leistungskatalog -------------------------------------------------------

def lade_kunden():
    return lade("kunden.json", [])


KATALOG_SEED = [
    # Dienstleistungen (Marktspannen = Orientierung dt. IT-Freelancer-Markt 2026,
    # in den Einstellungen/im Katalog anpassbar — KEINE Live-Daten)
    {"name": "Softwareentwicklung (Web/Python/React)", "typ": "dienstleistung",
     "einheit": "Std", "preis_eur": 85, "marktpreis": "80–120 €/Std", "plattform": "—", "aktiv": True},
    {"name": "KI-Integration & LLM-Anwendungen (RAG, Agenten)", "typ": "dienstleistung",
     "einheit": "Std", "preis_eur": 100, "marktpreis": "95–150 €/Std", "plattform": "—", "aktiv": True},
    {"name": "Prozess-Automatisierung (n8n, Workflows)", "typ": "dienstleistung",
     "einheit": "Std", "preis_eur": 85, "marktpreis": "75–110 €/Std", "plattform": "—", "aktiv": True},
    {"name": "CRM-/Lead-System-Setup (Done-for-you, Paket)", "typ": "dienstleistung",
     "einheit": "Pauschale", "preis_eur": 2500, "marktpreis": "1.500–5.000 €", "plattform": "AI-OS + Trace-AI OS", "aktiv": True},
    {"name": "IT-Beratung / Analyse", "typ": "dienstleistung",
     "einheit": "Std", "preis_eur": 90, "marktpreis": "85–130 €/Std", "plattform": "—", "aktiv": True},
    # Produkte aktuell in Produktion (beide Plattformen)
    {"name": "DocuCheck Local (Browser-KI Dokumentprüfung)", "typ": "produkt",
     "einheit": "Lizenz/Setup", "preis_eur": 0, "marktpreis": "n. a.", "plattform": "AI-OS", "aktiv": True},
    {"name": "KI-Avatar Video-Pipeline (YouTube/TikTok-Automation)", "typ": "produkt",
     "einheit": "Projekt", "preis_eur": 0, "marktpreis": "n. a.", "plattform": "AI-OS", "aktiv": True},
    {"name": "LeadPilot CRM (IT Pipeline System)", "typ": "produkt",
     "einheit": "Setup", "preis_eur": 0, "marktpreis": "n. a.", "plattform": "AI-OS + Trace-AI OS", "aktiv": True},
]


def lade_katalog():
    kat = lade("katalog.json", None)
    if kat is None:
        kat = [dict(k, id=str(uuid.uuid4())) for k in KATALOG_SEED]
        speichere("katalog.json", kat)
    return kat


# --- Dokumente: Angebot / Rechnung / Mahnung / Vertrag --------------------------------

DOK_TYPEN = {"angebot": "Angebot", "rechnung": "Rechnung",
             "mahnung": "Zahlungserinnerung", "vertrag": "Dienstvertrag"}
DOK_PREFIX = {"angebot": "A-", "rechnung": "", "mahnung": "M-", "vertrag": "V-"}


def lade_dokumente():
    return lade("dokumente.json", [])


def naechste_nummer(dokumente, typ):
    """Fortlaufende Nummer je Typ und Jahr — Rechnungen im Vorlagen-Format '2026-001'."""
    jahr = datetime.now().year
    praefix = DOK_PREFIX[typ]
    muster = f"{praefix}{jahr}-"
    laufend = [int(d["nummer"].split("-")[-1]) for d in dokumente
               if d["typ"] == typ and d["nummer"].startswith(muster)]
    return f"{muster}{(max(laufend) + 1 if laufend else 1):03d}"


def berechne_summen(dok, cfg):
    netto = sum(round(float(p.get("menge") or 0) * float(p.get("preis") or 0), 2)
                for p in dok.get("positionen", []))
    kleinunternehmer = dok.get("kleinunternehmer", cfg["kleinunternehmer"])
    ust_prozent = 0 if kleinunternehmer else int(dok.get("ust_prozent", cfg["ust_prozent"]))
    ust = round(netto * ust_prozent / 100, 2)
    dok.update({"summe_netto": round(netto, 2), "ust_prozent": ust_prozent,
                "summe_ust": ust, "summe_brutto": round(netto + ust, 2),
                "kleinunternehmer": kleinunternehmer})


VERTRAG_VORLAGE = """DIENSTVERTRAG über freiberufliche IT-Leistungen

zwischen
{firma_name}, {firma_adresse_zeile} („Auftragnehmer")
und
{kunde_name}, {kunde_adresse_zeile} („Auftraggeber")

§1 Vertragsgegenstand
Der Auftragnehmer erbringt für den Auftraggeber folgende Leistungen: {leistung}.
Der Auftragnehmer erbringt die Leistungen selbstständig und eigenverantwortlich.
Ein Arbeitsverhältnis wird nicht begründet; der Auftragnehmer unterliegt keinen
Weisungen zu Arbeitszeit und Arbeitsort und ist berechtigt, für weitere
Auftraggeber tätig zu sein.

§2 Vergütung
Die Vergütung beträgt {verguetung}. Rechnungen sind innerhalb von
{zahlungsziel} Tagen nach Zugang ohne Abzug zahlbar.
{ust_klausel}

§3 Laufzeit und Kündigung
Der Vertrag beginnt am {beginn} und läuft {laufzeit}.
Er kann von beiden Seiten mit einer Frist von {kuendigungsfrist} in Textform
gekündigt werden. Das Recht zur außerordentlichen Kündigung bleibt unberührt.

§4 Nutzungsrechte
Der Auftragnehmer räumt dem Auftraggeber mit vollständiger Bezahlung die
ausschließlichen, zeitlich und räumlich unbeschränkten Nutzungsrechte an den
vertragsgegenständlichen Arbeitsergebnissen ein. Vorbestehende Werkzeuge,
Bibliotheken und Know-how des Auftragnehmers bleiben davon ausgenommen; hieran
erhält der Auftraggeber ein einfaches Nutzungsrecht, soweit für die Nutzung der
Arbeitsergebnisse erforderlich.

§5 Vertraulichkeit und Datenschutz
Beide Parteien behandeln vertrauliche Informationen der jeweils anderen Partei
geheim. Verarbeitet der Auftragnehmer personenbezogene Daten im Auftrag, wird
ergänzend ein Auftragsverarbeitungsvertrag nach Art. 28 DSGVO geschlossen.

§6 Haftung
Der Auftragnehmer haftet unbeschränkt für Vorsatz und grobe Fahrlässigkeit sowie
bei Verletzung von Leben, Körper und Gesundheit. Bei einfacher Fahrlässigkeit
haftet er nur für die Verletzung wesentlicher Vertragspflichten, begrenzt auf
den vertragstypischen, vorhersehbaren Schaden, höchstens jedoch auf die Höhe
der in den letzten 12 Monaten gezahlten Vergütung.

§7 Schlussbestimmungen
Änderungen bedürfen der Textform. Es gilt deutsches Recht. Gerichtsstand ist,
soweit zulässig, der Sitz des Auftragnehmers. Sollten einzelne Bestimmungen
unwirksam sein, bleibt der Vertrag im Übrigen wirksam.

{ort_datum}

_______________________          _______________________
Auftragnehmer                    Auftraggeber

Hinweis: Dieses Muster wurde automatisch erstellt und ersetzt keine
Rechtsberatung — vor Verwendung bei wichtigen Aufträgen anwaltlich prüfen lassen."""

# Vertragsprüfung: Pflicht-Klauseln + Risikosignale (Heuristik, keine Rechtsberatung)
VERTRAG_PFLICHT = [
    ("Leistungsbeschreibung", r"leistung|vertragsgegenstand|aufgaben"),
    ("Vergütung", r"vergütung|honorar|stundensatz|pauschal"),
    ("Zahlungsziel", r"zahlungsziel|zahlbar|fällig"),
    ("Laufzeit/Beginn", r"laufzeit|beginn|vertragsbeginn"),
    ("Kündigung", r"kündig"),
    ("Nutzungsrechte/IP", r"nutzungsrecht|urheber|arbeitsergebnis"),
    ("Vertraulichkeit", r"vertraulich|geheim"),
    ("Datenschutz/AVV", r"datenschutz|dsgvo|auftragsverarbeitung"),
    ("Haftungsregelung", r"haftung|haftet"),
    ("Anwendbares Recht/Gerichtsstand", r"gerichtsstand|deutsches recht|anwendbares recht"),
]
VERTRAG_RISIKEN = [
    ("Scheinselbstständigkeit: Weisungsbindung", r"weisungsgebunden|weisungen des auftraggebers (unterliegt|folgt)"),
    ("Scheinselbstständigkeit: feste Arbeitszeiten", r"feste[n]? arbeitszeiten|arbeitszeit von \d|kernarbeitszeit"),
    ("Scheinselbstständigkeit: Urlaubsregelung wie Arbeitnehmer", r"urlaubsanspruch|urlaubstage"),
    ("Unbeschränkte Haftung", r"haftet unbeschränkt|unbegrenzte haftung"),
    ("Vertragsstrafe", r"vertragsstrafe|pönale"),
    ("Weites Wettbewerbsverbot", r"wettbewerbsverbot"),
    ("Exklusivbindung", r"ausschließlich für den auftraggeber|exklusiv"),
    ("Unklare/kostenlose Nacharbeit", r"unentgeltlich nachzubessern|kostenlose änderungen"),
]


def pruefe_vertrag(text):
    t = text.lower()
    gefunden = [{"punkt": name, "ok": bool(re.search(muster, t))} for name, muster in VERTRAG_PFLICHT]
    risiken = [name for name, muster in VERTRAG_RISIKEN if re.search(muster, t)]
    fehlend = [g["punkt"] for g in gefunden if not g["ok"]]
    score = round(10 * sum(1 for g in gefunden if g["ok"]) / len(gefunden) - len(risiken), 1)
    return {"checkliste": gefunden, "fehlend": fehlend, "risiken": risiken,
            "score": max(0, score),
            "hinweis": "Heuristische Prüfung (Muster-Erkennung) — ersetzt keine Rechtsberatung. "
                       "Bei fehlenden Punkten oder Risiken vor Unterschrift anwaltlich klären."}


# --- Arbeitszeit-Erfassung -------------------------------------------------------------

def lade_zeiten():
    return lade("zeiten.json", [])


# --- Täglicher Radar-Auto-Scan (7 Uhr) — zusätzlich zum "Jetzt scannen"-Button ---------

def autoscan_pruefen():
    """Wird bei jedem Stats-Aufruf geprüft UND von einem Hintergrund-Thread:
    einmal pro Tag ab konfigurierter Stunde automatisch scannen."""
    cfg = lade_config()
    radar = lade("radar.json", {"seen": [], "treffer": [], "letzter_scan": None})
    heute = datetime.now().date().isoformat()
    if radar.get("letzter_autoscan") == heute:
        return False
    if datetime.now().hour < int(cfg.get("radar_autoscan_stunde", 7)):
        return False
    radar["letzter_autoscan"] = heute
    speichere("radar.json", radar)  # Marker zuerst (verhindert Doppel-Scan)
    try:
        radar_scan()
        radar = lade("radar.json", {})
        radar["letzter_autoscan"] = heute
        speichere("radar.json", radar)
    except Exception as e:
        print(f"Auto-Scan fehlgeschlagen: {type(e).__name__}: {e}")
    return True


def autoscan_thread():
    while True:
        try:
            autoscan_pruefen()
        except Exception:
            pass
        time.sleep(600)  # alle 10 Minuten prüfen (scannt trotzdem max. 1x/Tag)


# --- API: UI & Health ---------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "leadpilot-crm", "port": PORT,
                    "smtp_konfiguriert": smtp_konfiguriert()})


@app.route("/api/stats")
def stats():
    erinnert = pruefe_erinnerungen()  # Mail-2-Prüfung bei jedem Dashboard-Aufruf
    cfg = lade_config()
    leads = lade_leads()
    outbox = lade("outbox.json", [])
    radar = lade("radar.json", {"treffer": [], "letzter_scan": None})
    woche = datetime.now() - timedelta(days=7)
    offen = [l for l in leads if l["stufe"] not in ("gewonnen", "verloren")]
    return jsonify({
        "leads_gesamt": len(leads),
        "leads_offen": len(offen),
        "leads_neu_7_tage": len([l for l in leads
                                 if datetime.fromisoformat(l["erstellt"]) > woche]),
        "gewonnen": len([l for l in leads if l["stufe"] == "gewonnen"]),
        "pipeline_wert": sum(float(l.get("wert_eur") or 0) for l in offen),
        "je_stufe": {s["id"]: len([l for l in leads if l["stufe"] == s["id"]]) for s in STUFEN},
        "mails_gesendet": len([m for m in outbox if m["status"] == "gesendet"]),
        "mails_wartend": len([m for m in outbox if m["status"] != "gesendet"]),
        "radar_treffer": len(radar["treffer"]),
        "radar_letzter_scan": radar["letzter_scan"],
        "dsgvo_faellig": len(dsgvo_faellige(leads, cfg)),
        "smtp_konfiguriert": smtp_konfiguriert(),
        "soeben_erinnert": erinnert,
        "stufen": STUFEN,
        "naechste_termine": sorted(
            [{"termin": l["termin"], "termin_text": termin_text(l["termin"]),
              "name": l.get("name", ""), "projektart": l.get("projektart", ""), "id": l["id"]}
             for l in leads if l.get("termin") and not l.get("anonymisiert")
             and l["termin"][:16] >= datetime.now().strftime("%Y-%m-%dT%H:%M")],
            key=lambda x: x["termin"])[:5],
    })


# --- API: Leads -----------------------------------------------------------------------

@app.route("/api/leads")
def api_leads():
    leads = lade_leads()
    stufe = request.args.get("stufe")
    q = (request.args.get("q") or "").lower()
    if stufe:
        leads = [l for l in leads if l["stufe"] == stufe]
    if q:
        leads = [l for l in leads if q in json.dumps(l, ensure_ascii=False).lower()]
    return jsonify({"leads": leads, "stufen": STUFEN})


@app.route("/api/leads", methods=["POST"])
def api_lead_neu():
    daten = request.get_json(silent=True) or {}
    if not (daten.get("name") or daten.get("email")):
        return jsonify({"error": "Name oder E-Mail ist Pflicht"}), 400
    lead, neu = neuer_lead(daten, daten.get("quelle") or "manuell")
    return jsonify({"lead": lead, "neu_angelegt": neu}), 201


@app.route("/api/leads/<lead_id>", methods=["PUT"])
def api_lead_update(lead_id):
    daten = request.get_json(silent=True) or {}
    leads = lade_leads()
    lead = finde_lead(leads, lead_id)
    if not lead:
        return jsonify({"error": "Lead nicht gefunden"}), 404
    for feld in ("name", "email", "telefon", "firma", "projektart", "nachricht", "wert_eur", "termin"):
        if feld in daten:
            lead[feld] = daten[feld]
    protokoll(lead, "Daten bearbeitet")
    speichere("leads.json", leads)
    return jsonify(lead)


@app.route("/api/leads/<lead_id>/move", methods=["POST"])
def api_lead_move(lead_id):
    stufe = (request.get_json(silent=True) or {}).get("stufe")
    if stufe not in STUFEN_IDS:
        return jsonify({"error": f"Unbekannte Stufe: {stufe}"}), 400
    leads = lade_leads()
    lead = finde_lead(leads, lead_id)
    if not lead:
        return jsonify({"error": "Lead nicht gefunden"}), 404
    protokoll(lead, f"Stufe: {lead['stufe']} → {stufe}")
    lead["stufe"] = stufe
    speichere("leads.json", leads)
    return jsonify(lead)


@app.route("/api/leads/<lead_id>/notiz", methods=["POST"])
def api_lead_notiz(lead_id):
    text = ((request.get_json(silent=True) or {}).get("text") or "").strip()
    if not text:
        return jsonify({"error": "Leere Notiz"}), 400
    leads = lade_leads()
    lead = finde_lead(leads, lead_id)
    if not lead:
        return jsonify({"error": "Lead nicht gefunden"}), 404
    protokoll(lead, f"Notiz: {text[:500]}")
    speichere("leads.json", leads)
    return jsonify(lead)


@app.route("/api/leads/<lead_id>/export")
def api_lead_export(lead_id):
    """DSGVO Art. 15 — vollständige Auskunft als JSON-Download."""
    lead = finde_lead(lade_leads(), lead_id)
    if not lead:
        return jsonify({"error": "Lead nicht gefunden"}), 404
    outbox = [m for m in lade("outbox.json", []) if m.get("lead_id") == lead_id]
    return jsonify({"export_zeitpunkt": _now(), "lead": lead, "mails": outbox})


@app.route("/api/leads/<lead_id>", methods=["DELETE"])
def api_lead_loeschen(lead_id):
    """DSGVO Art. 17 — vollständige Löschung inkl. zugehöriger Mails."""
    leads = lade_leads()
    lead = finde_lead(leads, lead_id)
    if not lead:
        return jsonify({"error": "Lead nicht gefunden"}), 404
    leads.remove(lead)
    speichere("leads.json", leads)
    outbox = [m for m in lade("outbox.json", []) if m.get("lead_id") != lead_id]
    speichere("outbox.json", outbox)
    return jsonify({"geloescht": lead_id})


@app.route("/api/leads/<lead_id>/anonymisieren", methods=["POST"])
def api_lead_anonymisieren(lead_id):
    leads = lade_leads()
    lead = finde_lead(leads, lead_id)
    if not lead:
        return jsonify({"error": "Lead nicht gefunden"}), 404
    anonymisiere(lead)
    speichere("leads.json", leads)
    return jsonify(lead)


@app.route("/api/dsgvo/aufraeumen", methods=["POST"])
def api_dsgvo_aufraeumen():
    cfg = lade_config()
    leads = lade_leads()
    faellig = dsgvo_faellige(leads, cfg)
    for lead in faellig:
        anonymisiere(lead)
    speichere("leads.json", leads)
    return jsonify({"anonymisiert": len(faellig)})


# --- API: Webhooks (Stufe 1 des Konzepts) ------------------------------------------------

@app.route("/api/webhooks/kontaktformular", methods=["POST"])
def webhook_formular():
    daten = request.get_json(silent=True) or request.form.to_dict() or {}
    if not daten.get("email"):
        return jsonify({"error": "email fehlt"}), 400
    lead, neu = neuer_lead(daten, "formular")
    return jsonify({"ok": True, "lead_id": lead["id"], "neu_angelegt": neu}), 201


@app.route("/api/webhooks/calcom", methods=["POST"])
def webhook_calcom():
    """Cal.com Webhook (BOOKING_CREATED): Buchung wird zum Lead mit Termin."""
    body = request.get_json(silent=True) or {}
    payload = body.get("payload", body)
    attendee = (payload.get("attendees") or [{}])[0]
    daten = {
        "name": attendee.get("name", ""),
        "email": attendee.get("email", ""),
        "projektart": payload.get("title") or payload.get("eventTitle", "Terminbuchung"),
        "nachricht": (payload.get("additionalNotes") or "")[:2000],
        "termin": payload.get("startTime", ""),
    }
    if not daten["email"]:
        return jsonify({"error": "Kein Teilnehmer im Payload"}), 400
    lead, neu = neuer_lead(daten, "calcom")
    return jsonify({"ok": True, "lead_id": lead["id"], "neu_angelegt": neu}), 201


# --- API: Radar, Postausgang, Config ------------------------------------------------------

@app.route("/api/radar")
def api_radar():
    radar = lade("radar.json", {"treffer": [], "letzter_scan": None})
    return jsonify({"treffer": radar["treffer"][:150], "letzter_scan": radar["letzter_scan"],
                    "quellen": [q["name"] for q in RADAR_QUELLEN]
                               + [q.get("name", "eigene") for q in lade_config().get("radar_quellen_eigene", [])]})


@app.route("/api/radar/scan", methods=["POST"])
def api_radar_scan():
    return jsonify(radar_scan())


@app.route("/api/radar/<treffer_id>/uebernehmen", methods=["POST"])
def api_radar_uebernehmen(treffer_id):
    radar = lade("radar.json", {"seen": [], "treffer": [], "letzter_scan": None})
    t = next((x for x in radar["treffer"] if x["id"] == treffer_id), None)
    if not t:
        return jsonify({"error": "Treffer nicht gefunden"}), 404
    lead, neu = neuer_lead({
        "name": t["quelle"], "projektart": t["titel"],
        "nachricht": f"Lead-Radar-Treffer ({', '.join(t['keywords'])}): {t['url']}",
    }, "radar")
    radar["treffer"].remove(t)
    speichere("radar.json", radar)
    return jsonify({"ok": True, "lead_id": lead["id"]})


@app.route("/api/outbox")
def api_outbox():
    return jsonify({"mails": lade("outbox.json", [])[:100],
                    "smtp_konfiguriert": smtp_konfiguriert()})


@app.route("/api/config", methods=["GET", "PUT"])
def api_config():
    if request.method == "GET":
        return jsonify(lade_config())
    daten = request.get_json(silent=True) or {}
    cfg = lade("config.json", {})
    for k in DEFAULT_CONFIG:
        if k in daten:
            cfg[k] = daten[k]
    speichere("config.json", cfg)
    return jsonify(lade_config())


# --- API: Kunden ------------------------------------------------------------------------

@app.route("/api/kunden")
def api_kunden():
    return jsonify({"kunden": lade_kunden()})


@app.route("/api/kunden", methods=["POST"])
def api_kunde_neu():
    d = request.get_json(silent=True) or {}
    if not d.get("name"):
        return jsonify({"error": "Name ist Pflicht"}), 400
    kunden = lade_kunden()
    kunde = {"id": str(uuid.uuid4()), "status": d.get("status", "neu"),
             "erstellt": _now(), "lead_id": d.get("lead_id", "")}
    for f in ("name", "firma", "email", "telefon", "adresse", "ansprechpartner",
              "ust_id", "notizen", "stundensatz"):
        kunde[f] = d.get(f, "")
    kunden.insert(0, kunde)
    speichere("kunden.json", kunden)
    return jsonify(kunde), 201


@app.route("/api/kunden/<kid>", methods=["PUT"])
def api_kunde_update(kid):
    d = request.get_json(silent=True) or {}
    kunden = lade_kunden()
    kunde = next((k for k in kunden if k["id"] == kid), None)
    if not kunde:
        return jsonify({"error": "Kunde nicht gefunden"}), 404
    for f in ("name", "firma", "email", "telefon", "adresse", "ansprechpartner",
              "ust_id", "notizen", "status", "stundensatz"):
        if f in d:
            kunde[f] = d[f]
    speichere("kunden.json", kunden)
    return jsonify(kunde)


@app.route("/api/kunden/<kid>", methods=["DELETE"])
def api_kunde_loeschen(kid):
    kunden = [k for k in lade_kunden() if k["id"] != kid]
    speichere("kunden.json", kunden)
    return jsonify({"geloescht": kid})


@app.route("/api/leads/<lead_id>/zum-kunden", methods=["POST"])
def api_lead_zum_kunden(lead_id):
    lead = finde_lead(lade_leads(), lead_id)
    if not lead:
        return jsonify({"error": "Lead nicht gefunden"}), 404
    kunden = lade_kunden()
    vorhanden = next((k for k in kunden if k.get("email") and
                      k["email"].lower() == (lead.get("email") or "").lower()), None)
    if vorhanden:
        return jsonify({"kunde": vorhanden, "neu": False})
    kunde = {"id": str(uuid.uuid4()), "name": lead.get("name", ""),
             "firma": lead.get("firma", ""), "email": lead.get("email", ""),
             "telefon": lead.get("telefon", ""), "adresse": "", "ansprechpartner": "",
             "ust_id": "", "notizen": f"Aus Lead übernommen ({lead.get('projektart', '')})",
             "status": "neu", "stundensatz": "", "erstellt": _now(), "lead_id": lead_id}
    kunden.insert(0, kunde)
    speichere("kunden.json", kunden)
    return jsonify({"kunde": kunde, "neu": True}), 201


# --- API: Leistungskatalog ----------------------------------------------------------------

@app.route("/api/katalog")
def api_katalog():
    return jsonify({"katalog": lade_katalog()})


@app.route("/api/katalog", methods=["POST"])
def api_katalog_neu():
    d = request.get_json(silent=True) or {}
    if not d.get("name"):
        return jsonify({"error": "Name ist Pflicht"}), 400
    kat = lade_katalog()
    eintrag = {"id": str(uuid.uuid4()), "name": d["name"][:200],
               "typ": d.get("typ", "dienstleistung"), "einheit": d.get("einheit", "Std"),
               "preis_eur": float(d.get("preis_eur") or 0),
               "marktpreis": d.get("marktpreis", ""), "plattform": d.get("plattform", "—"),
               "aktiv": bool(d.get("aktiv", True))}
    kat.insert(0, eintrag)
    speichere("katalog.json", kat)
    return jsonify(eintrag), 201


@app.route("/api/katalog/<eid>", methods=["PUT", "DELETE"])
def api_katalog_bearbeiten(eid):
    kat = lade_katalog()
    eintrag = next((k for k in kat if k["id"] == eid), None)
    if not eintrag:
        return jsonify({"error": "Eintrag nicht gefunden"}), 404
    if request.method == "DELETE":
        kat.remove(eintrag)
        speichere("katalog.json", kat)
        return jsonify({"geloescht": eid})
    d = request.get_json(silent=True) or {}
    for f in ("name", "typ", "einheit", "preis_eur", "marktpreis", "plattform", "aktiv"):
        if f in d:
            eintrag[f] = d[f]
    speichere("katalog.json", kat)
    return jsonify(eintrag)


# --- API: Dokumente (Angebot/Rechnung/Mahnung/Vertrag) --------------------------------------

@app.route("/api/dokumente")
def api_dokumente():
    doks = lade_dokumente()
    typ = request.args.get("typ")
    if typ:
        doks = [d for d in doks if d["typ"] == typ]
    # Überfällige Rechnungen markieren
    heute = datetime.now().date().isoformat()
    for d in doks:
        if (d["typ"] == "rechnung" and d["status"] == "gesendet"
                and d.get("faellig_bis") and d["faellig_bis"] < heute):
            d["status"] = "ueberfaellig"
    return jsonify({"dokumente": doks, "typen": DOK_TYPEN})


@app.route("/api/dokumente", methods=["POST"])
def api_dokument_neu():
    d = request.get_json(silent=True) or {}
    typ = d.get("typ")
    if typ not in DOK_TYPEN:
        return jsonify({"error": "Unbekannter Dokumenttyp"}), 400
    kunde = next((k for k in lade_kunden() if k["id"] == d.get("kunde_id")), None)
    if not kunde:
        return jsonify({"error": "Kunde wählen (zuerst unter Kunden anlegen)"}), 400
    cfg = lade_config()
    doks = lade_dokumente()
    dok = {
        "id": str(uuid.uuid4()), "typ": typ, "nummer": naechste_nummer(doks, typ),
        "kunde_id": kunde["id"], "kunde_name": kunde["name"],
        "datum": datetime.now().date().isoformat(),
        "leistungszeitraum": d.get("leistungszeitraum", ""),
        "positionen": d.get("positionen", []),
        "intro": d.get("intro", ""), "outro": d.get("outro", ""),
        "status": "entwurf", "bezug_id": d.get("bezug_id", ""),
        "faellig_bis": (datetime.now().date()
                        + timedelta(days=int(cfg["zahlungsziel_tage"]))).isoformat(),
        "erstellt": _now(),
    }
    if typ == "vertrag":
        adresse_kunde = ", ".join((kunde.get("adresse") or "Adresse").splitlines())
        ust_klausel = ("Als Kleinunternehmer i. S. d. §19 UStG wird keine Umsatzsteuer berechnet."
                       if cfg["kleinunternehmer"] else
                       "Alle Beträge verstehen sich zuzüglich der gesetzlichen Umsatzsteuer.")
        dok["vertragstext"] = VERTRAG_VORLAGE.format(
            firma_name=cfg["firma_name"],
            firma_adresse_zeile=", ".join(cfg["firma_adresse"].splitlines()),
            kunde_name=(kunde.get("firma") or kunde["name"]),
            kunde_adresse_zeile=adresse_kunde,
            leistung=d.get("leistung", "IT-Dienstleistungen gemäß Angebot"),
            verguetung=d.get("verguetung", f"{cfg['stundensatz_standard']} € pro Stunde"),
            zahlungsziel=cfg["zahlungsziel_tage"],
            ust_klausel=ust_klausel,
            beginn=d.get("beginn", datetime.now().strftime("%d.%m.%Y")),
            laufzeit=d.get("laufzeit", "auf unbestimmte Zeit"),
            kuendigungsfrist=d.get("kuendigungsfrist", "14 Tagen zum Monatsende"),
            ort_datum=datetime.now().strftime("Ort, %d.%m.%Y"))
    berechne_summen(dok, cfg)
    doks.insert(0, dok)
    speichere("dokumente.json", doks)
    return jsonify(dok), 201


@app.route("/api/dokumente/<did>", methods=["PUT", "DELETE"])
def api_dokument_bearbeiten(did):
    doks = lade_dokumente()
    dok = next((x for x in doks if x["id"] == did), None)
    if not dok:
        return jsonify({"error": "Dokument nicht gefunden"}), 404
    if request.method == "DELETE":
        doks.remove(dok)
        speichere("dokumente.json", doks)
        return jsonify({"geloescht": did})
    d = request.get_json(silent=True) or {}
    for f in ("positionen", "intro", "outro", "status", "leistungszeitraum",
              "faellig_bis", "vertragstext"):
        if f in d:
            dok[f] = d[f]
    berechne_summen(dok, lade_config())
    speichere("dokumente.json", doks)
    return jsonify(dok)


@app.route("/api/dokumente/<did>/mahnung", methods=["POST"])
def api_mahnung_erstellen(did):
    """Erzeugt Zahlungserinnerung/Mahnung zu einer (überfälligen) Rechnung."""
    doks = lade_dokumente()
    rechnung = next((x for x in doks if x["id"] == did and x["typ"] == "rechnung"), None)
    if not rechnung:
        return jsonify({"error": "Rechnung nicht gefunden"}), 404
    stufe = int((request.get_json(silent=True) or {}).get("stufe", 1))
    cfg = lade_config()
    texte = {
        1: ("Zahlungserinnerung",
            f"sicher ist es Ihrer Aufmerksamkeit entgangen: Unsere Rechnung {rechnung['nummer']} "
            f"vom {rechnung['datum']} über {rechnung['summe_brutto']:.2f} € war am "
            f"{rechnung['faellig_bis']} fällig. Wir bitten um Ausgleich innerhalb von 7 Tagen. "
            "Sollte sich die Zahlung mit diesem Schreiben überschnitten haben, betrachten Sie es bitte als gegenstandslos."),
        2: ("1. Mahnung",
            f"trotz unserer Zahlungserinnerung ist die Rechnung {rechnung['nummer']} vom "
            f"{rechnung['datum']} über {rechnung['summe_brutto']:.2f} € weiterhin offen. "
            "Wir bitten um Zahlung innerhalb von 7 Tagen."),
        3: ("2. Mahnung",
            f"die Rechnung {rechnung['nummer']} über {rechnung['summe_brutto']:.2f} € ist trotz "
            "Erinnerung und Mahnung offen. Wir fordern Sie letztmalig zur Zahlung innerhalb von "
            "7 Tagen auf. Danach behalten wir uns vor, Verzugszinsen gemäß §288 BGB zu berechnen "
            "und das gerichtliche Mahnverfahren einzuleiten."),
    }
    titel, text = texte.get(stufe, texte[1])
    dok = {"id": str(uuid.uuid4()), "typ": "mahnung",
           "nummer": naechste_nummer(doks, "mahnung"),
           "kunde_id": rechnung["kunde_id"], "kunde_name": rechnung["kunde_name"],
           "datum": datetime.now().date().isoformat(), "leistungszeitraum": "",
           "positionen": [{"beschreibung": f"Offener Betrag aus Rechnung {rechnung['nummer']}",
                           "menge": 1, "einheit": "Pauschale", "preis": rechnung["summe_brutto"]}],
           "intro": text, "outro": "", "titel_zusatz": titel,
           "status": "entwurf", "bezug_id": rechnung["id"],
           "faellig_bis": (datetime.now().date() + timedelta(days=7)).isoformat(),
           "erstellt": _now(), "mahnstufe": stufe}
    berechne_summen(dok, cfg)
    dok["ust_prozent"] = 0
    dok["summe_ust"] = 0
    dok["summe_brutto"] = dok["summe_netto"]  # Mahnbetrag ist bereits brutto
    doks.insert(0, dok)
    speichere("dokumente.json", doks)
    return jsonify(dok), 201


@app.route("/dokument/<did>")
def dokument_drucken(did):
    dok = next((x for x in lade_dokumente() if x["id"] == did), None)
    if not dok:
        return "Dokument nicht gefunden", 404
    kunde = next((k for k in lade_kunden() if k["id"] == dok["kunde_id"]), {})
    return render_template("dokument.html", dok=dok, kunde=kunde, cfg=lade_config(),
                           titel=dok.get("titel_zusatz") or DOK_TYPEN[dok["typ"]])


@app.route("/api/vertrag/pruefen", methods=["POST"])
def api_vertrag_pruefen():
    text = (request.get_json(silent=True) or {}).get("text", "")
    if len(text) < 100:
        return jsonify({"error": "Bitte den vollständigen Vertragstext einfügen (min. 100 Zeichen)"}), 400
    return jsonify(pruefe_vertrag(text))


# --- API: Arbeitszeiten ----------------------------------------------------------------------

@app.route("/api/zeiten")
def api_zeiten():
    zeiten = lade_zeiten()
    kid = request.args.get("kunde_id")
    if kid:
        zeiten = [z for z in zeiten if z["kunde_id"] == kid]
    offen = [z for z in zeiten if not z.get("abgerechnet")]
    return jsonify({"zeiten": zeiten[:300],
                    "offen_stunden": round(sum(float(z["stunden"]) for z in offen), 2),
                    "offen_betrag": round(sum(float(z["stunden"]) * float(z["stundensatz"]) for z in offen), 2)})


@app.route("/api/zeiten", methods=["POST"])
def api_zeit_neu():
    d = request.get_json(silent=True) or {}
    if not (d.get("kunde_id") and d.get("stunden")):
        return jsonify({"error": "Kunde und Stunden sind Pflicht"}), 400
    cfg = lade_config()
    kunde = next((k for k in lade_kunden() if k["id"] == d["kunde_id"]), None)
    if not kunde:
        return jsonify({"error": "Kunde nicht gefunden"}), 404
    zeiten = lade_zeiten()
    z = {"id": str(uuid.uuid4()), "kunde_id": kunde["id"], "kunde_name": kunde["name"],
         "datum": d.get("datum") or datetime.now().date().isoformat(),
         "stunden": round(float(d["stunden"]), 2),
         "beschreibung": (d.get("beschreibung") or "")[:300],
         "stundensatz": float(d.get("stundensatz") or kunde.get("stundensatz")
                              or cfg["stundensatz_standard"]),
         "abgerechnet": False, "erstellt": _now()}
    zeiten.insert(0, z)
    speichere("zeiten.json", zeiten)
    return jsonify(z), 201


@app.route("/api/zeiten/<zid>", methods=["DELETE"])
def api_zeit_loeschen(zid):
    zeiten = [z for z in lade_zeiten() if z["id"] != zid]
    speichere("zeiten.json", zeiten)
    return jsonify({"geloescht": zid})


@app.route("/api/zeiten/abrechnen", methods=["POST"])
def api_zeiten_abrechnen():
    """Alle offenen Zeiten eines Kunden -> Rechnungs-Entwurf (Positionen je Tag)."""
    kid = (request.get_json(silent=True) or {}).get("kunde_id")
    kunde = next((k for k in lade_kunden() if k["id"] == kid), None)
    if not kunde:
        return jsonify({"error": "Kunde nicht gefunden"}), 404
    zeiten = lade_zeiten()
    offene = [z for z in zeiten if z["kunde_id"] == kid and not z.get("abgerechnet")]
    if not offene:
        return jsonify({"error": "Keine offenen Zeiten für diesen Kunden"}), 400
    cfg = lade_config()
    doks = lade_dokumente()
    positionen = [{"beschreibung": f"{z['datum']}: {z['beschreibung'] or 'IT-Dienstleistung'}",
                   "menge": z["stunden"], "einheit": "Std", "preis": z["stundensatz"]}
                  for z in sorted(offene, key=lambda x: x["datum"])]
    dok = {"id": str(uuid.uuid4()), "typ": "rechnung",
           "nummer": naechste_nummer(doks, "rechnung"),
           "kunde_id": kid, "kunde_name": kunde["name"],
           "datum": datetime.now().date().isoformat(),
           "leistungszeitraum": f"{offene[-1]['datum']} – {offene[0]['datum']}",
           "positionen": positionen, "intro": "", "outro": "",
           "status": "entwurf", "bezug_id": "",
           "faellig_bis": (datetime.now().date()
                           + timedelta(days=int(cfg["zahlungsziel_tage"]))).isoformat(),
           "erstellt": _now()}
    berechne_summen(dok, cfg)
    doks.insert(0, dok)
    speichere("dokumente.json", doks)
    for z in zeiten:
        if z["kunde_id"] == kid and not z.get("abgerechnet"):
            z["abgerechnet"] = True
            z["rechnung_id"] = dok["id"]
    speichere("zeiten.json", zeiten)
    return jsonify({"rechnung": dok, "abgerechnete_zeiten": len(offene)}), 201


if __name__ == "__main__":
    threading.Thread(target=autoscan_thread, daemon=True).start()
    print(f"LeadPilot CRM läuft auf http://localhost:{PORT}"
          + ("" if smtp_konfiguriert() else "  (SMTP nicht konfiguriert — Mails landen im Postausgang)"))
    app.run(host="127.0.0.1", port=PORT, debug=False)
