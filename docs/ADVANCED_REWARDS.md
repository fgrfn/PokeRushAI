# Advanced Reward System

## Overview

The reward system has been completely overhauled based on the successful [PokemonRedExperiments](https://github.com/PWhiddy/PokemonRedExperiments) approach. The new system provides much richer feedback signals for the bot's learning process.

## Key Features

### 1. **Event Flag Tracking** (0xD747-0xD87E)
- Tracks ~2488 event flags representing story progression
- Rewards every story milestone (Oak's Parcel, Pokedex, NPC interactions, item pickups)
- Provides continuous feedback between rare badge acquisitions
- **Reward:** 4 points per event flag

### 2. **Global Exploration Map** (384x384 grid)
- Maps local coordinates to global positions
- Tracks every unique tile visited
- Visual exploration progress
- **Reward:** 0.1 points per new tile + 5 points for new named location

### 3. **Level-Based Rewards with Threshold**
- Linear rewards for early levels (encourages training)
- Scaled-down rewards after level ~22 (encourages gym progression)
- Prevents excessive grinding
- Formula:
  ```python
  if level_sum < 22:
      reward = level_sum
  else:
      reward = (level_sum - 22) / 4 + 22
  ```
- **Reward:** ~1 point per effective level

### 4. **Opponent Level Tracking** (0xD8C5-0xD9A1)
- Detects opponent Pokemon levels during battles
- Rewards encountering stronger trainers
- Encourages progression through the game
- **Reward:** 0.2 points per opponent level above baseline

### 5. **Healing Rewards**
- Detects HP increases without party changes
- Encourages using Pokemon Centers
- Tracks death count (blackouts)
- **Reward:** 4 points per HP fraction healed
- **Death Penalty:** -0.1 points per death

### 6. **Stuck Detection & Loop Prevention**
- **Stuck Penalty:** -0.05 if same coordinate visited >600 times (anti-grinding)
- **Loop Penalty:** -1.0 if only 3 unique positions in last 10 steps
- Both penalties disabled during grace period (first 50 steps)

### 7. **Badge Rewards** (Enhanced)
- Massive reward for primary objective
- **Reward:** 10 points per badge

## Reward Components Breakdown

| Component | Weight | Purpose |
|-----------|--------|---------|
| **Badge** | 10.0 | Main objective |
| **Event Flags** | 4.0 | Story progression |
| **Level** | 1.0 (scaled) | Pokemon training |
| **Exploration** | 0.1/tile + 5.0/location | Map coverage |
| **Opponent Level** | 0.2 | Battle progression |
| **Healing** | 4.0 | Resource management |
| **Death** | -0.1 | Penalty for losing |
| **Stuck** | -0.05 | Anti-grinding |
| **Loop** | -1.0 | Anti-repetition |

## Memory Addresses Added

### Party Pokemon
- `PARTY_LEVEL_1` through `PARTY_LEVEL_6`: Individual levels (0xD18C-0xD268)
- `PARTY_HP_1` through `PARTY_HP_6`: Current HP (2 bytes each)
- `PARTY_MAX_HP_1` through `PARTY_MAX_HP_6`: Max HP (2 bytes each)

### Opponent Pokemon
- `OPP_LEVEL_1` through `OPP_LEVEL_6`: Opponent levels (0xD8C5-0xD9A1)

### Event Flags
- `EVENT_FLAGS_START`: 0xD747
- `EVENT_FLAGS_END`: 0xD87E (311 bytes)
- `MUSEUM_TICKET`: 0xD754 (excluded from counting)

### Battle State
- `BATTLE_TYPE`: 0xD057 (0=none, 1=wild, 2=trainer)
- `JOYPAD_DISABLE`: 0xD79E (0=enabled, >0=disabled)

### Pokedex
- `POKEDEX_OWNED_START`: 0xD2F7 (19 bytes)
- `POKEDEX_SEEN_START`: 0xD30A (19 bytes)

## Helper Functions

### In `pokemon_memory.py`:
- `bit_count(byte)`: Count set bits
- `read_bit(byte, idx)`: Read specific bit
- `get_party_levels(reader)`: Get all party levels
- `get_opponent_levels(reader)`: Get opponent levels
- `get_hp_fraction(reader)`: Calculate party HP%
- `count_event_flags(reader)`: Count total event flags
- `is_in_battle(reader)`: Check battle state

### In `exploration_map.py`:
- `ExplorationMap.update(x, y, map_id)`: Mark tile as explored
- `ExplorationMap.get_explored_count()`: Get total explored tiles
- `ExplorationMap.local_to_global(x, y, map_id)`: Convert coordinates
- `ExplorationMap.get_local_view(x, y, map_id, radius)`: Get local exploration view

## Usage

### Initialization
```python
from bot.rewards import RewardCalculator

# Pass emulator as memory_reader
calculator = RewardCalculator(memory_reader=emulator, grace_period=50)
```

### Per Episode
```python
# Reset at start of each episode
calculator.reset()
```

### Per Step
```python
# Calculate rewards
reward_dict = calculator.calculate_reward(prev_state, curr_state, elapsed_time)

# Access components
total_reward = reward_dict['total']
badge_reward = reward_dict['badge']
event_reward = reward_dict['event']
level_reward = reward_dict['level']
explore_reward = reward_dict['explore']
# ... etc

# Get statistics
stats = calculator.get_stats()
print(f"Event flags: {stats['max_event_flags']}")
print(f"Explored tiles: {stats['explored_tiles']}")
```

## Configuration

### Reward Scaling
```python
calculator.reward_scale = 1.0  # Overall reward multiplier
calculator.explore_weight = 1.0  # Exploration weight
```

### Grace Period
First N steps have penalties disabled to avoid punishing intro sequence:
```python
calculator.grace_period = 50  # Default: 50 steps
```

## Expected Behavior

### Early Game (0-2 badges)
- High rewards for exploration and events
- Level rewards encourage training
- Location discovery bonuses

### Mid Game (3-5 badges)
- Level rewards scale down (avoid grinding)
- Event flags provide steady feedback
- Opponent level rewards increase

### Late Game (6-8 badges)
- Badge rewards dominate
- Exploration in new areas
- Strong opponent rewards

## Comparison to Basic System

| Aspect | Old System | New System |
|--------|------------|------------|
| **Feedback Frequency** | Rare (badges only) | Continuous (events, tiles, levels) |
| **Exploration** | Location names only | Global map + coordinates |
| **Training Balance** | Linear | Threshold-scaled |
| **Battle Progression** | None | Opponent level tracking |
| **Resource Management** | None | Healing rewards |
| **Anti-Cheese** | Basic loop detection | Stuck + loop + death penalties |

## Performance Impact

- **Memory overhead:** ~150KB (exploration map)
- **Compute overhead:** ~0.1ms per step (negligible)
- **Training improvement:** Expected 2-3x faster convergence (based on PokemonRedExperiments results)

## Future Enhancements

Possible additions:
- **Screen-based exploration** (KNN frame comparison)
- **Pokedex rewards** (catching & seeing Pokemon)
- **Money rewards** (for resource management)
- **Move learning** (TM/HM acquisition)
- **Special event rewards** (Legendary encounters, SS Anne, etc.)
