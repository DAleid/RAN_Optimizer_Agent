"""
RAN Network Environment Simulator
Supports both real data from CSV and simulated data modes
"""

import numpy as np
import gym
from gym import spaces
from typing import Optional, Dict, List
import os


class RANEnvironment(gym.Env):
    """
    RAN Network Simulation Environment

    Supports two modes:
    1. Real data mode: Uses data from 6G_HetNet_Transmission_Management.csv
    2. Simulated mode: Generates synthetic data (legacy behavior)

    State:
    - Number of users
    - Throughput (download speed)
    - Call drop rate
    - Power consumption
    - Interference with neighboring cells

    Actions:
    - Adjust transmission power: [-3, 0, +3] dB
    - Adjust antenna tilt: [-2, 0, +2] degrees
    - Adjust handover threshold: [-5, 0, +5]
    """

    def __init__(self, num_cells: int = 10, use_real_data: bool = True,
                 data_path: Optional[str] = None, random_seed: Optional[int] = None):
        """
        Initialize the RAN environment.

        Args:
            num_cells: Number of cells in the network
            use_real_data: If True, use real data from CSV; if False, use simulated data
            data_path: Path to the CSV file (only used if use_real_data=True)
            random_seed: Random seed for reproducibility
        """
        super(RANEnvironment, self).__init__()

        self.num_cells = num_cells
        self.use_real_data = use_real_data
        self.data_path = data_path
        self.random_seed = random_seed
        self.data_loader = None
        self.episode_count = 0

        # Initialize data loader if using real data
        if self.use_real_data:
            self._init_data_loader()

        # Define action space (3 parameters x 3 options each = 27 actions)
        self.action_space = spaces.Discrete(27)

        # Define state space (5 metrics per cell)
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(num_cells * 5,), dtype=np.float32
        )

        # Default settings for each cell
        self.reset()

    def _init_data_loader(self):
        """Initialize the data loader for real data."""
        try:
            from data_loader import NetworkDataLoader
            self.data_loader = NetworkDataLoader(self.data_path)
            print(f"[OK] Loaded real data: {self.data_loader.get_num_cells()} unique cells")
        except ImportError:
            print("[WARNING] data_loader module not found, falling back to simulated data")
            self.use_real_data = False
        except FileNotFoundError as e:
            print(f"[WARNING] Data file not found: {e}, falling back to simulated data")
            self.use_real_data = False

    def reset(self):
        """Reset environment to initial state"""
        self.cells = []
        self.episode_count += 1

        if self.use_real_data and self.data_loader is not None:
            self._reset_from_real_data()
        else:
            self._reset_simulated()

        self.current_cell_idx = 0
        self.episode_step = 0

        return self._get_state()

    def _reset_from_real_data(self):
        """Reset using real data from CSV."""
        # Sample cells from real data, using episode count for different seeds
        seed = self.random_seed if self.random_seed is not None else self.episode_count
        real_cells = self.data_loader.sample_network_state(
            num_cells=self.num_cells,
            seed=seed
        )

        for i, real_cell in enumerate(real_cells):
            cell = {
                'id': i,
                'cell_type': real_cell.get('cell_type', 'Macro'),
                'tx_power': real_cell['tx_power'],
                'antenna_tilt': real_cell.get('antenna_tilt', 3.0),
                'handover_threshold': real_cell.get('handover_threshold', 70.0),
                'num_users': real_cell['num_users'],
                'throughput': real_cell['throughput'],
                'drop_rate': real_cell['drop_rate'],
                'power_consumption': real_cell['power_consumption'],
                'interference': real_cell['interference'],
                # Additional metrics from real data
                'latency': real_cell.get('latency', 15.0),
                'snr': real_cell.get('snr', 20.0),
                'qos_satisfaction': real_cell.get('qos_satisfaction', 80.0),
                'frequency': real_cell.get('frequency', 3.5),
                'bandwidth': real_cell.get('bandwidth', 100),
                'optimized_action': real_cell.get('optimized_action', 'Maintain_Power'),
                'optimized_power': real_cell.get('optimized_power', real_cell['tx_power'])
            }
            self.cells.append(cell)

    def _reset_simulated(self):
        """Reset using simulated data (legacy behavior)."""
        for i in range(self.num_cells):
            cell = {
                'id': i,
                'cell_type': 'Macro',
                'tx_power': 40.0,           # Transmission power (dBm)
                'antenna_tilt': 3.0,        # Antenna tilt angle (degrees)
                'handover_threshold': 70.0, # Handover threshold (%)
                'num_users': np.random.randint(50, 500),
                'throughput': np.random.uniform(20, 100),  # Mbps
                'drop_rate': np.random.uniform(0, 0.1),    # 0-10%
                'power_consumption': 0.0,
                'interference': np.random.uniform(0, 0.3),
                'latency': np.random.uniform(10, 50),
                'snr': np.random.uniform(10, 30),
                'qos_satisfaction': np.random.uniform(70, 100),
                'frequency': 3.5,
                'bandwidth': 100,
                'optimized_action': 'Maintain_Power',
                'optimized_power': 40.0
            }
            # Calculate power consumption based on transmission power
            cell['power_consumption'] = cell['tx_power'] * 0.5

            self.cells.append(cell)

    def _get_state(self):
        """Get current network state"""
        state = []
        for cell in self.cells:
            # Normalize values between 0 and 1
            state.extend([
                min(cell['num_users'] / 500.0, 1.0),           # Number of users
                min(cell['throughput'] / 1000.0, 1.0),         # Throughput (scaled for higher values in real data)
                min(cell['drop_rate'] / 0.15, 1.0),            # Drop rate
                min(cell['power_consumption'] / 50.0, 1.0),    # Power
                min(cell['interference'], 1.0)                  # Interference (already normalized)
            ])
        return np.array(state, dtype=np.float32)

    def _decode_action(self, action):
        """Convert action number to parameter adjustments"""
        # 27 actions = 3x3x3 (power x tilt x handover)
        power_changes = [-3, 0, 3]
        tilt_changes = [-2, 0, 2]
        handover_changes = [-5, 0, 5]

        power_idx = action // 9
        tilt_idx = (action % 9) // 3
        handover_idx = action % 3

        return {
            'power': power_changes[power_idx],
            'tilt': tilt_changes[tilt_idx],
            'handover': handover_changes[handover_idx]
        }

    def step(self, action):
        """Execute action and return (new_state, reward, done, info)"""

        # Select a cell to optimize
        cell = self.cells[self.current_cell_idx]

        # Decode action
        changes = self._decode_action(action)

        # Apply changes
        old_metrics = self._calculate_cell_metrics(cell)

        cell['tx_power'] = np.clip(cell['tx_power'] + changes['power'], 10, 50)
        cell['antenna_tilt'] = np.clip(cell['antenna_tilt'] + changes['tilt'], 0, 10)
        cell['handover_threshold'] = np.clip(cell['handover_threshold'] + changes['handover'], 50, 90)

        # Simulate impact of changes
        self._simulate_changes(cell, changes)

        # Calculate new metrics
        new_metrics = self._calculate_cell_metrics(cell)

        # Calculate reward
        reward = self._calculate_reward(old_metrics, new_metrics, cell)

        # Move to next cell
        self.current_cell_idx = (self.current_cell_idx + 1) % self.num_cells
        self.episode_step += 1

        # Episode ends after 100 steps
        done = self.episode_step >= 100

        info = {
            'cell_id': cell['id'],
            'cell_type': cell.get('cell_type', 'Unknown'),
            'old_metrics': old_metrics,
            'new_metrics': new_metrics,
            'changes': changes,
            'optimized_action': cell.get('optimized_action', 'Unknown')
        }

        return self._get_state(), reward, done, info

    def _simulate_changes(self, cell, changes):
        """Simulate the impact of parameter changes on cell performance"""

        # Get cell type multiplier (different cell types respond differently)
        cell_type = cell.get('cell_type', 'Macro')
        type_multiplier = {
            'Macro': 1.0,
            'Micro': 0.8,
            'Pico': 0.6,
            'Femto': 0.4
        }.get(cell_type, 1.0)

        # Impact of transmission power
        if changes['power'] > 0:
            cell['throughput'] += np.random.uniform(2, 8) * type_multiplier
            cell['interference'] += 0.05 * type_multiplier
            cell['power_consumption'] = cell['tx_power'] * 0.5
        elif changes['power'] < 0:
            cell['throughput'] -= np.random.uniform(1, 4) * type_multiplier
            cell['interference'] -= 0.03 * type_multiplier
            cell['power_consumption'] = cell['tx_power'] * 0.5

        # Impact of antenna tilt
        if changes['tilt'] != 0:
            # Tilt affects coverage
            cell['throughput'] += np.random.uniform(-3, 5) * type_multiplier
            cell['interference'] += np.random.uniform(-0.02, 0.02)

        # Impact of handover threshold
        if changes['handover'] < 0:
            # Lower threshold = faster handover = fewer drops
            cell['drop_rate'] *= 0.9
            cell['num_users'] = int(cell['num_users'] * 0.95)  # Some users move to other cells
        elif changes['handover'] > 0:
            cell['drop_rate'] *= 1.05
            cell['num_users'] = int(cell['num_users'] * 1.05)

        # Add randomness to simulate reality
        cell['throughput'] += np.random.uniform(-2, 2)
        cell['drop_rate'] += np.random.uniform(-0.005, 0.005)

        # Keep values within valid ranges
        cell['throughput'] = np.clip(cell['throughput'], 10, 1000)
        cell['drop_rate'] = np.clip(cell['drop_rate'], 0, 0.15)
        cell['interference'] = np.clip(cell['interference'], 0, 1.0)
        cell['num_users'] = max(1, cell['num_users'])

    def _calculate_cell_metrics(self, cell):
        """Calculate cell performance metrics"""
        return {
            'throughput': cell['throughput'],
            'drop_rate': cell['drop_rate'],
            'power': cell['power_consumption'],
            'interference': cell['interference'],
            'user_satisfaction': self._calculate_satisfaction(cell)
        }

    def _calculate_satisfaction(self, cell):
        """Calculate user satisfaction score (0-100)"""
        # Use QoS satisfaction from real data if available
        if 'qos_satisfaction' in cell and cell['qos_satisfaction'] > 0:
            base_satisfaction = cell['qos_satisfaction']
        else:
            # User satisfaction depends on throughput and drop rate
            throughput_score = min(cell['throughput'] / 100.0, 1.0) * 50
            drop_score = (1 - min(cell['drop_rate'] / 0.1, 1.0)) * 30
            interference_score = (1 - min(cell['interference'] / 0.5, 1.0)) * 20
            base_satisfaction = throughput_score + drop_score + interference_score

        return base_satisfaction

    def _calculate_reward(self, old_metrics, new_metrics, cell):
        """
        Calculate reward based on improvement

        Goals:
        - Increase throughput
        - Reduce call drops
        - Reduce power consumption
        - Reduce interference
        - Increase user satisfaction
        """

        reward = 0.0

        # Reward for throughput improvement
        throughput_improvement = new_metrics['throughput'] - old_metrics['throughput']
        reward += throughput_improvement * 0.1  # Scaled for larger throughput values

        # Reward for reducing drop rate
        drop_improvement = old_metrics['drop_rate'] - new_metrics['drop_rate']
        reward += drop_improvement * 100  # High weight - very important

        # Reward for power savings
        power_saving = old_metrics['power'] - new_metrics['power']
        reward += power_saving * 0.2

        # Reward for reducing interference
        interference_reduction = old_metrics['interference'] - new_metrics['interference']
        reward += interference_reduction * 10

        # Reward for user satisfaction improvement (most important!)
        satisfaction_improvement = new_metrics['user_satisfaction'] - old_metrics['user_satisfaction']
        reward += satisfaction_improvement * 0.5

        # Bonus reward for matching recommended action from data
        if self.use_real_data and 'optimized_action' in cell:
            if self._action_matches_recommendation(cell):
                reward += 2.0  # Bonus for following data recommendation

        # Penalty if performance degrades significantly
        if new_metrics['drop_rate'] > 0.08:  # More than 8%
            reward -= 10

        if new_metrics['throughput'] < 30:  # Less than 30 Mbps
            reward -= 5

        return reward

    def _action_matches_recommendation(self, cell):
        """Check if current action matches the recommended action from data."""
        optimized_action = cell.get('optimized_action', 'Maintain_Power')
        current_power = cell['tx_power']
        optimized_power = cell.get('optimized_power', current_power)

        # Simple check based on power direction
        if optimized_action == 'Reduce_Power' and current_power > optimized_power:
            return True
        elif optimized_action == 'Increase_Power' and current_power < optimized_power:
            return True
        elif optimized_action == 'Maintain_Power' and abs(current_power - optimized_power) < 3:
            return True
        return False

    def render(self, mode='human'):
        """Display network state"""
        print("\n" + "="*60)
        print(f"Step: {self.episode_step} | Mode: {'Real Data' if self.use_real_data else 'Simulated'}")
        print("="*60)

        for cell in self.cells[:3]:  # Show first 3 cells only
            cell_type = cell.get('cell_type', 'Unknown')
            print(f"\nCell {cell['id']} ({cell_type}):")
            print(f"  Users: {cell['num_users']}")
            print(f"  Throughput: {cell['throughput']:.1f} Mbps")
            print(f"  Drop rate: {cell['drop_rate']*100:.2f}%")
            print(f"  TX Power: {cell['tx_power']:.1f} dBm")
            print(f"  Antenna tilt: {cell['antenna_tilt']:.1f} degrees")
            print(f"  User satisfaction: {self._calculate_satisfaction(cell):.1f}/100")
            if self.use_real_data:
                print(f"  Recommended action: {cell.get('optimized_action', 'N/A')}")

    def get_network_stats(self):
        """Get overall network statistics"""
        stats = {
            'avg_throughput': np.mean([c['throughput'] for c in self.cells]),
            'avg_drop_rate': np.mean([c['drop_rate'] for c in self.cells]),
            'total_power': np.sum([c['power_consumption'] for c in self.cells]),
            'avg_satisfaction': np.mean([self._calculate_satisfaction(c) for c in self.cells]),
            'avg_interference': np.mean([c['interference'] for c in self.cells])
        }

        if self.use_real_data:
            stats['cell_types'] = {}
            for cell in self.cells:
                ct = cell.get('cell_type', 'Unknown')
                stats['cell_types'][ct] = stats['cell_types'].get(ct, 0) + 1

        return stats

    def get_data_info(self):
        """Get information about the data source."""
        if self.use_real_data and self.data_loader is not None:
            return {
                'mode': 'real_data',
                'data_path': self.data_path,
                'statistics': self.data_loader.get_statistics()
            }
        else:
            return {
                'mode': 'simulated',
                'data_path': None,
                'statistics': None
            }


