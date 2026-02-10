# Session Statistics System

Comprehensive statistics tracking and CSV export for PokeRushAI training sessions.

Based on **PokemonRedExperiments** agent_stats approach.

## Features

- **Detailed Step Tracking**: Records detailed information at every training step
- **CSV Export**: Automatic export to CSV files for analysis
- **Compressed Storage**: Automatic .csv.gz compression for large datasets (>1000 rows)
- **Episode Summaries**: Summary statistics for completed episodes
- **Lightweight Fallback**: CompactSessionStats for minimal overhead

## Tracked Statistics

Each step records:

### Position & State
- `x`, `y`: Player coordinates
- `map`: Current map ID
- `location`: Human-readable location name

### Party Information
- `party_count`: Number of Pokemon in party
- `levels`: List of Pokemon levels (e.g., [5, 4])
- `party_types`: List of Pokemon species IDs
- `hp`: Current HP as fraction (0.0 to 1.0)

### Progress Metrics
- `badges`: Number of gym badges earned
- `event_reward`: Reward from event flags
- `total_reward`: Cumulative total reward
- `unique_coords`: Number of unique tiles visited
- `unique_frames`: Number of unique screens explored (KNN)
- `deaths`: Number of times party was defeated

### Metadata
- `episode`: Episode number
- `step`: Step within episode
- `total_step`: Total steps across all episodes
- `action`: Action taken (up, down, left, right, a, b, start)
- `timestamp`: Unix timestamp

## Usage

### Automatic (Default)

Statistics are automatically recorded when using the bot:

```bash
# CLI mode
python main.py bot --use-init-state --max-steps 50000

# Statistics saved to: data/session_stats/stats_episode_1.csv
```

### Configuration

```python
from bot.session_stats import SessionStats

stats = SessionStats(
    session_dir=Path("data/session_stats"),
    save_interval=100,  # Save every 100 steps
    enabled=True
)
```

### Manual Recording

```python
# Start new episode
stats.start_episode()

# Record a step
stats.record_step(
    step=0,
    x=0, y=0,
    map_id=0,
    location="Pallet Town",
    action="up",
    party_count=1,
    levels=[5],
    party_types=[1],
    hp_fraction=1.0,
    badges=0,
    event_reward=0.0,
    total_reward=0.0,
    unique_coords=1,
    unique_frames=1,
    deaths=0
)

# Save to CSV
stats.save_to_csv()
```

## Output Format

### CSV Columns

```csv
episode,step,total_step,x,y,map,location,action,party_count,level_sum,levels,party_types,hp,badges,event_reward,total_reward,unique_coords,unique_frames,deaths,timestamp
1,0,0,5,6,0,Pallet Town,up,1,5,[5],[1],1.0,0,0.0,0.0,1,1,0,1704067200.0
1,1,1,5,5,0,Pallet Town,up,1,5,[5],[1],1.0,0,0.0,0.001,2,2,0,1704067200.1
```

### File Structure

```
data/session_stats/
├── stats_episode_1.csv          # Episode 1 statistics
├── stats_episode_1.csv.gz       # Compressed (if >1000 rows)
├── stats_episode_2.csv          # Episode 2 statistics
└── episode_summaries.txt        # Episode summaries
```

## Analysis

### Load Statistics

```python
import pandas as pd

# Load episode data
df = pd.read_csv("data/session_stats/stats_episode_1.csv")

# Basic analysis
print(f"Total steps: {len(df)}")
print(f"Max reward: {df['total_reward'].max()}")
print(f"Badges earned: {df['badges'].max()}")
print(f"Unique locations: {df['location'].nunique()}")
```

### Visualize Progress

```python
import matplotlib.pyplot as plt

# Reward over time
plt.plot(df['step'], df['total_reward'])
plt.xlabel('Step')
plt.ylabel('Total Reward')
plt.title('Reward Progress')
plt.show()

# Badge progress
badge_steps = df[df['badges'] > df['badges'].shift(1)]['step']
print(f"Badge earned at steps: {list(badge_steps)}")
```

### Compare Episodes

```python
# Load multiple episodes
episode1 = pd.read_csv("data/session_stats/stats_episode_1.csv")
episode2 = pd.read_csv("data/session_stats/stats_episode_2.csv")

# Compare performance
print(f"Episode 1 max reward: {episode1['total_reward'].max()}")
print(f"Episode 2 max reward: {episode2['total_reward'].max()}")
```

## Integration with PokemonRedExperiments Features

Session Statistics works seamlessly with other PokemonRedExperiments features:

- **KNN Screen Exploration**: `unique_frames` tracked automatically
- **Event Flags**: `event_reward` includes all event flag bonuses
- **Opponent Tracking**: Opponent defeats reflected in rewards
- **Video Recording**: Correlate video frames with CSV timestamps

## Performance

- **Overhead**: ~0.5ms per step (negligible)
- **Memory**: ~100KB per 1000 steps
- **Disk**: ~50KB per 1000 steps (compressed)
- **Save Interval**: Default 100 steps (configurable)

## Disabling Statistics

To disable statistics tracking:

```python
stats = SessionStats(
    session_dir=Path("data/session_stats"),
    enabled=False  # Disable tracking
)
```

Or if pandas is not installed:
```
⚠️  Warning: pandas not available. CSV export disabled.
```

## Implementation Details

### SessionStats Class

Full-featured statistics tracker with pandas DataFrame export.

### CompactSessionStats Class

Lightweight alternative without pandas dependency:
- Records episode summaries only
- Text-based output
- Minimal memory footprint

## Example Output

```
📊 Stats saved: data/session_stats/stats_episode_1.csv (50000 rows)

Episode 1 Summary:
  Total steps: 50000
  Max reward: 142.5
  Max badges: 2
  Unique locations: 45
  Deaths: 3
```

## Credits

Based on [PokemonRedExperiments](https://github.com/PWhiddy/PokemonRedExperiments) agent statistics system by PWhiddy.
