from __future__ import annotations
import json
import logging
import threading
import time
from pathlib import Path
from typing import Optional

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
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            content = STATE_PATH.read_text()
            if not content or len(content) < 2:
                if attempt < max_retries - 1:
                    time.sleep(0.05)
                    continue
                return jsonify({"status": "updating", "state": {}})
            state_data = json.loads(content)
            return jsonify({"status": "ok", "state": state_data})
        except (json.JSONDecodeError, FileNotFoundError):
            if attempt < max_retries - 1:
                time.sleep(0.05)
                continue
            return jsonify({"status": "updating", "state": {}})
        except Exception as e:
            return jsonify({"status": "error", "state": {}, "message": str(e)})
    return jsonify({"status": "updating", "state": {}})

@app.route("/api/scoreboard")
def api_scoreboard():
    edition = request.args.get("edition", "red")
    all_runs = load_scoreboard(CONFIG.log_dir, edition)
    filtered_runs = [run for run in all_runs if run.get("badges", 0) >= 1]
    return jsonify({"edition": edition, "runs": filtered_runs})

@app.route("/api/maps")
def api_maps():
    return jsonify({
        key: {"name": edition.name, "map_url": edition.map_url}
        for key, edition in CONFIG.editions.items()
    })

@app.route("/api/logs")
def api_logs():
    edition = request.args.get("edition", "red")
    max_count = int(request.args.get("max", 30))
    from run_logging.run_logger import RunLogger
    logger = RunLogger(CONFIG.log_dir, edition)
    latest_run_id = logger.get_latest_run_id()
    if latest_run_id is None:
        return jsonify({"status": "no_runs", "logs": []})
    logs = logger.get_recent_decisions(latest_run_id, max_count)
    return jsonify({"status": "ok", "run_id": latest_run_id, "logs": logs})

@app.route("/api/status")
def api_status():
    return jsonify({"emulator_running": False, "bot_running": False})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
