"""Session statistics tracking and CSV export.

Tracks detailed statistics during training episodes and exports to CSV
for analysis and visualization.

Based on PokemonRedExperiments agent_stats approach.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import time

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  Warning: pandas not available. CSV export disabled.")


class SessionStats:
    """Tracks and exports detailed session statistics."""
    
    def __init__(
        self,
        session_dir: Path,
        save_interval: int = 100,
        enabled: bool = True
    ):
        """Initialize session statistics tracker.
        
        Args:
            session_dir: Directory to save statistics
            save_interval: Save CSV every N steps
            enabled: Whether statistics tracking is enabled
        """
        self.session_dir = Path(session_dir)
        self.save_interval = save_interval
        self.enabled = enabled and PANDAS_AVAILABLE
        
        self.stats_data: List[Dict[str, Any]] = []
        self.episode_count = 0
        self.total_steps = 0
        
        if self.enabled:
            self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def record_step(
        self,
        step: int,
        x: int,
        y: int,
        map_id: int,
        location: str,
        action: str,
        party_count: int,
        levels: List[int],
        party_types: List[int],
        hp_fraction: float,
        badges: int,
        event_reward: float,
        total_reward: float,
        unique_coords: int,
        unique_frames: int,
        deaths: int,
        **extra_stats
    ):
        """Record statistics for a single step.
        
        Args:
            step: Current step number
            x: Player X coordinate
            y: Player Y coordinate
            map_id: Current map ID
            location: Human-readable location name
            action: Action taken
            party_count: Number of Pokemon in party
            levels: List of Pokemon levels
            party_types: List of Pokemon species IDs
            hp_fraction: Current HP as fraction (0.0 to 1.0)
            badges: Number of badges earned
            event_reward: Event flags reward
            total_reward: Total cumulative reward
            unique_coords: Number of unique coordinates visited
            unique_frames: Number of unique frames seen
            deaths: Number of times party was defeated
            **extra_stats: Additional statistics to record
        """
        if not self.enabled:
            return
        
        self.total_steps += 1
        
        # Create stats entry
        stats_entry = {
            'episode': self.episode_count,
            'step': step,
            'total_step': self.total_steps,
            'x': x,
            'y': y,
            'map': map_id,
            'location': location,
            'action': action,
            'party_count': party_count,
            'level_sum': sum(levels) if levels else 0,
            'levels': str(levels),  # Store as string for CSV
            'party_types': str(party_types),  # Store as string for CSV
            'hp': hp_fraction,
            'badges': badges,
            'event_reward': event_reward,
            'total_reward': total_reward,
            'unique_coords': unique_coords,
            'unique_frames': unique_frames,
            'deaths': deaths,
            'timestamp': time.time(),
        }
        
        # Add extra stats
        stats_entry.update(extra_stats)
        
        self.stats_data.append(stats_entry)
        
        # Periodic save
        if len(self.stats_data) % self.save_interval == 0:
            self.save_to_csv()
    
    def start_episode(self):
        """Mark the start of a new episode."""
        self.episode_count += 1
    
    def save_to_csv(self, filename: Optional[str] = None):
        """Save statistics to CSV file.
        
        Args:
            filename: Optional custom filename (without extension)
        """
        if not self.enabled or not self.stats_data:
            return
        
        try:
            df = pd.DataFrame(self.stats_data)
            
            if filename is None:
                filename = f"stats_episode_{self.episode_count}"
            
            csv_path = self.session_dir / f"{filename}.csv"
            df.to_csv(csv_path, index=False)
            
            # Also save compressed version for large datasets
            if len(self.stats_data) > 1000:
                gz_path = self.session_dir / f"{filename}.csv.gz"
                df.to_csv(gz_path, index=False, compression='gzip')
            
            print(f"📊 Stats saved: {csv_path} ({len(self.stats_data)} rows)")
        except Exception as e:
            print(f"⚠️  Failed to save stats: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for current session.
        
        Returns:
            Dictionary with summary stats
        """
        if not self.stats_data:
            return {}
        
        try:
            df = pd.DataFrame(self.stats_data)
            
            return {
                'total_steps': self.total_steps,
                'episodes': self.episode_count,
                'avg_reward': df['total_reward'].mean(),
                'max_reward': df['total_reward'].max(),
                'avg_badges': df['badges'].mean(),
                'max_badges': df['badges'].max(),
                'unique_locations': df['location'].nunique(),
                'total_deaths': df['deaths'].max(),
            }
        except Exception:
            return {'total_steps': self.total_steps, 'episodes': self.episode_count}
    
    def clear(self):
        """Clear current statistics (for new run)."""
        self.stats_data.clear()
        self.episode_count = 0
        self.total_steps = 0
    
    def get_stats(self) -> dict:
        """Get recorder statistics."""
        return {
            'enabled': self.enabled,
            'total_steps': self.total_steps,
            'episodes': self.episode_count,
            'data_points': len(self.stats_data),
            'session_dir': str(self.session_dir),
        }


class CompactSessionStats:
    """Lightweight statistics tracker without pandas dependency."""
    
    def __init__(self, session_dir: Path):
        """Initialize compact stats tracker.
        
        Args:
            session_dir: Directory to save statistics
        """
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.episode_summaries: List[Dict[str, Any]] = []
        self.current_episode_stats = {
            'max_reward': 0.0,
            'max_badges': 0,
            'steps': 0,
            'deaths': 0,
            'unique_coords': 0,
        }
    
    def update(self, reward: float, badges: int, coords: int, deaths: int):
        """Update current episode stats.
        
        Args:
            reward: Current total reward
            badges: Current badge count
            coords: Unique coordinates visited
            deaths: Death count
        """
        self.current_episode_stats['steps'] += 1
        self.current_episode_stats['max_reward'] = max(
            self.current_episode_stats['max_reward'], reward
        )
        self.current_episode_stats['max_badges'] = max(
            self.current_episode_stats['max_badges'], badges
        )
        self.current_episode_stats['unique_coords'] = coords
        self.current_episode_stats['deaths'] = deaths
    
    def finish_episode(self):
        """Mark current episode as complete and save summary."""
        self.episode_summaries.append(dict(self.current_episode_stats))
        
        # Reset for next episode
        self.current_episode_stats = {
            'max_reward': 0.0,
            'max_badges': 0,
            'steps': 0,
            'deaths': 0,
            'unique_coords': 0,
        }
        
        # Save summary
        summary_path = self.session_dir / "episode_summaries.txt"
        with open(summary_path, 'w') as f:
            f.write(f"Total Episodes: {len(self.episode_summaries)}\n\n")
            for i, summary in enumerate(self.episode_summaries):
                f.write(f"Episode {i+1}:\n")
                for key, value in summary.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
