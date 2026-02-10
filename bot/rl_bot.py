from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from bot.policy import select_action, update_q_learning, save_q_table, get_agent_stats
from bot.rewards import RewardCalculator
from bot.session_stats import SessionStats
from bot.tensorboard_logger import TensorboardLogger
from bot.checkpoint_manager import CheckpointManager
from bot.map_visualizer import MapVisualizer
from core.models import GameState, RunDecision
from emulator.game_starter import GameStarter
from emulator.pyboy_emulator import PyBoyEmulator
from run_logging.run_logger import RunLogger


@dataclass
class BotSettings:
    actions: List[str]
    max_steps: int = 100


class PokeRushBot:
    def __init__(
        self,
        emulator: PyBoyEmulator,
        logger: RunLogger,
        data_path: Path,
        settings: BotSettings,
    ) -> None:
        self.emulator = emulator
        self.logger = logger
        self.data_path = data_path
        self.settings = settings
        self.reward_calculator = RewardCalculator(memory_reader=emulator)
        self.recent_actions = []  # Store recent actions for WebUI
        self.current_step = 0
        self.total_reward = 0.0
        self.visited_tiles = set()  # Track unique tiles visited
        
        # Session statistics tracker (use parent of data_path since it points to state.json)
        stats_dir = data_path.parent / "session_stats"
        self.session_stats = SessionStats(
            session_dir=stats_dir,
            save_interval=100,
            enabled=True
        )
        
        # Tensorboard logger
        tensorboard_dir = data_path.parent / "tensorboard"
        self.tensorboard = TensorboardLogger(
            log_dir=tensorboard_dir,
            enabled=True
        )
        
        # Checkpoint manager
        checkpoint_dir = data_path.parent / "checkpoints"
        self.checkpoint_manager = CheckpointManager(
            checkpoint_dir=checkpoint_dir,
            save_interval=1000,
            keep_best=3,
            enabled=True
        )
        
        # Map visualizer
        map_dir = data_path.parent / "maps"
        self.map_visualizer = MapVisualizer(
            output_dir=map_dir,
            save_interval=500,
            enabled=True
        )
        
        self.episode_count = 0
        self.best_reward = float('-inf')
        self.best_badges = 0

    def run(self, milestones: Iterable[str], auto_start: bool = True, use_init_state: bool = False) -> None:
        """Run bot with Q-Learning (CLI mode).
        
        Args:
            milestones: Milestones to track
            auto_start: Whether to auto-start new game
            use_init_state: Whether to use pre-loaded init state (skip emulator.load())
        """
        try:
            self._run_internal(milestones, auto_start, use_init_state)
        finally:
            # Always cleanup emulator
            try:
                self.emulator.stop()
            except:
                pass
    
    def _run_internal(self, milestones: Iterable[str], auto_start: bool = True, use_init_state: bool = False) -> None:
        """Internal run method with cleanup handling.
        
        Args:
            milestones: Milestones to track
            auto_start: Whether to auto-start new game
            use_init_state: Whether to use pre-loaded init state
        """
        # Only load emulator if NOT using init state
        # (init state is loaded externally before calling run())
        if not use_init_state:
            self.emulator.load()
            
            # Auto-start game if requested, otherwise wait for manual start
            if auto_start:
                from emulator.game_starter import GameStarter
                print("🎮 Waiting for manual start (play intro yourself)...")
                starter = GameStarter(self.emulator)
                success = starter.wait_for_manual_start()
                if not success:
                    print("❌ Failed to start game")
                    return
            else:
                print("👤 Manual start mode enabled")
                from emulator.game_starter import GameStarter
                starter = GameStarter(self.emulator)
                success = starter.wait_for_manual_start()
                if not success:
                    print("❌ Timeout waiting for manual start")
                    return
        else:
            print("✅ Using pre-loaded init state - starting directly in Pallet Town!")
            # No GameStarter needed - state is already loaded and ready to go
        
        # Define badge milestones
        badge_names = [
            "Boulder Badge (Pewter City)",
            "Cascade Badge (Cerulean City)",
            "Thunder Badge (Vermilion City)",
            "Rainbow Badge (Celadon City)",
            "Soul Badge (Fuchsia City)",
            "Marsh Badge (Saffron City)",
            "Volcano Badge (Cinnabar Island)",
            "Earth Badge (Viridian City)",
            "Elite Four Victory"
        ]
        
        run_id = self.logger.start_run(badge_names)
        
        # Reset reward calculator for new episode
        self.reward_calculator.reset()
        
        # Increment episode counter
        self.episode_count += 1
        
        # Get initial state
        prev_state = self.emulator.get_state()
        prev_action = None
        self.total_reward = 0.0
        self.current_step = 0
        self.recent_actions = []
        self.visited_tiles = set()
        prev_badges = prev_state.badges
        
        print(f"\n🚀 Starting Q-Learning bot for {self.settings.max_steps} steps...")
        print(f"   Location: {prev_state.location}, Badges: {prev_state.badges}\n")
        
        for step in range(self.settings.max_steps):
            self.current_step = step
            step_start = time.time()
            
            # Select action
            action, reason = select_action(prev_state, self.settings.actions)
            
            # Execute action
            self.emulator.step(action)
            curr_state = self.emulator.get_state()
            
            # Calculate reward
            elapsed = time.time() - step_start
            reward_dict = self.reward_calculator.calculate_reward(
                prev_state, curr_state, elapsed
            )
            reward = reward_dict['total']
            self.total_reward += reward
            
            # Update Q-Learning (if we have previous experience)
            if prev_action is not None:
                done = (step == self.settings.max_steps - 1)
                update_q_learning(prev_state, prev_action, reward, curr_state, done)
            
            # Track visited tiles
            tile_key = f"{curr_state.location}_{curr_state.x}_{curr_state.y}"
            self.visited_tiles.add(tile_key)
            
            # Record session statistics
            reward_stats = self.reward_calculator.get_stats()
            # Read party info directly from memory (GameState doesn't include it)
            from emulator.pokemon_memory import MEMORY_MAP
            party_count = self.emulator.read_memory(MEMORY_MAP["PARTY_COUNT"])
            levels = [
                self.emulator.read_memory(MEMORY_MAP[f"PARTY_LEVEL_{i}"])
                for i in range(1, min(party_count + 1, 7))
            ] if party_count > 0 else []
            
            self.session_stats.record_step(
                step=step,
                x=curr_state.x,
                y=curr_state.y,
                map_id=curr_state.map_id,
                location=curr_state.location,
                action=action,
                party_count=party_count,
                levels=levels,
                party_types=[],  # Species IDs not critical for stats
                hp_fraction=1.0,  # HP tracking not critical for basic stats
                badges=curr_state.badges,
                event_reward=reward_stats.get('event_flags', 0),
                total_reward=self.total_reward,
                unique_coords=len(self.visited_tiles),
                unique_frames=reward_stats.get('unique_frames', 0),
                deaths=reward_stats.get('deaths', 0),
            )
            
            # Track coordinate for map visualization
            self.map_visualizer.add_coordinate(curr_state.map_id, curr_state.x, curr_state.y)
            
            # Log to Tensorboard (every 20 steps)
            if step % 20 == 0:
                agent_stats = get_agent_stats()
                self.tensorboard.log_step(
                    step=step,
                    reward=reward,
                    total_reward=self.total_reward,
                    badges=curr_state.badges,
                    location=curr_state.location,
                    action=action
                )
                self.tensorboard.log_q_learning(
                    step=step,
                    q_table_size=agent_stats['q_table_size'],
                    states_explored=agent_stats['states_explored'],
                    total_updates=agent_stats['total_updates']
                )
                self.tensorboard.log_exploration(
                    step=step,
                    unique_coords=len(self.visited_tiles),
                    unique_frames=reward_stats.get('unique_frames', 0),
                    event_flags=reward_stats.get('event_flags', 0),
                    heal_count=reward_stats.get('heal_count', 0),
                    opponent_count=reward_stats.get('opponent_count', 0)
                )
            
            # Save map visualization periodically
            if self.map_visualizer.should_save(step):
                self.map_visualizer.save_map(step, self.episode_count)
            
            # Save checkpoint periodically
            if self.checkpoint_manager.should_checkpoint(step):
                q_table_path = self.data_path.parent / "q_table.pkl"
                checkpoint_stats = {
                    'step': step,
                    'episode': self.episode_count,
                    'total_reward': self.total_reward,
                    'badges': curr_state.badges,
                    'unique_coords': len(self.visited_tiles),
                    **agent_stats
                }
                self.checkpoint_manager.save_checkpoint(
                    step=step,
                    episode=self.episode_count,
                    q_table_path=q_table_path,
                    stats=checkpoint_stats,
                    score=self.total_reward
                )
            
            # Check for badge progress
            if curr_state.badges > prev_badges:
                badge_num = curr_state.badges
                if badge_num <= len(badge_names):
                    milestone_name = badge_names[badge_num - 1]
                    self.logger.log_milestone(run_id, milestone_name, curr_state)
                    print(f"\n🏅 BADGE EARNED: {milestone_name}")
                    print(f"   Total badges: {badge_num}/8")
                    print(f"   Steps taken: {step}")
                    print(f"   Total reward: {self.total_reward:+.1f}\n")
                    
                    # Save best checkpoint for new badge
                    if curr_state.badges > self.best_badges:
                        self.best_badges = curr_state.badges
                        q_table_path = self.data_path.parent / "q_table.pkl"
                        agent_stats = get_agent_stats()
                        self.checkpoint_manager.save_best_checkpoint(
                            step=step,
                            episode=self.episode_count,
                            score=self.total_reward,
                            q_table_path=q_table_path,
                            stats={
                                'badges': curr_state.badges,
                                'total_reward': self.total_reward,
                                'unique_coords': len(self.visited_tiles),
                                **agent_stats
                            },
                            reason=f"badge{curr_state.badges}"
                        )
                prev_badges = curr_state.badges
            
            # Store recent action for WebUI
            self.recent_actions.append({
                "step": step,
                "action": action,
                "reward": round(reward, 2),
                "location": curr_state.location
            })
            if len(self.recent_actions) > 100:
                self.recent_actions.pop(0)
            
            # Logging
            decision = RunDecision(
                step=step,
                action=action,
                reason=reason,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )
            self.logger.log_decision(run_id, decision, curr_state)
            self._write_state(curr_state)
            
            # Progress output
            if step % 20 == 0:
                stats = get_agent_stats()
                print(f"Step {step:3d}: {curr_state.location:20s} "
                      f"Badges: {curr_state.badges}  "
                      f"Reward: {self.total_reward:+7.1f}  "
                      f"Q-States: {stats['states_explored']}  "
                      f"Tiles: {len(self.visited_tiles)}")
            
            # Update for next iteration
            prev_state = curr_state
            prev_action = action
            
            time.sleep(0.01)
        
        # Save Q-table
        save_q_table()
        
        # Save session statistics
        self.session_stats.save_to_csv()
        
        # Save final map visualization
        self.map_visualizer.save_map(self.settings.max_steps, self.episode_count)
        try:
            self.map_visualizer.save_heatmap(self.settings.max_steps, self.episode_count)
        except Exception:
            pass  # Heatmap requires matplotlib, skip if not available
        
        # Save final checkpoint
        q_table_path = self.data_path.parent / "q_table.pkl"
        final_stats = {
            'step': self.settings.max_steps,
            'episode': self.episode_count,
            'total_reward': self.total_reward,
            'badges': curr_state.badges,
            'unique_coords': len(self.visited_tiles),
            **stats
        }
        self.checkpoint_manager.save_checkpoint(
            step=self.settings.max_steps,
            episode=self.episode_count,
            q_table_path=q_table_path,
            stats=final_stats,
            score=self.total_reward,
            is_best=False
        )
        
        # Check if this is best run
        if self.total_reward > self.best_reward:
            self.best_reward = self.total_reward
            self.checkpoint_manager.save_best_checkpoint(
                step=self.settings.max_steps,
                episode=self.episode_count,
                score=self.total_reward,
                q_table_path=q_table_path,
                stats=final_stats,
                reason="highest_reward"
            )
        
        # Log final episode to Tensorboard
        self.tensorboard.log_episode(
            episode=self.episode_count,
            total_steps=self.settings.max_steps,
            total_reward=self.total_reward,
            max_badges=curr_state.badges,
            unique_coords=len(self.visited_tiles),
            unique_frames=reward_stats.get('unique_frames', 0),
            deaths=reward_stats.get('deaths', 0)
        )
        self.tensorboard.flush()
        
        # Final summary
        print(f"\n? Bot completed {self.settings.max_steps} steps")
        print(f"   Total reward: {self.total_reward:+.1f}")
        print(f"   Final badges: {curr_state.badges}")
        print(f"   States explored: {stats['states_explored']}")
        print(f"   Q-table size: {stats['q_table_size']}")
        print(f"   Learning updates: {stats['total_updates']}")
        print(f"   Tiles visited: {len(self.visited_tiles)}\n")
        
        self.logger.finish_run(run_id)
    
    def run_in_webui(
        self,
        milestones: Iterable[str],
        auto_start: bool = False,
        use_init_state: bool = False,
        stop_flag: Optional[callable] = None
    ) -> None:
        """Run bot for WebUI (emulator already loaded).
        
        Args:
            milestones: Milestones to track
            auto_start: Whether to auto-start new game
            use_init_state: Whether to use pre-loaded init state
            stop_flag: Function that returns True if bot should stop
        """
        # Don't reload emulator if using init state or already loaded in WebUI
        if not use_init_state:
            # Emulator was already loaded in WebUI, no need to reload
            # But if auto_start requested, use GameStarter
            if auto_start:
                from emulator.game_starter import GameStarter
                print("🎮 Waiting for manual start (play intro yourself)...")
                starter = GameStarter(self.emulator)
                success = starter.wait_for_manual_start()
                if not success:
                    print("❌ Failed to start game")
                    return
        else:
            print("✅ Using pre-loaded init state - starting directly in Pallet Town! (WebUI mode)")
            # No GameStarter needed - state is already loaded and ready
        
        # Define badge milestones
        badge_names = [
            "Boulder Badge (Pewter City)",
            "Cascade Badge (Cerulean City)",
            "Thunder Badge (Vermilion City)",
            "Rainbow Badge (Celadon City)",
            "Soul Badge (Fuchsia City)",
            "Marsh Badge (Saffron City)",
            "Volcano Badge (Cinnabar Island)",
            "Earth Badge (Viridian City)",
            "Elite Four Victory"
        ]
        
        run_id = self.logger.start_run(badge_names)
        
        # Reset reward calculator for new episode
        self.reward_calculator.reset()
        
        # Start episode tracking (WebUI)
        self.session_stats.start_episode()
        
        # Get initial state
        prev_state = self.emulator.get_state()
        prev_action = None
        self.total_reward = 0.0
        self.current_step = 0
        self.recent_actions = []
        self.visited_tiles = set()
        prev_badges = prev_state.badges
        
        print(f"\n🚀 Starting Q-Learning bot for {self.settings.max_steps} steps...")
        print(f"   Location: {prev_state.location}, Badges: {prev_state.badges}\n")
        
        for step in range(self.settings.max_steps):
            # Check if we should stop
            if stop_flag and stop_flag():
                print("\n🛑 Bot stopped by user")
                break
            step_start = time.time()
            
            # Select action
            action, reason = select_action(prev_state, self.settings.actions)
            
            # Execute action
            self.emulator.step(action)
            curr_state = self.emulator.get_state()
            
            # Calculate reward
            elapsed = time.time() - step_start
            reward_dict = self.reward_calculator.calculate_reward(
                prev_state, curr_state, elapsed
            )
            reward = reward_dict['total']
            self.total_reward += reward
            # Read party info directly from memory (GameState doesn't include it)
            from emulator.pokemon_memory import MEMORY_MAP
            party_count = self.emulator.read_memory(MEMORY_MAP["PARTY_COUNT"])
            levels = [
                self.emulator.read_memory(MEMORY_MAP[f"PARTY_LEVEL_{i}"])
                for i in range(1, min(party_count + 1, 7))
            ] if party_count > 0 else []
            
            self.session_stats.record_step(
                step=step,
                x=curr_state.x,
                y=curr_state.y,
                map_id=curr_state.map_id,
                location=curr_state.location,
                action=action,
                party_count=party_count,
                levels=levels,
                party_types=[],  # Species IDs not critical for stats
                hp_fraction=1.0,  # HP tracking not critical for basic stats
                badges=curr_state.badges,
                event_reward=reward_stats.get('event_flags', 0),
                total_reward=self.total_reward,
                unique_coords=len(self.visited_tiles),
                unique_frames=reward_stats.get('unique_frames', 0),
                deaths=reward_stats.get('deaths', 0),
            )
            
            # Track recent actions (keep last 100)
            self.recent_actions.append({
                'step': step,
                'action': action,
                'reward': round(reward, 2),
                'location': curr_state.location
            })
            if len(self.recent_actions) > 100:
                self.recent_actions.pop(0)
            
            # Update Q-Learning (if we have previous experience)
            if prev_action is not None:
                done = (step == self.settings.max_steps - 1)
                update_q_learning(prev_state, prev_action, reward, curr_state, done)
            
            # Check for badge progress
            if curr_state.badges > prev_badges:
                badge_num = curr_state.badges
                if badge_num <= len(badge_names):
                    milestone_name = badge_names[badge_num - 1]
                    self.logger.log_milestone(run_id, milestone_name, curr_state)
                    print(f"\n🏅 BADGE EARNED: {milestone_name}")
                    print(f"   Total badges: {badge_num}/8")
                    print(f"   Steps taken: {step}")
                    print(f"   Total reward: {self.total_reward:+.1f}\n")
                prev_badges = curr_state.badges
            
            # Logging
            decision = RunDecision(
                step=step,
                action=action,
                reason=reason,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )
            self.logger.log_decision(run_id, decision, curr_state)
            self._write_state(curr_state)
            
            # Progress output
            if step % 20 == 0:
                stats = get_agent_stats()
                print(f"Step {step:3d}: {curr_state.location:20s} "
                      f"Badges: {curr_state.badges}  "
                      f"Reward: {self.total_reward:+7.1f}  "
                      f"Tiles: {len(self.visited_tiles)}  "
                      f"Q-States: {stats['states_explored']}")
            
            # Update for next iteration
            prev_state = curr_state
            prev_action = action
            
            # Slower for viewing in WebUI
            time.sleep(0.05)
        
        # Save Q-table
        save_q_table()
        
        # Save session statistics
        self.session_stats.save_to_csv()
        
        # Final summary
        stats = get_agent_stats()
        print(f"\n? Bot completed {self.settings.max_steps} steps")
        print(f"   Total reward: {total_reward:+.1f}")
        print(f"   Final badges: {curr_state.badges}")
        print(f"   States explored: {stats['states_explored']}")
        print(f"   Q-table size: {stats['q_table_size']}")
        print(f"   Learning updates: {stats['total_updates']}\n")
        
        self.logger.finish_run(run_id)

    def _write_state(self, state: GameState) -> None:
        # Get Q-Learning stats
        stats = get_agent_stats()
        
        # Track visited tile
        tile_key = f"{state.map_id}_{state.x}_{state.y}"
        self.visited_tiles.add(tile_key)
        
        # Get party and money
        try:
            party = self.emulator.get_party_pokemon()
        except:
            party = []
        
        try:
            money = self.emulator.get_money()
        except:
            money = 0
        
        payload = {
            "edition": state.edition,
            "location": state.location,
            "map_id": state.map_id,
            "x": state.x,
            "y": state.y,
            "badges": state.badges,
            "play_time_seconds": state.play_time_seconds,
            # Party & Resources
            "party": party,
            "money": money,
            # Training Metrics
            "current_step": self.current_step,
            "total_reward": round(self.total_reward, 2),
            # Q-Learning Stats
            "states_explored": stats['states_explored'],
            "q_table_size": stats['q_table_size'],
            "total_updates": stats['total_updates'],
            "epsilon": stats.get('epsilon', 0.1),
            "tiles_visited": len(self.visited_tiles),
            # Recent Actions (last 30)
            "recent_actions": self.recent_actions[-30:]
        }
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.data_path.write_text(json.dumps(payload, indent=2))


