from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from core.models import GameState, RunDecision, RunSummary, SplitTime


class RunLogger:
    def __init__(self, base_log_dir: Path, edition: str) -> None:
        self.base_log_dir = base_log_dir
        self.edition = edition
        self.edition_dir = base_log_dir / edition
        self.edition_dir.mkdir(parents=True, exist_ok=True)
        self.counter_path = self.edition_dir / "run_counter.json"

    def start_run(self, milestones: Iterable[str]) -> int:
        run_id = self._next_run_id()
        start_time = self._timestamp()
        run_dir = self._run_dir(run_id)
        run_dir.mkdir(parents=True, exist_ok=True)
        metadata = {
            "run_id": run_id,
            "edition": self.edition,
            "started_at": start_time,
            "milestones": list(milestones),
        }
        (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
        (run_dir / "decisions.jsonl").write_text("")
        (run_dir / "events.jsonl").write_text("")
        return run_id

    def log_decision(self, run_id: int, decision: RunDecision, state: GameState) -> None:
        payload = {
            "step": decision.step,
            "action": decision.action,
            "reason": decision.reason,
            "timestamp": decision.timestamp,
            "state": {
                "location": state.location,
                "x": state.x,
                "y": state.y,
                "badges": state.badges,
                "play_time_seconds": state.play_time_seconds,
            },
        }
        self._append_jsonl(run_id, "decisions.jsonl", payload)

    def log_event(
        self,
        run_id: int,
        level: str,
        message: str,
        details: Optional[Dict[str, object]] = None,
    ) -> None:
        payload = {
            "timestamp": self._timestamp(),
            "level": level,
            "message": message,
        }
        if details:
            payload["details"] = details
        self._append_jsonl(run_id, "events.jsonl", payload)
        self._print_event(payload)

    def finish_run(self, run_id: int) -> None:
        run_dir = self._run_dir(run_id)
        summary = RunSummary(
            run_id=run_id,
            edition=self.edition,
            started_at=self._read_metadata(run_id).get("started_at", ""),
            finished_at=self._timestamp(),
            total_time_seconds=self._elapsed_seconds(run_id),
            split_times=self._load_split_times(run_id),
        )
        (run_dir / "summary.json").write_text(
            json.dumps(self._summary_to_dict(summary), indent=2)
        )
        self._update_scoreboard(summary)

    def _summary_to_dict(self, summary: RunSummary) -> Dict[str, object]:
        return {
            "run_id": summary.run_id,
            "edition": summary.edition,
            "started_at": summary.started_at,
            "finished_at": summary.finished_at,
            "total_time_seconds": summary.total_time_seconds,
            "split_times": [
                {"name": split.name, "time_seconds": split.time_seconds}
                for split in summary.split_times
            ],
            "metadata": summary.metadata,
        }

    def _update_scoreboard(self, summary: RunSummary) -> None:
        scoreboard_path = self.edition_dir / "scoreboard.json"
        if scoreboard_path.exists():
            entries = json.loads(scoreboard_path.read_text())
        else:
            entries = []
        entries.append(self._summary_to_dict(summary))
        entries.sort(key=lambda entry: entry.get("total_time_seconds", 0))
        scoreboard_path.write_text(json.dumps(entries, indent=2))

    def _load_split_times(self, run_id: int) -> List[SplitTime]:
        split_path = self._run_dir(run_id) / "splits.json"
        if not split_path.exists():
            return []
        data = json.loads(split_path.read_text())
        return [SplitTime(**split) for split in data]

    def _read_metadata(self, run_id: int) -> Dict[str, object]:
        metadata_path = self._run_dir(run_id) / "metadata.json"
        if not metadata_path.exists():
            return {}
        return json.loads(metadata_path.read_text())

    def _elapsed_seconds(self, run_id: int) -> float:
        metadata = self._read_metadata(run_id)
        started_at = metadata.get("started_at")
        if not started_at:
            return 0.0
        return time.time() - time.mktime(time.strptime(started_at, "%Y-%m-%dT%H:%M:%SZ"))

    def _append_jsonl(self, run_id: int, filename: str, payload: Dict[str, object]) -> None:
        path = self._run_dir(run_id) / filename
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")

    def _print_event(self, payload: Dict[str, object]) -> None:
        timestamp = payload.get("timestamp", "")
        level = payload.get("level", "info").upper()
        message = payload.get("message", "")
        details = payload.get("details")
        if details:
            print(f"[{timestamp}] [{level}] {message} | {details}")
        else:
            print(f"[{timestamp}] [{level}] {message}")

    def _next_run_id(self) -> int:
        if self.counter_path.exists():
            payload = json.loads(self.counter_path.read_text())
            run_id = int(payload.get("next_id", 1))
        else:
            run_id = 1
        self.counter_path.write_text(json.dumps({"next_id": run_id + 1}, indent=2))
        return run_id

    def _run_dir(self, run_id: int) -> Path:
        return self.edition_dir / f"run_{run_id:04d}"

    def _timestamp(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
