from __future__ import annotations

import random
from typing import List

from core.models import GameState


def select_action(state: GameState, available_actions: List[str]) -> str:
    _ = state
    return random.choice(available_actions)
