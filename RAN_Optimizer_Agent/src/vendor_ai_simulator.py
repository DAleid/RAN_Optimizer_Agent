"""
Vendor AI Simulators
Simulates how Ericsson, Nokia, and Huawei AIs behave independently
Each vendor AI only optimizes its own cells, creating conflicts
"""

import numpy as np

class VendorAI:
    """
    Simulates a vendor's AI system (Ericsson/Nokia/Huawei)
    Key limitation: Can only see and optimize its OWN cells
    """

    def __init__(self, vendor_name, environment):
        self.vendor = vendor_name
        self.env = environment

        # Vendor-specific optimization strategy
        self.strategy = self._get_vendor_strategy()

        # History of actions
        self.action_history = []

    def _get_vendor_strategy(self):
        """
        Each vendor has slightly different optimization approach
        (In reality they're similar, but this adds realism to demo)
        """

        strategies = {
            'ericsson': {
                'priority': 'throughput',
                'aggressiveness': 1.2,  # More aggressive power increases
                'name': 'Ericsson Expert Analytics'
            },
            'nokia': {
                'priority': 'quality',
                'aggressiveness': 1.0,  # Moderate
                'name': 'Nokia AVA'
            },
            'huawei': {
                'priority': 'efficiency',
                'aggressiveness': 0.8,  # More conservative
                'name': 'Huawei iMaster MAE'
            }
        }

        return strategies.get(self.vendor, strategies['nokia'])

    def get_my_cells(self):
        """Get only cells belonging to this vendor"""
        return self.env.get_cells_by_vendor(self.vendor)

    def optimize(self):
        """
        Optimize all my cells independently
        KEY LIMITATION: Cannot see other vendors' cells!
        """

        my_cells = self.get_my_cells()
        actions = {}

        for cell in my_cells:
            action = self._optimize_single_cell(cell)
            if action:
                actions[cell['id']] = action

        # Store in history
        self.action_history.append(actions)

        return actions

    def _optimize_single_cell(self, cell):
        """
        Greedy optimization for a single cell
        This is simplified but shows typical vendor AI behavior
        """

        action = {
            'power_delta': 0,
            'tilt_delta': 0,
            'ho_delta': 0,
            'reason': 'No change needed'
        }

        changed = False

        # Strategy 1: If throughput is low, increase power
        if cell['throughput'] < 50:
            power_increase = 3 * self.strategy['aggressiveness']
            action['power_delta'] = power_increase
            action['reason'] = f"{self.strategy['name']}: Low throughput, increasing power"
            changed = True

        # Strategy 2: If interference is high, try to overcome it (creates escalation!)
        elif cell['interference'] > 0.3:
            # Vendor AI thinks: "External interference! Need more power!"
            # Doesn't realize it might be from another vendor's cell
            power_increase = 4 * self.strategy['aggressiveness']
            action['power_delta'] = power_increase
            action['reason'] = f"{self.strategy['name']}: High interference, boosting signal"
            changed = True

        # Strategy 3: If drop rate is high, increase power
        elif cell['drop_rate'] > 0.06:
            power_increase = 2 * self.strategy['aggressiveness']
            action['power_delta'] = power_increase
            action['reason'] = f"{self.strategy['name']}: High drops, increasing coverage"
            changed = True

        # Strategy 4: If utilization is very high, try to expand coverage
        elif cell['num_users'] > 250:
            action['power_delta'] = 2
            action['tilt_delta'] = 1  # Widen beam
            action['reason'] = f"{self.strategy['name']}: High load, expanding coverage"
            changed = True

        return action if changed else None


