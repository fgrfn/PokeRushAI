"""Q-Learning Agent for Pokemon Red.

This module implements a tabular Q-Learning agent that learns to play
Pokemon Red through reinforcement learning.
"""

import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.models import GameState


class QLearningAgent:
    """Tabular Q-Learning agent with persistent knowledge."""
    
    def __init__(
        self,
        actions: List[str],
        alpha: float = 0.1,
        gamma: float = 0.95,
        epsilon: float = 0.2,
        q_table_path: Optional[Path] = None
    ):
        """Initialize Q-Learning agent.
        
        Args:
            actions: List of available actions (e.g., ["UP", "DOWN", "A", "B"])
            alpha: Learning rate (0-1)
            gamma: Discount factor (0-1)
            epsilon: Exploration rate (0-1)
            q_table_path: Path to save/load Q-table
        """
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table_path = q_table_path
        
        # Q-table: state -> action -> value
        self.q_table: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        # Statistics
        self.total_updates = 0
        self.states_explored = set()
        
        # Load existing knowledge
        if q_table_path and q_table_path.exists():
            self.load_q_table()
    
    def get_state_key(self, state: GameState) -> str:
        """Convert game state to string key for Q-table.
        
        Uses map_id and badges for manageable state space.
        
        Args:
            state: Current game state
            
        Returns:
            State key string
        """
        return f"map_{state.map_id}_badges_{state.badges}"
    
    def select_action(
        self,
        state: GameState,
        available_actions: Optional[List[str]] = None
    ) -> Tuple[str, bool]:
        """Select action using epsilon-greedy policy.
        
        Args:
            state: Current game state
            available_actions: Actions to choose from (defaults to all)
            
        Returns:
            Tuple of (action, is_exploration)
        """
        if available_actions is None:
            available_actions = self.actions
        
        state_key = self.get_state_key(state)
        self.states_explored.add(state_key)
        
        # Epsilon-greedy: explore vs exploit
        if random.random() < self.epsilon:
            # Explore: random action
            action = random.choice(available_actions)
            return action, True
        else:
            # Exploit: best known action
            q_values = self.q_table[state_key]
            
            if not q_values:
                # No knowledge yet, random action
                action = random.choice(available_actions)
                return action, True
            
            # Choose action with highest Q-value
            best_action = max(
                available_actions,
                key=lambda a: q_values.get(a, 0.0)
            )
            return best_action, False
    
    def update(
        self,
        state: GameState,
        action: str,
        reward: float,
        next_state: GameState,
        done: bool
    ):
        """Update Q-value using Q-learning rule.
        
        Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
        
        Args:
            state: Previous state
            action: Action taken
            reward: Reward received
            next_state: Current state after action
            done: Whether episode is complete
        """
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Current Q-value
        current_q = self.q_table[state_key][action]
        
        # Best Q-value for next state
        if done:
            max_next_q = 0.0
        else:
            next_q_values = self.q_table[next_state_key]
            max_next_q = max(next_q_values.values()) if next_q_values else 0.0
        
        # Q-learning update
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state_key][action] = new_q
        
        self.total_updates += 1
        
        # Auto-save every 100 updates
        if self.total_updates % 100 == 0 and self.q_table_path:
            self.save_q_table()
    
    def save_q_table(self):
        """Save Q-table to JSON file."""
        if not self.q_table_path:
            return
        
        # Convert defaultdict to regular dict for JSON
        regular_q_table = {
            state: dict(actions)
            for state, actions in self.q_table.items()
        }
        
        data = {
            "q_table": regular_q_table,
            "total_updates": self.total_updates,
            "states_explored": len(self.states_explored),
            "alpha": self.alpha,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
        }
        
        self.q_table_path.parent.mkdir(parents=True, exist_ok=True)
        self.q_table_path.write_text(json.dumps(data, indent=2))
    
    def load_q_table(self):
        """Load Q-table from JSON file."""
        if not self.q_table_path or not self.q_table_path.exists():
            return
        
        data = json.loads(self.q_table_path.read_text())
        
        # Load Q-table
        loaded_table = data.get("q_table", {})
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        for state, actions in loaded_table.items():
            for action, value in actions.items():
                self.q_table[state][action] = value
        
        # Load statistics
        self.total_updates = data.get("total_updates", 0)
        states_count = data.get("states_explored", 0)
        
        # Rebuild states_explored from Q-table keys
        self.states_explored = set(self.q_table.keys())
        
        print(f"✓ Loaded Q-table: {len(self.q_table)} states, {self.total_updates} updates")
    
    def get_stats(self) -> Dict[str, int]:
        """Get learning statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            "states_explored": len(self.states_explored),
            "total_updates": self.total_updates,
            "q_table_size": sum(len(actions) for actions in self.q_table.values()),
        }
