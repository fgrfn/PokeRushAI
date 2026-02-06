from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass(frozen=True)
class EditionConfig:
    name: str
    rom_path: Path
    map_url: str


@dataclass(frozen=True)
class AppConfig:
    base_dir: Path
    editions: Dict[str, EditionConfig]
    data_dir: Path
    log_dir: Path


def build_config(base_dir: Path) -> AppConfig:
    data_dir = base_dir / "data"
    log_dir = base_dir / "logs"
    editions = {
        "red": EditionConfig(
            name="Red",
            rom_path=base_dir / "roms" / "pokemon_red.gb",
            map_url=(
                "https://raw.githubusercontent.com/pret/pokered/master/maps/overworld.png"
            ),
        ),
        "blue": EditionConfig(
            name="Blue",
            rom_path=base_dir / "roms" / "pokemon_blue.gb",
            map_url=(
                "https://raw.githubusercontent.com/pret/pokeblue/master/maps/overworld.png"
            ),
        ),
        "yellow": EditionConfig(
            name="Yellow",
            rom_path=base_dir / "roms" / "pokemon_yellow.gbc",
            map_url=(
                "https://raw.githubusercontent.com/pret/pokeyellow/master/maps/overworld.png"
            ),
        ),
    }
    return AppConfig(base_dir=base_dir, editions=editions, data_dir=data_dir, log_dir=log_dir)
