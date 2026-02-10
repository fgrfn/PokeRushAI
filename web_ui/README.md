# PokeRushAI WebUI - Start Anleitung

## 🚀 Schnellstart

### Methode 1: PowerShell Script (empfohlen)
```powershell
.\start_webui.ps1
```

### Methode 2: Direkt mit Python
```powershell
python web_ui/app.py
```

### Methode 3: Über main.py
```powershell
python main.py web
```

## 📋 Voraussetzungen

1. **Python Virtual Environment aktivieren** (optional aber empfohlen):
   ```powershell
   .\venv\Scripts\activate
   ```

2. **ROM-Datei platzieren**:
   - Lege `pokered.gb` in den `roms/` Ordner
   - Ohne ROM funktioniert der "▶ Start" Button nicht

## 🌐 WebUI öffnen

Nach dem Start:
- Öffne Browser: **http://localhost:5000**
- Oder von anderem Gerät: **http://<deine-ip>:5000**

## 🎮 Nutzung

### Schritt 1: Emulator starten
- Klicke **"▶ Start"** Button (oben in Control-Leiste)
- Warte auf **🟢 Running** Status
- ROM wird geladen, PyBoy startet

### Schritt 2: Spiel steuern
**Manual Controls:**
- **D-Pad**: ▲ ▼ ◀ ▶ (Bewegung)
- **A/B**: Action Buttons
- **START**: Menü öffnen/schließen
- **SELECT**: Item wechseln

**Training Controls:**
- **⏭ Step**: Einen Schritt ausführen (für RL Training)
- **💾 Save**: Spielstand speichern (Slot 1)
- **📂 Load**: Spielstand laden (Slot 1)

### Schritt 3: Beobachten
- **Game Boy Screen**: Live Emulator-Anzeige (4x skaliert)
- **Game State**: Position, Badges, Spielzeit
- **Kanto Map**: Spieler-Position auf der Karte
- **Training Metrics**: Episode, Steps, Reward
- **Action History**: Letzte 20 Aktionen

## 🔧 Fehlerbehebung

### "ModuleNotFoundError: No module named 'core'"
✅ **Gelöst!** `web_ui/app.py` passt jetzt automatisch den Python-Path an.

### "ROM not found"
1. Prüfe ob `roms/pokered.gb` existiert
2. Teste mit: `python test_start_function.py`

### "Port 5000 already in use"
Ändere den Port:
```powershell
python web_ui/app.py --port 5001  # Falls main.py
# Oder direkt in app.py: port=5001
```

### Emulator startet nicht
```powershell
# Teste PyBoy separat
python test_pyboy.py

# Prüfe Requirements
pip install -r requirements.txt
```

## 📊 Verfügbare Endpunkte

### Haupt-UI
- `GET /` - WebUI Dashboard

### State & Daten
- `GET /api/state` - Aktueller Spielstand
- `GET /api/maps` - Karten-Konfiguration
- `GET /api/screen` - Emulator Screenshot (PNG)
- `GET /api/metrics` - Training Metriken
- `GET /api/scoreboard?edition=red` - Leaderboard

### Emulator Kontrolle
- `POST /api/control/start` - Emulator starten
- `POST /api/control/stop` - Emulator stoppen
- `POST /api/control/step` - Einen Schritt ausführen
- `POST /api/control/button` - Button drücken (A, B, UP, etc.)
- `GET /api/control/status` - Status abfragen

### Save/Load
- `POST /api/control/save_state` - Spielstand speichern
- `POST /api/control/load_state` - Spielstand laden

## 🎯 Features

✅ Live Game Boy Emulation (PyBoy)  
✅ Pixel-genaue Karten-Positionierung (40+ Locations)  
✅ Manuelle Spiel-Steuerung (8 Buttons)  
✅ Training Metrics Dashboard  
✅ Episode Rewards Chart  
✅ Action History Log  
✅ FPS Counter  
✅ Save/Load State System  
✅ Professional Kanto Map  

## 💡 Tipps

- **FPS niedrig?** Normal bei PyBoy Emulation (~5 FPS für WebUI Refresh)
- **Karte scrollbar:** Nutze Mausrad oder Scrollbars (Map ist 1344x2016px)
- **Multiple Saves:** Edit slot parameter in app.js (1-10 möglich)
- **Headless Mode:** Setze `show_window: False` in EmulatorSettings

## 🐛 Debug-Modus

Flask läuft im Debug-Modus:
- Auto-Reload bei Code-Änderungen
- Detaillierte Fehlermeldungen
- Browser Console (F12) für JavaScript-Logs

---

**Version:** 1.0  
**Datum:** Februar 2026  
**Framework:** Flask 3.0.0 + PyBoy 2.0.0
