# -*- coding: utf-8 -*-
"""
Market-Research-Agent v1 (AI Business Checker) — erster lauffähiger Dienst.

Durchsucht Reddit (öffentliche JSON-API), RSS-Feeds (Verbraucherportale) und
optional SearXNG nach neuen "Geld verdienen mit KI"-Angeboten und Beschwerden,
bewertet Funde heuristisch gegen den Warnsignal-Katalog W1-W8 und liefert
Themen-Kandidaten als JSON. Dedup gegen bereits gesehene URLs.

v1 = Heuristik ohne LLM-Pflicht: Wenn LiteLLM (:4000) erreichbar ist, wird
optional eine Zusammenfassung erzeugt; sonst funktioniert alles trotzdem.
Agent-Prompt/Spezifikation: ../Konzept-KI Avatar/market-research-agent.md

Start:  python 10_Business/KI-Avatar/research-agent/app.py
URL:    http://localhost:5320
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

from flask import Flask, jsonify, render_template, request

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STORE_FILE = os.path.join(DATA_DIR, "research_store.json")

PORT = int(os.environ.get("RESEARCH_AGENT_PORT", "5320"))
SEARXNG_URL = os.environ.get("SEARXNG_URL", "").rstrip("/")  # optional, z.B. http://localhost:8888
# Browser-UA: Reddits JSON-API liefert 403 für Skript-UAs, die RSS-Endpunkte
# (search.rss) funktionieren mit Browser-UA — deshalb v1 komplett über RSS/Atom.
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# --- Quellen-Konfiguration ---------------------------------------------------

REDDIT_SUBS = ["Scams", "passive_income", "Finanzen", "artificial"]
REDDIT_QUERIES = [
    "AI money", "KI Geld verdienen", "AI trading bot", "AI side hustle scam",
    "chatgpt money", "passive income AI",
]
# Eingebaute Feeds — global: DE/AT, USA, Vietnam (Kanal-Ziel: weltweite Sichtbarkeit).
# Verbraucherschutz-Portale und seriöse News-Rubriken, die wie Verbraucherzentralen
# dokumentieren. Eigene Quellen kommen zusätzlich aus data/custom_sources.json.
RSS_FEEDS = [
    {"name": "Verbraucherdienst-Blog", "markt": "DE", "url": "https://blog.verbraucherdienst.com/feed/"},
    {"name": "Watchlist Internet", "markt": "AT", "url": "https://www.watchlist-internet.at/rss/"},
    {"name": "FTC Consumer Alerts", "markt": "US", "url": "https://consumer.ftc.gov/blog/rss"},
    {"name": "FTC Consumer Protection News", "markt": "US", "url": "https://www.ftc.gov/feeds/press-release-consumer-protection.xml"},
    {"name": "VnExpress Pháp luật", "markt": "VN", "url": "https://vnexpress.net/rss/phap-luat.rss"},
    {"name": "VnExpress Số hóa", "markt": "VN", "url": "https://vnexpress.net/rss/so-hoa.rss"},
    {"name": "Tuổi Trẻ Pháp luật", "markt": "VN", "url": "https://tuoitre.vn/rss/phap-luat.rss"},
]
CUSTOM_SOURCES_FILE = os.path.join(DATA_DIR, "custom_sources.json")
SEARX_QUERIES = [
    "KI Geld verdienen Erfahrungen seriös", "AI Trading Bot Abzocke",
    "mit ChatGPT Geld verdienen Kurs Erfahrungen",
]

# --- Warnsignal-Heuristik (Katalog W1-W8 aus market-research-agent.md) -------

WARNSIGNALE = {
    "W1": {"name": "Einkommensversprechen",
           "muster": [r"\d+\s*(€|\$|euro|dollar)\s*(am tag|pro tag|täglich|/tag|a day|per day|daily)",
                      r"passiv(es)?\s*einkommen", r"passive income", r"schnell\s*(reich|geld)",
                      r"get rich", r"guaranteed (income|profit|returns)", r"garantiert\w*\s*(gewinn|einkommen|rendite)",
                      r"(earn|make)\s*\$?\d+", r"việc nhẹ lương cao", r"kiếm\s*(tiền|\d+\s*(triệu|tr)\b)",
                      r"lợi nhuận\s*(cao|khủng|cam kết)", r"thu nhập thụ động"]},
    "W2": {"name": "Künstlicher Zeitdruck",
           "muster": [r"nur noch \d+ (plätze|plätzen|spots)", r"limited (spots|time)", r"countdown",
                      r"nur (heute|diese woche)", r"last chance"]},
    "W3": {"name": "Impressum/Firmensitz",
           "muster": [r"kein impressum", r"no imprint", r"briefkastenfirma", r"offshore",
                      r"impressum fehlt", r"fake (firma|company|address)"]},
    "W4": {"name": "Gekaufte Social Proofs",
           "muster": [r"fake (bewertung|review|testimonial)", r"gekaufte bewertung",
                      r"bot (comments|kommentare)", r"paid review"]},
    "W5": {"name": "Vorauszahlung/Advance-Fee",
           "muster": [r"(erst|zuerst|upfront)\s*(einzahlen|bezahlen|zahlen|deposit|pay)",
                      r"auszahlung.{0,40}(gebühr|fee|freischalt)", r"withdrawal fee",
                      r"kann nicht auszahlen", r"can'?t withdraw"]},
    "W6": {"name": "Unklares Geschäftsmodell",
           "muster": [r"(kurs|course|mentoring|coaching).{0,50}(verkauf|sell|teuer|\d{3,}\s*€)",
                      r"mlm", r"pyramid", r"schneeball", r"ponzi", r"đa cấp", r"mô hình kim tự tháp"]},
    "W7": {"name": "Fake-Autorität",
           "muster": [r"bekannt aus", r"as seen on", r"(forbes|höhle der löwen|galileo).{0,30}(fake|lüge|nie)",
                      r"fake (celebrity|promi)", r"deepfake.{0,30}(werbung|ad)"]},
    "W8": {"name": "Abo-Falle",
           "muster": [r"abo[- ]?falle", r"versteckte kosten", r"hidden (fees|costs)",
                      r"kündigung.{0,40}(unmöglich|schwer|nicht)", r"subscription trap"]},
}
SCAM_HINWEIS = [r"scam", r"abzock\w*", r"betrug", r"betrüger", r"fraud", r"warnung", r"warning",
                r"seriös\??", r"legit\??", r"erfahrung(en)?", r"rip[- ]?off", r"finger weg",
                # Vietnamesisch: Betrug / Warnung / Geld verloren / erschlichen
                r"lừa đảo", r"cảnh báo", r"mất tiền", r"chiếm đoạt", r"sập bẫy"]
# Der Kanal prüft speziell KI-Angebote — ohne KI-Bezug kein Video-Kandidat
KI_RELEVANZ = [r"\bki\b", r"\ba\.?i\.?\b", r"künstliche intelligenz", r"artificial intelligence",
               r"chatgpt", r"gpt", r"deepfake", r"trading[- ]?bot", r"ai[- ]?bot",
               r"algorithm\w*", r"machine learning", r"neural", r"midjourney", r"claude",
               r"trí tuệ nhân tạo", r"công nghệ ai"]

app = Flask(__name__)


def _now():
    return datetime.now().isoformat(timespec="seconds")


def load_store():
    if not os.path.exists(STORE_FILE):
        return {"seen_urls": [], "funde": [], "letzter_scan": None}
    with open(STORE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_store(store):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = STORE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STORE_FILE)


def http_get(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "ignore")


# --- Eigene Quellen (vom User über die UI hinzugefügte Foren/Websites/Feeds) ---

def load_custom_sources():
    if not os.path.exists(CUSTOM_SOURCES_FILE):
        return []
    with open(CUSTOM_SOURCES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_custom_sources(quellen):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = CUSTOM_SOURCES_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(quellen, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CUSTOM_SOURCES_FILE)


def erkenne_quelle(url):
    """Prüft eine URL: RSS/Atom-Feed, HTML-Seite mit Feed-Link, oder reine HTML-Seite.
    Gibt (typ, feed_url, seitentitel) zurück. Wirft Exception bei Nichterreichbarkeit."""
    inhalt = http_get(url)
    kopf = inhalt[:3000].lower()
    if "<rss" in kopf or "<feed" in kopf or kopf.strip().startswith("<?xml"):
        return "feed", url, ""
    # HTML: nach verlinktem RSS/Atom-Feed suchen (<link type="application/rss+xml" href=...>)
    m = re.search(r'<link[^>]+type=["\']application/(?:rss|atom)\+xml["\'][^>]*href=["\']([^"\']+)["\']',
                  inhalt, re.I) or \
        re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*type=["\']application/(?:rss|atom)\+xml["\']',
                  inhalt, re.I)
    titel_m = re.search(r"<title[^>]*>([^<]+)</title>", inhalt, re.I)
    titel = (titel_m.group(1).strip() if titel_m else "")[:120]
    if m:
        feed_url = urllib.parse.urljoin(url, m.group(1))
        return "feed", feed_url, titel
    return "html", url, titel


def scan_custom(fehler):
    """Eigene Quellen scannen: Feeds wie eingebaute Feeds, HTML-Seiten als Volltext."""
    funde = []
    for q in load_custom_sources():
        try:
            if q["typ"] == "feed":
                for item in parse_feed(http_get(q["feed_url"])):
                    funde.append({
                        "quelle": f"eigene: {q['name']}",
                        "titel": item["titel"],
                        "url": item["url"],
                        "datum": item["datum"],
                        "text_auszug": item["beschreibung"][:500],
                        "_volltext": item["titel"] + " " + item["beschreibung"],
                    })
            else:  # HTML-Seite: sichtbaren Text extrahieren, als ein Fund scannen
                html = http_get(q["url"])
                text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
                text = re.sub(r"<[^>]+>", " ", text)
                text = re.sub(r"\s+", " ", text)[:6000]
                # Inhalts-Hash in der Dedup-URL: geänderte Seite = neuer Fund,
                # unveränderte Seite wird nicht doppelt gemeldet
                h = hashlib.md5(text.encode("utf-8")).hexdigest()[:10]
                funde.append({
                    "quelle": f"eigene: {q['name']}",
                    "titel": q.get("seitentitel") or q["name"],
                    "url": q["url"] + "#v-" + h,
                    "datum": "",
                    "text_auszug": text[:500],
                    "_volltext": text,
                })
        except Exception as e:
            fehler.append(f"eigene {q['name']}: {type(e).__name__}")
    return funde


def bewerte_text(text, quelle=""):
    """Prüft Text gegen Warnsignal-Katalog. Gibt (treffer, score, ki_relevanz) zurück."""
    t = text.lower()
    treffer = []
    for code, sig in WARNSIGNALE.items():
        for muster in sig["muster"]:
            m = re.search(muster, t)
            if m:
                treffer.append({"code": code, "name": sig["name"], "beleg_zitat": m.group(0)[:120]})
                break
    hinweis_score = sum(1 for p in SCAM_HINWEIS if re.search(p, t))
    ki_relevanz = any(re.search(p, t) for p in KI_RELEVANZ)
    score = len(treffer) * 2 + min(hinweis_score, 4)
    if ki_relevanz:
        score += 2
    if quelle.startswith(("Watchlist", "Verbraucherdienst")):
        score += 1  # redaktionell vorgeprüfte Warnungen wiegen mehr
    return treffer, score, ki_relevanz


# --- Feed-Parsing (RSS 2.0 <item> UND Atom <entry>, Namespace-agnostisch) -----

def _tag(el):
    return el.tag.split("}")[-1]


def _text(parent, name):
    for child in parent:
        if _tag(child) == name:
            return (child.text or "").strip()
    return ""


def parse_feed(xml_text):
    """Liefert Items aus RSS- oder Atom-Feeds als einheitliche Dicts."""
    items = []
    root = ET.fromstring(xml_text)
    for el in root.iter():
        if _tag(el) not in ("item", "entry"):
            continue
        titel = _text(el, "title")
        link = _text(el, "link")
        if not link:  # Atom: <link href="..."/>
            for child in el:
                if _tag(child) == "link" and child.get("href"):
                    link = child.get("href")
                    break
        beschreibung = _text(el, "description") or _text(el, "content") or _text(el, "summary")
        beschreibung = re.sub(r"<[^>]+>", " ", beschreibung)
        datum = _text(el, "pubDate") or _text(el, "updated") or _text(el, "published")
        items.append({"titel": titel[:200], "url": link, "datum": datum[:30],
                      "beschreibung": beschreibung[:1500]})
    return items


# --- Quellen-Scanner ----------------------------------------------------------

def scan_reddit(fehler):
    """Reddit-Suche über die RSS-Endpunkte (JSON-API liefert 403, RSS nicht)."""
    funde = []
    for sub in REDDIT_SUBS:
        for query in REDDIT_QUERIES[:2]:  # Rate-Limit-freundlich
            url = (f"https://old.reddit.com/r/{sub}/search.rss?"
                   + urllib.parse.urlencode({"q": query, "sort": "new", "t": "month",
                                             "restrict_sr": "on", "limit": 15}))
            try:
                for item in parse_feed(http_get(url)):
                    text = item["titel"] + " " + item["beschreibung"]
                    funde.append({
                        "quelle": f"reddit/r/{sub}",
                        "titel": item["titel"],
                        "url": item["url"],
                        "datum": item["datum"],
                        "text_auszug": item["beschreibung"][:500],
                        "_volltext": text,
                    })
                time.sleep(4)  # Reddit drosselt RSS bei <2s Abstand (429)
            except Exception as e:
                fehler.append(f"reddit/r/{sub} '{query}': {type(e).__name__}")
    return funde


def scan_rss(fehler):
    funde = []
    for feed in RSS_FEEDS:
        try:
            for item in parse_feed(http_get(feed["url"])):
                funde.append({
                    "quelle": feed["name"],
                    "titel": item["titel"],
                    "url": item["url"],
                    "datum": item["datum"],
                    "text_auszug": item["beschreibung"][:500],
                    "_volltext": item["titel"] + " " + item["beschreibung"],
                })
        except Exception as e:
            fehler.append(f"rss {feed['name']}: {type(e).__name__}")
    return funde


def scan_searxng(fehler):
    """Optional: nur wenn SEARXNG_URL gesetzt und erreichbar."""
    if not SEARXNG_URL:
        return []
    funde = []
    for query in SEARX_QUERIES:
        url = f"{SEARXNG_URL}/search?" + urllib.parse.urlencode({"q": query, "format": "json"})
        try:
            data = json.loads(http_get(url))
            for r in data.get("results", [])[:10]:
                text = (r.get("title", "") + " " + r.get("content", ""))
                funde.append({
                    "quelle": "searxng",
                    "titel": r.get("title", "")[:200],
                    "url": r.get("url", ""),
                    "datum": "",
                    "text_auszug": r.get("content", "")[:500],
                    "_volltext": text,
                })
        except Exception as e:
            fehler.append(f"searxng '{query}': {type(e).__name__}")
    return funde


def scan_alle():
    """Alle Quellen scannen, bewerten, deduplizieren, persistieren."""
    store = load_store()
    seen = set(store["seen_urls"])
    fehler = []
    roh = scan_reddit(fehler) + scan_rss(fehler) + scan_searxng(fehler) + scan_custom(fehler)

    neue_funde = []
    for f in roh:
        if not f["url"] or f["url"] in seen:
            continue
        seen.add(f["url"])
        treffer, score, ki_relevanz = bewerte_text(f.pop("_volltext"), f["quelle"])
        if score < 2:  # gar kein Signal -> Rauschen, verwerfen
            continue
        f["warnsignale"] = treffer
        f["score"] = score
        f["ki_relevanz"] = ki_relevanz
        # Video-Kandidat nur mit KI-Bezug (Kanal-Fokus!) + starkem Signal
        f["empfehlung"] = ("video_kandidat" if ki_relevanz and score >= 6 and treffer
                           else "beobachtungsliste" if ki_relevanz and score >= 4
                           else "hinweis")
        f["gefunden_am"] = _now()
        neue_funde.append(f)

    neue_funde.sort(key=lambda x: -x["score"])
    store["seen_urls"] = list(seen)[-5000:]
    store["funde"] = (neue_funde + store["funde"])[:500]
    store["letzter_scan"] = _now()
    save_store(store)
    return {
        "neue_funde": len(neue_funde),
        "video_kandidaten": [f for f in neue_funde if f["empfehlung"] == "video_kandidat"],
        "beobachtungsliste": [f for f in neue_funde if f["empfehlung"] == "beobachtungsliste"],
        "quellen_fehler": fehler,
        "hinweis": "v1-Heuristik: Kandidaten sind VOR-gefiltert, kein Ersatz für das Dossier "
                   "(2-Quellen-Minimum + Belege) laut market-research-agent.md",
    }


# --- API ----------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    store = load_store()
    return jsonify({"status": "ok", "service": "ki-avatar-research-agent", "port": PORT,
                    "letzter_scan": store["letzter_scan"], "funde_gesamt": len(store["funde"]),
                    "searxng": bool(SEARXNG_URL)})


@app.route("/api/scan", methods=["POST"])
def api_scan():
    return jsonify(scan_alle())


@app.route("/api/quellen")
def api_quellen():
    eingebaut = ([{"name": f"reddit/r/{s}", "markt": "global", "typ": "feed"} for s in REDDIT_SUBS]
                 + [{"name": f["name"], "markt": f["markt"], "typ": "feed"} for f in RSS_FEEDS])
    return jsonify({"eingebaut": eingebaut, "eigene": load_custom_sources()})


@app.route("/api/quellen", methods=["POST"])
def api_quelle_hinzufuegen():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url.startswith(("http://", "https://")):
        return jsonify({"error": "Bitte eine vollständige URL angeben (https://...)"}), 400
    quellen = load_custom_sources()
    if any(q["url"] == url for q in quellen):
        return jsonify({"error": "Diese Quelle ist schon eingetragen"}), 400
    try:
        typ, feed_url, seitentitel = erkenne_quelle(url)
    except Exception as e:
        return jsonify({"error": f"Quelle nicht erreichbar: {type(e).__name__}"}), 400
    name = (data.get("name") or "").strip() or seitentitel or urllib.parse.urlparse(url).netloc
    quelle = {"name": name[:80], "url": url, "typ": typ, "feed_url": feed_url,
              "seitentitel": seitentitel, "hinzugefuegt": _now()}
    quellen.append(quelle)
    save_custom_sources(quellen)
    return jsonify({"ok": True, "quelle": quelle,
                    "hinweis": ("Als RSS/Atom-Feed erkannt — Einträge werden wie ein Portal gescannt."
                                if typ == "feed" else
                                "Kein Feed gefunden — die Seite wird als Ganzes auf Warnsignale gescannt "
                                "(bei Änderung der Seite entsteht ein neuer Fund).")}), 201


@app.route("/api/quellen", methods=["DELETE"])
def api_quelle_loeschen():
    url = (request.args.get("url") or "").strip()
    quellen = load_custom_sources()
    neu = [q for q in quellen if q["url"] != url]
    if len(neu) == len(quellen):
        return jsonify({"error": "Quelle nicht gefunden"}), 404
    save_custom_sources(neu)
    return jsonify({"ok": True, "geloescht": url})


@app.route("/api/funde")
def api_funde():
    store = load_store()
    limit = int(request.args.get("limit", 50))
    nur = request.args.get("empfehlung")
    funde = store["funde"]
    if nur:
        funde = [f for f in funde if f.get("empfehlung") == nur]
    return jsonify({"letzter_scan": store["letzter_scan"], "funde": funde[:limit]})


if __name__ == "__main__":
    if "--scan" in sys.argv:  # CLI-Modus: einmal scannen, Ergebnis ausgeben, Ende
        print(json.dumps(scan_alle(), ensure_ascii=False, indent=2))
    else:
        print(f"Market-Research-Agent v1 läuft auf http://localhost:{PORT}")
        app.run(host="127.0.0.1", port=PORT, debug=False)
