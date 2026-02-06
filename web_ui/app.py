from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from core.config import build_config
from scoreboard.scoreboard import load_scoreboard


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG = build_config(BASE_DIR)
STATE_PATH = CONFIG.data_dir / "state.json"

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index() -> str:
    return render_template("index.html", editions=CONFIG.editions)


@app.route("/api/state")
def api_state():
    if not STATE_PATH.exists():
        return jsonify({"status": "missing", "state": {}})
    return jsonify({"status": "ok", "state": json.loads(STATE_PATH.read_text())})


@app.route("/api/scoreboard")
def api_scoreboard():
    edition = request.args.get("edition", "red")
    return jsonify({"edition": edition, "runs": load_scoreboard(CONFIG.log_dir, edition)})


@app.route("/api/maps")
def api_maps():
    return jsonify(
        {
            key: {"name": edition.name, "map_url": edition.map_url}
            for key, edition in CONFIG.editions.items()
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
