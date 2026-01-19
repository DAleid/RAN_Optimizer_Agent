"""
Main training program for the intelligent agent
Supports training with real data from 6G_HetNet_Transmission_Management.csv
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import argparse

# Add current path
sys.path.append(os.path.dirname(__file__))

from ran_environment import RANEnvironment
from agent import RANOptimizationAgent
from ab_testing import ABTestingSystem


def plot_training_results(stats, save_path='../results', data_mode='real_data'):
    """Plot training results"""

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    mode_str = "Real Data" if data_mode == 'real_data' else "Simulated Data"
    fig.suptitle(f'Training Results - Intelligent Agent ({mode_str})', fontsize=16, fontweight='bold')

    # 1. Rewards
    axes[0, 0].plot(stats['episode_rewards'], alpha=0.6, label='Reward')
    # Moving average
    window = 10
    if len(stats['episode_rewards']) >= window:
        moving_avg = np.convolve(
            stats['episode_rewards'],
            np.ones(window)/window,
            mode='valid'
        )
        axes[0, 0].plot(range(window-1, len(stats['episode_rewards'])),
                       moving_avg, 'r-', linewidth=2, label=f'Moving Avg ({window})')

    axes[0, 0].set_xlabel('Episode')
    axes[0, 0].set_ylabel('Reward')
    axes[0, 0].set_title('Reward Over Episodes')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 2. Loss
    axes[0, 1].plot(stats['episode_losses'], 'orange')
    axes[0, 1].set_xlabel('Episode')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].set_title('Training Loss')
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Epsilon
    axes[1, 0].plot(stats['epsilon_history'], 'green')
    axes[1, 0].set_xlabel('Episode')
    axes[1, 0].set_ylabel('Epsilon (Exploration Rate)')
    axes[1, 0].set_title('Exploration Decay Over Time')
    axes[1, 0].grid(True, alpha=0.3)

    # 4. Improvement summary
    episodes = len(stats['episode_rewards'])
    first_10 = np.mean(stats['episode_rewards'][:10]) if episodes >= 10 else 0
    last_10 = np.mean(stats['episode_rewards'][-10:]) if episodes >= 10 else 0
    improvement = ((last_10 - first_10) / abs(first_10) * 100) if first_10 != 0 else 0

    axes[1, 1].bar(['First 10 Episodes', 'Last 10 Episodes'], [first_10, last_10],
                   color=['lightcoral', 'lightgreen'])
    axes[1, 1].set_ylabel('Average Reward')
    axes[1, 1].set_title(f'Improvement: {improvement:+.1f}%')
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    # Add improvement text
    axes[1, 1].text(0.5, 0.5, f'{improvement:+.1f}%',
                   transform=axes[1, 1].transAxes,
                   fontsize=40, weight='bold', alpha=0.3,
                   ha='center', va='center')

    plt.tight_layout()

    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{save_path}/training_results_{data_mode}_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Graphs saved to: {filename}")

    plt.close()


def compare_before_after(env, agent, num_episodes=5):
    """Compare network performance before and after optimization"""

    print("\n" + "="*60)
    print("Before vs After Comparison")
    print("="*60)

    # Before: Random performance
    print("\n1. Before optimization (random actions):")
    before_stats = []
    for _ in range(num_episodes):
        state = env.reset()
        done = False
        while not done:
            action = env.action_space.sample()  # Random
            state, reward, done, info = env.step(action)
        before_stats.append(env.get_network_stats())

    avg_before = {
        key: np.mean([s[key] for s in before_stats])
        for key in before_stats[0].keys()
        if key != 'cell_types'  # Skip non-numeric fields
    }

    for key, value in avg_before.items():
        print(f"  {key}: {value:.2f}")

    # After: With intelligent agent
    print("\n2. After optimization (with intelligent agent):")
    after_stats = []
    for _ in range(num_episodes):
        state = env.reset()
        done = False
        while not done:
            action = agent.act(state, training=False)
            state, reward, done, info = env.step(action)
        after_stats.append(env.get_network_stats())

    avg_after = {
        key: np.mean([s[key] for s in after_stats])
        for key in after_stats[0].keys()
        if key != 'cell_types'  # Skip non-numeric fields
    }

    for key, value in avg_after.items():
        print(f"  {key}: {value:.2f}")

    # Calculate improvement
    print("\n3. Improvement (%):")
    for key in avg_before.keys():
        if 'drop_rate' in key or 'power' in key.lower() or 'interference' in key.lower():
            # Lower is better
            improvement = (avg_before[key] - avg_after[key]) / avg_before[key] * 100 if avg_before[key] != 0 else 0
        else:
            # Higher is better
            improvement = (avg_after[key] - avg_before[key]) / avg_before[key] * 100 if avg_before[key] != 0 else 0

        symbol = "UP" if improvement > 0 else "DOWN"
        print(f"  [{symbol}] {key}: {improvement:+.2f}%")

    print("="*60)

    return avg_before, avg_after


def main(use_real_data=True):
    """Main program"""

    print("="*60)
    print("  Training Intelligent Agent for RAN Optimization  ")
    print("="*60)

    # Settings
    NUM_CELLS = 10
    NUM_EPISODES = 100
    UPDATE_TARGET_EVERY = 10

    data_mode = 'real_data' if use_real_data else 'simulated'

    # 1. Create environment
    print("\n1. Creating simulation environment...")
    env = RANEnvironment(num_cells=NUM_CELLS, use_real_data=use_real_data)
    print(f"OK Created network with {NUM_CELLS} cells")

    # Display data info
    data_info = env.get_data_info()
    print(f"OK Data mode: {data_info['mode']}")
    if data_info['statistics']:
        stats = data_info['statistics']
        print(f"   Total records in dataset: {stats['total_records']}")
        print(f"   Unique cells: {stats['num_cells']}")
        print(f"   Cell types: {stats['cell_types']}")
        print(f"   Avg throughput: {stats['avg_throughput']:.2f} Mbps")
        print(f"   Action distribution: {stats['action_distribution']}")

    # 2. Create agent
    print("\n2. Creating intelligent agent...")
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    agent = RANOptimizationAgent(state_size, action_size)
    print(f"OK Agent created")
    print(f"   State size: {state_size}")
    print(f"   Actions: {action_size}")

    # 3. Training
    print("\n3. Starting training...")
    print(f"   Episodes: {NUM_EPISODES}")
    print(f"   Data mode: {data_mode}")
    print()

    stats = agent.train(
        env,
        num_episodes=NUM_EPISODES,
        update_target_every=UPDATE_TARGET_EVERY
    )

    # 4. Save model
    print("\n4. Saving model...")
    model_dir = '../results'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = f'{model_dir}/ran_agent_{data_mode}_{timestamp}.pth'
    agent.save(model_path)

    # 5. Plot results
    print("\n5. Plotting results...")
    plot_training_results(stats, data_mode=data_mode)

    # 6. Evaluation
    print("\n6. Evaluating performance...")
    eval_results = agent.evaluate(env, num_episodes=10, render=False)

    # 7. Before vs after comparison
    print("\n7. Before vs after comparison...")
    before, after = compare_before_after(env, agent)

    # 8. A/B testing
    print("\n8. Running A/B test...")
    ab_system = ABTestingSystem()
    ab_result = ab_system.run_test(
        env, agent,
        num_steps=50,
        test_name="final_test"
    )

    # Save A/B results
    ab_results_path = f'{model_dir}/ab_test_results_{data_mode}_{timestamp}.json'
    ab_system.export_results(ab_results_path)

    # 9. Final summary
    print("\n" + "="*60)
    print("  FINAL RESULTS SUMMARY  ")
    print("="*60)
    print(f"OK Training completed successfully!")
    print(f"OK Data mode: {data_mode}")
    print(f"OK Completed episodes: {NUM_EPISODES}")
    print(f"OK Final average reward: {np.mean(stats['episode_rewards'][-10:]):.2f}")
    print(f"OK Average throughput: {eval_results['avg_throughput']:.1f} Mbps")
    print(f"OK Average drop rate: {eval_results['avg_drop_rate']*100:.2f}%")
    print(f"OK Average satisfaction: {eval_results['avg_satisfaction']:.1f}/100")
    print()
    print(f"Saved model: {model_path}")
    print(f"A/B results: {ab_results_path}")
    print()
    print(ab_result.recommendation)
    print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train RAN Optimization Agent')
    parser.add_argument('--simulated', action='store_true',
                        help='Use simulated data instead of real data')
    args = parser.parse_args()

    # By default, use real data. Use --simulated flag for simulated data
    use_real_data = not args.simulated

    main(use_real_data=use_real_data)
