# -*- coding: utf-8 -*-
"""
KI-Avatar Pipeline-Board — Trello-artige Verwaltungsseite (AI-OS-Erweiterung).

Jedes Video ist eine Karte, die per Drag & Drop durch die 7 Pipeline-Stufen
wandert (Trend-Scan -> Skript -> Stimme -> Avatar -> Edit -> QA-Check ->
Posting -> Veroeffentlicht). Persistenz: data/board.json.

Start:  python "10_Business/01_Marktprodukte/KI-Avatar/board/app.py"
URL:    http://localhost:5310
"""
import json
import os
import sys
import uuid
from datetime import datetime

from flask import Flask, jsonify, render_template, request

# Windows-Konsole: UTF-8 erzwingen (bekannter Stolperstein im AI-OS)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "board.json")

PORT = int(os.environ.get("KIAVATAR_BOARD_PORT", "5310"))

STAGES = [
    {"id": "trend_scan",     "title": "Trend-Scan",     "subtitle": "SearXNG/Qdrant",   "color": "gray"},
    {"id": "skript",         "title": "Skript",          "subtitle": "Qwen3/Claude",     "color": "teal"},
    {"id": "stimme",         "title": "Stimme",          "subtitle": "Kokoro-TTS",       "color": "teal"},
    {"id": "avatar",         "title": "Avatar",          "subtitle": "HeyGen/Arcads",    "color": "coral"},
    {"id": "edit",           "title": "Edit",            "subtitle": "FFmpeg-Schnitt",   "color": "teal"},
    {"id": "qa_check",       "title": "QA-Check",        "subtitle": "KI-Label-Check",   "color": "teal"},
    {"id": "posting",        "title": "Posting",         "subtitle": "n8n Scheduler",    "color": "gray"},
    {"id": "veroeffentlicht","title": "Veröffentlicht",  "subtitle": "Live",             "color": "done"},
]
STAGE_IDS = {s["id"] for s in STAGES}

USECASES = {
    "youtube": "YouTube-Automation",
    "tiktok_shop": "TikTok-Shop",
    "ai_business_checker": "AI Business Checker",
}
PLATFORMS = ["tiktok", "youtube_shorts", "youtube_long", "instagram_reels"]
COMPLIANCE = ["open", "approved", "warning", "blocked"]

app = Flask(__name__)


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _seed_cards():
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "3 Dinge, die du beim Perfekt nicht wusstest",
            "usecase": "tiktok_shop",
            "platform": "tiktok",
            "channel": "Deutsch Dễ Hiểu",
            "notes": "Lernkarten-Set verlinken, Werbekennzeichnung Zeile 1",
            "stage": "qa_check",
            "compliance": "open",
            "created_at": _now(),
            "updated_at": _now(),
        },
        {
            "id": str(uuid.uuid4()),
            "title": "KI-News: Woche 29 Zusammenfassung",
            "usecase": "youtube",
            "platform": "youtube_shorts",
            "channel": "KI-News Redakteur",
            "notes": "",
            "stage": "skript",
            "compliance": "open",
            "created_at": _now(),
            "updated_at": _now(),
        },
    ]


def load_board():
    if not os.path.exists(DATA_FILE):
        board = {"cards": _seed_cards()}
        save_board(board)
        return board
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_board(board):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(board, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


def find_card(board, card_id):
    for card in board["cards"]:
        if card["id"] == card_id:
            return card
    return None


def validate_card_fields(data, partial=False):
    """Gibt (fehlerliste, bereinigte_felder) zurueck."""
    errors = []
    fields = {}
    checks = {
        "title": lambda v: isinstance(v, str) and v.strip(),
        "usecase": lambda v: v in USECASES,
        "platform": lambda v: v in PLATFORMS,
        "channel": lambda v: isinstance(v, str),
        "notes": lambda v: isinstance(v, str),
        "stage": lambda v: v in STAGE_IDS,
        "compliance": lambda v: v in COMPLIANCE,
    }
    for key, ok in checks.items():
        if key in data:
            if ok(data[key]):
                fields[key] = data[key].strip() if isinstance(data[key], str) else data[key]
            else:
                errors.append(f"Ungültiger Wert für '{key}'")
        elif not partial and key == "title":
            errors.append("'title' ist Pflicht")
    return errors, fields


@app.route("/")
def index():
    return render_template("board.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "ki-avatar-board", "port": PORT})


@app.route("/api/board")
def get_board():
    board = load_board()
    return jsonify({
        "stages": STAGES,
        "usecases": USECASES,
        "platforms": PLATFORMS,
        "compliance": COMPLIANCE,
        "cards": board["cards"],
    })


@app.route("/api/cards", methods=["POST"])
def create_card():
    data = request.get_json(silent=True) or {}
    errors, fields = validate_card_fields(data)
    if errors:
        return jsonify({"error": "; ".join(errors)}), 400
    card = {
        "id": str(uuid.uuid4()),
        "title": fields["title"],
        "usecase": fields.get("usecase", "youtube"),
        "platform": fields.get("platform", "youtube_shorts"),
        "channel": fields.get("channel", ""),
        "notes": fields.get("notes", ""),
        "stage": fields.get("stage", "trend_scan"),
        "compliance": fields.get("compliance", "open"),
        "created_at": _now(),
        "updated_at": _now(),
    }
    board = load_board()
    board["cards"].append(card)
    save_board(board)
    return jsonify(card), 201


@app.route("/api/cards/<card_id>", methods=["PUT"])
def update_card(card_id):
    data = request.get_json(silent=True) or {}
    errors, fields = validate_card_fields(data, partial=True)
    if errors:
        return jsonify({"error": "; ".join(errors)}), 400
    board = load_board()
    card = find_card(board, card_id)
    if not card:
        return jsonify({"error": "Karte nicht gefunden"}), 404
    card.update(fields)
    card["updated_at"] = _now()
    save_board(board)
    return jsonify(card)


@app.route("/api/cards/<card_id>", methods=["DELETE"])
def delete_card(card_id):
    board = load_board()
    card = find_card(board, card_id)
    if not card:
        return jsonify({"error": "Karte nicht gefunden"}), 404
    board["cards"].remove(card)
    save_board(board)
    return jsonify({"deleted": card_id})


@app.route("/api/cards/<card_id>/move", methods=["POST"])
def move_card(card_id):
    data = request.get_json(silent=True) or {}
    stage = data.get("stage")
    if stage not in STAGE_IDS:
        return jsonify({"error": f"Unbekannte Stufe: {stage}"}), 400
    board = load_board()
    card = find_card(board, card_id)
    if not card:
        return jsonify({"error": "Karte nicht gefunden"}), 404
    card["stage"] = stage
    card["updated_at"] = _now()
    save_board(board)
    return jsonify(card)


if __name__ == "__main__":
    print(f"KI-Avatar Pipeline-Board läuft auf http://localhost:{PORT}")
    app.run(host="127.0.0.1", port=PORT, debug=False)
