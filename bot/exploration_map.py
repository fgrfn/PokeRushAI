"""Global Exploration Map for tracking visited areas.

This module provides a global map overlay that tracks which areas
the bot has explored, similar to PokemonRedExperiments approach.
"""

import numpy as np
from typing import Tuple

# Global map dimensions (384x384 pixels)
GLOBAL_MAP_SHAPE = (384, 384)

# Map coordinates for major locations
# Each location has a global anchor point (y, x) on the 384x384 grid
MAP_COORDINATES = {
    # Cities and Towns
    0x00: (61, 9),    # Pallet Town
    0x01: (100, 54),  # Viridian City
    0x02: (135, 54),  # Pewter City
    0x03: (162, 135), # Cerulean City
    0x04: (197, 162), # Lavender Town
    0x05: (215, 135), # Vermilion City
    0x06: (197, 81),  # Celadon City
    0x07: (252, 9),   # Fuchsia City
    0x08: (270, 54),  # Cinnabar Island
    0x09: (9, 54),    # Indigo Plateau
    0x0A: (197, 135), # Saffron City
    
    # Routes
    0x0B: (81, 9),    # Route 1
    0x0C: (108, 54),  # Route 2
    0x0D: (135, 108), # Route 3
    0x0E: (135, 162), # Route 4
    0x0F: (170, 135), # Route 5
    0x10: (188, 135), # Route 6
    0x11: (197, 108), # Route 7
    0x12: (197, 162), # Route 8
    0x13: (215, 162), # Route 9
    0x14: (215, 189), # Route 10
    0x15: (215, 162), # Route 11
    0x16: (233, 162), # Route 12
    0x17: (243, 162), # Route 13
    0x18: (252, 162), # Route 14
    0x19: (252, 135), # Route 15
    0x1A: (197, 54),  # Route 16
    0x1B: (215, 54),  # Route 17
    0x1C: (252, 54),  # Route 18
    0x1D: (270, 81),  # Route 19
    0x1E: (270, 27),  # Route 20
    0x1F: (270, 9),   # Route 21
    0x25: (100, 20),  # Route 22
    0x26: (45, 54),   # Route 23
    0x27: (170, 162), # Route 24
    0x28: (162, 189), # Route 25
    
    # Pallet Town Buildings
    0x33: (61, 9),    # Red's House 1F
    0x34: (61, 0),    # Red's House 2F
    0x35: (91, 9),    # Blue's House
    0x36: (91, 1),    # Oak's Lab
    
    # Viridian City Buildings
    0x37: (100, 54),  # Pokémon Center Viridian
    0x38: (100, 62),  # Poké Mart Viridian
    0x39: (100, 79),  # School Viridian
    0x3A: (100, 45),  # House Viridian 1
    0x40: (100, 36),  # Viridian Gym
    
    # Pewter City Buildings
    0x41: (135, 45),  # Pewter Gym
    0x42: (135, 72),  # House Pewter 1
    0x43: (135, 63),  # Poké Mart Pewter
    0x44: (135, 36),  # House Pewter 2
    0x45: (135, 54),  # Pokémon Center Pewter
    0x46: (135, 99),  # Museum Pewter 1F
    0x47: (135, 90),  # Museum Pewter 2F
    
    # Cerulean City Buildings
    0x48: (162, 126), # Cerulean Gym
    0x49: (162, 144), # Bike Shop
    0x4A: (162, 135), # Pokémon Center Cerulean
    0x4B: (162, 117), # Poké Mart Cerulean
    0x4C: (162, 108), # House Cerulean 1
    0x4D: (162, 153), # House Cerulean 2
    0x4E: (162, 162), # House Cerulean 3
    0x4F: (162, 99),  # House Cerulean 4
    
    # Viridian Forest & Mt. Moon
    0x59: (117, 54),  # Viridian Forest
    0x6C: (135, 135), # Mt. Moon 1F
    0x6D: (135, 144), # Mt. Moon B1F
    0x6E: (135, 153), # Mt. Moon B2F
    
    # Rock Tunnel
    0xA4: (197, 189), # Rock Tunnel 1F
    0xA5: (197, 198), # Rock Tunnel B1F
    
    # Power Plant & Diglett's Cave
    0xAB: (215, 189), # Power Plant
    0xAC: (215, 81),  # Diglett's Cave
    
    # Pokemon Tower
    0xE7: (197, 162), # Pokemon Tower 1F
    0xE8: (197, 153), # Pokemon Tower 2F
    0xE9: (197, 144), # Pokemon Tower 3F
    0xEA: (197, 135), # Pokemon Tower 4F
    0xEB: (197, 126), # Pokemon Tower 5F
    0xEC: (197, 117), # Pokemon Tower 6F
    0xED: (197, 108), # Pokemon Tower 7F
    
    # Default fallback
    "default": (80, 0)
}


