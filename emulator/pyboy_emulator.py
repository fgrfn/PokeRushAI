from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pyboy import PyBoy
from core.models import GameState


@dataclass
class EmulatorSettings:
    frame_skip: int = 0
    emulation_speed: float = 1.0
    show_window: bool = True  # Show SDL2 window for visualization


class PyBoyEmulator:
    """Thin wrapper around PyBoy to keep the bot modular."""

    def __init__(self, rom_path: Path, settings: Optional[EmulatorSettings] = None) -> None:
        self.rom_path = rom_path
        self.settings = settings or EmulatorSettings()
        self._loaded = False
        self.pyboy: Optional[PyBoy] = None

    def load(self) -> None:
        if not self.rom_path.exists():
            raise FileNotFoundError(
                f"ROM not found at {self.rom_path}. Place the ROM before running."
            )
        window_type = "SDL2" if self.settings.show_window else "null"
        
        self.pyboy = PyBoy(
            str(self.rom_path),
            window=window_type,
            sound=False,
        )
        self._loaded = True
        print(f" PyBoy loaded: {self.rom_path.name}")
        print(f" Cartridge: {self.pyboy.cartridge_title}")
        print(f" Window mode: {window_type}")

    def get_state(self) -> GameState:
        if not self._loaded or not self.pyboy:
            raise RuntimeError("Emulator not loaded. Call load() first.")
        
        from emulator.pokemon_memory import (
            MEMORY_MAP, get_map_name, count_badges, get_edition_from_title
        )
        
        edition = get_edition_from_title(self.pyboy.cartridge_title)
        x = self.read_memory(MEMORY_MAP["PLAYER_X"])
        y = self.read_memory(MEMORY_MAP["PLAYER_Y"])
        map_id = self.read_memory(MEMORY_MAP["MAP_ID"])
        location =get_map_name(map_id)
        badge_byte = self.read_memory(MEMORY_MAP["BADGES"])
        badges = count_badges(badge_byte)
        
        hours_high = self.read_memory(MEMORY_MAP["PLAYTIME_HOURS_HIGH"])
        hours_low = self.read_memory(MEMORY_MAP["PLAYTIME_HOURS_LOW"])
        hours = (hours_high << 8) | hours_low
        minutes = self.read_memory(MEMORY_MAP["PLAYTIME_MINUTES"])
        seconds = self.read_memory(MEMORY_MAP["PLAYTIME_SECONDS"])
        play_time_seconds = hours * 3600 + minutes * 60 + seconds
        
        map_id = self.read_memory(MEMORY_MAP["MAP_ID"])
        
        return GameState(
            edition=edition, location=location, x=x, y=y, map_id=map_id,
            badges=badges, play_time_seconds=float(play_time_seconds),
        )

    def step(self, action: str) -> None:
        if not self._loaded or not self.pyboy:
            raise RuntimeError("Emulator not loaded. Call load() first.")
        
        button_map = {
            "A": "a", "B": "b", "START": "start", "SELECT": "select",
            "UP": "up", "DOWN": "down", "LEFT": "left", "RIGHT": "right",
        }
        
        button_code = button_map.get(action.upper())
        if button_code:
            self.pyboy.button_press(button_code)
            for _ in range(8):
                self.pyboy.tick()
            self.pyboy.button_release(button_code)
            for _ in range(8):
                self.pyboy.tick()

    def read_memory(self, address: int) -> int:
        if not self._loaded or not self.pyboy:
            raise RuntimeError("Emulator not loaded.")
        return self.pyboy.memory[address]
    
    def write_memory(self, address: int, value: int) -> None:
        if not self._loaded or not self.pyboy:
            raise RuntimeError("Emulator not loaded.")
        self.pyboy.memory[address] = value
    
    def tick(self, count: int = 1) -> None:
        if not self._loaded or not self.pyboy:
            raise RuntimeError("Emulator not loaded.")
        for _ in range(count):
            self.pyboy.tick()
    
    def stop(self) -> None:
        """Stop and cleanup the emulator."""
        if self.pyboy:
            self.pyboy.stop()
            self._loaded = False
            print("✓ Emulator stopped")
            self._loaded = False
