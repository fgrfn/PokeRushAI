from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GameState:
    edition: str
    location: str
    x: int
    y: int
    map_id: int
    badges: int
    play_time_seconds: float


@dataclass
class SplitTime:
    name: str
    time_seconds: float


@dataclass
class RunDecision:
    step: int
    action: str
    reason: str
    timestamp: str


@dataclass
class RunSummary:
    run_id: int
    edition: str
    started_at: str
    finished_at: str
    total_time_seconds: float
    split_times: List[SplitTime] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
