#!/usr/bin/env python3
"""Comprehensive test suite for PokéRushAI components."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from emulator.pyboy_emulator import PyBoyEmulator, EmulatorSettings
from core.config import build_config
from core.models import GameState, RunDecision
from bot.policy import select_action
from run_logging.run_logger import RunLogger
from web_ui.app import app


def test_emulator():
    """Test PyBoyEmulator component."""
    print("Testing PyBoyEmulator...")
    
    # Test instantiation
    rom_path = Path('roms/pokemon_red.gb')
    emulator = PyBoyEmulator(rom_path)
    assert emulator.rom_path == rom_path
    print("  ✓ Instantiation successful")
    
    # Test settings
    settings = EmulatorSettings(frame_skip=2, emulation_speed=2.0)
    emulator_with_settings = PyBoyEmulator(rom_path, settings)
    assert emulator_with_settings.settings.frame_skip == 2
    assert emulator_with_settings.settings.emulation_speed == 2.0
    print("  ✓ Custom settings work")
    
    # Test error handling for missing ROM
    try:
        emulator.load()
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError as e:
        assert "ROM not found" in str(e)
        print("  ✓ FileNotFoundError raised for missing ROM")
    
    # Test error handling for unloaded emulator
    try:
        emulator.get_state()
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "not loaded" in str(e)
        print("  ✓ RuntimeError raised for unloaded emulator")
    
    try:
        emulator.step("UP")
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "not loaded" in str(e)
        print("  ✓ RuntimeError raised for step() on unloaded emulator")
    
    print("  ✓ All emulator tests passed\n")
    return True


def test_config():
    """Test configuration system."""
    print("Testing Config System...")
    
    base_dir = Path('.')
    config = build_config(base_dir)
    
    # Test editions
    assert 'red' in config.editions
    assert 'blue' in config.editions
    assert 'yellow' in config.editions
    print(f"  ✓ All 3 editions loaded: {list(config.editions.keys())}")
    
    # Test paths
    assert config.data_dir.name == 'data'
    assert config.log_dir.name == 'logs'
    print(f"  ✓ Paths configured correctly")
    
    # Test edition config
    red_config = config.editions['red']
    assert red_config.rom_path.name == 'pokemon_red.gb'
    print(f"  ✓ Edition config accessible")
    
    print("  ✓ All config tests passed\n")
    return True


def test_models():
    """Test data models."""
    print("Testing Data Models...")
    
    # Test GameState
    state = GameState(
        edition='red',
        location='Pallet Town',
        x=5,
        y=9,
        badges=0,
        play_time_seconds=0.0
    )
    assert state.edition == 'red'
    assert state.location == 'Pallet Town'
    assert state.x == 5
    assert state.y == 9
    assert state.badges == 0
    assert state.play_time_seconds == 0.0
    print(f"  ✓ GameState created: {state.location} at ({state.x}, {state.y})")
    
    # Test RunDecision
    decision = RunDecision(
        step=1,
        action='UP',
        reason='exploration',
        timestamp='2026-02-08T16:00:00Z'
    )
    assert decision.step == 1
    assert decision.action == 'UP'
    assert decision.reason == 'exploration'
    print(f"  ✓ RunDecision created: step={decision.step}, action={decision.action}")
    
    print("  ✓ All model tests passed\n")
    return True


def test_policy():
    """Test policy/action selection."""
    print("Testing Policy...")
    
    state = GameState(
        edition='red',
        location='Pallet Town',
        x=5,
        y=9,
        badges=0,
        play_time_seconds=0.0
    )
    actions = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'B']
    
    # Test multiple selections
    selected_actions = [select_action(state, actions) for _ in range(10)]
    assert all(action in actions for action in selected_actions)
    print(f"  ✓ Policy selected valid actions: {set(selected_actions)}")
    
    # Test with different action sets
    minimal_actions = ['A', 'B']
    action = select_action(state, minimal_actions)
    assert action in minimal_actions
    print(f"  ✓ Policy works with minimal action set")
    
    print("  ✓ All policy tests passed\n")
    return True


def test_run_logger():
    """Test run logging functionality."""
    print("Testing RunLogger...")
    
    log_dir = Path('/tmp/test_logs_comprehensive')
    logger = RunLogger(log_dir, 'red')
    
    # Test start_run
    run_id = logger.start_run(['Start', 'First Badge', 'Elite Four'])
    assert isinstance(run_id, int)
    assert run_id > 0
    print(f"  ✓ start_run created run_id: {run_id}")
    
    # Test log_decision
    state = GameState(
        edition='red',
        location='Pallet Town',
        x=5,
        y=9,
        badges=0,
        play_time_seconds=0.0
    )
    decision = RunDecision(
        step=1,
        action='UP',
        reason='exploration',
        timestamp='2026-02-08T16:00:00Z'
    )
    logger.log_decision(run_id, decision, state)
    print(f"  ✓ log_decision recorded decision")
    
    # Test finish_run
    logger.finish_run(run_id)
    print(f"  ✓ finish_run completed")
    
    print("  ✓ All run logger tests passed\n")
    return True


def test_web_app():
    """Test Flask web application."""
    print("Testing Flask Web App...")
    
    # Test app exists
    assert app is not None
    print(f"  ✓ Flask app loaded: {app.name}")
    
    # Test routes
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    assert '/' in routes or any('index' in r for r in routes)
    print(f"  ✓ Routes registered: {len(routes)} routes")
    
    # Test app config
    assert app.config is not None
    print(f"  ✓ App configuration accessible")
    
    print("  ✓ All web app tests passed\n")
    return True


def test_cli():
    """Test command-line interface."""
    print("Testing CLI...")
    
    from main import parse_args
    
    # Test bot command
    sys.argv = ['main.py', 'bot', '--edition', 'red', '--max-steps', '100']
    args = parse_args()
    assert args.command == 'bot'
    assert args.edition == 'red'
    assert args.max_steps == 100
    print(f"  ✓ Bot command parsed: edition={args.edition}, max_steps={args.max_steps}")
    
    # Test web command
    sys.argv = ['main.py', 'web', '--host', '127.0.0.1', '--port', '8000']
    args = parse_args()
    assert args.command == 'web'
    assert args.host == '127.0.0.1'
    assert args.port == 8000
    print(f"  ✓ Web command parsed: host={args.host}, port={args.port}")
    
    # Test default values
    sys.argv = ['main.py', 'bot']
    args = parse_args()
    assert args.edition == 'red'
    assert args.max_steps == 100
    print(f"  ✓ Default values work correctly")
    
    print("  ✓ All CLI tests passed\n")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("PokéRushAI Comprehensive Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Emulator", test_emulator),
        ("Config", test_config),
        ("Models", test_models),
        ("Policy", test_policy),
        ("RunLogger", test_run_logger),
        ("Web App", test_web_app),
        ("CLI", test_cli),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ✗ {name} test FAILED: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED - System is ready!")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
