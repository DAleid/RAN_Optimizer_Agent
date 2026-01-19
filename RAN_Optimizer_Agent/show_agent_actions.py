"""
Demonstrate what actions the agent takes
"""
import sys
sys.path.insert(0, 'src')

from ran_environment import RANEnvironment
from agent import RANOptimizationAgent
import numpy as np

print("="*70)
print("  DEMONSTRATING AGENT ACTIONS")
print("="*70)

# Create environment and agent
env = RANEnvironment(num_cells=3)  # Small network for clarity
state_size = env.observation_space.shape[0]
action_size = env.action_space.n

# Create untrained agent (random actions)
random_agent = RANOptimizationAgent(state_size, action_size)
random_agent.epsilon = 1.0  # Force random exploration

# Try to load trained agent (needs same size as training)
try:
    env_trained = RANEnvironment(num_cells=10)  # Same as training
    trained_agent = RANOptimizationAgent(env_trained.observation_space.shape[0], action_size)
    trained_agent.load('results/ran_agent_20260112_103014.pth')
    has_trained = True
    print("\nLoaded trained agent for comparison")
except:
    has_trained = False
    print("\nNo trained agent found - showing random actions only")

print("\n" + "="*70)
print("EXAMPLE 1: WHAT ACTIONS LOOK LIKE")
print("="*70)

# Decode all possible actions
print("\nAll 27 possible actions the agent can take:")
print("-"*70)
for action_num in range(27):
    changes = env._decode_action(action_num)
    print(f"Action {action_num:2d}: Power {changes['power']:+2d}dB, "
          f"Tilt {changes['tilt']:+2d}°, Handover {changes['handover']:+2d}")

print("\n" + "="*70)
print("EXAMPLE 2: RANDOM AGENT (UNTRAINED)")
print("="*70)

state = env.reset()
print("\nInitial network state:")
for i, cell in enumerate(env.cells):
    print(f"  Tower {i}: Speed={cell['throughput']:.1f}Mbps, "
          f"Drops={cell['drop_rate']*100:.1f}%, Power={cell['tx_power']:.1f}dBm")

print("\nRandom agent taking 5 actions:")
print("-"*70)
for step in range(5):
    action = random_agent.act(state, training=True)
    changes = env._decode_action(action)

    print(f"\nStep {step+1}:")
    print(f"  Chose Action {action}: {changes}")

    next_state, reward, done, info = env.step(action)

    print(f"  Result: Reward = {reward:+.2f}")
    print(f"  New speed: {env.cells[env.current_cell_idx-1]['throughput']:.1f} Mbps")

    state = next_state

if has_trained:
    print("\n" + "="*70)
    print("EXAMPLE 3: TRAINED AGENT (SMART DECISIONS)")
    print("="*70)

    state = env_trained.reset()
    print("\nInitial network state (10 towers):")
    for i, cell in enumerate(env_trained.cells[:3]):  # Show first 3
        print(f"  Tower {i}: Speed={cell['throughput']:.1f}Mbps, "
              f"Drops={cell['drop_rate']*100:.1f}%, Power={cell['tx_power']:.1f}dBm")
    print("  ... (7 more towers)")

    print("\nTrained agent taking 5 smart actions:")
    print("-"*70)
    for step in range(5):
        action = trained_agent.act(state, training=False)  # Use learned policy
        changes = env_trained._decode_action(action)

        print(f"\nStep {step+1}:")
        print(f"  Chose Action {action}: {changes}")

        next_state, reward, done, info = env_trained.step(action)

        print(f"  Result: Reward = {reward:+.2f}")
        print(f"  New speed: {env_trained.cells[env_trained.current_cell_idx-1]['throughput']:.1f} Mbps")

        state = next_state

    print("\n" + "="*70)
    print("COMPARISON:")
    print("="*70)
    print("Random Agent:  Takes any action (exploring)")
    print("Trained Agent: Takes smart actions (learned what works)")
    print("="*70)

print("\n" + "="*70)
print("WHAT YOU LEARNED:")
print("="*70)
print("✅ The agent takes 27 different types of actions")
print("✅ Each action adjusts power, tilt, and handover settings")
print("✅ Untrained = random actions")
print("✅ Trained = smart actions based on learning")
print("✅ The agent executes actions 100s of times during training")
print("="*70)