class ExplorationMap:
    """Tracks explored areas on a global map."""
    
    def __init__(self, map_size: Tuple[int, int] = GLOBAL_MAP_SHAPE):
        """Initialize exploration map.
        
        Args:
            map_size: Size of global map (height, width)
        """
        self.map_size = map_size
        self.explore_map = np.zeros(map_size, dtype=np.uint8)
        self.coords_pad = 100  # Padding around edges
        
    def local_to_global(self, x: int, y: int, map_id: int) -> Tuple[int, int]:
        """Convert local game coordinates to global map coordinates.
        
        Args:
            x: Local X position
            y: Local Y position
            map_id: Current map ID
            
        Returns:
            (global_y, global_x) coordinates
        """
        # Get anchor coordinates for this map
        if map_id in MAP_COORDINATES:
            anchor_y, anchor_x = MAP_COORDINATES[map_id]
        else:
            anchor_y, anchor_x = MAP_COORDINATES["default"]
        
        # Convert to global coordinates
        # Note: y is inverted in Pokemon (0 is top)
        global_x = anchor_x + x + self.coords_pad * 2
        global_y = self.map_size[0] - (anchor_y - y + self.coords_pad * 2)
        
        # Clamp to map bounds
        global_y = max(0, min(global_y, self.map_size[0] - 1))
        global_x = max(0, min(global_x, self.map_size[1] - 1))
        
        return (global_y, global_x)
    
    def update(self, x: int, y: int, map_id: int) -> bool:
        """Mark a position as explored.
        
        Args:
            x: Local X position
            y: Local Y position
            map_id: Current map ID
            
        Returns:
            True if this is a newly explored position
        """
        global_y, global_x = self.local_to_global(x, y, map_id)
        
        # Check if already explored
        was_explored = self.explore_map[global_y, global_x] > 0
        
        # Mark as explored (255 = fully explored)
        self.explore_map[global_y, global_x] = 255
        
        return not was_explored
    
    def get_explored_count(self) -> int:
        """Get total number of explored positions.
        
        Returns:
            Count of explored tiles
        """
        return np.count_nonzero(self.explore_map)
    
    def get_local_view(self, x: int, y: int, map_id: int, radius: int = 16) -> np.ndarray:
        """Get local view around current position.
        
        Args:
            x: Local X position
            y: Local Y position
            map_id: Current map ID
            radius: Radius of view (in tiles)
            
        Returns:
            2D array of explored tiles around position
        """
        global_y, global_x = self.local_to_global(x, y, map_id)
        
        # Extract local window
        y_min = max(0, global_y - radius)
        y_max = min(self.map_size[0], global_y + radius)
        x_min = max(0, global_x - radius)
        x_max = min(self.map_size[1], global_x + radius)
        
        view = self.explore_map[y_min:y_max, x_min:x_max]
        
        # Pad if at edges
        if view.shape[0] < radius * 2 or view.shape[1] < radius * 2:
            padded = np.zeros((radius * 2, radius * 2), dtype=np.uint8)
            y_offset = radius - (global_y - y_min)
            x_offset = radius - (global_x - x_min)
            padded[y_offset:y_offset+view.shape[0], x_offset:x_offset+view.shape[1]] = view
            return padded
        
        return view
    
    def reset(self):
        """Reset exploration map."""
        self.explore_map.fill(0)
