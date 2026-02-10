#!/usr/bin/env python3
"""PokeRushAI - CLI Entry Point.

Usage:
    python main.py bot [options]              # Run bot only
    python main.py webui [options]            # Run WebUI only
    python main.py interactive [options]      # Run bot + WebUI together
    
Bot Options:
    --max-steps N         Maximum training steps (default: 50000)
    --use-init-state      Load init_state.state for fast training
    --auto-start          Auto-start game (vs manual intro)
    --show-window         Show PyBoy SDL2 window
    --headless            Run without window (faster)
    --edition EDITION     Pokemon edition: red/blue/yellow (default: red)
    
WebUI Options:
    --port PORT           WebUI port (default: 5000)
    --no-browser          Don't auto-open browser
    
Examples:
    # Fast training with init state
    python main.py bot --use-init-state --max-steps 100000
    
    # Visible window for watching
    python main.py bot --show-window --max-steps 10000
    
    # Interactive mode (recommended)
    python main.py interactive
    
    # Just WebUI
    python main.py webui --port 8080
"""

import sys
import argparse
import webbrowser
import time
import threading
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Disable Flask/Werkzeug HTTP logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def run_bot_cli(args):
    """Run bot in CLI mode."""
    from bot.rl_bot import BotSettings, PokeRushBot
    from core.config import build_config
    from emulator.pyboy_emulator import PyBoyEmulator, EmulatorSettings
    from run_logging.run_logger import RunLogger
    
    base_dir = Path(__file__).resolve().parent
    config = build_config(base_dir)
    
    # Emulator settings
    show_window = args.show_window or (not args.headless)
    emulator_settings = EmulatorSettings(
        show_window=show_window,
        emulation_speed=1.0 if show_window else 0  # Unlimited speed when headless
    )
    
    # Select ROM
    edition = args.edition.lower()
    if edition == "red":
        rom_path = config.project_root / "roms" / "pokered.gb"
    elif edition == "blue":
        rom_path = config.project_root / "roms" / "pokeblue.gb"
    elif edition == "yellow":
        rom_path = config.project_root / "roms" / "pokeyellow.gb"
    else:
        print(f"❌ Unknown edition: {edition}")
        return 1
    
    if not rom_path.exists():
        print(f"❌ ROM not found: {rom_path}")
        print(f"   Please place the ROM at {rom_path}")
        return 1
    
    emulator = PyBoyEmulator(rom_path, settings=emulator_settings)
    logger = RunLogger(config.log_dir, edition)
    
    bot = PokeRushBot(
        emulator=emulator,
        logger=logger,
        data_path=config.data_dir / "state.json",
        settings=BotSettings(
            actions=["UP", "DOWN", "LEFT", "RIGHT", "A", "B"],
            max_steps=args.max_steps
        )
    )
    
    print("\n" + "=" * 70)
    print("  🎮 POKERUSH AI - Q-Learning Bot")
    print("=" * 70)
    print(f"\n📋 Configuration:")
    print(f"   Edition: {edition.upper()}")
    print(f"   Max Steps: {args.max_steps:,}")
    print(f"   Window: {'Visible' if show_window else 'Headless'}")
    print(f"   Init State: {'Enabled' if args.use_init_state else 'Disabled'}")
    print(f"   Auto-Start: {'Yes' if args.auto_start else 'No (Manual)'}")
    print(f"   ROM: {rom_path.name}")
    print()
    
    if args.use_init_state:
        init_state_path = config.data_dir / "init_state.state"
        if not init_state_path.exists():
            print(f"⚠️  Init state not found: {init_state_path}")
            print(f"   Create it first: python create_init_state.py")
            return 1
        print(f"✅ Init state loaded from: {init_state_path}")
        print()
    
    # Load init state if requested
    if args.use_init_state:
        init_state_path = config.data_dir / "init_state.state"
        emulator.load()
        with open(init_state_path, "rb") as f:
            emulator.pyboy.load_state(f)
        print("🚀 Starting from init state (Pallet Town)...")
        # Pass use_init_state=True to prevent emulator.load() in bot.run()
        bot.run(milestones=[], auto_start=False, use_init_state=True)
    else:
        print("🚀 Starting bot...")
        bot.run(milestones=[], auto_start=args.auto_start, use_init_state=False)
    
    return 0


