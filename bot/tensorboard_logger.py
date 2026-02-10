"""Tensorboard integration for training metrics visualization.

Logs rewards, badges, exploration stats, and Q-learning metrics to Tensorboard.
View with: tensorboard --logdir=data/tensorboard
"""

from pathlib import Path
from typing import Dict, Any, Optional

try:
    from torch.utils.tensorboard import SummaryWriter
    TENSORBOARD_AVAILABLE = True
except ImportError:
    TENSORBOARD_AVAILABLE = False
    print("⚠️  Warning: tensorboard not available. Metrics logging disabled.")


class TensorboardLogger:
    """Logs training metrics to Tensorboard."""
    
    def __init__(
        self,
        log_dir: Path,
        enabled: bool = True,
        comment: str = ""
    ):
        """Initialize Tensorboard logger.
        
        Args:
            log_dir: Directory for tensorboard logs
            enabled: Whether logging is enabled
            comment: Optional comment to append to log directory name
        """
        self.enabled = enabled and TENSORBOARD_AVAILABLE
        self.writer: Optional[SummaryWriter] = None
        
        if self.enabled:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            self.writer = SummaryWriter(
                log_dir=str(log_dir),
                comment=comment
            )
            print(f"📊 Tensorboard logging enabled: {log_dir}")
            print(f"   View with: tensorboard --logdir={log_dir.parent}")
    
    def log_step(
        self,
        step: int,
        reward: float,
        total_reward: float,
        badges: int,
        location: str,
        action: str,
        **extra_metrics
    ):
        """Log metrics for a single training step.
        
        Args:
            step: Current step number
            reward: Step reward
            total_reward: Cumulative reward
            badges: Current badge count
            location: Current location name
            action: Action taken
            **extra_metrics: Additional metrics to log
        """
        if not self.enabled or not self.writer:
            return
        
        # Basic metrics
        self.writer.add_scalar('Reward/Step', reward, step)
        self.writer.add_scalar('Reward/Total', total_reward, step)
        self.writer.add_scalar('Progress/Badges', badges, step)
        
        # Extra metrics
        for key, value in extra_metrics.items():
            if isinstance(value, (int, float)):
                self.writer.add_scalar(f'Metrics/{key}', value, step)
    
    def log_episode(
        self,
        episode: int,
        total_steps: int,
        total_reward: float,
        max_badges: int,
        unique_coords: int,
        unique_frames: int,
        deaths: int,
        **extra_stats
    ):
        """Log episode summary metrics.
        
        Args:
            episode: Episode number
            total_steps: Total steps in episode
            total_reward: Final cumulative reward
            max_badges: Maximum badges achieved
            unique_coords: Number of unique coordinates visited
            unique_frames: Number of unique frames seen
            deaths: Number of deaths
            **extra_stats: Additional episode statistics
        """
        if not self.enabled or not self.writer:
            return
        
        self.writer.add_scalar('Episode/TotalReward', total_reward, episode)
        self.writer.add_scalar('Episode/MaxBadges', max_badges, episode)
        self.writer.add_scalar('Episode/Steps', total_steps, episode)
        self.writer.add_scalar('Episode/UniqueCoords', unique_coords, episode)
        self.writer.add_scalar('Episode/UniqueFrames', unique_frames, episode)
        self.writer.add_scalar('Episode/Deaths', deaths, episode)
        
        # Extra stats
        for key, value in extra_stats.items():
            if isinstance(value, (int, float)):
                self.writer.add_scalar(f'Episode/{key}', value, episode)
    
    def log_q_learning(
        self,
        step: int,
        q_table_size: int,
        states_explored: int,
        total_updates: int,
        **extra_metrics
    ):
        """Log Q-learning specific metrics.
        
        Args:
            step: Current step number
            q_table_size: Size of Q-table
            states_explored: Number of states explored
            total_updates: Total Q-value updates
            **extra_metrics: Additional Q-learning metrics
        """
        if not self.enabled or not self.writer:
            return
        
        self.writer.add_scalar('QLearning/QTableSize', q_table_size, step)
        self.writer.add_scalar('QLearning/StatesExplored', states_explored, step)
        self.writer.add_scalar('QLearning/TotalUpdates', total_updates, step)
        
        # Extra metrics
        for key, value in extra_metrics.items():
            if isinstance(value, (int, float)):
                self.writer.add_scalar(f'QLearning/{key}', value, step)
    
    def log_exploration(
        self,
        step: int,
        unique_coords: int,
        unique_frames: int,
        event_flags: int,
        heal_count: int,
        opponent_count: int,
        **extra_metrics
    ):
        """Log exploration and reward component metrics.
        
        Args:
            step: Current step number
            unique_coords: Unique coordinates visited
            unique_frames: Unique frames seen
            event_flags: Event flags triggered
            heal_count: Number of heals
            opponent_count: Opponents defeated
            **extra_metrics: Additional exploration metrics
        """
        if not self.enabled or not self.writer:
            return
        
        self.writer.add_scalar('Exploration/UniqueCoords', unique_coords, step)
        self.writer.add_scalar('Exploration/UniqueFrames', unique_frames, step)
        self.writer.add_scalar('Exploration/EventFlags', event_flags, step)
        self.writer.add_scalar('Exploration/Heals', heal_count, step)
        self.writer.add_scalar('Exploration/Opponents', opponent_count, step)
        
        # Extra metrics
        for key, value in extra_metrics.items():
            if isinstance(value, (int, float)):
                self.writer.add_scalar(f'Exploration/{key}', value, step)
    
    def log_text(self, tag: str, text: str, step: int):
        """Log text information.
        
        Args:
            tag: Text tag
            text: Text content
            step: Step number
        """
        if not self.enabled or not self.writer:
            return
        
        self.writer.add_text(tag, text, step)
    
    def log_histogram(self, tag: str, values, step: int):
        """Log histogram data.
        
        Args:
            tag: Histogram tag
            values: Array of values
            step: Step number
        """
        if not self.enabled or not self.writer:
            return
        
        self.writer.add_histogram(tag, values, step)
    
    def flush(self):
        """Flush pending logs to disk."""
        if self.enabled and self.writer:
            self.writer.flush()
    
    def close(self):
        """Close the logger and flush remaining logs."""
        if self.enabled and self.writer:
            self.writer.flush()
            self.writer.close()
            print("📊 Tensorboard logger closed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logger statistics.
        
        Returns:
            Dictionary with logger stats
        """
        return {
            'enabled': self.enabled,
            'tensorboard_available': TENSORBOARD_AVAILABLE,
        }
