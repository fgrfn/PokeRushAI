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

### ✅ WebUI Dashboard (Monitoring)
- **Live Map**: Echtzeit-Position des Bots auf Kanto-Karte
- **Game State**: Location, Badges, Spielzeit, Koordinaten
- **Pokemon Team**: Party mit Level und HP
- **Resources**: Aktuelles Ingame-Geld
- **Training Metrics**: Steps, Rewards, Tiles Visited
- **Q-Learning Stats**: States Explored, Q-Table Size, Updates
- **Scoreboard**: Bestenliste mit Badge-Zeiten

### ✅ Bot Training
- **PyBoy-Fenster**: Sichtbares Spiel-Fenster zum Zuschauen
- **Badge Challenge**: Bot trainiert bis alle 8 Badges erreicht sind
- **Automatisches Training**: Q-Learning mit Epsilon-Greedy Policy
- **Persistente Q-Table**: Lernt über mehrere Sessions hinweg

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
│       ├── app.js       ← Frontend Logic
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

### Start:

```bash
python launch.py
```

### Was passiert:

1. **PyBoy-Fenster öffnet sich**: Hier siehst du das Spiel live
2. **WebUI öffnet im Browser**: `http://localhost:5000` für Monitoring
3. **Bot trainiert automatisch**: Badge Challenge (max. 500.000 Steps)

### Während des Trainings:

- **PyBoy-Fenster**: Zeigt das Spiel in Echtzeit
- **WebUI Dashboard**: Zeigt Stats, Map-Position, Team und Scoreboard
- **Terminal**: Zeigt Bot-Logs und Badge-Meldungen

### Beenden:

- Schließe das PyBoy-Fenster oder drücke `Ctrl+C` im Terminal

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
- **PyBoy**: Game Boy Emulator mit SDL2-Fenster
- **ROM**: Pokémon Rot (pokered.gb)
- **Memory Reading**: Direct RAM access für Game State
- **Window**: Sichtbares Fenster für Live-Beobachtung

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
- `docs/USAGE.md` - Advanced Usage
- `docs/INIT_STATE_USAGE.md` - Init State Guide
- `docs/ADVANCED_REWARDS.md` - Reward System
- `docs/SESSION_STATS.md` - Session Statistics

---

## 🎮 Troubleshooting

**Bot startet nicht?**
- ROM vorhanden? (`roms/pokered.gb`)
- Dependencies installiert? (`pip install -r requirements.txt`)

**WebUI lädt nicht?**
- Port 5000 frei? Prüfe mit `lsof -i :5000` oder `netstat -tuln | grep 5000`
- Browser öffnet nicht automatisch? Öffne manuell: `http://localhost:5000`

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
- **Neue Rewards**: `bot/rewards.py` anpassen
- **Neue Policies**: `bot/policy.py` erweitern
- **Init State Training**: `python create_init_state.py` + `main.py --use-init-state`
- **Neue Metriken**: `web_ui/app.py` + `templates/index.html`

## 🔬 Erweiterte Nutzung

### CLI mit main.py

Für erweiterte Konfiguration nutze `main.py`:

```bash
# Bot mit Init State (schnelleres Training)
python main.py bot --use-init-state --max-steps 100000

# Nur WebUI starten
python main.py webui --port 5000

# Interaktiver Modus
python main.py interactive
```

### Init State erstellen

```bash
python create_init_state.py
```

Spiele manuell durch das Intro bis Pallet Town, dann Enter drücken.

---

**Viel Erfolg beim Training!** 🚀
