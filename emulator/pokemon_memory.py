"""Pokemon Red/Blue/Yellow Memory Map - Known addresses for game state."""

# Pokemon Red/Blue/Yellow Memory Addresses
MEMORY_MAP = {
    # Player position
    "PLAYER_X": 0xD362,
    "PLAYER_Y": 0xD361,
    
    # Map and location
    "MAP_ID": 0xD35E,
    "MAP_WIDTH": 0xD369,
    "MAP_HEIGHT": 0xD368,
    
    # Badges (bitflags: Boulder, Cascade, Thunder, Rainbow, Soul, Marsh, Volcano, Earth)
    "BADGES": 0xD356,
    
    # Play time
    "PLAYTIME_HOURS_HIGH": 0xDA40,  # High byte of hours
    "PLAYTIME_HOURS_LOW": 0xDA41,   # Low byte of hours
    "PLAYTIME_MINUTES": 0xDA42,
    "PLAYTIME_SECONDS": 0xDA43,
    "PLAYTIME_FRAMES": 0xDA44,
    
    # Party Pokemon
    "PARTY_COUNT": 0xD163,
    "PARTY_SPECIES": 0xD164,  # Array of 6 species IDs
    "PARTY_DATA": 0xD16B,      # Start of party Pokemon data (44 bytes per Pokemon)
    
    # Player info
    "PLAYER_ID": 0xD359,
    "PLAYER_NAME": 0xD158,  # 11 bytes
    
    # Money (3 bytes BCD)
    "MONEY_HIGH": 0xD347,
    "MONEY_MID": 0xD348,
    "MONEY_LOW": 0xD349,
    
    # Items
    "ITEMSBAG_COUNT": 0xD31D,
    "ITEMSBAG_ITEMS": 0xD31E,  # Array
    
    # Event Flags (400+ flags tracking story progress, items, NPCs)
    "EVENT_FLAGS_START": 0xD747,
    "EVENT_FLAGS_END": 0xD87E,  # 311 bytes = ~2488 event flags
    "MUSEUM_TICKET": 0xD754,  # Museum ticket flag (bit 0)
    
    # Party Pokemon Levels (individual level addresses)
    "PARTY_LEVEL_1": 0xD18C,
    "PARTY_LEVEL_2": 0xD1B8,
    "PARTY_LEVEL_3": 0xD1E4,
    "PARTY_LEVEL_4": 0xD210,
    "PARTY_LEVEL_5": 0xD23C,
    "PARTY_LEVEL_6": 0xD268,
    
    # Party Pokemon HP (Current HP is 2 bytes per Pokemon)
    "PARTY_HP_1": 0xD16D,  # Pokemon 1 current HP (2 bytes)
    "PARTY_HP_2": 0xD199,
    "PARTY_HP_3": 0xD1C5,
    "PARTY_HP_4": 0xD1F1,
    "PARTY_HP_5": 0xD21D,
    "PARTY_HP_6": 0xD249,
    
    # Party Pokemon Max HP
    "PARTY_MAX_HP_1": 0xD18D,  # Pokemon 1 max HP (2 bytes)
    "PARTY_MAX_HP_2": 0xD1B9,
    "PARTY_MAX_HP_3": 0xD1E5,
    "PARTY_MAX_HP_4": 0xD211,
    "PARTY_MAX_HP_5": 0xD23D,
    "PARTY_MAX_HP_6": 0xD269,
    
    # Opponent Pokemon Levels (in battle)
    "OPP_LEVEL_1": 0xD8C5,
    "OPP_LEVEL_2": 0xD8F1,
    "OPP_LEVEL_3": 0xD91D,
    "OPP_LEVEL_4": 0xD949,
    "OPP_LEVEL_5": 0xD975,
    "OPP_LEVEL_6": 0xD9A1,
    
    # Battle state
    "BATTLE_TYPE": 0xD057,  # 0 = no battle, 1 = wild, 2 = trainer
    "JOYPAD_DISABLE": 0xD79E,  # 0 = enabled, >0 = disabled (cutscene/dialog)
    
    # Pokedex
    "POKEDEX_OWNED_START": 0xD2F7,  # 19 bytes
    "POKEDEX_SEEN_START": 0xD30A,   # 19 bytes
}