if __name__ == "__main__":
    # Test the environment with real data
    print("Testing RAN Environment with Real Data...")
    print("=" * 60)

    # Test with real data
    print("\n1. Testing with REAL DATA mode:")
    env = RANEnvironment(num_cells=5, use_real_data=True)
    state = env.reset()

    print(f"State size: {state.shape}")
    print(f"Number of possible actions: {env.action_space.n}")

    data_info = env.get_data_info()
    print(f"Data mode: {data_info['mode']}")
    if data_info['statistics']:
        print(f"Total cells in dataset: {data_info['statistics']['num_cells']}")

    # Execute some random actions
    for i in range(5):
        action = env.action_space.sample()
        state, reward, done, info = env.step(action)

        print(f"\nStep {i+1}:")
        print(f"  Cell Type: {info.get('cell_type', 'N/A')}")
        print(f"  Action: {info['changes']}")
        print(f"  Reward: {reward:.2f}")
        print(f"  Recommended: {info.get('optimized_action', 'N/A')}")

        if done:
            break

    env.render()

    stats = env.get_network_stats()
    print("\nNetwork statistics:")
    for key, value in stats.items():
        if key != 'cell_types':
            print(f"  {key}: {value:.2f}")
    if 'cell_types' in stats:
        print(f"  cell_types: {stats['cell_types']}")

    # Test with simulated data for comparison
    print("\n" + "=" * 60)
    print("\n2. Testing with SIMULATED DATA mode:")
    env_sim = RANEnvironment(num_cells=5, use_real_data=False)
    state = env_sim.reset()

    print(f"Data mode: {env_sim.get_data_info()['mode']}")

    for i in range(3):
        action = env_sim.action_space.sample()
        state, reward, done, info = env_sim.step(action)
        print(f"Step {i+1}: Reward = {reward:.2f}")

    print("\n[OK] Environment tests completed!")
