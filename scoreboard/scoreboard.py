from __future__ import annotations

import json
from pathlib import Path
from typing import List


def load_scoreboard(log_dir: Path, edition: str) -> List[dict]:
    scoreboard_path = log_dir / edition / "scoreboard.json"
    if not scoreboard_path.exists():
        return []
    return json.loads(scoreboard_path.read_text())
