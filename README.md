# PokéRushAI

PokéRushAI ist ein modularer Reinforcement-Learning-Bot für die englische Game-Boy-Edition Pokémon Rot, der mit PyBoy emuliert und auf Speedruns optimiert wird. Die Web-UI zeigt externe Karten, ordnet die Spielerposition zu und verwaltet ein Scoreboard mit Zwischenzeiten. Die Struktur ist bewusst schlank, damit weitere Editionen (Rot, Blau, Gelb) leicht ergänzt werden können.

## Module

- **bot/** – RL-Logik, Policy und Run-Steuerung.
- **emulator/** – PyBoy-Abstraktion.
- **web_ui/** – Flask-Dashboard mit Karte, State und Scoreboard.
- **run_logging/** – Run-Rotation, Entscheidungen und Scoreboard-Logik.
- **scoreboard/** – Scoreboard-Leser.
- **docs/** – Architektur- und Nutzungsdokumentation.

## Schnellstart

1. ROM-Dateien (nicht enthalten) ablegen:
   - `roms/pokemon_red.gb`
   - `roms/pokemon_blue.gb`
   - `roms/pokemon_yellow.gbc`
2. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
3. Bot starten:
   ```bash
   python main.py bot --edition red --max-steps 200
   ```
4. Web-UI starten:
   ```bash
   python main.py web --host 0.0.0.0 --port 5000
   ```

Weitere Details finden sich in `docs/USAGE.md` und `docs/ARCHITECTURE.md`.
