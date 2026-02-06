# Nutzung

## Voraussetzungen

- Python 3.10+
- ROM-Dateien für Rot/Blau/Gelb (nicht enthalten)
- Abhängigkeiten aus `requirements.txt`

## Bot starten

```bash
python main.py bot --edition red --max-steps 200
```

Der Bot erzeugt einen neuen Run und schreibt:

- `data/state.json` für die Web-UI
- `logs/<edition>/run_XXXX/` mit Entscheidungslog und Zusammenfassung

## Web-UI starten

```bash
python main.py web --host 0.0.0.0 --port 5000
```

Die Web-UI zeigt:

- Auswahl der Edition (Rot, Blau, Gelb)
- Externe Karten mit Positionsmarker
- Aktuellen Game-State
- Scoreboard mit Zwischenzeiten

## Splits hinzufügen

Optional können Zwischenzeiten als `splits.json` im Run-Ordner abgelegt werden:

```json
[
  {"name": "Boulder Badge", "time_seconds": 120.5},
  {"name": "Cascade Badge", "time_seconds": 420.2}
]
```

Beim Abschluss eines Runs werden die Splits automatisch in die `summary.json` und `scoreboard.json` übernommen.
