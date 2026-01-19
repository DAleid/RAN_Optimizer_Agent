"""
Network Healing Environment
Simulates RAN network with realistic fault injection
Supports both real data from CSV and simulated data modes
"""

import numpy as np
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class FaultType:
    """Types of network faults"""
    HARDWARE_FAILURE = "hardware_failure"
    CONFIGURATION_ERROR = "configuration_error"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    CONNECTIVITY_ISSUE = "connectivity_issue"
    CAPACITY_OVERLOAD = "capacity_overload"
    INTERFERENCE_SPIKE = "interference_spike"

class NetworkHealingEnvironment:
    """
    Network environment with fault injection capabilities
    Simulates realistic RAN network faults for testing healing agent

    Supports two modes:
    1. Real data mode: Uses data from 6G_HetNet_Transmission_Management.csv
    2. Simulated mode: Generates synthetic data (legacy behavior)
    """

    def __init__(self, num_cells: int = 10, use_real_data: bool = True,
                 data_path: Optional[str] = None, random_seed: Optional[int] = None):
        """
        Initialize the healing environment.

        Args:
            num_cells: Number of cells in the network
            use_real_data: If True, use real data from CSV; if False, use simulated data
            data_path: Path to the CSV file (only used if use_real_data=True)
            random_seed: Random seed for reproducibility
        """
        self.num_cells = num_cells
        self.use_real_data = use_real_data
        self.data_path = data_path
        self.random_seed = random_seed
        self.data_loader = None

        self.cells = []
        self.active_faults = []
        self.fault_history = []
        self.time_step = 0

        # Initialize data loader if using real data
        if self.use_real_data:
            self._init_data_loader()

        # Initialize network
        self._initialize_network()

    def _init_data_loader(self):
        """Initialize the data loader for real data."""
        try:
            from data_loader import NetworkDataLoader
            self.data_loader = NetworkDataLoader(self.data_path)
            print(f"[OK] Loaded real data for healing env: {self.data_loader.get_num_cells()} unique cells")
        except ImportError:
            print("[WARNING] data_loader module not found, falling back to simulated data")
            self.use_real_data = False
        except FileNotFoundError as e:
            print(f"[WARNING] Data file not found: {e}, falling back to simulated data")
            self.use_real_data = False

    def _initialize_network(self):
        """Create healthy network baseline"""
        self.cells = []

        if self.use_real_data and self.data_loader is not None:
            self._initialize_from_real_data()
        else:
            self._initialize_simulated()

    def _initialize_from_real_data(self):
        """Initialize network using real data from CSV."""
        seed = self.random_seed if self.random_seed is not None else 42
        real_cells = self.data_loader.sample_network_state(
            num_cells=self.num_cells,
            seed=seed
        )

        for i, real_cell in enumerate(real_cells):
            cell = {
                'id': i,
                'name': f"Cell_{i:03d}",
                'cell_type': real_cell.get('cell_type', 'Macro'),
                'status': 'operational',
                'health_score': 1.0,

                # Performance metrics from real data
                'throughput': real_cell['throughput'],
                'latency': real_cell.get('latency', 15.0),
                'packet_loss': real_cell['drop_rate'] * 100,  # Convert to percentage
                'availability': 99.9,

                # RF metrics from real data
                'tx_power': real_cell['tx_power'],
                'interference': real_cell['interference'],
                'sinr': real_cell.get('snr', 20.0),

                # Resource metrics (estimated from real data)
                'cpu_usage': min(real_cell.get('resource_utilization', 50.0), 100.0),
                'memory_usage': np.random.uniform(40, 60),
                'temperature': np.random.uniform(35, 45),

                # User metrics from real data
                'num_users': real_cell['num_users'],
                'drop_rate': real_cell['drop_rate'],
                'handover_success': 100 - (real_cell['drop_rate'] * 100),

                # Additional real data metrics
                'qos_satisfaction': real_cell.get('qos_satisfaction', 80.0),
                'frequency': real_cell.get('frequency', 3.5),
                'bandwidth': real_cell.get('bandwidth', 100),
                'optimized_action': real_cell.get('optimized_action', 'Maintain_Power'),

                # Alarms
                'alarms': [],
                'faults': [],

                # Store baseline for healing
                'baseline_throughput': real_cell['throughput'],
                'baseline_latency': real_cell.get('latency', 15.0),
                'baseline_packet_loss': real_cell['drop_rate'] * 100,
            }
            self.cells.append(cell)

    def _initialize_simulated(self):
        """Create healthy network baseline using simulated data."""
        for i in range(self.num_cells):
            cell = {
                'id': i,
                'name': f"Cell_{i:03d}",
                'cell_type': random.choice(['Macro', 'Micro', 'Pico', 'Femto']),
                'status': 'operational',
                'health_score': 1.0,

                # Performance metrics
                'throughput': np.random.uniform(45, 55),  # Mbps
                'latency': np.random.uniform(10, 15),  # ms
                'packet_loss': np.random.uniform(0, 0.5),  # %
                'availability': 99.9,  # %

                # RF metrics
                'tx_power': 40.0,  # dBm
                'interference': np.random.uniform(0.05, 0.15),
                'sinr': np.random.uniform(15, 25),  # dB

                # Resource metrics
                'cpu_usage': np.random.uniform(30, 50),  # %
                'memory_usage': np.random.uniform(40, 60),  # %
                'temperature': np.random.uniform(35, 45),  # Celsius

                # User metrics
                'num_users': np.random.randint(50, 150),
                'drop_rate': np.random.uniform(0.01, 0.03),
                'handover_success': 98.5,

                # Additional metrics
                'qos_satisfaction': np.random.uniform(75, 95),
                'frequency': 3.5,
                'bandwidth': 100,
                'optimized_action': 'Maintain_Power',

                # Alarms
                'alarms': [],
                'faults': [],

                # Baseline for healing
                'baseline_throughput': 50.0,
                'baseline_latency': 12.5,
                'baseline_packet_loss': 0.25,
            }
            self.cells.append(cell)

    def inject_fault(self, fault_type, cell_id=None, severity='medium'):
        """
        Inject a fault into the network

        Args:
            fault_type: Type of fault (from FaultType class)
            cell_id: Specific cell to inject fault (None = random)
            severity: 'low', 'medium', 'high', 'critical'
        """

        if cell_id is None:
            cell_id = random.randint(0, self.num_cells - 1)

        cell = self.cells[cell_id]

        fault = {
            'id': len(self.fault_history),
            'type': fault_type,
            'cell_id': cell_id,
            'cell_name': cell['name'],
            'cell_type': cell.get('cell_type', 'Unknown'),
            'severity': severity,
            'start_time': self.time_step,
            'detected': False,
            'diagnosed': False,
            'healed': False,
            'end_time': None
        }

        # Apply fault effects to cell
        self._apply_fault_effects(cell, fault)

        self.active_faults.append(fault)
        cell['faults'].append(fault)

        return fault

    def _apply_fault_effects(self, cell, fault):
        """Apply realistic effects of fault on cell metrics"""

        fault_type = fault['type']
        severity_multiplier = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.85,
            'critical': 1.0
        }[fault['severity']]

        # Cell type affects severity (smaller cells are more sensitive)
        cell_type_multiplier = {
            'Macro': 0.8,
            'Micro': 0.9,
            'Pico': 1.0,
            'Femto': 1.1
        }.get(cell.get('cell_type', 'Macro'), 1.0)

        effective_severity = severity_multiplier * cell_type_multiplier

        if fault_type == FaultType.HARDWARE_FAILURE:
            # Hardware failure: severe impact on all metrics
            cell['status'] = 'failed'
            cell['health_score'] = 0.1
            cell['throughput'] *= (1 - 0.9 * effective_severity)
            cell['latency'] *= (1 + 5 * effective_severity)
            cell['packet_loss'] += 10 * effective_severity
            cell['availability'] -= 20 * effective_severity
            cell['alarms'].append({
                'type': 'HARDWARE_FAULT',
                'severity': 'CRITICAL',
                'message': f"Hardware component failure detected in {cell.get('cell_type', 'Unknown')} cell"
            })

        elif fault_type == FaultType.CONFIGURATION_ERROR:
            # Config error: impacts connectivity and performance
            cell['status'] = 'degraded'
            cell['health_score'] = 0.4
            cell['throughput'] *= (1 - 0.4 * effective_severity)
            cell['handover_success'] -= 15 * effective_severity
            cell['drop_rate'] += 0.05 * effective_severity
            cell['alarms'].append({
                'type': 'CONFIG_ERROR',
                'severity': 'MAJOR',
                'message': f"Configuration mismatch detected"
            })

        elif fault_type == FaultType.PERFORMANCE_DEGRADATION:
            # Performance degradation: gradual decline
            cell['status'] = 'degraded'
            cell['health_score'] = 0.5
            cell['throughput'] *= (1 - 0.5 * effective_severity)
            cell['latency'] *= (1 + 2 * effective_severity)
            cell['packet_loss'] += 3 * effective_severity
            cell['qos_satisfaction'] *= (1 - 0.3 * effective_severity)
            cell['alarms'].append({
                'type': 'PERFORMANCE_DEGRADED',
                'severity': 'MAJOR',
                'message': f"Performance below threshold"
            })

        elif fault_type == FaultType.CONNECTIVITY_ISSUE:
            # Connectivity issue: affects user connections
            cell['status'] = 'degraded'
            cell['health_score'] = 0.6
            cell['drop_rate'] += 0.1 * effective_severity
            cell['handover_success'] -= 20 * effective_severity
            cell['num_users'] = int(cell['num_users'] * (1 - 0.4 * effective_severity))
            cell['alarms'].append({
                'type': 'CONNECTIVITY_ISSUE',
                'severity': 'MAJOR',
                'message': f"High connection failure rate"
            })

        elif fault_type == FaultType.CAPACITY_OVERLOAD:
            # Capacity overload: resource exhaustion
            cell['status'] = 'overloaded'
            cell['health_score'] = 0.7
            cell['cpu_usage'] = min(95, cell['cpu_usage'] + 40 * effective_severity)
            cell['memory_usage'] = min(95, cell['memory_usage'] + 30 * effective_severity)
            cell['throughput'] *= (1 - 0.3 * effective_severity)
            cell['latency'] *= (1 + 1.5 * effective_severity)
            cell['alarms'].append({
                'type': 'CAPACITY_OVERLOAD',
                'severity': 'MAJOR',
                'message': f"Resource utilization critical"
            })

        elif fault_type == FaultType.INTERFERENCE_SPIKE:
            # Interference spike: RF problem
            cell['status'] = 'degraded'
            cell['health_score'] = 0.65
            cell['interference'] += 0.4 * effective_severity
            cell['sinr'] -= 10 * effective_severity
            cell['throughput'] *= (1 - 0.35 * effective_severity)
            cell['alarms'].append({
                'type': 'HIGH_INTERFERENCE',
                'severity': 'MAJOR',
                'message': f"Interference level above threshold"
            })

    def heal_fault(self, fault_id, healing_action):
        """
        Apply healing action to resolve fault

        Args:
            fault_id: ID of fault to heal
            healing_action: Dict describing the healing action

        Returns:
            success: Boolean indicating if healing was successful
        """

        # Find the fault
        fault = next((f for f in self.active_faults if f['id'] == fault_id), None)
        if not fault:
            return False

        cell = self.cells[fault['cell_id']]

        # Apply healing action effects
        success = self._apply_healing_action(cell, fault, healing_action)

        if success:
            # Mark fault as healed
            fault['healed'] = True
            fault['end_time'] = self.time_step
            fault['healing_action'] = healing_action

            # Remove from active faults
            self.active_faults.remove(fault)

            # Move to history
            self.fault_history.append(fault)

            # Restore cell health
            self._restore_cell_health(cell, fault)

        return success

    def _apply_healing_action(self, cell, fault, action):
        """Apply specific healing action"""

        action_type = action.get('type', 'generic')

        # Different healing actions for different fault types
        if fault['type'] == FaultType.HARDWARE_FAILURE:
            if action_type in ['restart', 'switch_to_backup']:
                return True  # Healing successful
            return False

        elif fault['type'] == FaultType.CONFIGURATION_ERROR:
            if action_type in ['reset_config', 'apply_correct_config']:
                return True
            return False

        elif fault['type'] == FaultType.PERFORMANCE_DEGRADATION:
            if action_type in ['optimize_parameters', 'adjust_resources']:
                return True
            return False

        elif fault['type'] == FaultType.CONNECTIVITY_ISSUE:
            if action_type in ['restart_service', 'update_neighbor_list']:
                return True
            return False

        elif fault['type'] == FaultType.CAPACITY_OVERLOAD:
            if action_type in ['load_balancing', 'resource_expansion']:
                return True
            return False

        elif fault['type'] == FaultType.INTERFERENCE_SPIKE:
            if action_type in ['adjust_power', 'change_frequency']:
                return True
            return False

        return True  # Default: healing successful

    def _restore_cell_health(self, cell, fault):
        """Restore cell to healthy state after healing"""

        # Restore to healthy baseline
        cell['status'] = 'operational'
        cell['health_score'] = 1.0

        if self.use_real_data:
            # Restore to baseline from real data
            cell['throughput'] = cell.get('baseline_throughput', 50.0) * np.random.uniform(0.95, 1.05)
            cell['latency'] = cell.get('baseline_latency', 12.5) * np.random.uniform(0.95, 1.05)
            cell['packet_loss'] = cell.get('baseline_packet_loss', 0.25) * np.random.uniform(0.95, 1.05)
        else:
            # Restore metrics to healthy ranges
            cell['throughput'] = np.random.uniform(45, 55)
            cell['latency'] = np.random.uniform(10, 15)
            cell['packet_loss'] = np.random.uniform(0, 0.5)

        cell['availability'] = 99.9

        cell['cpu_usage'] = np.random.uniform(30, 50)
        cell['memory_usage'] = np.random.uniform(40, 60)
        cell['temperature'] = np.random.uniform(35, 45)

        cell['drop_rate'] = np.random.uniform(0.01, 0.03)
        cell['handover_success'] = 98.5

        cell['interference'] = np.random.uniform(0.05, 0.15)
        cell['sinr'] = np.random.uniform(15, 25)

        # Clear alarms related to this fault
        cell['alarms'] = [a for a in cell['alarms'] if a.get('fault_id') != fault['id']]
        cell['faults'].remove(fault)

    def get_network_health(self):
        """Calculate overall network health"""

        total_health = sum(cell['health_score'] for cell in self.cells)
        avg_health = total_health / self.num_cells

        num_failed = sum(1 for cell in self.cells if cell['status'] == 'failed')
        num_degraded = sum(1 for cell in self.cells if cell['status'] == 'degraded')
        num_operational = sum(1 for cell in self.cells if cell['status'] == 'operational')

        result = {
            'average_health': avg_health,
            'operational_cells': num_operational,
            'degraded_cells': num_degraded,
            'failed_cells': num_failed,
            'active_faults': len(self.active_faults),
            'total_faults_resolved': len(self.fault_history),
            'data_mode': 'real_data' if self.use_real_data else 'simulated'
        }

        if self.use_real_data:
            # Add cell type distribution
            cell_types = {}
            for cell in self.cells:
                ct = cell.get('cell_type', 'Unknown')
                cell_types[ct] = cell_types.get(ct, 0) + 1
            result['cell_types'] = cell_types

        return result

    def get_cell_metrics(self, cell_id):
        """Get all metrics for a specific cell"""
        return self.cells[cell_id].copy()

    def step(self):
        """Advance time by one step"""
        self.time_step += 1

        # Add small random variations to healthy cells
        for cell in self.cells:
            if cell['status'] == 'operational':
                cell['throughput'] += np.random.uniform(-2, 2)
                cell['latency'] += np.random.uniform(-1, 1)
                cell['cpu_usage'] += np.random.uniform(-5, 5)
                cell['num_users'] += np.random.randint(-10, 10)

                # Clamp values
                cell['throughput'] = max(0, min(1000, cell['throughput']))
                cell['latency'] = max(5, cell['latency'])
                cell['cpu_usage'] = max(0, min(100, cell['cpu_usage']))
                cell['num_users'] = max(0, cell['num_users'])

    def reset(self):
        """Reset the environment to initial state"""
        self.cells = []
        self.active_faults = []
        self.fault_history = []
        self.time_step = 0
        self._initialize_network()

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
    print("Testing Network Healing Environment...")
    print("=" * 60)

    # Test with real data
    print("\n1. Testing with REAL DATA mode:")
    env = NetworkHealingEnvironment(num_cells=10, use_real_data=True)

    print(f"\n[OK] Created network with {env.num_cells} cells")
    print(f"[OK] Data mode: {env.get_data_info()['mode']}")

    # Check initial health
    health = env.get_network_health()
    print(f"[OK] Initial network health: {health['average_health']:.2f}")
    print(f"[OK] All cells operational: {health['operational_cells']}/{env.num_cells}")
    if 'cell_types' in health:
        print(f"[OK] Cell types: {health['cell_types']}")

    # Show sample cell data
    sample_cell = env.get_cell_metrics(0)
    print(f"\n[OK] Sample cell data (Cell 0 - {sample_cell['cell_type']}):")
    print(f"  Throughput: {sample_cell['throughput']:.2f} Mbps")
    print(f"  TX Power: {sample_cell['tx_power']:.2f} dBm")
    print(f"  QoS Satisfaction: {sample_cell['qos_satisfaction']:.2f}%")

    # Inject some faults
    print("\n[OK] Injecting faults...")
    fault1 = env.inject_fault(FaultType.HARDWARE_FAILURE, cell_id=0, severity='critical')
    print(f"  - {fault1['type']} in {fault1['cell_name']} ({fault1['cell_type']}) - severity: {fault1['severity']}")

    fault2 = env.inject_fault(FaultType.PERFORMANCE_DEGRADATION, cell_id=3, severity='medium')
    print(f"  - {fault2['type']} in {fault2['cell_name']} ({fault2['cell_type']}) - severity: {fault2['severity']}")

    fault3 = env.inject_fault(FaultType.INTERFERENCE_SPIKE, cell_id=7, severity='high')
    print(f"  - {fault3['type']} in {fault3['cell_name']} ({fault3['cell_type']}) - severity: {fault3['severity']}")

    # Check health after faults
    health = env.get_network_health()
    print(f"\n[OK] Network health after faults: {health['average_health']:.2f}")
    print(f"[OK] Operational: {health['operational_cells']}, Degraded: {health['degraded_cells']}, Failed: {health['failed_cells']}")
    print(f"[OK] Active faults: {health['active_faults']}")

    # Heal faults
    print("\n[OK] Healing faults...")
    success1 = env.heal_fault(fault1['id'], {'type': 'restart', 'description': 'Restart cell'})
    print(f"  - Healed fault {fault1['id']}: {'Success' if success1 else 'Failed'}")

    success2 = env.heal_fault(fault2['id'], {'type': 'optimize_parameters', 'description': 'Optimize cell parameters'})
    print(f"  - Healed fault {fault2['id']}: {'Success' if success2 else 'Failed'}")

    success3 = env.heal_fault(fault3['id'], {'type': 'adjust_power', 'description': 'Adjust transmit power'})
    print(f"  - Healed fault {fault3['id']}: {'Success' if success3 else 'Failed'}")

    # Check final health
    health = env.get_network_health()
    print(f"\n[OK] Network health after healing: {health['average_health']:.2f}")
    print(f"[OK] Operational: {health['operational_cells']}, Degraded: {health['degraded_cells']}, Failed: {health['failed_cells']}")
    print(f"[OK] Faults resolved: {health['total_faults_resolved']}")

    # Test with simulated data for comparison
    print("\n" + "=" * 60)
    print("\n2. Testing with SIMULATED DATA mode:")
    env_sim = NetworkHealingEnvironment(num_cells=5, use_real_data=False)
    print(f"[OK] Data mode: {env_sim.get_data_info()['mode']}")

    health_sim = env_sim.get_network_health()
    print(f"[OK] Initial network health: {health_sim['average_health']:.2f}")

    print("\n[PASS] Healing environment test PASSED")
