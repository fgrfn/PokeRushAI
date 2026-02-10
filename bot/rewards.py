"""Reward calculation and heuristic guidance for Q-Learning.

This module defines the reward structure that guides the bot's learning.
Rewards are shaped to encourage speedrun-relevant behavior.

Based on PokemonRedExperiments reward system with enhancements:
- Event flag tracking (story progress)
- Global exploration map
- Level-based rewards with threshold
- Opponent level tracking
- Healing rewards
- Death penalty
- Stuck detection
"""

from typing import Dict, List, Optional, Any
import numpy as np

from core.models import GameState
from bot.exploration_map import ExplorationMap
from bot.screen_explorer import ScreenExplorer
from emulator import pokemon_memory


class RewardCalculator:
    """Calculates rewards based on game state changes."""
    
    def __init__(self, memory_reader=None, grace_period: int = 50):
        """Initialize reward calculator.
        
        Args:
            memory_reader: Emulator memory reader with read_memory(address) method
            grace_period: Number of initial steps with disabled penalties
        """
        self.memory_reader = memory_reader
        self.grace_period = grace_period
        self.step_count = 0
        
        # Exploration tracking
        self.exploration_map = ExplorationMap()
        self.screen_explorer = ScreenExplorer()  # KNN-based frame deduplication
        self.visited_locations = set()
        self.seen_coords: Dict[str, int] = {}  # coord_string -> visit_count
        self.base_screen_explore = 0  # Baseline unique frames at episode start
        
        # Position tracking
        self.position_history: List[tuple] = []
        self.max_history = 10
        
        # Max progress trackers (for monotonic rewards)
        self.base_event_flags = 0  # Set at reset
        self.max_event_flags = 0
        self.max_level_sum = 0
        self.max_opponent_level = 0
        self.max_explored_tiles = 0
        
        # Health tracking
        self.last_health = 1.0
        self.party_size = 0
        self.died_count = 0
        self.total_healing_reward = 0.0
        
        # Reward scaling
        self.reward_scale = 1.0
        self.explore_weight = 1.0
        
    def reset(self):
        """Reset per-episode state."""
        self.exploration_map.reset()
        self.screen_explorer.reset()
        self.visited_locations.clear()
        self.seen_coords.clear()
        self.position_history.clear()
        self.base_screen_explore = 0
        
        # Initialize base event flags if we have access to memory
        if self.memory_reader:
            self.base_event_flags = pokemon_memory.count_event_flags(self.memory_reader)
        
        self.max_event_flags = 0
        self.max_level_sum = 0
        self.max_opponent_level = 0
        self.max_explored_tiles = 0
        
        self.last_health = 1.0
        self.party_size = 1  # Starter
        self.died_count = 0
        self.total_healing_reward = 0.0
        self.step_count = 0
    
    def calculate_reward(
        self,
        prev_state: GameState,
        curr_state: GameState,
        elapsed_time: float
    ) -> Dict[str, float]:
        """Calculate detailed reward breakdown for state transition.
        
        Args:
            prev_state: Previous game state
            curr_state: Current game state
            elapsed_time: Time taken for this step (seconds)
            
        Returns:
            Dictionary with reward components and total
        """
        self.step_count += 1
        rewards = {}
        
        # Core rewards (always active)
        rewards['badge'] = self._badge_reward(prev_state, curr_state)
        rewards['event'] = self._event_reward()
        rewards['level'] = self._level_reward()
        rewards['explore'] = self._exploration_reward(curr_state)
        rewards['opponent'] = self._opponent_level_reward()
        
        # Conditional rewards (grace period aware)
        rewards['heal'] = self._healing_reward(curr_state)
        rewards['death'] = self._death_penalty()
        
        # Penalties (disabled during grace period)
        in_grace_period = self.step_count <= self.grace_period
        if not in_grace_period:
            rewards['stuck'] = self._stuck_penalty(curr_state)
            rewards['loop'] = self._loop_penalty(curr_state)
        else:
            rewards['stuck'] = 0.0
            rewards['loop'] = 0.0
        
        # Update tracking state
        self._update_tracking(curr_state)
        
        # Calculate total
        rewards['total'] = sum(rewards.values())
        
        return rewards
    
    def _badge_reward(self, prev_state: GameState, curr_state: GameState) -> float:
        """Massive reward for earning badges (primary objective)."""
        if curr_state.badges > prev_state.badges:
            badge_increase = curr_state.badges - prev_state.badges
            reward = self.reward_scale * badge_increase * 10.0  # 10 points per badge
            print(f"🎖️ Badge earned! Total: {curr_state.badges} (+{reward:.1f} reward)")
            return reward
        return 0.0
    
    def _event_reward(self) -> float:
        """Reward for triggering event flags (story progress).
        
        Event flags track:
        - Story progression (Oak's Parcel, Pokedex, etc.)
        - Item pickups
        - NPC interactions
        - Gym badge flags (duplicate of badge byte)
        - Cut tree usage, strength boulder moves
        """
        if not self.memory_reader:
            return 0.0
        
        # Count current event flags (excluding museum ticket to avoid cheese)
        current_events = pokemon_memory.count_event_flags(self.memory_reader)
        
        # Subtract museum ticket if set (0xD754 bit 0)
        museum_byte = self.memory_reader.read_memory(pokemon_memory.MEMORY_MAP["MUSEUM_TICKET"])
        museum_ticket_set = pokemon_memory.read_bit(museum_byte, 0)
        if museum_ticket_set:
            current_events -= 1
        
        # Get events relative to episode start
        events_this_episode = max(0, current_events - self.base_event_flags)
        
        # Monotonic reward (only increases)
        if events_this_episode > self.max_event_flags:
            reward_increase = events_this_episode - self.max_event_flags
            self.max_event_flags = events_this_episode
            return self.reward_scale * reward_increase * 4.0  # 4 points per event
        
        return 0.0
    
    def _level_reward(self) -> float:
        """Reward for leveling up Pokemon with threshold scaling.
        
        Early levels are rewarded linearly to encourage training.
        After level ~22 (threshold), rewards scale down to encourage gym progression.
        """
        if not self.memory_reader:
            return 0.0
        
        party_levels = pokemon_memory.get_party_levels(self.memory_reader)
        if not party_levels:
            return 0.0
        
        # Calculate total level sum, subtracting starter level
        min_poke_level = 2
        starter_additional_levels = 4
        level_sum = sum(max(level - min_poke_level, 0) for level in party_levels)
        level_sum = max(0, level_sum - starter_additional_levels)
        
        # Apply threshold scaling
        explore_threshold = 22
        scale_factor = 4
        
        if level_sum < explore_threshold:
            scaled_level_sum = level_sum
        else:
            # Reduce reward rate after threshold
            scaled_level_sum = (level_sum - explore_threshold) / scale_factor + explore_threshold
        
        # Monotonic reward
        if scaled_level_sum > self.max_level_sum:
            reward_increase = scaled_level_sum - self.max_level_sum
            self.max_level_sum = scaled_level_sum
            return self.reward_scale * reward_increase
        
        return 0.0
    
    def _exploration_reward(self, curr_state: GameState) -> float:
        """Reward for exploring new areas.
        
        Two components:
        1. Global map exploration (new tiles visited)
        2. Location discovery (new named locations)
        """
        reward = 0.0
        
        # Update global exploration map
        is_new_tile = self.exploration_map.update(
            curr_state.x, curr_state.y, curr_state.map_id
        )
        
        if is_new_tile:
            explored_count = self.exploration_map.get_explored_count()
            if explored_count > self.max_explored_tiles:
                tile_increase = explored_count - self.max_explored_tiles
                self.max_explored_tiles = explored_count
                # 0.1 points per new tile
                reward += self.reward_scale * self.explore_weight * tile_increase * 0.1
        
        # Update coordinate visit tracking
        coord_string = f"x:{curr_state.x} y:{curr_state.y} m:{curr_state.map_id}"
        if coord_string not in self.seen_coords:
            self.seen_coords[coord_string] = 0
        self.seen_coords[coord_string] += 1
        
        # Location discovery bonus
        location_key = f"{curr_state.location}_{curr_state.map_id}"
        if location_key not in self.visited_locations:
            self.visited_locations.add(location_key)
            reward += self.reward_scale * 5.0  # 5 points for new location
            print(f"🗺️ New location: {curr_state.location}")
        
        return reward
    
    def _opponent_level_reward(self) -> float:
        """Reward for encountering stronger opponents.
        
        Encourages progression by rewarding battles with higher-level trainers.
        """
        if not self.memory_reader:
            return 0.0
        
        # Check if in battle
        if not pokemon_memory.is_in_battle(self.memory_reader):
            return 0.0
        
        opponent_levels = pokemon_memory.get_opponent_levels(self.memory_reader)
        if not opponent_levels:
            return 0.0
        
        max_opp_level = max(opponent_levels) - 5  # Subtract base level
        max_opp_level = max(0, max_opp_level)
        
        # Monotonic reward
        if max_opp_level > self.max_opponent_level:
            reward_increase = max_opp_level - self.max_opponent_level
            self.max_opponent_level = max_opp_level
            return self.reward_scale * reward_increase * 0.5  # 0.5 points per opponent level
        
        return 0.0
    
    def _healing_reward(self, curr_state: GameState) -> float:
        """Reward for healing Pokemon (encourages using Pokemon Centers).
        
        Detects health increases without party size changes (rules out Pokemon capture).
        """
        if not self.memory_reader:
            return 0.0
        
        current_health = pokemon_memory.get_hp_fraction(self.memory_reader)
        current_party_size = self.memory_reader.read_memory(
            pokemon_memory.MEMORY_MAP["PARTY_COUNT"]
        )
        
        # Check if healed (health increased without capturing new Pokemon)
        if current_health > self.last_health and current_party_size == self.party_size:
            if self.last_health > 0:
                # Normal healing
                heal_amount = current_health - self.last_health
                reward = self.reward_scale * heal_amount * 10.0  # 10 points per HP fraction healed
                self.total_healing_reward += reward
                return reward
            else:
                # Revived from being blacked out (no reward, just track death)
                self.died_count += 1
        
        return 0.0
    
    def _death_penalty(self) -> float:
        """Penalty for dying (all Pokemon fainted)."""
        return self.reward_scale * self.died_count * -0.1
    
    def _stuck_penalty(self, curr_state: GameState) -> float:
        """Penalty for getting stuck in one area (anti-grinding).
        
        If the same coordinate has been visited >600 times, apply penalty.
        """
        coord_string = f"x:{curr_state.x} y:{curr_state.y} m:{curr_state.map_id}"
        visit_count = self.seen_coords.get(coord_string, 0)
        
        if visit_count > 600:
            return self.reward_scale * -0.05
        
        return 0.0
    
    def _loop_penalty(self, curr_state: GameState) -> float:
        """Penalty for moving in tight loops (repetitive behavior)."""
        current_pos = (curr_state.x, curr_state.y, curr_state.map_id)
        self.position_history.append(current_pos)
        
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)
        
        # Check if stuck (only 3 unique positions in last 10 steps)
        if len(self.position_history) >= self.max_history:
            unique_positions = len(set(self.position_history))
            if unique_positions <= 3:
                return -1.0  # Fixed penalty
        
        return 0.0
    
    def _update_tracking(self, curr_state: GameState):
        """Update internal tracking state."""
        if self.memory_reader:
            self.last_health = pokemon_memory.get_hp_fraction(self.memory_reader)
            self.party_size = self.memory_reader.read_memory(
                pokemon_memory.MEMORY_MAP["PARTY_COUNT"]
            )
    
    def add_screen_frame(self, frame: np.ndarray) -> bool:
        """Add screen frame for KNN exploration tracking.
        
        Args:
            frame: Screen frame (H, W, C) numpy array
            
        Returns:
            True if frame is novel
        """
        is_novel = self.screen_explorer.add_frame(frame)
        return is_novel
    
    def get_screen_exploration_reward(self) -> float:
        """Get reward for screen-based exploration.
        
        Uses KNN to deduplicate frames - rewards novel screens.
        Helps prevent getting stuck in menus or repeated states.
        """
        unique_frames = self.screen_explorer.get_unique_frame_count()
        
        # Calculate reward based on new unique frames
        new_frames = unique_frames - self.base_screen_explore
        
        if new_frames > 0:
            # Small reward per unique frame (0.004 points)
            # This adds up over time but doesn't overwhelm other rewards
            reward = self.reward_scale * self.explore_weight * new_frames * 0.004
            self.base_screen_explore = unique_frames
            return reward
        
        return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current reward statistics.
        
        Returns:
            Dictionary with current stats
        """
        screen_stats = self.screen_explorer.get_stats()
        return {
            'max_event_flags': self.max_event_flags,
            'max_level_sum': self.max_level_sum,
            'max_opponent_level': self.max_opponent_level,
            'explored_tiles': self.max_explored_tiles,
            'unique_coords': len(self.seen_coords),
            'unique_frames': screen_stats['unique_frames'],
            'died_count': self.died_count,
            'total_healing_reward': self.total_healing_reward,
        }


class HeuristicGuide:
    """Provides directional hints to accelerate learning."""
    
    @staticmethod
    def get_hint(state: GameState) -> Optional[str]:
        """Get directional hint based on current state.
        
        Args:
            state: Current game state
            
        Returns:
            Hint string or None
        """
        location = state.location.lower()
        
        # Early game routing
        if "pallet" in location and state.badges == 0:
            return "Try going UP/NORTH to leave Pallet Town"
        
        if "route 1" in location and state.badges == 0:
            return "Continue NORTH to Viridian City"
        
        if "viridian" in location and state.badges == 0:
            return "Go NORTH through forest to Pewter City"
        
        if "pewter" in location and state.badges == 0:
            return "Enter gym (building) to battle for first badge"
        
        return None
    
    @staticmethod
    def suggest_action(
        state: GameState,
        available_actions: List[str]
    ) -> Optional[str]:
        """Suggest action based on hint.
        
        Args:
            state: Current game state
            available_actions: Actions to choose from
            
        Returns:
            Suggested action or None
        """
        hint = HeuristicGuide.get_hint(state)
        
        if not hint:
            return None
        
        # Map hints to actions
        if "UP" in hint or "NORTH" in hint:
            if "UP" in available_actions:
                return "UP"
        
        if "DOWN" in hint or "SOUTH" in hint:
            if "DOWN" in available_actions:
                return "DOWN"
        
        if "LEFT" in hint or "WEST" in hint:
            if "LEFT" in available_actions:
                return "LEFT"
        
        if "RIGHT" in hint or "EAST" in hint:
            if "RIGHT" in available_actions:
                return "RIGHT"
        
        # For entering buildings/fighting
        if "gym" in hint or "building" in hint or "battle" in hint:
            if "A" in available_actions:
                return "A"
        
        return None

        """Get directional hint based on current state.
        
        Args:
            state: Current game state
            
        Returns:
            Hint string or None
        """
        location = state.location.lower()
        
        # Early game routing
        if "pallet" in location and state.badges == 0:
            return "Try going UP/NORTH to leave Pallet Town"
        
        if "route 1" in location and state.badges == 0:
            return "Continue NORTH to Viridian City"
        
        if "viridian" in location and state.badges == 0:
            return "Go NORTH through forest to Pewter City"
        
        if "pewter" in location and state.badges == 0:
            return "Enter gym (building) to battle for first badge"
        
        return None
    
    @staticmethod
    def suggest_action(
        state: GameState,
        available_actions: List[str]
    ) -> Optional[str]:
        """Suggest action based on hint.
        
        Args:
            state: Current game state
            available_actions: Actions to choose from
            
        Returns:
            Suggested action or None
        """
        hint = HeuristicGuide.get_hint(state)
        
        if not hint:
            return None
        
        # Map hints to actions
        if "UP" in hint or "NORTH" in hint:
            if "UP" in available_actions:
                return "UP"
        
        if "DOWN" in hint or "SOUTH" in hint:
            if "DOWN" in available_actions:
                return "DOWN"
        
        if "LEFT" in hint or "WEST" in hint:
            if "LEFT" in available_actions:
                return "LEFT"
        
        if "RIGHT" in hint or "EAST" in hint:
            if "RIGHT" in available_actions:
                return "RIGHT"
        
        # For entering buildings/fighting
        if "gym" in hint or "building" in hint or "battle" in hint:
            if "A" in available_actions:
                return "A"
        
        return None
