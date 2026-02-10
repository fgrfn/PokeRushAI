"""Action selection policy for bot.

Uses Q-Learning agent with heuristic guidance.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from bot.q_learning import QLearningAgent
from bot.rewards import HeuristicGuide
from core.models import GameState


# Global agent instance (singleton)
_agent: Optional[QLearningAgent] = None


def get_agent(
    actions: List[str] = None,
    q_table_path: Optional[Path] = None
) -> QLearningAgent:
    """Get or create Q-Learning agent instance.
    
    Args:
        actions: Available actions
        q_table_path: Path to Q-table file
        
    Returns:
        QLearningAgent instance
    """
    global _agent
    
    if _agent is None:
        if actions is None:
            actions = ["UP", "DOWN", "LEFT", "RIGHT", "A", "B"]
        
        if q_table_path is None:
            q_table_path = Path("data/q_table.json")
        
        _agent = QLearningAgent(
            actions=actions,
            alpha=0.1,
            gamma=0.95,
            epsilon=0.2,
            q_table_path=q_table_path
        )
    
    return _agent


def select_action(
    state: GameState,
    available_actions: List[str],
    q_table_path: Optional[Path] = None
) -> Tuple[str, str]:
    """Select action using Q-Learning with heuristic guidance.
    
    Args:
        state: Current game state
        available_actions: Actions to choose from
        q_table_path: Path to Q-table file
        
    Returns:
        Tuple of (action, reason)
    """
    agent = get_agent(available_actions, q_table_path)
    
    # Try heuristic guidance first during exploration
    action, is_exploration = agent.select_action(state, available_actions)
    
    if is_exploration:
        # Check if heuristic can guide us
        heuristic_action = HeuristicGuide.suggest_action(state, available_actions)
        if heuristic_action:
            return heuristic_action, "heuristic_guidance"
        return action, "exploration"
    else:
        return action, "exploitation"


def update_q_learning(
    state: GameState,
    action: str,
    reward: float,
    next_state: GameState,
    done: bool
):
    """Update Q-Learning agent with experience.
    
    Args:
        state: Previous state
        action: Action taken
        reward: Reward received
        next_state: New state
        done: Episode complete
    """
    global _agent
    if _agent:
        _agent.update(state, action, reward, next_state, done)


def save_q_table():
    """Save Q-table to disk."""
    global _agent
    if _agent:
        _agent.save_q_table()


def get_agent_stats() -> Dict[str, int]:
    """Get learning statistics.
    
    Returns:
        Stats dictionary
    """
    global _agent
    if _agent:
        return _agent.get_stats()
    return {"states_explored": 0, "total_updates": 0, "q_table_size": 0}