# Pokemon Species ID to Name mapping (First 151 Pokemon)
POKEMON_NAMES = {
    0x01: "Rhydon", 0x02: "Kangaskhan", 0x03: "Nidoran♂", 0x04: "Clefairy",
    0x05: "Spearow", 0x06: "Voltorb", 0x07: "Nidoking", 0x08: "Slowbro",
    0x09: "Ivysaur", 0x0A: "Exeggutor", 0x0B: "Lickitung", 0x0C: "Exeggcute",
    0x0D: "Grimer", 0x0E: "Gengar", 0x0F: "Nidoran♀", 0x10: "Nidoqueen",
    0x11: "Cubone", 0x12: "Rhyhorn", 0x13: "Lapras", 0x14: "Arcanine",
    0x15: "Mew", 0x16: "Gyarados", 0x17: "Shellder", 0x18: "Tentacool",
    0x19: "Gastly", 0x1A: "Scyther", 0x1B: "Staryu", 0x1C: "Blastoise",
    0x1D: "Pinsir", 0x1E: "Tangela", 0x21: "Growlithe", 0x22: "Onix",
    0x23: "Fearow", 0x24: "Pidgey", 0x25: "Slowpoke", 0x26: "Kadabra",
    0x27: "Graveler", 0x28: "Chansey", 0x29: "Machoke", 0x2A: "Mr. Mime",
    0x2B: "Hitmonlee", 0x2C: "Hitmonchan", 0x2D: "Arbok", 0x2E: "Parasect",
    0x2F: "Psyduck", 0x30: "Drowzee", 0x31: "Golem", 0x33: "Hypno",
    0x34: "Magmar", 0x36: "Electabuzz", 0x37: "Magneton", 0x38: "Koffing",
    0x3A: "Mankey", 0x3B: "Seel", 0x3C: "Diglett", 0x3D: "Tauros",
    0x40: "Farfetch'd", 0x41: "Venonat", 0x42: "Dragonite", 0x46: "Doduo",
    0x47: "Poliwag", 0x48: "Jynx", 0x49: "Moltres", 0x4A: "Articuno",
    0x4B: "Zapdos", 0x4C: "Ditto", 0x4D: "Meowth", 0x4E: "Krabby",
    0x52: "Vulpix", 0x53: "Ninetales", 0x54: "Pikachu", 0x55: "Raichu",
    0x58: "Dratini", 0x59: "Dragonair", 0x5A: "Kabuto", 0x5B: "Kabutops",
    0x5C: "Horsea", 0x5D: "Seadra", 0x60: "Sandshrew", 0x61: "Sandslash",
    0x62: "Omanyte", 0x63: "Omastar", 0x64: "Jigglypuff", 0x65: "Wigglytuff",
    0x66: "Eevee", 0x67: "Flareon", 0x68: "Jolteon", 0x69: "Vaporeon",
    0x6A: "Machop", 0x6B: "Zubat", 0x6C: "Ekans", 0x6D: "Paras",
    0x6E: "Poliwhirl", 0x6F: "Poliwrath", 0x70: "Weedle", 0x71: "Kakuna",
    0x72: "Beedrill", 0x73: "Dodrio", 0x74: "Primeape", 0x75: "Dugtrio",
    0x76: "Venomoth", 0x77: "Dewgong", 0x7B: "Caterpie", 0x7C: "Metapod",
    0x7D: "Butterfree", 0x7E: "Machamp", 0x80: "Golduck", 0x81: "Hypno",
    0x82: "Golbat", 0x83: "Mewtwo", 0x84: "Snorlax", 0x85: "Magikarp",
    0x88: "Muk", 0x8A: "Kingler", 0x8B: "Cloyster", 0x8D: "Electrode",
    0x8E: "Clefable", 0x8F: "Weezing", 0x90: "Persian", 0x91: "Marowak",
    0x93: "Haunter", 0x94: "Abra", 0x95: "Alakazam", 0x96: "Pidgeotto",
    0x97: "Pidgeot", 0x98: "Starmie", 0x99: "Bulbasaur", 0x9A: "Venusaur",
    0x9B: "Tentacruel", 0x9D: "Goldeen", 0x9E: "Seaking", 0xA3: "Ponyta",
    0xA4: "Rapidash", 0xA5: "Rattata", 0xA6: "Raticate", 0xA7: "Nidorino",
    0xA8: "Nidorina", 0xA9: "Geodude", 0xAA: "Porygon", 0xAB: "Aerodactyl",
    0xAC: "Magnemite", 0xB0: "Charmander", 0xB1: "Squirtle", 0xB2: "Charmeleon",
    0xB3: "Wartortle", 0xB4: "Charizard", 0xB9: "Oddish", 0xBA: "Gloom",
    0xBB: "Vileplume", 0xBC: "Bellsprout", 0xBD: "Weepinbell", 0xBE: "Victreebel",
}

