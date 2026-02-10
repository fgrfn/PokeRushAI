"""Map visualization for exploration progress.

Visualizes visited coordinates as heatmaps and images.
"""

from pathlib import Path
from typing import Dict, Set, Tuple, Optional
import time

try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  Warning: Pillow not available. Map visualization disabled.")

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  Warning: matplotlib not available. Heatmap visualization disabled.")


# Kanto map dimensions (approximate)
MAP_WIDTH = 256
MAP_HEIGHT = 256

# Color scheme for different map IDs
MAP_COLORS = {
    0: (255, 200, 200),    # Pallet Town - light red
    1: (200, 255, 200),    # Viridian City - light green
    2: (200, 200, 255),    # Pewter City - light blue
    12: (255, 255, 200),   # Route 1 - light yellow
    13: (255, 220, 200),   # Route 2 - light orange
}


class MapVisualizer:
    """Visualizes exploration progress on game maps."""
    
    def __init__(
        self,
        output_dir: Path,
        save_interval: int = 100,
        enabled: bool = True
    ):
        """Initialize map visualizer.
        
        Args:
            output_dir: Directory to save map images
            save_interval: Save map every N steps
            enabled: Whether visualization is enabled
        """
        self.output_dir = Path(output_dir)
        self.save_interval = save_interval
        self.enabled = enabled and PIL_AVAILABLE
        
        # Track visited coordinates: map_id -> set of (x, y) tuples
        self.visited_coords: Dict[int, Set[Tuple[int, int]]] = {}
        
        # Track coordinate visit counts for heatmap
        self.coord_visits: Dict[Tuple[int, int, int], int] = {}  # (map_id, x, y) -> count
        
        self.last_save_step = 0
        self.total_unique_coords = 0
        
        if self.enabled:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            print(f"🗺️  Map visualization enabled: {self.output_dir}")
    
    def add_coordinate(self, map_id: int, x: int, y: int):
        """Record a visited coordinate.
        
        Args:
            map_id: Map ID
            x: X coordinate
            y: Y coordinate
        """
        if not self.enabled:
            return
        
        # Add to visited set
        if map_id not in self.visited_coords:
            self.visited_coords[map_id] = set()
        
        coord = (x, y)
        if coord not in self.visited_coords[map_id]:
            self.visited_coords[map_id].add(coord)
            self.total_unique_coords += 1
        
        # Increment visit count
        key = (map_id, x, y)
        self.coord_visits[key] = self.coord_visits.get(key, 0) + 1
    
    def should_save(self, current_step: int) -> bool:
        """Check if map should be saved.
        
        Args:
            current_step: Current training step
            
        Returns:
            True if map should be saved
        """
        if not self.enabled:
            return False
        
        return (current_step - self.last_save_step) >= self.save_interval
    
    def save_map(self, step: int, episode: int):
        """Save current exploration map.
        
        Args:
            step: Current step number
            episode: Current episode number
        """
        if not self.enabled:
            return
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"map_step{step}_ep{episode}_{timestamp}.png"
        filepath = self.output_dir / filename
        
        try:
            self._generate_map_image(filepath)
            self.last_save_step = step
            print(f"🗺️  Map saved: {filename} ({self.total_unique_coords} unique coords)")
        except Exception as e:
            print(f"⚠️  Failed to save map: {e}")
    
    def _generate_map_image(self, filepath: Path):
        """Generate and save map visualization image.
        
        Args:
            filepath: Path to save image
        """
        if not PIL_AVAILABLE:
            return
        
        # Create image with multiple map sections
        cell_size = 4  # pixels per coordinate
        margin = 20
        
        # Calculate layout
        maps_per_row = 4
        num_maps = len(self.visited_coords)
        
        if num_maps == 0:
            # Create simple message image
            img = Image.new('RGB', (400, 100), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((50, 40), "No coordinates visited yet", fill='black')
            img.save(filepath)
            return
        
        # Create canvas
        map_display_width = 100
        map_display_height = 100
        canvas_width = (map_display_width + margin) * maps_per_row + margin
        rows = (num_maps + maps_per_row - 1) // maps_per_row
        canvas_height = (map_display_height + margin) * rows + margin * 2
        
        img = Image.new('RGB', (canvas_width, canvas_height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw each map
        for idx, (map_id, coords) in enumerate(sorted(self.visited_coords.items())):
            if not coords:
                continue
            
            row = idx // maps_per_row
            col = idx % maps_per_row
            
            offset_x = margin + col * (map_display_width + margin)
            offset_y = margin * 2 + row * (map_display_height + margin)
            
            # Find coordinate bounds
            xs = [x for x, y in coords]
            ys = [y for x, y in coords]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            
            # Scale to fit display area
            width = max(max_x - min_x + 1, 1)
            height = max(max_y - min_y + 1, 1)
            scale_x = map_display_width / width
            scale_y = map_display_height / height
            scale = min(scale_x, scale_y, 10)  # Max 10 pixels per coord
            
            # Draw visited coordinates
            color = MAP_COLORS.get(map_id, (100, 150, 255))
            
            for x, y in coords:
                px = offset_x + int((x - min_x) * scale)
                py = offset_y + int((y - min_y) * scale)
                
                # Get visit count for intensity
                visit_count = self.coord_visits.get((map_id, x, y), 1)
                intensity = min(1.0, visit_count / 10.0)  # Normalize to 0-1
                
                # Adjust color based on intensity
                r = int(color[0] * intensity)
                g = int(color[1] * intensity)
                b = int(color[2] * intensity)
                
                draw.rectangle(
                    [px, py, px + int(scale), py + int(scale)],
                    fill=(r, g, b),
                    outline=(0, 0, 0)
                )
            
            # Draw map label
            draw.text(
                (offset_x, offset_y - 15),
                f"Map {map_id} ({len(coords)} coords)",
                fill='black'
            )
        
        img.save(filepath)
    
    def save_heatmap(self, step: int, episode: int, map_id: Optional[int] = None):
        """Save heatmap visualization.
        
        Args:
            step: Current step number
            episode: Current episode number
            map_id: Optional specific map ID to visualize
        """
        if not self.enabled or not MATPLOTLIB_AVAILABLE:
            return
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"heatmap_step{step}_ep{episode}_{timestamp}.png"
        filepath = self.output_dir / filename
        
        try:
            self._generate_heatmap(filepath, map_id)
            print(f"🔥 Heatmap saved: {filename}")
        except Exception as e:
            print(f"⚠️  Failed to save heatmap: {e}")
    
    def _generate_heatmap(self, filepath: Path, map_id: Optional[int] = None):
        """Generate heatmap visualization.
        
        Args:
            filepath: Path to save heatmap
            map_id: Optional specific map ID
        """
        if not MATPLOTLIB_AVAILABLE:
            return
        
        # Filter coordinates by map_id if specified
        if map_id is not None:
            coords_to_plot = {
                (x, y): count
                for (mid, x, y), count in self.coord_visits.items()
                if mid == map_id
            }
            title = f"Exploration Heatmap - Map {map_id}"
        else:
            # Plot all coordinates (ignoring map_id)
            coords_to_plot = {}
            for (mid, x, y), count in self.coord_visits.items():
                key = (x, y)
                coords_to_plot[key] = coords_to_plot.get(key, 0) + count
            title = "Exploration Heatmap - All Maps"
        
        if not coords_to_plot:
            return
        
        # Create grid
        xs = [x for x, y in coords_to_plot.keys()]
        ys = [y for x, y in coords_to_plot.keys()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        
        grid = np.zeros((height, width))
        
        for (x, y), count in coords_to_plot.items():
            grid[y - min_y, x - min_x] = count
        
        # Plot heatmap
        plt.figure(figsize=(10, 8))
        plt.imshow(grid, cmap='hot', interpolation='nearest', origin='upper')
        plt.colorbar(label='Visit Count')
        plt.title(title)
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.tight_layout()
        plt.savefig(filepath, dpi=150)
        plt.close()
    
    def get_stats(self) -> Dict:
        """Get visualization statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            'enabled': self.enabled,
            'maps_visited': len(self.visited_coords),
            'total_unique_coords': self.total_unique_coords,
            'output_dir': str(self.output_dir),
        }
