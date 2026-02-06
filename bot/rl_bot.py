from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from bot.policy import select_action
from core.models import GameState, RunDecision
from emulator.pyboy_emulator import PyBoyEmulator
from run_logging.run_logger import RunLogger


@dataclass
class BotSettings:
    actions: List[str]
    max_steps: int = 100


class PokeRushBot:
    def __init__(
        self,
        emulator: PyBoyEmulator,
        logger: RunLogger,
        data_path: Path,
        settings: BotSettings,
    ) -> None:
        self.emulator = emulator
        self.logger = logger
        self.data_path = data_path
        self.settings = settings

    def run(self, milestones: Iterable[str]) -> None:
        self.emulator.load()
        run_id = self.logger.start_run(milestones)
        for step in range(self.settings.max_steps):
            state = self.emulator.get_state()
            action = select_action(state, self.settings.actions)
            decision = RunDecision(
                step=step,
                action=action,
                reason="exploration",
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )
            self.emulator.step(action)
            self.logger.log_decision(run_id, decision, state)
            self._write_state(state)
            time.sleep(0.01)
        self.logger.finish_run(run_id)

    def _write_state(self, state: GameState) -> None:
        payload = {
            "edition": state.edition,
            "location": state.location,
            "x": state.x,
            "y": state.y,
            "badges": state.badges,
            "play_time_seconds": state.play_time_seconds,
        }
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.data_path.write_text(json.dumps(payload, indent=2))
