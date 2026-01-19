"""
Test script for the RAN Optimization AI Agents
Tests the agent system without requiring API calls (mock mode)
"""

import os
import sys

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))


def test_data_loader():
    """Test the data loader"""
    print("\n" + "=" * 60)
    print("TEST 1: Data Loader")
    print("=" * 60)

    try:
        from src.data_loader import NetworkDataLoader

        loader = NetworkDataLoader()
        stats = loader.get_statistics()

        print("[OK] Data loaded successfully!")
        print(f"   Total records: {stats['total_records']}")
        print(f"   Unique cells: {stats['num_cells']}")
        print(f"   Cell types: {stats['cell_types']}")

        return True
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


def test_environment():
    """Test the RAN environment"""
    print("\n" + "=" * 60)
    print("TEST 2: RAN Environment")
    print("=" * 60)

    try:
        from src.ran_environment import RANEnvironment

        env = RANEnvironment(num_cells=5, use_real_data=True)
        state = env.reset()

        print("[OK] Environment created!")
        print(f"   Cells: {len(env.cells)}")
        print(f"   State shape: {state.shape}")
        print(f"   Data mode: {env.get_data_info()['mode']}")

        # Test a step
        action = env.action_space.sample()
        next_state, reward, done, info = env.step(action)
        print(f"   Step test: reward={reward:.2f}")

        return True
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


def test_task_formatting():
    """Test task formatting functions"""
    print("\n" + "=" * 60)
    print("TEST 3: Task Formatting")
    print("=" * 60)

    try:
        from agents.ran_tasks import format_network_state, parse_final_actions

        # Test network state formatting
        sample_state = {
            'cells': [
                {
                    'id': 0, 'cell_type': 'Macro', 'num_users': 150,
                    'throughput': 450.0, 'drop_rate': 0.03, 'tx_power': 40.0,
                    'antenna_tilt': 5.0, 'interference': 0.15, 'power_consumption': 20.0
                }
            ],
            'stats': {'avg_throughput': 450.0, 'avg_drop_rate': 0.03}
        }

        formatted = format_network_state(sample_state)
        print("[OK] Network state formatted!")
        print(f"   Output length: {len(formatted)} chars")

        # Test action parsing
        sample_output = """
        Some analysis text...

        FINAL_ACTIONS:
        - cell_id: 0, power_change: -3, tilt_change: 2, handover_change: 0, status: APPROVED
        - cell_id: 1, power_change: 3, tilt_change: 0, handover_change: -5, status: APPROVED
        """

        actions = parse_final_actions(sample_output)
        print("[OK] Actions parsed!")
        print(f"   Actions found: {len(actions)}")

        return True
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


def test_agent_creation():
    """Test agent creation (requires API key)"""
    print("\n" + "=" * 60)
    print("TEST 4: Agent Creation")
    print("=" * 60)

    if not os.getenv("GROQ_API_KEY"):
        print("[SKIP] Skipped: GROQ_API_KEY not set")
        print("   Set your API key to test agent creation:")
        print("   export GROQ_API_KEY='gsk_your_key_here'")
        return None

    try:
        from agents.ran_agents import create_agents

        agents = create_agents()

        print("[OK] Agents created!")
        for name, agent in agents.items():
            print(f"   - {name}: {agent.role}")

        return True
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


def test_crew_initialization():
    """Test crew initialization (requires API key)"""
    print("\n" + "=" * 60)
    print("TEST 5: Crew Initialization")
    print("=" * 60)

    if not os.getenv("GROQ_API_KEY"):
        print("[SKIP] Skipped: GROQ_API_KEY not set")
        return None

    try:
        from agents.ran_crew import RANOptimizationCrew

        crew = RANOptimizationCrew()

        if crew.is_ready():
            print("[OK] Crew initialized and ready!")
            print(f"   Agents: {len(crew.agents)}")
            return True
        else:
            print("[FAIL] Crew not ready")
            return False
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  RAN OPTIMIZATION AGENTS - TEST SUITE")
    print("=" * 60)

    results = {}

    results['data_loader'] = test_data_loader()
    results['environment'] = test_environment()
    results['task_formatting'] = test_task_formatting()
    results['agent_creation'] = test_agent_creation()
    results['crew_init'] = test_crew_initialization()

    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for test_name, result in results.items():
        status = "[PASS]" if result is True else ("[FAIL]" if result is False else "[SKIP]")
        print(f"   {test_name}: {status}")

    print(f"\n   Total: {passed} passed, {failed} failed, {skipped} skipped")

    if failed == 0:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[WARNING] Some tests failed. Check the output above.")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
