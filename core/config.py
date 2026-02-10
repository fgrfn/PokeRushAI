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
    project_root: Path
    editions: Dict[str, EditionConfig]
    data_dir: Path
    log_dir: Path


def build_config(base_dir: Path) -> AppConfig:
    data_dir = base_dir / "data"
    log_dir = base_dir / "logs"
    
    # Using high-quality Kanto map from PokemonRedExperiments
    # This map has pixel-perfect coordinates for all locations
    map_url = "https://raw.githubusercontent.com/PWhiddy/PokemonRedExperiments/master/visualization/poke_map/pokemap_full_calibrated_CROPPED_1.png"
    
    editions = {
        "red": EditionConfig(
            name="Red",
            rom_path=base_dir / "rom" / "pokemon_red.gb",
            map_url=map_url,
        ),
        "blue": EditionConfig(
            name="Blue",
            rom_path=base_dir / "rom" / "pokemon_blue.gb",
            map_url=map_url,
        ),
        "yellow": EditionConfig(
            name="Yellow",
            rom_path=base_dir / "rom" / "pokemon_yellow.gbc",
            map_url=map_url,
        ),
    }
    return AppConfig(
        base_dir=base_dir,
        project_root=base_dir,
        editions=editions,
        data_dir=data_dir,
        log_dir=log_dir
    )
