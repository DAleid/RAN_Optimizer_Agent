"""
Quick test to verify everything works correctly
"""

import sys
import os

print("="*60)
print("  Quick Test - RAN Optimizer Project  ")
print("="*60)

# 1. Test imports
print("\n1. Testing library imports...")
try:
    import numpy as np
    try:
        import gymnasium as gym
    except ImportError:
        import gym
    print("   OK NumPy:", np.__version__)
    print("   OK Gym:", gym.__version__)
except ImportError as e:
    print(f"   ERROR: {e}")
    print("   Solution: pip install -r requirements.txt")
    sys.exit(1)

# 2. Test RAN environment
print("\n2. Testing RAN Environment...")
try:
    from ran_environment import RANEnvironment

    env = RANEnvironment(num_cells=3)
    state = env.reset()
    print(f"   OK Created environment with {env.num_cells} cells")
    print(f"   OK State size: {state.shape}")
    print(f"   OK Action space: {env.action_space.n}")

    # Execute one step
    action = env.action_space.sample()
    next_state, reward, done, info = env.step(action)
    print(f"   OK Action executed successfully")
    print(f"   OK Reward: {reward:.2f}")

except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

# 3. Test agent
print("\n3. Testing Intelligent Agent...")
try:
    from agent import RANOptimizationAgent

    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    agent = RANOptimizationAgent(state_size, action_size)

    print(f"   OK Agent created")
    print(f"   OK Device: {agent.device}")

    # Test action selection
    state = env.reset()
    action = agent.act(state, training=True)
    print(f"   OK Action selected: {action}")

    # Test memory
    next_state, reward, done, info = env.step(action)
    agent.remember(state, action, reward, next_state, done)
    print(f"   OK Memory size: {len(agent.memory)}")

except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

# 4. Test A/B Testing system
print("\n4. Testing A/B Testing System...")
try:
    from ab_testing import ABTestingSystem

    ab_system = ABTestingSystem()
    print(f"   OK A/B system created")

    # Split into groups
    group_a, group_b = ab_system.create_test_groups(env.cells, test_ratio=0.5)
    print(f"   OK Group A: {len(group_a)} cells")
    print(f"   OK Group B: {len(group_b)} cells")

except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

# 5. Quick training
print("\n5. Quick training (5 episodes)...")
try:
    mini_env = RANEnvironment(num_cells=3)
    state_size = mini_env.observation_space.shape[0]
    action_size = mini_env.action_space.n
    mini_agent = RANOptimizationAgent(state_size, action_size)

    # Train for 5 episodes only
    for episode in range(5):
        state = mini_env.reset()
        episode_reward = 0
        done = False
        step = 0

        while not done and step < 20:  # Max 20 steps
            action = mini_agent.act(state, training=True)
            next_state, reward, done, info = mini_env.step(action)
            mini_agent.remember(state, action, reward, next_state, done)

            # Train if we have enough memory
            if len(mini_agent.memory) > 32:
                mini_agent.replay()

            episode_reward += reward
            state = next_state
            step += 1

        print(f"   Episode {episode + 1}: reward = {episode_reward:.2f}")

    print("   OK Quick training succeeded!")

except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. Final result
print("\n" + "="*60)
print("  ALL TESTS PASSED!  ")
print("="*60)
print("\nNext steps:")
print("1. Run full training:")
print("   python train_agent.py")
print()
print("2. Run dashboard:")
print("   python dashboard.py")
print()
print("3. Read the guide:")
print("   Open GUIDE.md")
print("="*60)
