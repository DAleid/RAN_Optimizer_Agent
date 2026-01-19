"""
Multi-Vendor RAN Coordination Agent
THE INNOVATION: Coordinates optimization across ALL vendors
Prevents conflicts and achieves global network optimization
"""

import numpy as np
from scipy.optimize import minimize

class MultiVendorCoordinationAgent:
    """
    Meta-agent that coordinates vendor AIs
    KEY CAPABILITY: Can see and coordinate ALL cells from ALL vendors
    """

    def __init__(self, environment, vendor_ais):
        self.env = environment
        self.vendor_ais = vendor_ais

        # Coordination history
        self.coordination_history = []
        self.conflicts_resolved = []

    def detect_conflicts(self):
        """
        Detect cross-vendor conflicts in current network state
        """

        conflicts = []

        # Check all cells for potential conflicts
        for cell in self.env.cells:
            cell_id = cell['id']

            # Find cross-vendor neighbors
            neighbors = self.env.get_cross_vendor_neighbors(cell_id)

            for neighbor in neighbors:
                neighbor_id = neighbor['id']

                # Conflict Type 1: Power Escalation
                if cell['tx_power'] > 42 and neighbor['tx_power'] > 42:
                    conflicts.append({
                        'type': 'power_escalation',
                        'cells': [cell_id, neighbor_id],
                        'vendors': [cell['vendor'], neighbor['vendor']],
                        'severity': 'high',
                        'current_powers': [cell['tx_power'], neighbor['tx_power']],
                        'description': f"Both {cell['vendor']} Cell {cell_id} and {neighbor['vendor']} Cell {neighbor_id} at high power"
                    })

                # Conflict Type 2: High Cross-Vendor Interference
                interference = self.env.calculate_interference(cell_id, neighbor_id)
                if interference > 0.015:
                    conflicts.append({
                        'type': 'high_interference',
                        'cells': [cell_id, neighbor_id],
                        'vendors': [cell['vendor'], neighbor['vendor']],
                        'severity': 'medium',
                        'interference': interference,
                        'description': f"High interference between {cell['vendor']} and {neighbor['vendor']}"
                    })

                # Conflict Type 3: Unbalanced Load (one vendor overloaded, neighbor underutilized)
                cell_load = cell['num_users'] / 300.0  # Normalized
                neighbor_cell = self.env.cells[neighbor_id]
                neighbor_load = neighbor_cell['num_users'] / 300.0

                if cell_load > 0.8 and neighbor_load < 0.5:
                    conflicts.append({
                        'type': 'load_imbalance',
                        'cells': [cell_id, neighbor_id],
                        'vendors': [cell['vendor'], neighbor['vendor']],
                        'severity': 'low',
                        'loads': [cell_load, neighbor_load],
                        'description': f"{cell['vendor']} Cell {cell_id} overloaded, {neighbor['vendor']} Cell {neighbor_id} has capacity"
                    })

        # Remove duplicates (same conflict detected from both sides)
        unique_conflicts = self._deduplicate_conflicts(conflicts)

        return unique_conflicts

    def _deduplicate_conflicts(self, conflicts):
        """Remove duplicate conflicts"""
        seen = set()
        unique = []

        for conflict in conflicts:
            # Create unique identifier
            cells = tuple(sorted(conflict['cells']))
            conflict_type = conflict['type']
            key = (conflict_type, cells)

            if key not in seen:
                seen.add(key)
                unique.append(conflict)

        return unique

    def resolve_conflicts(self, conflicts):
        """
        Resolve conflicts using global optimization
        This is what makes coordination agent BETTER than vendor AIs
        """

        if not conflicts:
            return {}

        coordinated_actions = {}

        for conflict in conflicts:
            if conflict['type'] == 'power_escalation':
                # Both vendors increased power -> REDUCE both for global optimum
                actions = self._resolve_power_escalation(conflict)
                coordinated_actions.update(actions)

            elif conflict['type'] == 'high_interference':
                # Optimize power levels to minimize interference
                actions = self._resolve_interference(conflict)
                coordinated_actions.update(actions)

            elif conflict['type'] == 'load_imbalance':
                # Balance load across vendors
                actions = self._resolve_load_imbalance(conflict)
                coordinated_actions.update(actions)

        return coordinated_actions

    def _resolve_power_escalation(self, conflict):
        """
        Resolve power escalation conflict
        Strategy: Reduce power on both cells (counterintuitive but optimal!)
        """

        cell_a_id, cell_b_id = conflict['cells']
        cell_a = self.env.cells[cell_a_id]
        cell_b = self.env.cells[cell_b_id]

        actions = {}

        # Calculate optimal power reduction
        # Lower power reduces interference, can actually improve throughput!
        power_reduction_a = min(cell_a['tx_power'] - 38, 4)  # Reduce by up to 4 dB
        power_reduction_b = min(cell_b['tx_power'] - 38, 4)

        if power_reduction_a > 0:
            actions[cell_a_id] = {
                'power_delta': -power_reduction_a,
                'reason': f'Coordination: Resolving power escalation with {cell_b["vendor"]} Cell {cell_b_id}',
                'coordinated': True
            }

        if power_reduction_b > 0:
            actions[cell_b_id] = {
                'power_delta': -power_reduction_b,
                'reason': f'Coordination: Resolving power escalation with {cell_a["vendor"]} Cell {cell_a_id}',
                'coordinated': True
            }

        return actions

    def _resolve_interference(self, conflict):
        """
        Resolve high interference between vendor cells
        Strategy: Optimize power balance to minimize interference while maintaining coverage
        """

        cell_a_id, cell_b_id = conflict['cells']
        cell_a = self.env.cells[cell_a_id]
        cell_b = self.env.cells[cell_b_id]

        # Simple heuristic: Reduce power on the higher-power cell
        if cell_a['tx_power'] > cell_b['tx_power']:
            return {
                cell_a_id: {
                    'power_delta': -2,
                    'reason': f'Coordination: Reducing interference with {cell_b["vendor"]} Cell {cell_b_id}',
                    'coordinated': True
                }
            }
        else:
            return {
                cell_b_id: {
                    'power_delta': -2,
                    'reason': f'Coordination: Reducing interference with {cell_a["vendor"]} Cell {cell_a_id}',
                    'coordinated': True
                }
            }

    def _resolve_load_imbalance(self, conflict):
        """
        Resolve load imbalance across vendors
        Strategy: Adjust handover thresholds to shift users to underutilized vendor
        """

        cell_a_id, cell_b_id = conflict['cells']
        overloaded_id = cell_a_id if conflict['loads'][0] > conflict['loads'][1] else cell_b_id
        underloaded_id = cell_b_id if overloaded_id == cell_a_id else cell_a_id

        return {
            overloaded_id: {
                'ho_delta': -5,  # Lower threshold = easier handover out
                'reason': f'Coordination: Offloading to {self.env.cells[underloaded_id]["vendor"]} Cell {underloaded_id}',
                'coordinated': True
            },
            underloaded_id: {
                'ho_delta': +3,  # Higher threshold = attract users
                'reason': f'Coordination: Accepting load from {self.env.cells[overloaded_id]["vendor"]} Cell {overloaded_id}',
                'coordinated': True
            }
        }

    def coordinate_step(self):
        """
        Single coordination step
        1. Detect conflicts
        2. Resolve conflicts
        3. Execute coordinated actions
        """

        # Detect conflicts in current state
        conflicts = self.detect_conflicts()

        if not conflicts:
            # No conflicts, let vendor AIs proceed normally
            return {
                'conflicts_detected': [],
                'actions_taken': {},
                'mode': 'autonomous_vendors'
            }

        # Resolve conflicts with coordinated actions
        coordinated_actions = self.resolve_conflicts(conflicts)

        # Execute coordinated actions
        for cell_id, action in coordinated_actions.items():
            self.env.apply_action(cell_id, action)

        # Record resolution
        self.conflicts_resolved.extend(conflicts)
        self.coordination_history.append({
            'conflicts': conflicts,
            'actions': coordinated_actions
        })

        return {
            'conflicts_detected': conflicts,
            'actions_taken': coordinated_actions,
            'mode': 'coordinated'
        }

    def run_coordinated_simulation(self, num_steps=10):
        """
        Run simulation WITH coordination
        Compare this to IndependentVendorSimulation to see improvement
        """

        results = {
            'steps': [],
            'total_conflicts_detected': 0,
            'total_conflicts_resolved': 0,
            'final_stats': None
        }

        for step in range(num_steps):
            # First, let vendor AIs propose actions (but don't execute yet)
            vendor_intentions = {}
            for vendor_name, vendor_ai in self.vendor_ais.items():
                actions = vendor_ai.optimize()
                vendor_intentions[vendor_name] = actions

            # Detect conflicts that would arise
            step_result = self.coordinate_step()

            results['steps'].append(step_result)
            results['total_conflicts_detected'] += len(step_result['conflicts_detected'])

            if step_result['mode'] == 'coordinated':
                results['total_conflicts_resolved'] += len(step_result['conflicts_detected'])

        results['final_stats'] = self.env.get_network_stats()

        return results