# Map ID to Location Name mapping
# Covers 160+ major locations, cities, routes, gyms, and dungeons
MAP_NAMES = {
    # Cities and Towns (11 locations)
    0x00: "Pallet Town",
    0x01: "Viridian City",
    0x02: "Pewter City",
    0x03: "Cerulean City",
    0x04: "Lavender Town",
    0x05: "Vermilion City",
    0x06: "Celadon City",
    0x07: "Fuchsia City",
    0x08: "Cinnabar Island",
    0x09: "Indigo Plateau",
    0x0A: "Saffron City",
    
    # Routes (25 routes)
    0x0B: "Route 1", 0x0C: "Route 2", 0x0D: "Route 3", 0x0E: "Route 4",
    0x0F: "Route 5", 0x10: "Route 6", 0x11: "Route 7", 0x12: "Route 8",
    0x13: "Route 9", 0x14: "Route 10", 0x15: "Route 11", 0x16: "Route 12",
    0x17: "Route 13", 0x18: "Route 14", 0x19: "Route 15", 0x1A: "Route 16",
    0x1B: "Route 17", 0x1C: "Route 18", 0x1D: "Route 19", 0x1E: "Route 20",
    0x1F: "Route 21", 0x25: "Route 22", 0x26: "Route 23", 0x27: "Route 24",
    0x28: "Route 25",
    
    # Pallet Town Buildings
    0x33: "Red's House 1F", 0x34: "Red's House 2F",
    0x35: "Blue's House", 0x36: "Oak's Lab",
    
    # Viridian City Buildings
    0x37: "Pokémon Center Viridian", 0x38: "Poké Mart Viridian",
    0x39: "School Viridian", 0x3A: "House Viridian 1",
    0x40: "Viridian Gym",
    
    # Pewter City Buildings  
    0x41: "Pewter Gym", 0x42: "House Pewter 1",
    0x43: "Poké Mart Pewter", 0x44: "House Pewter 2",
    0x45: "Pokémon Center Pewter",
    0x46: "Museum Pewter 1F", 0x47: "Museum Pewter 2F",
    
    # Cerulean City Buildings
    0x48: "Cerulean Gym", 0x49: "Bike Shop",
    0x4A: "Pokémon Center Cerulean", 0x4B: "Poké Mart Cerulean",
    0x4C: "House Cerulean 1", 0x4D: "House Cerulean 2",
    0x4E: "House Cerulean 3", 0x4F: "House Cerulean 4",
    
    # Lavender Town Buildings
    0x50: "Pokémon Center Lavender", 0x51: "Poké Mart Lavender",
    0x52: "House Lavender 1", 0x53: "House Lavender 2",
    0x54: "Name Rater House",
    
    # Vermilion City Buildings
    0x55: "Vermilion Gym", 0x56: "Pokémon Center Vermilion",
    0x57: "Pokémon Fan Club", 0x58: "Poké Mart Vermilion",
    0x5A: "House Vermilion",
    0x5B: "S.S. Anne 1F", 0x5C: "S.S. Anne 2F", 0x5D: "S.S. Anne B1F",
    
    # Celadon City Buildings
    0x5E: "Celadon Gym", 0x5F: "Celadon Mansion 1F",
    0x60: "Celadon Mansion 2F", 0x61: "Celadon Mansion 3F",
    0x62: "Celadon Mansion Roof", 0x63: "Celadon Mansion Roof House",
    0x64: "Pokémon Center Celadon", 0x65: "Game Corner",
    0x66: "Celadon Mart 1F", 0x67: "Celadon Mart 2F",
    0x68: "Celadon Mart 3F", 0x69: "Celadon Mart 4F",
    0x6A: "Celadon Mart Roof", 0x6B: "Celadon Mart Elevator",
    
    # Fuchsia City Buildings + Safari Zone
    0x6F: "Fuchsia Gym", 0x70: "House Fuchsia 1",
    0x71: "Pokémon Center Fuchsia", 0x72: "Poké Mart Fuchsia",
    0x73: "Safari Zone Entrance", 0x74: "House Fuchsia 2",
    0x75: "Warden's House",
    0x76: "Safari Zone East", 0x77: "Safari Zone North",
    0x78: "Safari Zone West", 0x79: "Safari Zone Center",
    0x7A: "Safari Zone Rest House 1", 0x7B: "Safari Zone Rest House 2",
    0x7C: "Safari Zone Rest House 3", 0x7D: "Safari Zone Rest House 4",
    0x7E: "Safari Zone Secret House",
    
    # Cinnabar Island Buildings
    0x7F: "Cinnabar Gym", 0x80: "Cinnabar Lab",
    0x81: "Cinnabar Lab Trade Room", 0x82: "Cinnabar Lab Metronome Room",
    0x83: "Cinnabar Lab Fossil Room", 0x84: "Pokémon Center Cinnabar",
    0x85: "Poké Mart Cinnabar", 0x86: "House Cinnabar",
    
    # Indigo Plateau
    0x87: "Indigo Plateau Lobby",
    
    # Saffron City Buildings
    0x88: "Saffron Gym", 0x89: "Fighting Dojo",
    0x8A: "Pokémon Center Saffron", 0x8B: "Poké Mart Saffron",
    0x8C: "House Saffron 1", 0x8D: "House Saffron 2",
    0x8E: "Copycat's House 1F", 0x8F: "Copycat's House 2F",
    0x90: "Mr. Psychic's House", 0x91: "Pidgey House",
    
    # Forests, Caves & Underground Paths
    0x59: "Viridian Forest",
    0x6C: "Mt. Moon 1F", 0x6D: "Mt. Moon B1F", 0x6E: "Mt. Moon B2F",
    0x92: "Underground Path Route 5", 0x93: "Underground Path Route 6",
    0x94: "Underground Path Route 7", 0x95: "Underground Path Route 8",
    0xA4: "Rock Tunnel 1F", 0xA5: "Rock Tunnel B1F",
    0xA6: "Seafoam Islands 1F", 0xA7: "Seafoam Islands B1F",
    0xA8: "Seafoam Islands B2F", 0xA9: "Seafoam Islands B3F",
    0xAA: "Seafoam Islands B4F",
    
    # Special Locations
    0xAB: "Power Plant",
    0xAC: "Diglett's Cave",
    
    # Victory Road
    0xAD: "Victory Road 1F", 0xAE: "Victory Road 2F", 0xAF: "Victory Road 3F",
    
    # Pokemon Tower (7 floors)
    0xE7: "Pokemon Tower 1F", 0xE8: "Pokemon Tower 2F",
    0xE9: "Pokemon Tower 3F", 0xEA: "Pokemon Tower 4F",
    0xEB: "Pokemon Tower 5F", 0xEC: "Pokemon Tower 6F",
    0xED: "Pokemon Tower 7F",
    
    # Team Rocket Hideout
    0xEE: "Rocket Hideout B1F", 0xEF: "Rocket Hideout B2F",
    0xF0: "Rocket Hideout B3F", 0xF1: "Rocket Hideout B4F",
    0xF2: "Rocket Hideout Elevator",
    
    # Silph Co. (11 floors)
    0xF3: "Silph Co. 1F", 0xF4: "Silph Co. 2F", 0xF5: "Silph Co. 3F",
    0xF6: "Silph Co. 4F", 0xF7: "Silph Co. 5F", 0xF8: "Silph Co. 6F",
    0xF9: "Silph Co. 7F", 0xFA: "Silph Co. 8F", 0xFB: "Silph Co. 9F",
    0xFC: "Silph Co. 10F", 0xFD: "Silph Co. 11F",
    
    # Pokemon Mansion
    0xA0: "Pokemon Mansion 1F", 0xA1: "Pokemon Mansion 2F",
    0xA2: "Pokemon Mansion 3F", 0xA3: "Pokemon Mansion B1F",
    
    # Cerulean Cave (Post-Game)
    0xB0: "Cerulean Cave 1F", 0xB1: "Cerulean Cave 2F",
    0xB2: "Cerulean Cave B1F",
}

