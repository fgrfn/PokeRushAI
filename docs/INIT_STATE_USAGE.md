# Init State Usage Guide (PokemonRedExperiments Style)

## Overview

The init state system allows instant episode resets by loading a pre-saved game state, eliminating the need to play through the intro sequence every episode. This dramatically speeds up training (< 1 second vs 30-60 seconds per episode).

## How It Works

1. **Creating the Init State** (one-time setup):
   ```powershell
   python create_init_state.py
   ```
   - PyBoy window opens
   - Play through intro manually
   - Stop at Pallet Town (outside, with full control)
   - Press ENTER
   - State saved to `data/init_state.state`

2. **Using the Init State** (training):
   ```powershell
   python main.py bot --use-init-state --max-steps 50000
   ```

## Correct Implementation

### What Happens When You Use `--use-init-state`:

```python
# In main.py (simplified):
if args.use_init_state:
    # 1. Load emulator
    emulator.load()
    
    # 2. Load saved state from file
    with open("data/init_state.state", "rb") as f:
        emulator.pyboy.load_state(f)
    
    # 3. Start bot with use_init_state=True
    bot.run(milestones=[], auto_start=False, use_init_state=True)
```

### Critical: `use_init_state=True` Parameter

The `use_init_state=True` parameter tells `bot.run()` to:
- **Skip `emulator.load()`** inside the bot
- **Preserve the pre-loaded state** instead of resetting to ROM start
- **Reset reward calculator** for the new episode

### Without This Fix

**Before:**
```python
# main.py loads state
emulator.load()
emulator.pyboy.load_state(f)  # ✅ State loaded

# bot.run() is called
bot.run(milestones=[])

# Inside bot.run():
emulator.load()  # ❌ State OVERWRITTEN! ROM reloads from start
```

**After (Correct):**
```python
# main.py loads state
emulator.load()
emulator.pyboy.load_state(f)  # ✅ State loaded

# bot.run() is called with use_init_state=True
bot.run(milestones=[], use_init_state=True)

# Inside bot.run():
if not use_init_state:
    emulator.load()  # ✅ SKIPPED! State preserved
```

## File Changes

### 1. `bot/rl_bot.py`

**Added `use_init_state` parameter:**
```python
def run(self, milestones, auto_start=True, use_init_state=False):
    self._run_internal(milestones, auto_start, use_init_state)

def _run_internal(self, milestones, auto_start=True, use_init_state=False):
    # Only load emulator if NOT using init state
    if not use_init_state:
        self.emulator.load()
    else:
        print("✅ Using pre-loaded init state (skipping emulator.load())")
    
    # Reset reward calculator for new episode
    self.reward_calculator.reset()
    
    # ... rest of training loop
```

### 2. `main.py`

**Passes `use_init_state=True` to bot:**
```python
if args.use_init_state:
    init_state_path = config.data_dir / "init_state.state"
    emulator.load()
    with open(init_state_path, "rb") as f:
        emulator.pyboy.load_state(f)
    print("🚀 Starting from init state (Pallet Town)...")
    bot.run(milestones=[], auto_start=False, use_init_state=True)  # ✅ Pass flag
```

## Verification

### Test Init State Loading:

```powershell
# 1. Create state (if not already created)
python create_init_state.py

# 2. Verify state file exists
Test-Path data/init_state.state
# Should output: True

# 3. Run bot with init state
python main.py bot --use-init-state --max-steps 1000 --show-window
```

### Expected Output:

```
📋 Configuration:
   Edition: RED
   Max Steps: 1,000
   Window: Visible
   Init State: Enabled
   ROM: pokered.gb

✅ Init state loaded from: C:\...\data\init_state.state

🚀 Starting from init state (Pallet Town)...
✅ Using pre-loaded init state (skipping emulator.load())

🚀 Starting Q-Learning bot for 1000 steps...
   Location: Pallet Town, Badges: 0

Step   0: Pallet Town          Badges: 0  Reward:   +5.1  ...
```

### Key Indicators:

✅ **"Using pre-loaded init state"** - Confirms state is preserved
✅ **Location starts at "Pallet Town"** - Not at intro screen
✅ **Badges: 0** - Correct starting state
✅ **Fast episode start** - No intro delay

## Speed Comparison

| Method | Episode Start Time | Episodes/Hour |
|--------|-------------------|---------------|
| **Without Init State** | 30-60 seconds | ~60-120 |
| **With Init State** | < 1 second | ~3600+ |

**Result:** ~30-60x faster training with init state! 🚀

## Troubleshooting

### Error: "Init state not found"

```powershell
⚠️ Init state not found: C:\...\data\init_state.state
   Create it first: python create_init_state.py
```

**Solution:** Run `python create_init_state.py` first.

### Bot starts at intro instead of Pallet Town

**Cause:** `use_init_state=True` not passed to `bot.run()`

**Solution:** Make sure you're using the updated `main.py` that passes the flag:
```python
bot.run(milestones=[], auto_start=False, use_init_state=True)
```

### State loads but bot resets to ROM start

**Cause:** Old version of `bot/rl_bot.py` without `use_init_state` parameter

**Solution:** Update `bot/rl_bot.py` to check the flag before calling `emulator.load()`.

## Advanced Usage

### Multiple Init States

Create different starting points:
```powershell
# Pallet Town start
python create_init_state.py
# Saves to: data/init_state.state

# Manually rename for different starting points:
Move-Item data/init_state.state data/init_pallet.state
Move-Item data/init_state.state data/init_pewter.state
```

### Training Multiple Episodes

The init state is automatically reused for each episode:
```powershell
# Train for 100,000 steps with multiple episode resets
python main.py bot --use-init-state --max-steps 100000
```

Each time the bot completes a "run" (death, timeout, etc.), it can re-load the init state for a fresh start.

## References

- Original Implementation: [PokemonRedExperiments](https://github.com/PWhiddy/PokemonRedExperiments)
- Their approach: `with open(init_state, "rb") as f: pyboy.load_state(f)`
- Our implementation: Same approach + `use_init_state` flag to prevent overwriting
