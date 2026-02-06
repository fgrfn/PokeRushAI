from __future__ import annotations

import argparse
from pathlib import Path

from bot.rl_bot import BotSettings, PokeRushBot
from core.config import build_config
from emulator.pyboy_emulator import EmulatorSettings, PyBoyEmulator
from run_logging.run_logger import RunLogger


def run_bot(edition: str, max_steps: int, allow_missing_rom: bool) -> None:
    base_dir = Path(__file__).resolve().parent
    config = build_config(base_dir)
    edition_config = config.editions[edition]
    emulator = PyBoyEmulator(
        edition_config.rom_path,
        settings=EmulatorSettings(allow_missing_rom=allow_missing_rom),
    )
    logger = RunLogger(config.log_dir, edition)
    bot = PokeRushBot(
        emulator=emulator,
        logger=logger,
        data_path=config.data_dir / "state.json",
        settings=BotSettings(actions=["UP", "DOWN", "LEFT", "RIGHT", "A", "B"], max_steps=max_steps),
    )
    bot.run(milestones=["Start", "First Badge", "Elite Four"])


def run_web(host: str, port: int) -> None:
    from web_ui.app import app

    app.run(debug=True, host=host, port=port)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PokéRushAI control center")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bot_parser = subparsers.add_parser("bot", help="Run the RL bot")
    bot_parser.add_argument("--edition", default="red", choices=["red", "blue", "yellow"])
    bot_parser.add_argument("--max-steps", type=int, default=100)
    bot_parser.add_argument(
        "--require-rom",
        action="store_false",
        dest="allow_missing_rom",
        help="Fail if the ROM is missing",
    )
    bot_parser.set_defaults(allow_missing_rom=True)

    web_parser = subparsers.add_parser("web", help="Run the web UI")
    web_parser.add_argument("--host", default="0.0.0.0")
    web_parser.add_argument("--port", type=int, default=5000)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "bot":
        run_bot(args.edition, args.max_steps, args.allow_missing_rom)
    if args.command == "web":
        run_web(args.host, args.port)


if __name__ == "__main__":
    main()
