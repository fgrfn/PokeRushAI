# PokéRushAI

🎮 **Reinforcement-Learning-Bot für Pokémon Rot** mit Q-Learning, PyBoy-Emulator und WebUI Dashboard.

Der Bot lernt selbstständig Pokémon zu spielen und misst seine Performance anhand von Badge-Checkpoints. Das WebUI zeigt alle Metriken in Echtzeit: Map, Team, Geld, Trainingsfortschritt und Bestenliste.

---

## 🚀 Schnellstart (3 Schritte)

### 1. ROM ablegen
```
roms/pokered.gb
```
*(ROM-Dateien nicht enthalten - bitte selbst besorgen)*

### 2. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 3. Starten!
```bash
python launch.py
```

**Das war's!** 🎉

Der Browser öffnet automatisch `http://localhost:5000` mit dem Dashboard.

---

## 📊 Features

### ✅ WebUI Dashboard
- **Live Map**: Echtzeit-Position des Bots auf Kanto-Karte
- **Game State**: Location, Badges, Spielzeit, Koordinaten
- **Pokemon Team**: Party mit Level und HP
- **Resources**: Aktuelles Ingame-Geld
- **Training Metrics**: Steps, Rewards, Tiles Visited
- **Q-Learning Stats**: States Explored, Q-Table Size, Updates
- **Scoreboard**: Bestenliste mit Badge-Zeiten

### ✅ Bot Konfiguration (direkt im WebUI)
- **Badge Challenge**: Bot läuft bis alle 8 Badges erreicht sind
- **Speed Run**: Bot versucht Elite Four zu besiegen
- **Free Run**: Custom Anzahl Steps

### ✅ Badge-Checkpoint System
Jedes Badge wird als Meilenstein getrackt:
1. Boulder Badge (Pewter City)
2. Cascade Badge (Cerulean City)
3. Thunder Badge (Vermilion City)
4. Rainbow Badge (Celadon City)
5. Soul Badge (Fuchsia City)
6. Marsh Badge (Saffron City)
7. Volcano Badge (Cinnabar Island)
8. Earth Badge (Viridian City)
9. Elite Four Victory

Die Bestenliste zeigt Zeiten zwischen den Badges!

---

## 📁 Projektstruktur

```
PokeRushAI/
├── launch.py              ← EINZIGER STARTPUNKT!
├── bot/                   ← Q-Learning Bot Logik
│   ├── rl_bot.py         ← Haupt-Bot mit Badge-Tracking
│   ├── policy.py         ← Q-Learning Policy
│   ├── rewards.py        ← Reward Calculator
│   └── q_learning.py     ← Q-Table Management
├── emulator/             ← PyBoy Emulator Integration
│   ├── pyboy_emulator.py
│   ├── pokemon_memory.py  ← Memory Reading
│   └── game_starter.py    ← Game Initialization
├── web_ui/               ← Flask WebUI
│   ├── app.py            ← API Endpoints
│   ├── templates/
│   │   └── index.html    ← Dashboard UI
│   └── static/
│       ├── styles.css    ← Red/White Theme
│       ├── app_extended.js ← Frontend Logic
│       └── kanto_map.svg
├── run_logging/          ← Run History & Scoreboard
├── scoreboard/           ← Scoreboard Management
├── data/                 ← State & Q-Table Storage
│   ├── state.json       ← Current Game State
│   └── q_table.json     ← Learned Q-Values
├── roms/                 ← ROM Files (not included)
└── docs/                 ← Documentation
```

---

## 🎯 Bedienung

### Im WebUI Dashboard:

1. **Run-Typ wählen**:
   - Badge Challenge (empfohlen für Training)
   - Speed Run (für vollständigen Durchlauf)
   - Free Run (für Tests)

2. **Bot starten**: Button "▶ Start Bot" klicken

3. **Training beobachten**:
   - Map zeigt aktuelle Position
   - Training Metrics zeigen Fortschritt
   - Q-Learning Stats zeigen Lernfortschritt
   - Scoreboard zeigt beste Runs

4. **Bot stoppen**: Button "⏹ Stop Bot" klicken

### Badge-Tracking:
Der Bot gibt automatisch eine Meldung aus wenn ein Badge erreicht wird:
```
🏅 BADGE EARNED: Boulder Badge (Pewter City)
   Total badges: 1/8
   Steps taken: 15234
   Total reward: +234.5
```

---

## 📈 Q-Learning

Der Bot nutzt Q-Learning um optimale Aktionen zu lernen:
- **State**: Location, Position, Badges, Team
- **Actions**: UP, DOWN, LEFT, RIGHT, A, B
- **Rewards**: Badge-Progress, Tile-Exploration, Event-Completion

Das Q-Table wird in `data/q_table.json` gespeichert und wächst mit jedem Run.

---

## 🔧 Technische Details

### Emulator
- **PyBoy**: Game Boy Emulator (headless mode)
- **ROM**: Pokémon Rot (pokered.gb)
- **Memory Reading**: Direct RAM access für Game State

### WebUI
- **Flask**: Backend API
- **JavaScript**: Frontend Updates (1s Refresh)
- **Theme**: High-Contrast Red/White für Readability

### Bot
- **Q-Learning**: Epsilon-Greedy Policy
- **Reward Shaping**: Badge-based + Exploration
- **State Space**: Location-based mit Badge-Tracking
- **Action Space**: 6 Buttons (D-Pad + A/B)

---

## 📚 Dokumentation

- `docs/ARCHITECTURE.md` - System-Architektur
- `docs/Q_LEARNING.md` - Q-Learning Details
- `docs/USAGE.md` - Advanced Usage
- `docs/TESTING.md` - Testing Guide

---

## 🎮 Troubleshooting

**Bot startet nicht?**
- ROM vorhanden? (`roms/pokered.gb`)
- Dependencies installiert? (`pip install -r requirements.txt`)

**WebUI lädt nicht?**
- Port 5000 frei? Prüfe mit `netstat -an | findstr 5000`
- Firewall blockiert? Flask erlauben

**Bot lernt nicht?**
- Q-Table vorhanden? (`data/q_table.json`)
- Rewards richtig konfiguriert? (`bot/rewards.py`)

---

## 🏆 Bestenliste

Die Scoreboard zeigt:
- Run ID
- Total Time (Sekunden)
- Badges Reached
- Milestone Times (Zeit zwischen Badges)

Die besten Runs werden in `data/run_logs/` gespeichert.

---

## ⚙️ Konfiguration

Alle Settings in `core/config.py`:
- ROM Paths
- Data Directories
- Log Directories
- Edition Configs

---

## 🤝 Erweiterungen

Das System ist modular aufgebaut:
- Neue Editionen: `core/config.py` erweitern
- Neue Rewards: `bot/rewards.py` anpassen
- Neue Actions: `bot/rl_bot.py` erweitern
- Neue Metriken: `web_ui/app.py` + `templates/index.html`

---

**Viel Erfolg beim Training!** 🚀
