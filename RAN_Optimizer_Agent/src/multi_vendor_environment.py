"""
Multi-Vendor Network Environment
Simulates network with cells from different vendors (Ericsson, Nokia, Huawei)
Each vendor's AI operates independently, creating potential conflicts
"""

import numpy as np
try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError:
    import gym
    from gym import spaces

class MultiVendorEnvironment(gym.Env):
    """
    Simulates a multi-vendor RAN network
    Different cells belong to different vendors
    """

    def __init__(self, num_cells=12):
        super(MultiVendorEnvironment, self).__init__()

        self.num_cells = num_cells
        self.current_step = 0
        self.max_steps = 100

        # Initialize cells with vendor assignment
        self.cells = []
        self._initialize_cells()

        # Define observation and action spaces
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(num_cells * 6,),
            dtype=np.float32
        )
        self.action_space = spaces.Discrete(27)  # 3^3 actions

        # Track history for conflict detection
        self.history = []

    def _initialize_cells(self):
        """Initialize cells and assign to vendors"""

        vendors = ['ericsson', 'nokia', 'huawei']
        vendor_colors = {
            'ericsson': '#0033A0',  # Ericsson blue
            'nokia': '#124191',      # Nokia blue
            'huawei': '#FF0000'      # Huawei red
        }

        cells_per_vendor = self.num_cells // 3

        for i in range(self.num_cells):
            # Assign vendor
            vendor_idx = i // cells_per_vendor
            if vendor_idx >= len(vendors):
                vendor_idx = len(vendors) - 1
            vendor = vendors[vendor_idx]

            # Create cell
            cell = {
                'id': i,
                'vendor': vendor,
                'color': vendor_colors[vendor],

                # Position (for visualization)
                'x': (i % 4) * 2,
                'y': (i // 4) * 2,

                # Configuration parameters
                'tx_power': np.random.uniform(35, 40),  # dBm
                'antenna_tilt': np.random.uniform(2, 6),  # degrees
                'handover_threshold': np.random.uniform(60, 80),  # dB

                # Performance metrics
                'num_users': np.random.randint(50, 300),
                'throughput': np.random.uniform(40, 60),  # Mbps
                'drop_rate': np.random.uniform(0.02, 0.08),  # 2-8%
                'power_consumption': 0,
                'interference': np.random.uniform(0.1, 0.3),

                # Vendor AI state
                'vendor_ai_action': None,
                'vendor_ai_active': True
            }

            # Calculate power consumption
            cell['power_consumption'] = cell['tx_power'] * 0.5

            self.cells.append(cell)

    def reset(self):
        """Reset environment to initial state"""
        self._initialize_cells()
        self.current_step = 0
        self.history = []
        return self._get_state()

    def _get_state(self):
        """Get current network state as observation"""
        state = []
        for cell in self.cells:
            state.extend([
                cell['num_users'] / 500.0,
                cell['throughput'] / 100.0,
                cell['drop_rate'] / 0.1,
                cell['tx_power'] / 50.0,
                cell['interference'],
                cell['power_consumption'] / 50.0
            ])
        return np.array(state, dtype=np.float32)

    def get_cells_by_vendor(self, vendor):
        """Get all cells belonging to a specific vendor"""
        return [cell for cell in self.cells if cell['vendor'] == vendor]

    def get_cross_vendor_neighbors(self, cell_id):
        """
        Find neighboring cells from DIFFERENT vendors
        This is the key for detecting cross-vendor conflicts
        """
        cell = self.cells[cell_id]
        cell_vendor = cell['vendor']
        cell_x, cell_y = cell['x'], cell['y']

        neighbors = []

        for other_cell in self.cells:
            if other_cell['vendor'] != cell_vendor:
                # Calculate distance
                dx = cell_x - other_cell['x']
                dy = cell_y - other_cell['y']
                distance = np.sqrt(dx**2 + dy**2)

                # Cells within 3 units are neighbors
                if distance < 3.5 and distance > 0:
                    neighbors.append({
                        'id': other_cell['id'],
                        'vendor': other_cell['vendor'],
                        'distance': distance,
                        'tx_power': other_cell['tx_power'],
                        'interference': other_cell['interference']
                    })

        return neighbors

    def calculate_interference(self, cell_a_id, cell_b_id):
        """Calculate interference between two cells"""
        cell_a = self.cells[cell_a_id]
        cell_b = self.cells[cell_b_id]

        # Distance-based interference
        dx = cell_a['x'] - cell_b['x']
        dy = cell_a['y'] - cell_b['y']
        distance = np.sqrt(dx**2 + dy**2) + 0.1  # Avoid division by zero

        # Interference proportional to power and inversely to distance
        interference = (cell_a['tx_power'] * cell_b['tx_power']) / (100 * distance**2)

        return interference

    def apply_action(self, cell_id, action_params):
        """Apply configuration changes to a cell"""
        cell = self.cells[cell_id]

        # Apply power change
        if 'power_delta' in action_params:
            cell['tx_power'] = np.clip(
                cell['tx_power'] + action_params['power_delta'],
                30, 46  # Power limits
            )

        # Apply tilt change
        if 'tilt_delta' in action_params:
            cell['antenna_tilt'] = np.clip(
                cell['antenna_tilt'] + action_params['tilt_delta'],
                0, 10
            )

        # Apply handover threshold change
        if 'ho_delta' in action_params:
            cell['handover_threshold'] = np.clip(
                cell['handover_threshold'] + action_params['ho_delta'],
                50, 90
            )

        # Update power consumption
        cell['power_consumption'] = cell['tx_power'] * 0.5

        # Recalculate metrics
        self._update_cell_metrics(cell_id)

    def _update_cell_metrics(self, cell_id):
        """Update cell performance metrics after configuration change"""
        cell = self.cells[cell_id]

        # Calculate total interference from all neighbors
        total_interference = 0
        for other_id in range(self.num_cells):
            if other_id != cell_id:
                total_interference += self.calculate_interference(cell_id, other_id)

        cell['interference'] = total_interference

        # Throughput based on power and interference (simplified Shannon)
        signal_power = cell['tx_power']
        noise_plus_interference = 20 + total_interference * 100
        sinr = signal_power / noise_plus_interference

        # Shannon capacity approximation
        cell['throughput'] = 20 * np.log2(1 + sinr)
        cell['throughput'] = np.clip(cell['throughput'], 10, 100)

        # Drop rate inversely related to SINR
        cell['drop_rate'] = 0.1 / (1 + sinr)
        cell['drop_rate'] = np.clip(cell['drop_rate'], 0.01, 0.15)

    def get_network_stats(self):
        """Get aggregate network statistics"""
        return {
            'avg_throughput': np.mean([c['throughput'] for c in self.cells]),
            'avg_drop_rate': np.mean([c['drop_rate'] for c in self.cells]),
            'avg_interference': np.mean([c['interference'] for c in self.cells]),
            'total_power': sum([c['power_consumption'] for c in self.cells]),
            'num_cells': self.num_cells
        }

    def step(self, action):
        """Environment step (for compatibility, not used in multi-vendor demo)"""
        self.current_step += 1
        done = self.current_step >= self.max_steps

        state = self._get_state()
        reward = 0  # Not used in demo
        info = {}

        return state, reward, done, info


if __name__ == "__main__":
    # Test the environment
    print("Testing Multi-Vendor Environment...")

    env = MultiVendorEnvironment(num_cells=12)

    print(f"\nTotal cells: {env.num_cells}")

    for vendor in ['ericsson', 'nokia', 'huawei']:
        vendor_cells = env.get_cells_by_vendor(vendor)
        print(f"{vendor.capitalize()}: {len(vendor_cells)} cells")

    # Test cross-vendor neighbors
    print("\nCross-vendor neighbors for Cell 0:")
    neighbors = env.get_cross_vendor_neighbors(0)
    for n in neighbors:
        print(f"  Cell {n['id']} ({n['vendor']}) - Distance: {n['distance']:.2f}")

    # Test network stats
    print("\nInitial Network Stats:")
    stats = env.get_network_stats()
    for key, value in stats.items():
        print(f"  {key}: {value:.2f}")

    print("\n✅ Multi-Vendor Environment working!")
