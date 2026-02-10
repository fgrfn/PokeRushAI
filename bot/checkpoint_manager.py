"""Checkpoint system for saving training progress.

Automatically saves Q-table, statistics, and best models at regular intervals.
"""

import json
import shutil
import time
from pathlib import Path
from typing import Dict, Any, Optional


class CheckpointManager:
    """Manages training checkpoints and backups."""
    
    def __init__(
        self,
        checkpoint_dir: Path,
        save_interval: int = 1000,
        keep_best: int = 3,
        enabled: bool = True
    ):
        """Initialize checkpoint manager.
        
        Args:
            checkpoint_dir: Directory for checkpoints
            save_interval: Save checkpoint every N steps
            keep_best: Number of best checkpoints to keep
            enabled: Whether checkpointing is enabled
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.save_interval = save_interval
        self.keep_best = keep_best
        self.enabled = enabled
        
        self.last_checkpoint_step = 0
        self.best_scores: list = []  # List of (score, checkpoint_path) tuples
        
        if self.enabled:
            self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
            print(f"💾 Checkpoint system enabled: {self.checkpoint_dir}")
            print(f"   Auto-save every {save_interval} steps")
    
    def should_checkpoint(self, current_step: int) -> bool:
        """Check if checkpoint should be saved.
        
        Args:
            current_step: Current training step
            
        Returns:
            True if checkpoint should be saved
        """
        if not self.enabled:
            return False
        
        return (current_step - self.last_checkpoint_step) >= self.save_interval
    
    def save_checkpoint(
        self,
        step: int,
        episode: int,
        q_table_path: Optional[Path] = None,
        stats: Optional[Dict[str, Any]] = None,
        score: float = 0.0,
        is_best: bool = False
    ):
        """Save a checkpoint.
        
        Args:
            step: Current step number
            episode: Current episode number
            q_table_path: Path to Q-table file to backup
            stats: Statistics dictionary to save
            score: Score for this checkpoint (for best tracking)
            is_best: Whether this is explicitly marked as best
        """
        if not self.enabled:
            return
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        checkpoint_name = f"checkpoint_step{step}_ep{episode}_{timestamp}"
        checkpoint_path = self.checkpoint_dir / checkpoint_name
        checkpoint_path.mkdir(parents=True, exist_ok=True)
        
        # Save Q-table backup
        if q_table_path and q_table_path.exists():
            dest = checkpoint_path / "q_table.pkl"
            shutil.copy2(q_table_path, dest)
        
        # Save statistics
        if stats:
            stats_file = checkpoint_path / "stats.json"
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        
        # Save checkpoint metadata
        metadata = {
            'step': step,
            'episode': episode,
            'timestamp': timestamp,
            'score': score,
            'is_best': is_best,
        }
        
        metadata_file = checkpoint_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.last_checkpoint_step = step
        
        # Track best checkpoints
        if is_best or score > 0:
            self._update_best_checkpoints(score, checkpoint_path)
        
        print(f"💾 Checkpoint saved: {checkpoint_name}")
    
    def save_best_checkpoint(
        self,
        step: int,
        episode: int,
        score: float,
        q_table_path: Optional[Path] = None,
        stats: Optional[Dict[str, Any]] = None,
        reason: str = ""
    ):
        """Save a checkpoint marked as 'best'.
        
        Args:
            step: Current step number
            episode: Current episode number
            score: Score for this checkpoint
            q_table_path: Path to Q-table file
            stats: Statistics dictionary
            reason: Reason for best checkpoint (e.g., "highest_reward")
        """
        if not self.enabled:
            return
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        checkpoint_name = f"best_{reason}_step{step}_{timestamp}"
        checkpoint_path = self.checkpoint_dir / checkpoint_name
        checkpoint_path.mkdir(parents=True, exist_ok=True)
        
        # Save Q-table
        if q_table_path and q_table_path.exists():
            dest = checkpoint_path / "q_table.pkl"
            shutil.copy2(q_table_path, dest)
        
        # Save stats
        if stats:
            stats_file = checkpoint_path / "stats.json"
            enhanced_stats = {**stats, 'reason': reason, 'score': score}
            with open(stats_file, 'w') as f:
                json.dump(enhanced_stats, f, indent=2)
        
        # Save metadata
        metadata = {
            'step': step,
            'episode': episode,
            'timestamp': timestamp,
            'score': score,
            'reason': reason,
            'is_best': True,
        }
        
        metadata_file = checkpoint_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self._update_best_checkpoints(score, checkpoint_path)
        
        print(f"🏆 Best checkpoint saved: {checkpoint_name} (score: {score:.1f})")
    
    def _update_best_checkpoints(self, score: float, checkpoint_path: Path):
        """Update list of best checkpoints and clean up old ones.
        
        Args:
            score: Score for the checkpoint
            checkpoint_path: Path to the checkpoint
        """
        self.best_scores.append((score, checkpoint_path))
        self.best_scores.sort(key=lambda x: x[0], reverse=True)
        
        # Keep only top N best checkpoints
        if len(self.best_scores) > self.keep_best:
            # Remove checkpoints beyond keep_best limit
            for _, old_path in self.best_scores[self.keep_best:]:
                if old_path.exists() and not old_path.name.startswith('best_'):
                    # Only auto-delete regular checkpoints, not explicitly marked best
                    try:
                        shutil.rmtree(old_path)
                        print(f"🗑️  Removed old checkpoint: {old_path.name}")
                    except Exception as e:
                        print(f"⚠️  Failed to remove checkpoint {old_path}: {e}")
            
            self.best_scores = self.best_scores[:self.keep_best]
    
    def cleanup_old_checkpoints(self, keep_recent: int = 5):
        """Clean up old checkpoints, keeping only recent ones.
        
        Args:
            keep_recent: Number of recent checkpoints to keep
        """
        if not self.enabled:
            return
        
        checkpoints = sorted(
            [d for d in self.checkpoint_dir.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # Keep best checkpoints and recent ones
        protected = set([path for _, path in self.best_scores])
        
        removed_count = 0
        for checkpoint in checkpoints[keep_recent:]:
            if checkpoint not in protected and not checkpoint.name.startswith('best_'):
                try:
                    shutil.rmtree(checkpoint)
                    removed_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to remove {checkpoint}: {e}")
        
        if removed_count > 0:
            print(f"🗑️  Cleaned up {removed_count} old checkpoints")
    
    def get_latest_checkpoint(self) -> Optional[Path]:
        """Get path to the most recent checkpoint.
        
        Returns:
            Path to latest checkpoint or None
        """
        if not self.enabled or not self.checkpoint_dir.exists():
            return None
        
        checkpoints = [
            d for d in self.checkpoint_dir.iterdir()
            if d.is_dir() and (d / "metadata.json").exists()
        ]
        
        if not checkpoints:
            return None
        
        return max(checkpoints, key=lambda x: x.stat().st_mtime)
    
    def get_best_checkpoint(self) -> Optional[Path]:
        """Get path to the best checkpoint.
        
        Returns:
            Path to best checkpoint or None
        """
        if not self.best_scores:
            return None
        
        return self.best_scores[0][1]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get checkpoint manager statistics.
        
        Returns:
            Dictionary with checkpoint stats
        """
        return {
            'enabled': self.enabled,
            'checkpoint_dir': str(self.checkpoint_dir),
            'save_interval': self.save_interval,
            'last_checkpoint_step': self.last_checkpoint_step,
            'best_count': len(self.best_scores),
            'best_score': self.best_scores[0][0] if self.best_scores else 0.0,
        }
