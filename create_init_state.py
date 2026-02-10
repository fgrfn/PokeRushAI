"""Create Initial Save State for Fast Bot Training.

Run this script ONCE to create a clean save state after completing the intro manually.
The bot will then load this state instantly instead of going through the intro every time.

Usage:
    python create_init_state.py
    
    1. PyBoy window opens
    2. Play through intro manually:
       - Press A through title
       - Select NEW GAME
       - Choose player name
       - Choose rival name
       - Get to Pallet Town (outside, controllable)
    3. Press ENTER when you have full control in Pallet Town
    4. Script saves the state to data/init_state.state
"""

from pathlib import Path
import sys
import time

from emulator.pyboy_emulator import PyBoyEmulator, EmulatorSettings
from core.config import build_config

def create_init_state():
    """Interactive state creator."""
    print("\n" + "="*70)
    print("📀 INITIAL STATE CREATOR")
    print("="*70)
    print()
    print("This tool creates a save state that the bot can load instantly,")
    print("skipping the intro sequence entirely (like PokemonRedExperiments).")
    print()
    print("INSTRUCTIONS:")
    print("  1. PyBoy window will open with the title screen")
    print("  2. Play through the intro manually:")
    print("     - Press A through copyright/intro")
    print("     - Select NEW GAME")
    print("     - Choose your player name (e.g., ASH)")
    print("     - Choose rival name (e.g., GARY)")
    print("     - Listen to Oak's speech")
    print("     - Walk to the door and exit Oak's lab")
    print("  3. Once you're OUTSIDE in Pallet Town with full control:")
    print("     - Press ENTER in this terminal to save the state")
    print()
    print("="*70)
    
    input("Press ENTER to start...")
    
    # Setup
    config = build_config(Path.cwd())
    
    # Use Pokemon Red by default
    edition = "red"
    if edition not in config.editions:
        print(f"❌ Edition '{edition}' not found!")
        return
    
    edition_config = config.editions[edition]
    save_path = config.data_dir / "init_state.state"
    
    print(f"\n🎮 Loading emulator...")
    print(f"   Edition: {edition_config.name}")
    print(f"   ROM: {edition_config.rom_path}")
    print(f"   Save will be created at: {save_path}")
    
    if not edition_config.rom_path.exists():
        print(f"\n❌ ROM not found: {edition_config.rom_path}")
        print("   Please place pokemon_red.gb in the roms/ folder")
        return
    
    # Load emulator with SDL2 window
    settings = EmulatorSettings(show_window=True)
    emulator = PyBoyEmulator(rom_path=edition_config.rom_path, settings=settings)
    emulator.load()
    
    print("\n✅ PyBoy window opened!")
    print("\n👉 Play through the intro now...")
    print("   Press ENTER in this terminal when you reach Pallet Town (outside)\n")
    
    # Windows input handling
    if sys.platform == "win32":
        import msvcrt
        
        print("⏳ Waiting for ENTER key...")
        frame = 0
        last_status = ""
        
        while True:
            emulator.pyboy.tick()
            frame += 1
            
            # Show status every 2 seconds
            if frame % 120 == 0:
                try:
                    state = emulator.get_state()
                    joypad = emulator.pyboy.memory[0xD79E]
                    battle = emulator.pyboy.memory[0xD057]
                    map_id = emulator.pyboy.memory[0xD35E]
                    
                    has_control = (joypad == 0) and (battle == 0)
                    in_pallet = "Pallet" in state.location
                    outside = map_id in [0, 1]
                    
                    status = f"📍 {state.location} (Map:{map_id})"
                    if has_control and in_pallet and outside:
                        status += " ✅ READY TO SAVE!"
                    elif not has_control:
                        status += " ⏸️  (In dialog/cutscene)"
                    elif not outside:
                        status += " 🏠 (Still inside building)"
                    
                    if status != last_status:
                        print(f"   {status}")
                        last_status = status
                except:
                    pass
            
            # Check for Enter key
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\r':  # Enter
                    break
            
            time.sleep(0.016)
    else:
        # Unix: just wait for Enter
        input()
    
    # Verify state before saving
    print("\n🔍 Verifying state...")
    try:
        state = emulator.get_state()
        joypad = emulator.pyboy.memory[0xD79E]
        battle = emulator.pyboy.memory[0xD057]
        map_id = emulator.pyboy.memory[0xD35E]
        
        print(f"   Location: {state.location}")
        print(f"   Map ID: {map_id}")
        print(f"   Coordinates: ({state.x}, {state.y})")
        print(f"   Joypad enabled: {joypad == 0}")
        print(f"   Not in battle: {battle == 0}")
        
        has_control = (joypad == 0) and (battle == 0)
        in_pallet = "Pallet" in state.location
        outside = map_id in [0, 1]
        
        if not (has_control and in_pallet):
            print("\n⚠️  WARNING: State might not be ideal!")
            if not has_control:
                print("   - Player doesn't have control (in dialog/cutscene?)")
            if not in_pallet:
                print("   - Not in Pallet Town")
            if not outside:
                print("   - Still inside a building (Oak's Lab?)")
            
            confirm = input("\nSave anyway? (y/n): ")
            if confirm.lower() != 'y':
                print("❌ Cancelled")
                emulator.stop()
                return
    except Exception as e:
        print(f"⚠️  Could not verify state: {e}")
        print("   Saving anyway...")
    
    # Save state
    print(f"\n💾 Saving state to {save_path}...")
    save_path.parent.mkdir(exist_ok=True)
    
    with open(save_path, "wb") as f:
        emulator.pyboy.save_state(f)
    
    print("✅ Initial state saved!")
    print()
    print("="*70)
    print("SUCCESS! Bot can now load this state instantly.")
    print()
    print("To use:")
    print("  1. Run: python launch.py")
    print("  2. Bot loads this state and starts immediately in Pallet Town")
    print("  3. No more intro/name selection needed!")
    print("="*70)
    
    # Cleanup
    emulator.stop()

if __name__ == "__main__":
    try:
        create_init_state()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