class IndependentVendorSimulation:
    """
    Runs all vendor AIs independently
    This demonstrates THE PROBLEM: conflicts and suboptimal performance
    """

    def __init__(self, environment):
        self.env = environment

        # Create vendor AIs
        self.vendor_ais = {
            'ericsson': VendorAI('ericsson', environment),
            'nokia': VendorAI('nokia', environment),
            'huawei': VendorAI('huawei', environment)
        }

        # Track conflicts
        self.conflicts_history = []

    def run_one_step(self):
        """
        Each vendor AI acts independently in the same time step
        This is realistic: they don't coordinate in real networks!
        """

        all_actions = {}
        conflicts_detected = []

        # Each vendor optimizes independently
        for vendor_name, vendor_ai in self.vendor_ais.items():
            actions = vendor_ai.optimize()

            # Check if these actions will create cross-vendor conflicts
            for cell_id, action in actions.items():
                # Detect potential conflicts BEFORE applying
                if action['power_delta'] > 0:
                    # Power increase might create conflict
                    neighbors = self.env.get_cross_vendor_neighbors(cell_id)

                    for neighbor in neighbors:
                        # Check if neighbor also plans to increase power
                        conflict = self._check_conflict(cell_id, neighbor['id'], action)
                        if conflict:
                            conflicts_detected.append(conflict)

                all_actions[cell_id] = {
                    'action': action,
                    'vendor': vendor_name
                }

            # Apply vendor's actions to environment
            for cell_id, action in actions.items():
                self.env.apply_action(cell_id, action)

        self.conflicts_history.append(conflicts_detected)

        return {
            'actions': all_actions,
            'conflicts': conflicts_detected,
            'stats': self.env.get_network_stats()
        }

    def _check_conflict(self, cell_a, cell_b, action):
        """Check if action creates a conflict with neighboring cell"""

        cell_a_data = self.env.cells[cell_a]
        cell_b_data = self.env.cells[cell_b]

        # Different vendors
        if cell_a_data['vendor'] == cell_b_data['vendor']:
            return None

        # Both cells at high power = power escalation
        if (cell_a_data['tx_power'] > 40 and
            cell_b_data['tx_power'] > 40 and
            action['power_delta'] > 0):

            return {
                'type': 'power_escalation',
                'cells': [cell_a, cell_b],
                'vendors': [cell_a_data['vendor'], cell_b_data['vendor']],
                'severity': 'high',
                'description': f"{cell_a_data['vendor'].capitalize()} Cell {cell_a} and {cell_b_data['vendor'].capitalize()} Cell {cell_b} in power war"
            }

        # High interference between vendors
        interference = self.env.calculate_interference(cell_a, cell_b)
        if interference > 0.015:  # Threshold
            return {
                'type': 'cross_vendor_interference',
                'cells': [cell_a, cell_b],
                'vendors': [cell_a_data['vendor'], cell_b_data['vendor']],
                'severity': 'medium',
                'interference_level': interference,
                'description': f"High interference between {cell_a_data['vendor']} and {cell_b_data['vendor']}"
            }

        return None

    def run_simulation(self, num_steps=10):
        """Run complete simulation for N steps"""

        results = {
            'steps': [],
            'total_conflicts': 0,
            'final_stats': None
        }

        for step in range(num_steps):
            step_result = self.run_one_step()
            results['steps'].append(step_result)
            results['total_conflicts'] += len(step_result['conflicts'])

        results['final_stats'] = self.env.get_network_stats()

        return results


if __name__ == "__main__":
    from multi_vendor_environment import MultiVendorEnvironment

    print("Testing Vendor AI Simulators...")

    # Create environment
    env = MultiVendorEnvironment(num_cells=12)

    print("\n1. Testing Individual Vendor AIs:")
    for vendor in ['ericsson', 'nokia', 'huawei']:
        ai = VendorAI(vendor, env)
        actions = ai.optimize()
        print(f"\n{vendor.capitalize()} AI ({ai.strategy['name']}):")
        print(f"  Optimized {len(actions)} cells")
        if actions:
            sample_cell_id = list(actions.keys())[0]
            sample_action = actions[sample_cell_id]
            print(f"  Example: Cell {sample_cell_id} - {sample_action['reason']}")

    print("\n2. Running Independent Vendor Simulation:")
    env2 = MultiVendorEnvironment(num_cells=12)
    sim = IndependentVendorSimulation(env2)

    print("  Initial stats:", env2.get_network_stats())

    # Run for 5 steps
    for i in range(5):
        result = sim.run_one_step()
        print(f"\n  Step {i+1}:")
        print(f"    Actions taken: {len(result['actions'])}")
        print(f"    Conflicts detected: {len(result['conflicts'])}")
        if result['conflicts']:
            for conflict in result['conflicts']:
                print(f"      - {conflict['type']}: {conflict['description']}")

    print("\n  Final stats:", env2.get_network_stats())
    print(f"\n✅ Vendor AI Simulators working!")
    print(f"   Total conflicts in 5 steps: {sum(len(s['conflicts']) for s in sim.conflicts_history)}")
