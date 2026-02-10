"""
Map coordinate system for Pokemon Red/Blue/Yellow
Based on PokemonRedExperiments visualization mapping
"""

import numpy as np

# Pixel size of each game tile (16x16 pixels)
TILE_SIZE = 16

# Global offset for the map (calibration from PokemonRedExperiments)
GLOBAL_OFFSET = np.array([1056 - 16*12, 331])

# Map offsets: converts map_id to pixel grid offset
# Based on https://github.com/PWhiddy/PokemonRedExperiments
MAP_PIXEL_OFFSETS = {
    # Main Towns/Cities
    0: np.array([0, 0]),         # Pallet Town
    1: np.array([-10, 72]),      # Viridian City
    2: np.array([-10, 180]),     # Pewter City
    3: np.array([180, 198]),     # Cerulean City
    
    # Routes
    12: np.array([0, 36]),       # Route 1
    13: np.array([0, 144]),      # Route 2
    14: np.array([30, 172]),     # Route 3
    15: np.array([80, 190]),     # Route 4
    33: np.array([-50, 64]),     # Route 22
    
    # Buildings - Pallet Town
    37: np.array([-9, 2]),       # Red's House 1F
    38: np.array([-9, 25-32]),   # Red's House 2F
    39: np.array([9+12, 2]),     # Blue's House
    40: np.array([25-4, -6]),    # Oak's Lab
    
    # Buildings - Viridian City
    41: np.array([30, 47]),      # Pokemon Center
    42: np.array([30, 55]),      # Poke Mart
    43: np.array([30, 72]),      # School
    44: np.array([30, 64]),      # House 1
    
    # Gates & Transitions
    47: np.array([21, 136]),     # Gate (Viridian/Pewter)
    49: np.array([21, 108]),     # Gate (Route 2)
    50: np.array([21, 108]),     # Gate (Route 2/Viridian Forest)
    
    # Dungeons
    51: np.array([-35, 137]),    # Viridian Forest
    52: np.array([-10, 189]),    # Pewter Museum 1F
    53: np.array([-10, 198]),    # Pewter Museum 2F
    
    # Buildings - Pewter City
    54: np.array([-21, 169]),    # Pewter Gym
    55: np.array([-19, 177]),    # House with Nidoran
    56: np.array([-30, 163]),    # Poke Mart
    57: np.array([-19, 177]),    # House with Trainers
    58: np.array([-25, 154]),    # Pokemon Center
    
    # Mt. Moon
    59: np.array([83, 227]),     # Mt. Moon Entrance
    60: np.array([123, 227]),    # Mt. Moon B1F
    61: np.array([152, 227]),    # Mt. Moon B2F
    
    # Route 4
    68: np.array([65, 190]),     # Pokemon Center (Route 4) 
    
    # Special
    193: np.array([0, 0]),       # Badge Gate (Route 22)
}


def game_coords_to_pixel_coords(x: int, y: int, map_id: int, map_height: int = 2016) -> tuple:
    """
    Convert game coordinates (x, y, map_id) to pixel coordinates on the full Kanto map.
    
    Args:
        x: Player x position in game (0-255)
        y: Player y position in game (0-255)
        map_id: Map index
        map_height: Height of the map image in pixels
        
    Returns:
        (pixel_x, pixel_y) tuple for positioning on the map image
    """
    # Get map offset or default to origin
    if map_id in MAP_PIXEL_OFFSETS:
        offset = MAP_PIXEL_OFFSETS[map_id]
    else:
        # Unknown map - place at origin
        offset = np.array([0, 0])
        x, y = 0, 0
    
    # Calculate pixel coordinate
    # Formula: global_offset + tile_size * (map_offset + player_position)
    coord = GLOBAL_OFFSET + TILE_SIZE * (offset + np.array([x, y]))
    
    # Flip Y coordinate (image coordinates start from top-left)
    coord[1] = map_height - coord[1]
    
    return int(coord[0]), int(coord[1])


def get_map_bounds() -> dict:
    """
    Get the bounding box of the known mapped area.
    Useful for centering/scaling the map view.
    """
    all_coords = []
    for map_id, offset in MAP_PIXEL_OFFSETS.items():
        # Sample some positions in each map (0,0) and (10,10)
        px, py = game_coords_to_pixel_coords(0, 0, map_id)
        all_coords.append((px, py))
        px2, py2 = game_coords_to_pixel_coords(10, 10, map_id)
        all_coords.append((px2, py2))
    
    if not all_coords:
        return {"min_x": 0, "max_x": 1000, "min_y": 0, "max_y": 1000}
    
    xs = [c[0] for c in all_coords]
    ys = [c[1] for c in all_coords]
    
    return {
        "min_x": min(xs),
        "max_x": max(xs),
        "min_y": min(ys),
        "max_y": max(ys),
        "width": max(xs) - min(xs),
        "height": max(ys) - min(ys)
    }


if __name__ == "__main__":
    # Test the coordinate system
    print("Testing coordinate system...")
    print(f"Pallet Town (5, 9, map=0): {game_coords_to_pixel_coords(5, 9, 0)}")
    print(f"Viridian City (10, 10, map=1): {game_coords_to_pixel_coords(10, 10, 1)}")
    print(f"Oak's Lab (5, 5, map=40): {game_coords_to_pixel_coords(5, 5, 40)}")
    print(f"\nMap bounds: {get_map_bounds()}")
