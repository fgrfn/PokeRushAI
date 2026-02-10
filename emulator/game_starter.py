"""Game Starter - Automatically starts a new Pokemon game."""
from __future__ import annotations
import json, sys, time
from pathlib import Path
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from emulator.pyboy_emulator import PyBoyEmulator
class GameStarter:
    def __init__(self, emulator, player_name="ASH", data_dir=None):
        self.emulator = emulator
        self.player_name = player_name[:7].upper()
        self.data_dir = Path(data_dir or "data")
        self.data_dir.mkdir(exist_ok=True)
        self.learned_sequence_file = self.data_dir / "learned_game_start.json"
    def has_learned_sequence(self): return self.learned_sequence_file.exists()
    def wait_for_manual_start(self, max_wait_seconds=300, learn_mode=True):
        print("\n  MANUAL MODE"); print("="*60); print("Instructions:\n  1. PyBoy window\n  2. Press A\n  3. NEW GAME\n  4. Trainer name\n  5. Rival name\n  6. To Pallet Town")
        if learn_mode: print("\n Bot detects Pallet Town after 10 seconds\n   You have 10 seconds!")
        print("="*60); print("\n Booting...")
        for i in range(180):
            self.emulator.pyboy.tick()
            if i%60==0 and i>0: print(f"   Loading...{i}/180")
        print(" Ready!\n Watching for Pallet Town in 10s...\n")
        if sys.platform=="win32": import msvcrt
        start_time,frame_count,last_location,detection_delay,detection_active=time.time(),0,"",10.0,False
        try:
            while(time.time()-start_time)<max_wait_seconds:
                self.emulator.pyboy.tick(); frame_count+=1; elapsed=time.time()-start_time
                if not detection_active and elapsed>=detection_delay: detection_active=True; print(" Detection active!")
                if learn_mode and detection_active and frame_count%30==0:
                    try:
                        state=self.emulator.get_state(); current_location=state.location
                        if"Pallet"in current_location and"Pallet"not in last_location: print("\n Pallet Town detected!"); print(" Bot taking over..."); time.sleep(1); return True
                        if current_location!=last_location: print(f"   {current_location}")
                        last_location=current_location
                    except: pass
                if frame_count%600==0:
                    status="Active"if detection_active else f"{int(detection_delay-elapsed)}s until active"
                    print(f"  Waiting...({frame_count//60}s)[{status}]")
                if sys.platform=="win32" and msvcrt.kbhit():
                    if msvcrt.getch()==b'\r': print("\n Enter pressed"); return True
                time.sleep(0.016)
            print("\n Timeout"); return False
        except KeyboardInterrupt: print("\n Cancelled"); return False
    def start_new_game(self, max_attempts=400, use_learned=True):
        print("\n Auto-starting..."); print(f"   Player:{self.player_name}"); attempts,phase=0,"intro"
        while attempts<max_attempts:
            attempts+=1
            try: state=self.emulator.get_state(); location=state.location
            except: location="Unknown"
            if phase=="intro":
                if"Pallet"in location: phase="ready"; print(" In Pallet Town!"); break
                elif attempts<100: self.emulator.step("A"); time.sleep(0.1)
                elif attempts<150: self.emulator.step("START"); time.sleep(0.1)
                else: phase="menu"; print("   Selecting...")
            elif phase=="menu":
                if attempts<200: self.emulator.step("A"); time.sleep(0.2)
                else: phase="name"; print("   Name...")
            elif phase=="name":
                relative_attempt=attempts-200
                if relative_attempt<50:
                    self.emulator.step("A"); time.sleep(0.15)
                    if"Pallet"in location: phase="ready"; print(" Named!"); break
                else: phase="rival"; print("   Rival...")
            elif phase=="rival":
                relative_attempt=attempts-250
                if relative_attempt<120:
                    self.emulator.step("A"); time.sleep(0.15)
                    if"Pallet"in location: phase="ready"; print(" Started!"); break
                else: print(" Timeout"); phase="ready"; break
        if phase=="ready": print(f" Done ({attempts})"); time.sleep(0.5); return True
        else: print(f" Incomplete({phase},{attempts})"); return False
    def _press_button(self, button): self.emulator.step(button)
    def skip_intro_fast(self):
        print(" Skipping...")
        for _ in range(50): self._press_button("A"); time.sleep(0.05)
        print(" Skipped")
    def is_in_game(self):
        try:
            state=self.emulator.get_state()
            return state.x>0 or state.y>0 or"Pallet"in state.location or"Route"in state.location
        except: return False