def get_map_name(map_id: int) -> str:
    """Get human-readable location name from map ID."""
    return MAP_NAMES.get(map_id, f"Unknown Location (0x{map_id:02X})")

def count_badges(badge_byte: int) -> int:
    """Count number of badges from bitflags."""
    count = 0
    for i in range(8):
        if badge_byte & (1 << i):
            count += 1
    return count

def get_edition_from_title(title: str) -> str:
    """Detect Pokemon edition from cartridge title."""
    title_upper = title.upper().strip()
    if "RED" in title_upper or "POKEMON_R" in title_upper:
        return "red"
    elif "BLUE" in title_upper or "POKEMON_B" in title_upper:
        return "blue"
    elif "YELLOW" in title_upper or "POKEMON_Y" in title_upper:
        return "yellow"
    else:
        return "unknown"

def get_pokemon_name(species_id: int) -> str:
    """Get Pokemon name from species ID."""
    return POKEMON_NAMES.get(species_id, f"Unknown (0x{species_id:02X})")

def decode_bcd_money(high: int, mid: int, low: int) -> int:
    """Decode BCD-encoded money (3 bytes)."""
    # Each byte stores 2 decimal digits in BCD format
    return (
        ((high >> 4) * 100000) + ((high & 0x0F) * 10000) +
        ((mid >> 4) * 1000) + ((mid & 0x0F) * 100) +
        ((low >> 4) * 10) + (low & 0x0F)
    )