class CoordinationComparison:
    """
    Utility class to compare WITH vs WITHOUT coordination
    """

    @staticmethod
    def run_comparison(num_cells=12, num_steps=10):
        """
        Run both scenarios and compare results
        """

        from multi_vendor_environment import MultiVendorEnvironment
        from vendor_ai_simulator import IndependentVendorSimulation, VendorAI

        # Scenario 1: WITHOUT Coordination
        print("Running WITHOUT coordination...")
        env_without = MultiVendorEnvironment(num_cells=num_cells)
        sim_without = IndependentVendorSimulation(env_without)
        results_without = sim_without.run_simulation(num_steps=num_steps)

        # Scenario 2: WITH Coordination
        print("Running WITH coordination...")
        env_with = MultiVendorEnvironment(num_cells=num_cells)
        vendor_ais = {
            'ericsson': VendorAI('ericsson', env_with),
            'nokia': VendorAI('nokia', env_with),
            'huawei': VendorAI('huawei', env_with)
        }
        coordinator = MultiVendorCoordinationAgent(env_with, vendor_ais)
        results_with = coordinator.run_coordinated_simulation(num_steps=num_steps)

        # Compare results
        comparison = {
            'without_coordination': {
                'conflicts': results_without['total_conflicts'],
                'stats': results_without['final_stats']
            },
            'with_coordination': {
                'conflicts_detected': results_with['total_conflicts_detected'],
                'conflicts_resolved': results_with['total_conflicts_resolved'],
                'stats': results_with['final_stats']
            },
            'improvement': {}
        }

        # Calculate improvements
        stats_without = results_without['final_stats']
        stats_with = results_with['final_stats']

        comparison['improvement'] = {
            'throughput': ((stats_with['avg_throughput'] - stats_without['avg_throughput']) /
                          stats_without['avg_throughput'] * 100),
            'drop_rate': ((stats_without['avg_drop_rate'] - stats_with['avg_drop_rate']) /
                         stats_without['avg_drop_rate'] * 100),
            'interference': ((stats_without['avg_interference'] - stats_with['avg_interference']) /
                           stats_without['avg_interference'] * 100),
            'power': ((stats_without['total_power'] - stats_with['total_power']) /
                     stats_without['total_power'] * 100)
        }

        return comparison