def run_webui_cli(args):
    """Run WebUI only."""
    from web_ui.app import app
    
    print("\n" + "=" * 70)
    print("  🌐 POKERUSH AI - WebUI Dashboard")
    print("=" * 70)
    print(f"\n📊 Dashboard starting on: http://localhost:{args.port}")
    print("\nFeatures:")
    print("   📈 Live training metrics")
    print("   🗺️  Game state visualization")
    print("   🏆 Scoreboard & leaderboards")
    print("   📍 Badge checkpoints")
    print("\nPress Ctrl+C to stop")
    print("=" * 70)
    print()
    
    # Auto-open browser
    if not args.no_browser:
        def open_browser():
            time.sleep(1.5)
            try:
                webbrowser.open(f"http://localhost:{args.port}")
            except:
                pass
        threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        app.run(debug=False, host="0.0.0.0", port=args.port, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n✅ WebUI stopped")
        return 0


def run_interactive(args):
    """Run bot + WebUI together."""
    from bot.rl_bot import BotSettings, PokeRushBot
    from core.config import build_config
    from emulator.pyboy_emulator import PyBoyEmulator, EmulatorSettings
    from run_logging.run_logger import RunLogger
    from web_ui.app import app
    
    base_dir = Path(__file__).resolve().parent
    config = build_config(base_dir)
    
    print("\n" + "=" * 70)
    print("  🎮 POKERUSH AI - Interactive Mode")
    print("=" * 70)
    print(f"\nStarting:")
    print(f"   🎮 Bot (Edition: {args.edition.upper()}, Steps: {args.max_steps:,})")
    print(f"   🌐 WebUI Dashboard: http://localhost:{args.port}")
    print()
    print("Press Ctrl+C to stop both")
    print("=" * 70)
    print()
    
    # Bot function
    def run_bot():
        show_window = args.show_window or (not args.headless)
        emulator_settings = EmulatorSettings(
            show_window=show_window,
            emulation_speed=1.0
        )
        
        edition = args.edition.lower()
        rom_path = config.project_root / "roms" / f"poke{edition}.gb" if edition != "red" else config.project_root / "roms" / "pokered.gb"
        
        if not rom_path.exists():
            print(f"❌ ROM not found: {rom_path}")
            return
        
        emulator = PyBoyEmulator(rom_path, settings=emulator_settings)
        logger = RunLogger(config.log_dir, edition)
        
        bot = PokeRushBot(
            emulator=emulator,
            logger=logger,
            data_path=config.data_dir / "state.json",
            settings=BotSettings(
                actions=["UP", "DOWN", "LEFT", "RIGHT", "A", "B"],
                max_steps=args.max_steps
            )
        )
        
        if args.use_init_state:
            init_state_path = config.data_dir / "init_state.state"
            if init_state_path.exists():
                emulator.load()
                with open(init_state_path, "rb") as f:
                    emulator.pyboy.load_state(f)
                bot.run(milestones=[], auto_start=False, use_init_state=True)
            else:
                print(f"⚠️  Init state not found, using auto-start")
                bot.run(milestones=[], auto_start=args.auto_start, use_init_state=False)
        else:
            bot.run(milestones=[], auto_start=args.auto_start, use_init_state=False)
    
    # Start bot in thread
    bot_thread = threading.Thread(target=run_bot, daemon=False)
    bot_thread.start()
    
    # Wait for bot to initialize
    time.sleep(2)
    
    # Auto-open browser
    if not args.no_browser:
        def open_browser():
            time.sleep(1)
            try:
                webbrowser.open(f"http://localhost:{args.port}")
            except:
                pass
        threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        app.run(debug=False, host="0.0.0.0", port=args.port, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n✅ Shutting down...")
        return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PokeRushAI - Q-Learning Pokemon Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Bot command
    bot_parser = subparsers.add_parser('bot', help='Run bot only')
    bot_parser.add_argument('--max-steps', type=int, default=50000,
                           help='Maximum training steps (default: 50000)')
    bot_parser.add_argument('--use-init-state', action='store_true',
                           help='Load init_state.state for fast training')
    bot_parser.add_argument('--auto-start', action='store_true',
                           help='Auto-start game (vs manual intro)')
    bot_parser.add_argument('--show-window', action='store_true',
                           help='Show PyBoy SDL2 window')
    bot_parser.add_argument('--headless', action='store_true',
                           help='Run without window (faster)')
    bot_parser.add_argument('--edition', type=str, default='red',
                           choices=['red', 'blue', 'yellow'],
                           help='Pokemon edition (default: red)')
    
    # WebUI command
    webui_parser = subparsers.add_parser('webui', help='Run WebUI only')
    webui_parser.add_argument('--port', type=int, default=5000,
                             help='WebUI port (default: 5000)')
    webui_parser.add_argument('--no-browser', action='store_true',
                             help="Don't auto-open browser")
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Run bot + WebUI together')
    interactive_parser.add_argument('--max-steps', type=int, default=500000,
                                   help='Maximum training steps (default: 500000)')
    interactive_parser.add_argument('--use-init-state', action='store_true',
                                   help='Load init_state.state for fast training')
    interactive_parser.add_argument('--auto-start', action='store_true',
                                   help='Auto-start game (vs manual intro)')
    interactive_parser.add_argument('--show-window', action='store_true', default=True,
                                   help='Show PyBoy SDL2 window (default: True)')
    interactive_parser.add_argument('--headless', action='store_true',
                                   help='Run without window')
    interactive_parser.add_argument('--edition', type=str, default='red',
                                   choices=['red', 'blue', 'yellow'],
                                   help='Pokemon edition (default: red)')
    interactive_parser.add_argument('--port', type=int, default=5000,
                                   help='WebUI port (default: 5000)')
    interactive_parser.add_argument('--no-browser', action='store_true',
                                   help="Don't auto-open browser")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'bot':
        return run_bot_cli(args)
    elif args.command == 'webui':
        return run_webui_cli(args)
    elif args.command == 'interactive':
        return run_interactive(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