def bit_count(byte_value: int) -> int:
    """Count number of set bits in a byte."""
    return bin(byte_value).count('1')

def read_bit(byte_value: int, bit_index: int) -> bool:
    """Read a specific bit from a byte (0-7, where 0 is rightmost)."""
    return bool((byte_value >> bit_index) & 1)

def read_hp_16bit(high: int, low: int) -> int:
    """Read 16-bit HP value from two bytes."""
    return (high << 8) | low

def get_party_levels(memory_reader) -> list[int]:
    """Get all party Pokemon levels.
    
    Args:
        memory_reader: Object with read_memory(address) method
        
    Returns:
        List of up to 6 Pokemon levels
    """
    level_addresses = [
        MEMORY_MAP["PARTY_LEVEL_1"], MEMORY_MAP["PARTY_LEVEL_2"],
        MEMORY_MAP["PARTY_LEVEL_3"], MEMORY_MAP["PARTY_LEVEL_4"],
        MEMORY_MAP["PARTY_LEVEL_5"], MEMORY_MAP["PARTY_LEVEL_6"]
    ]
    party_count = memory_reader.read_memory(MEMORY_MAP["PARTY_COUNT"])
    return [memory_reader.read_memory(addr) for addr in level_addresses[:party_count]]

def get_opponent_levels(memory_reader) -> list[int]:
    """Get all opponent Pokemon levels in battle.
    
    Args:
        memory_reader: Object with read_memory(address) method
        
    Returns:
        List of opponent Pokemon levels (may be empty if not in battle)
    """
    opp_addresses = [
        MEMORY_MAP["OPP_LEVEL_1"], MEMORY_MAP["OPP_LEVEL_2"],
        MEMORY_MAP["OPP_LEVEL_3"], MEMORY_MAP["OPP_LEVEL_4"],
        MEMORY_MAP["OPP_LEVEL_5"], MEMORY_MAP["OPP_LEVEL_6"]
    ]
    return [memory_reader.read_memory(addr) for addr in opp_addresses]