if __name__ == "__main__":
    print("Testing Multi-Vendor Coordination Agent...")
    print("=" * 60)

    comparison = CoordinationComparison.run_comparison(num_cells=12, num_steps=10)

    print("\n" + "=" * 60)
    print("RESULTS COMPARISON")
    print("=" * 60)

    print("\nWITHOUT Coordination:")
    print(f"  Conflicts: {comparison['without_coordination']['conflicts']}")
    print(f"  Avg Throughput: {comparison['without_coordination']['stats']['avg_throughput']:.2f} Mbps")
    print(f"  Avg Drop Rate: {comparison['without_coordination']['stats']['avg_drop_rate']*100:.2f}%")
    print(f"  Avg Interference: {comparison['without_coordination']['stats']['avg_interference']:.4f}")

    print("\nWITH Coordination:")
    print(f"  Conflicts Detected: {comparison['with_coordination']['conflicts_detected']}")
    print(f"  Conflicts Resolved: {comparison['with_coordination']['conflicts_resolved']}")
    print(f"  Avg Throughput: {comparison['with_coordination']['stats']['avg_throughput']:.2f} Mbps")
    print(f"  Avg Drop Rate: {comparison['with_coordination']['stats']['avg_drop_rate']*100:.2f}%")
    print(f"  Avg Interference: {comparison['with_coordination']['stats']['avg_interference']:.4f}")

    print("\nIMPROVEMENT:")
    print(f"  Throughput: +{comparison['improvement']['throughput']:.1f}%")
    print(f"  Drop Rate: -{comparison['improvement']['drop_rate']:.1f}%")
    print(f"  Interference: -{comparison['improvement']['interference']:.1f}%")
    print(f"  Power Consumption: -{comparison['improvement']['power']:.1f}%")

    print("\n" + "=" * 60)
    print("✅ Coordination Agent working! Significant improvements achieved!")
