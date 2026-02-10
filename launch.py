#!/usr/bin/env python3
"""PokeRushAI Launcher - Bot mit PyBoy-Fenster + WebUI Stats.

EINFACHER START:
    python launch.py

Features:
    ✅ PyBoy-Fenster (sichtbar, spielbar)
    ✅ WebUI für Stats-Monitoring
    ✅ Badge-Checkpoints
    ✅ Bestenliste
"""

import sys
import webbrowser
import time
import threading
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Disable Flask/Werkzeug HTTP logs (nur Bot-Logs anzeigen)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def run_bot():
    """Run bot with PyBoy window."""
    from bot.rl_bot import BotSettings, PokeRushBot
    from core.config import build_config
    from emulator.pyboy_emulator import PyBoyEmulator, EmulatorSettings
    from run_logging.run_logger import RunLogger
    
    base_dir = Path(__file__).resolve().parent
    config = build_config(base_dir)
    
    # PyBoy mit sichtbarem Fenster!
    emulator_settings = EmulatorSettings(
        show_window=True,  # SDL2 Fenster anzeigen
        emulation_speed=1.0
    )
    
    rom_path = config.project_root / "roms" / "pokered.gb"
    emulator = PyBoyEmulator(rom_path, settings=emulator_settings)
    logger = RunLogger(config.log_dir, "red")
    
    bot = PokeRushBot(
        emulator=emulator,
        logger=logger,
        data_path=config.data_dir / "state.json",
        settings=BotSettings(
            actions=["UP", "DOWN", "LEFT", "RIGHT", "A", "B"],
            max_steps=500000  # Badge Challenge
        )
    )
    
    print("🎮 Starting Bot with PyBoy Window...")
    bot.run(milestones=[], auto_start=False, use_init_state=False)  # Manual mode: you play the intro!

def run_webui():
    """Run WebUI for monitoring."""
    from web_ui.app import app
    
    print("🌐 Starting WebUI on http://localhost:5000")
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True, use_reloader=False)

def main():
    """Start both bot and WebUI."""
    print("\n" + "=" * 70)
    print("  🎮 POKERUSH AI - Q-Learning Bot with PyBoy Window")
    print("=" * 70)
    print()
    print("Starting:")
    print("   🎮 Bot with PyBoy SDL2 Window")
    print("   🌐 WebUI Stats Dashboard: http://localhost:5000")
    print()
    print(" PyBoy-Fenster:")
    print("   ✅ Sichtbar - Du siehst das Spiel!")
    print("   ✅ Bot spielt automatisch")
    print("   ✅ Badge-Tracking aktiviert")
    print()
    print(" WebUI Dashboard:")
    print("   📊 Live Stats (Map, Team, Geld)")
    print("   📈 Training Metrics")
    print("   🏆 Bestenliste")
    print("   📍 Badge-Checkpoints")
    print()
    print(" ⏱️  Badge Challenge Mode:")
    print("   • Bot läuft bis alle 8 Badges erreicht sind")
    print("   • Max 500.000 Steps")
    print()
    print("Press Ctrl+C to stop both")
    print("=" * 70)
    print()
    
    # Start bot in separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=False)
    bot_thread.start()
    
    # Wait a bit for bot to initialize
    time.sleep(2)
    
    # Auto-open browser
    def open_browser():
        time.sleep(1)
        try:
            webbrowser.open("http://localhost:5000")
        except:
            pass
    
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    try:
        # Start WebUI (blocks main thread)
        run_webui()
    except KeyboardInterrupt:
        print("\n\n✅ Shutting down...")
        return 0

if __name__ == "__main__":
    sys.exit(main())
