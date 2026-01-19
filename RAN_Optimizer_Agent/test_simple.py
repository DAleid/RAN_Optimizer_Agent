"""
Simple test - avoids encoding issues on Windows
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("="*60)
print("SIMPLE TEST - RAN Optimizer")
print("="*60)

# Test 1: Libraries
print("\n[1/4] Testing libraries...")
try:
    import numpy as np
    import torch
    print("  OK - NumPy and PyTorch available")
except ImportError as e:
    print(f"  FAIL - {e}")
    print("  Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 2: Environment
print("\n[2/4] Testing RAN Environment...")
try:
    from ran_environment import RANEnvironment
    env = RANEnvironment(num_cells=5)
    state = env.reset()
    action = env.action_space.sample()
    next_state, reward, done, info = env.step(action)
    print(f"  OK - Environment works (5 cells, reward={reward:.2f})")
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

# Test 3: Agent
print("\n[3/4] Testing Agent...")
try:
    from agent import RANOptimizationAgent
    agent = RANOptimizationAgent(
        state_size=env.observation_space.shape[0],
        action_size=env.action_space.n
    )
    action = agent.act(state, training=True)
    agent.remember(state, action, reward, next_state, done)
    print(f"  OK - Agent works (device={agent.device})")
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

# Test 4: Mini training
print("\n[4/4] Mini training (3 episodes)...")
try:
    for ep in range(3):
        state = env.reset()
        total_reward = 0
        for step in range(10):
            action = agent.act(state, training=True)
            next_state, reward, done, info = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            if len(agent.memory) > 32:
                agent.replay()
            total_reward += reward
            state = next_state
            if done:
                break
        print(f"  Episode {ep+1}: reward={total_reward:.2f}")
    print("  OK - Training works!")
except Exception as e:
    print(f"  FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "="*60)
print("SUCCESS - All tests passed!")
print("="*60)
print("\nNext steps:")
print("1. Train full model: cd src && python train_agent.py")
print("2. Run dashboard: cd src && python dashboard.py")
print("="*60)