def get_hp_fraction(memory_reader) -> float:
    """Calculate party HP fraction (current / max).
    
    Args:
        memory_reader: Object with read_memory(address) method
        
    Returns:
        HP fraction (0.0 to 1.0)
    """
    hp_addresses = [
        (MEMORY_MAP["PARTY_HP_1"], MEMORY_MAP["PARTY_MAX_HP_1"]),
        (MEMORY_MAP["PARTY_HP_2"], MEMORY_MAP["PARTY_MAX_HP_2"]),
        (MEMORY_MAP["PARTY_HP_3"], MEMORY_MAP["PARTY_MAX_HP_3"]),
        (MEMORY_MAP["PARTY_HP_4"], MEMORY_MAP["PARTY_MAX_HP_4"]),
        (MEMORY_MAP["PARTY_HP_5"], MEMORY_MAP["PARTY_MAX_HP_5"]),
        (MEMORY_MAP["PARTY_HP_6"], MEMORY_MAP["PARTY_MAX_HP_6"]),
    ]
    
    party_count = memory_reader.read_memory(MEMORY_MAP["PARTY_COUNT"])
    if party_count == 0:
        return 1.0
    
    total_hp = 0
    total_max_hp = 0
    
    for i in range(min(party_count, 6)):
        hp_addr, max_hp_addr = hp_addresses[i]
        # Read 2 bytes for HP
        hp_high = memory_reader.read_memory(hp_addr)
        hp_low = memory_reader.read_memory(hp_addr + 1)
        max_hp_high = memory_reader.read_memory(max_hp_addr)
        max_hp_low = memory_reader.read_memory(max_hp_addr + 1)
        
        total_hp += read_hp_16bit(hp_high, hp_low)
        total_max_hp += read_hp_16bit(max_hp_high, max_hp_low)
    
    return total_hp / max(total_max_hp, 1)

def count_event_flags(memory_reader) -> int:
    """Count total number of set event flags.
    
    Args:
        memory_reader: Object with read_memory(address) method
        
    Returns:
        Total count of set event flags
    """
    total = 0
    for address in range(MEMORY_MAP["EVENT_FLAGS_START"], MEMORY_MAP["EVENT_FLAGS_END"]):
        byte_val = memory_reader.read_memory(address)
        total += bit_count(byte_val)
    return total

def is_in_battle(memory_reader) -> bool:
    """Check if currently in battle.
    
    Args:
        memory_reader: Object with read_memory(address) method
        
    Returns:
        True if in battle
    """
    return memory_reader.read_memory(MEMORY_MAP["BATTLE_TYPE"]) > 0
