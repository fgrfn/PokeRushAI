"""Video recording for gameplay sessions.

Records gameplay frames and saves as MP4 videos for analysis.
Based on PokemonRedExperiments video recording approach.
"""

from pathlib import Path
from typing import Optional
import numpy as np

try:
    import mediapy as media
    MEDIAPY_AVAILABLE = True
except ImportError:
    MEDIAPY_AVAILABLE = False
    print("⚠️  Warning: mediapy not available. Video recording disabled.")


class VideoRecorder:
    """Records gameplay frames to video files."""
    
    def __init__(
        self,
        output_dir: Path,
        fps: int = 60,
        enabled: bool = True
    ):
        """Initialize video recorder.
        
        Args:
            output_dir: Directory to save videos
            fps: Frames per second
            enabled: Whether recording is enabled
        """
        self.output_dir = Path(output_dir)
        self.fps = fps
        self.enabled = enabled and MEDIAPY_AVAILABLE
        
        self.writer: Optional[media.VideoWriter] = None
        self.current_video_path: Optional[Path] = None
        self.frame_count = 0
        
        if self.enabled:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def start_recording(self, video_name: str, frame_shape: tuple):
        """Start a new video recording.
        
        Args:
            video_name: Name for the video file (without extension)
            frame_shape: Shape of frames (height, width)
        """
        if not self.enabled:
            return
        
        # Stop any existing recording
        self.stop_recording()
        
        # Create new video path
        self.current_video_path = self.output_dir / f"{video_name}.mp4"
        
        try:
            # Create video writer
            self.writer = media.VideoWriter(
                self.current_video_path,
                shape=frame_shape,
                fps=self.fps,
                codec='h264'
            )
            self.writer.__enter__()
            self.frame_count = 0
            print(f"📹 Started recording: {self.current_video_path}")
        except Exception as e:
            print(f"⚠️  Failed to start video recording: {e}")
            self.writer = None
            self.enabled = False
    
    def add_frame(self, frame: np.ndarray):
        """Add a frame to the current video.
        
        Args:
            frame: Frame array (H, W, C) in RGB format
        """
        if not self.enabled or self.writer is None:
            return
        
        try:
            # Ensure frame is uint8
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            
            self.writer.add_image(frame)
            self.frame_count += 1
        except Exception as e:
            print(f"⚠️  Failed to add frame: {e}")
    
    def stop_recording(self):
        """Stop current recording and save video."""
        if not self.enabled or self.writer is None:
            return
        
        try:
            self.writer.__exit__(None, None, None)
            print(f"✅ Video saved: {self.current_video_path} ({self.frame_count} frames)")
        except Exception as e:
            print(f"⚠️  Failed to save video: {e}")
        finally:
            self.writer = None
            self.current_video_path = None
            self.frame_count = 0
    
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.enabled and self.writer is not None
    
    def get_stats(self) -> dict:
        """Get recording statistics."""
        return {
            'enabled': self.enabled,
            'recording': self.is_recording(),
            'frame_count': self.frame_count,
            'output_dir': str(self.output_dir),
            'current_video': str(self.current_video_path) if self.current_video_path else None,
        }


class DualVideoRecorder:
    """Records both full gameplay and model view simultaneously."""
    
    def __init__(
        self,
        output_dir: Path,
        fps: int = 60,
        enabled: bool = True
    ):
        """Initialize dual recorder.
        
        Args:
            output_dir: Directory to save videos
            fps: Frames per second
            enabled: Whether recording is enabled
        """
        self.full_recorder = VideoRecorder(output_dir / "full", fps, enabled)
        self.model_recorder = VideoRecorder(output_dir / "model", fps, enabled)
        self.enabled = enabled and MEDIAPY_AVAILABLE
    
    def start_recording(
        self,
        episode_id: str,
        full_shape: tuple,
        model_shape: tuple
    ):
        """Start recording both views.
        
        Args:
            episode_id: Unique identifier for this episode
            full_shape: Shape for full gameplay view
            model_shape: Shape for model input view
        """
        if not self.enabled:
            return
        
        self.full_recorder.start_recording(
            f"episode_{episode_id}_full",
            full_shape
        )
        self.model_recorder.start_recording(
            f"episode_{episode_id}_model",
            model_shape
        )
    
    def add_frames(self, full_frame: np.ndarray, model_frame: np.ndarray):
        """Add frames to both recorders.
        
        Args:
            full_frame: Full gameplay frame
            model_frame: Model input frame
        """
        self.full_recorder.add_frame(full_frame)
        self.model_recorder.add_frame(model_frame)
    
    def stop_recording(self):
        """Stop both recorders."""
        self.full_recorder.stop_recording()
        self.model_recorder.stop_recording()
    
    def is_recording(self) -> bool:
        """Check if either recorder is active."""
        return self.full_recorder.is_recording() or self.model_recorder.is_recording()
    
    def get_stats(self) -> dict:
        """Get combined statistics."""
        return {
            'enabled': self.enabled,
            'full': self.full_recorder.get_stats(),
            'model': self.model_recorder.get_stats(),
        }
