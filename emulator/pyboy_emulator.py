from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from core.models import GameState


@dataclass
class EmulatorSettings:
    frame_skip: int = 0
    emulation_speed: float = 1.0
    allow_missing_rom: bool = True


class PyBoyEmulator:
    """Thin wrapper around PyBoy to keep the bot modular.

    This stub exposes a minimal surface area while allowing the real PyBoy
    integration to be swapped in without touching the bot or UI.
    """

    def __init__(self, rom_path: Path, settings: Optional[EmulatorSettings] = None) -> None:
        self.rom_path = rom_path
        self.settings = settings or EmulatorSettings()
        self._loaded = False

    def load(self) -> None:
        if not self.rom_path.exists():
            if not self.settings.allow_missing_rom:
                raise FileNotFoundError(
                    f"ROM not found at {self.rom_path}. Place the ROM before running."
                )
        self._loaded = True

    def get_state(self) -> GameState:
        if not self._loaded:
            raise RuntimeError("Emulator not loaded. Call load() first.")
        return GameState(
            edition="red",
            location="Pallet Town",
            x=5,
            y=9,
            badges=0,
            play_time_seconds=0.0,
        )

    def step(self, action: str) -> None:
        if not self._loaded:
            raise RuntimeError("Emulator not loaded. Call load() first.")
        _ = action
