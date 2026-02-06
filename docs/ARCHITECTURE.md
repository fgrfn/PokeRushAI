# Architektur von PokéRushAI

## Überblick

PokéRushAI ist in klar abgegrenzte Module aufgeteilt, damit Emulator, Bot-Logik und Web-UI unabhängig voneinander weiterentwickelt werden können. Die Architektur ist bewusst minimalistisch gehalten, um neue Editionen oder weitere RL-Strategien schnell zu integrieren.

## Module und Verantwortlichkeiten

| Modul | Verantwortung |
| --- | --- |
| `bot/` | RL-Policy, Run-Steuerung, State-Updates in `data/state.json`. |
| `emulator/` | Abstraktion von PyBoy, lädt ROM und liefert Game-State. |
| `run_logging/` | Rotierendes Logging pro Run, Meilensteine, Scoreboard. |
| `web_ui/` | Flask-Dashboard mit Karten, Position, Scoreboard. |
| `scoreboard/` | Lesezugriff auf Scoreboard-JSON. |

## Datenfluss

1. **Bot** startet einen Run und lädt die ROM über den Emulator.
2. Jede Aktion wird als Entscheidung mit Timestamp geloggt.
3. Der aktuelle Game-State wird nach `data/state.json` geschrieben.
4. Die **Web-UI** liest State und Scoreboard per API und zeigt sie an.

## Logging

- Logs werden pro Edition in `logs/<edition>/` abgelegt.
- Jeder Run erhält ein Verzeichnis `run_XXXX` mit `metadata.json`, `decisions.jsonl`, optionalen `splits.json` und `summary.json`.
- `scoreboard.json` wird nach jedem Run aktualisiert und sortiert.

## Erweiterungen

- Neue Editionen können in `core/config.py` ergänzt werden.
- Neue Policies lassen sich im Modul `bot/policy.py` hinzufügen.
- Für echte PyBoy-Integration kann `emulator/pyboy_emulator.py` erweitert werden.
