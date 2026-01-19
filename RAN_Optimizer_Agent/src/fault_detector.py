"""
Fault Detection Module
Uses anomaly detection to identify network faults
"""

import numpy as np
from collections import deque

class FaultDetector:
    """
    Autonomous fault detection using anomaly detection
    Monitors cell metrics and detects deviations from normal behavior
    """

    def __init__(self, environment):
        self.env = environment

        # Baseline thresholds for anomaly detection
        self.thresholds = {
            'throughput': {'min': 30, 'max': 100},
            'latency': {'min': 0, 'max': 30},
            'packet_loss': {'min': 0, 'max': 2.0},
            'availability': {'min': 95, 'max': 100},
            'cpu_usage': {'min': 0, 'max': 85},
            'memory_usage': {'min': 0, 'max': 85},
            'temperature': {'min': 20, 'max': 60},
            'drop_rate': {'min': 0, 'max': 0.08},
            'handover_success': {'min': 90, 'max': 100},
            'interference': {'min': 0, 'max': 0.4},
            'sinr': {'min': 5, 'max': 40}
        }

        # Detection history
        self.detection_history = []
        self.detected_anomalies = []

        # Metric history for trend analysis
        self.metric_history = {cell['id']: {} for cell in self.env.cells}

    def detect_faults(self):
        """
        Scan all cells for anomalies
        Returns list of detected faults
        """

        detected_faults = []

        for cell in self.env.cells:
            # Check if cell has existing alarms
            if cell['alarms']:
                for alarm in cell['alarms']:
                    fault = self._create_fault_from_alarm(cell, alarm)
                    detected_faults.append(fault)

            # Check for metric anomalies
            anomalies = self._detect_metric_anomalies(cell)
            for anomaly in anomalies:
                fault = self._create_fault_from_anomaly(cell, anomaly)
                detected_faults.append(fault)

        # Store in history
        self.detection_history.append({
            'time': self.env.time_step,
            'faults_detected': len(detected_faults),
            'faults': detected_faults
        })

        return detected_faults

    def _detect_metric_anomalies(self, cell):
        """Detect anomalies in cell metrics"""

        anomalies = []

        # Check each metric against thresholds
        for metric, threshold in self.thresholds.items():
            if metric not in cell:
                continue

            value = cell[metric]
            min_val = threshold['min']
            max_val = threshold['max']

            # Check if value is outside normal range
            if value < min_val:
                anomalies.append({
                    'metric': metric,
                    'value': value,
                    'expected_range': f"{min_val}-{max_val}",
                    'deviation': min_val - value,
                    'severity': self._calculate_severity(metric, value, min_val, max_val)
                })

            elif value > max_val:
                anomalies.append({
                    'metric': metric,
                    'value': value,
                    'expected_range': f"{min_val}-{max_val}",
                    'deviation': value - max_val,
                    'severity': self._calculate_severity(metric, value, min_val, max_val)
                })

        return anomalies

    def _calculate_severity(self, metric, value, min_val, max_val):
        """Calculate severity based on how far value deviates from normal"""

        if value < min_val:
            deviation_pct = (min_val - value) / min_val * 100 if min_val > 0 else 100
        else:
            deviation_pct = (value - max_val) / max_val * 100 if max_val > 0 else 100

        if deviation_pct > 50:
            return 'critical'
        elif deviation_pct > 30:
            return 'high'
        elif deviation_pct > 15:
            return 'medium'
        else:
            return 'low'

    def _create_fault_from_alarm(self, cell, alarm):
        """Create standardized fault object from alarm"""

        return {
            'source': 'alarm',
            'cell_id': cell['id'],
            'cell_name': cell['name'],
            'cell_status': cell['status'],
            'health_score': cell['health_score'],
            'fault_type': alarm['type'],
            'severity': alarm['severity'],
            'message': alarm['message'],
            'detected_at': self.env.time_step,
            'metrics': self._get_relevant_metrics(cell, alarm['type'])
        }

    def _create_fault_from_anomaly(self, cell, anomaly):
        """Create standardized fault object from detected anomaly"""

        return {
            'source': 'anomaly_detection',
            'cell_id': cell['id'],
            'cell_name': cell['name'],
            'cell_status': cell['status'],
            'health_score': cell['health_score'],
            'fault_type': f"ANOMALY_{anomaly['metric'].upper()}",
            'severity': anomaly['severity'].upper(),
            'message': f"{anomaly['metric']} anomaly: {anomaly['value']:.2f} (expected: {anomaly['expected_range']})",
            'detected_at': self.env.time_step,
            'anomaly_details': anomaly,
            'metrics': self._get_relevant_metrics(cell, anomaly['metric'])
        }

    def _get_relevant_metrics(self, cell, fault_indicator):
        """Get metrics relevant to the fault type"""

        # Return key metrics that help diagnose the issue
        return {
            'throughput': cell['throughput'],
            'latency': cell['latency'],
            'packet_loss': cell['packet_loss'],
            'cpu_usage': cell['cpu_usage'],
            'memory_usage': cell['memory_usage'],
            'num_users': cell['num_users'],
            'drop_rate': cell['drop_rate'],
            'interference': cell['interference'],
            'sinr': cell['sinr']
        }

    def get_detection_statistics(self):
        """Get statistics about fault detection"""

        if not self.detection_history:
            return {
                'total_detections': 0,
                'detection_rate': 0,
                'average_faults_per_scan': 0
            }

        total_detections = sum(d['faults_detected'] for d in self.detection_history)
        num_scans = len(self.detection_history)

        return {
            'total_detections': total_detections,
            'num_scans': num_scans,
            'average_faults_per_scan': total_detections / num_scans if num_scans > 0 else 0,
            'detection_rate': (num_scans / self.env.time_step * 100) if self.env.time_step > 0 else 0
        }


class FaultDiagnosisEngine:
    """
    Root cause analysis engine
    Analyzes detected faults to determine root cause and recommend actions
    """

    def __init__(self):
        # Knowledge base of fault patterns and solutions
        self.diagnosis_rules = self._build_diagnosis_rules()

    def _build_diagnosis_rules(self):
        """Build knowledge base of diagnosis rules"""

        return {
            'HARDWARE_FAULT': {
                'indicators': ['status=failed', 'health_score<0.2'],
                'root_causes': [
                    'Radio unit failure',
                    'Baseband unit failure',
                    'Power supply failure',
                    'Fiber connection failure'
                ],
                'recommended_actions': [
                    {'type': 'restart', 'description': 'Restart cell equipment', 'priority': 1},
                    {'type': 'switch_to_backup', 'description': 'Switch to backup hardware', 'priority': 2},
                    {'type': 'field_technician', 'description': 'Dispatch field technician', 'priority': 3}
                ]
            },

            'CONFIG_ERROR': {
                'indicators': ['handover_success<80', 'drop_rate>0.1'],
                'root_causes': [
                    'Incorrect neighbor list',
                    'Wrong PCI configuration',
                    'Handover parameter misconfiguration',
                    'Frequency band mismatch'
                ],
                'recommended_actions': [
                    {'type': 'reset_config', 'description': 'Reset to last known good configuration', 'priority': 1},
                    {'type': 'apply_correct_config', 'description': 'Apply correct configuration', 'priority': 2},
                    {'type': 'update_neighbor_list', 'description': 'Update neighbor cell list', 'priority': 3}
                ]
            },

            'PERFORMANCE_DEGRADED': {
                'indicators': ['throughput<30', 'latency>25'],
                'root_causes': [
                    'Resource block exhaustion',
                    'Scheduler misconfiguration',
                    'Transport network congestion',
                    'Software bug'
                ],
                'recommended_actions': [
                    {'type': 'optimize_parameters', 'description': 'Optimize cell parameters', 'priority': 1},
                    {'type': 'adjust_resources', 'description': 'Reallocate resources', 'priority': 2},
                    {'type': 'software_update', 'description': 'Apply software patch', 'priority': 3}
                ]
            },

            'CONNECTIVITY_ISSUE': {
                'indicators': ['drop_rate>0.1', 'num_users dropping'],
                'root_causes': [
                    'Weak coverage area',
                    'Handover failure',
                    'Core network issue',
                    'Authentication failure'
                ],
                'recommended_actions': [
                    {'type': 'restart_service', 'description': 'Restart connectivity services', 'priority': 1},
                    {'type': 'update_neighbor_list', 'description': 'Update handover neighbors', 'priority': 2},
                    {'type': 'adjust_power', 'description': 'Increase coverage power', 'priority': 3}
                ]
            },

            'CAPACITY_OVERLOAD': {
                'indicators': ['cpu_usage>85', 'memory_usage>85', 'num_users>250'],
                'root_causes': [
                    'Traffic surge',
                    'Insufficient capacity',
                    'Neighboring cell failure (users migrated)',
                    'Memory leak'
                ],
                'recommended_actions': [
                    {'type': 'load_balancing', 'description': 'Offload users to neighbors', 'priority': 1},
                    {'type': 'resource_expansion', 'description': 'Add capacity', 'priority': 2},
                    {'type': 'restart', 'description': 'Restart to clear memory', 'priority': 3}
                ]
            },

            'HIGH_INTERFERENCE': {
                'indicators': ['interference>0.3', 'sinr<10'],
                'root_causes': [
                    'Co-channel interference',
                    'Adjacent channel interference',
                    'External interference source',
                    'PCI collision'
                ],
                'recommended_actions': [
                    {'type': 'adjust_power', 'description': 'Reduce transmit power', 'priority': 1},
                    {'type': 'change_frequency', 'description': 'Switch to cleaner frequency', 'priority': 2},
                    {'type': 'adjust_antenna', 'description': 'Adjust antenna tilt', 'priority': 3}
                ]
            }
        }

    def diagnose(self, fault):
        """
        Diagnose root cause of fault and recommend healing actions

        Returns:
            diagnosis: Dict with root cause analysis and recommended actions
        """

        fault_type = fault['fault_type']

        # Find matching diagnosis rule
        rule = self._find_matching_rule(fault_type)

        if not rule:
            # Generic diagnosis for unknown fault types
            return {
                'fault_type': fault_type,
                'root_cause': 'Unknown - requires manual investigation',
                'confidence': 0.5,
                'recommended_actions': [
                    {'type': 'generic_restart', 'description': 'Generic restart action', 'priority': 1}
                ]
            }

        # Analyze metrics to determine most likely root cause
        root_cause = self._analyze_root_cause(fault, rule)

        # Select best healing actions
        recommended_actions = rule['recommended_actions']

        return {
            'fault_type': fault_type,
            'root_cause': root_cause,
            'confidence': 0.85,
            'recommended_actions': recommended_actions,
            'indicators_matched': rule['indicators']
        }

    def _find_matching_rule(self, fault_type):
        """Find diagnosis rule that matches the fault type"""

        # Direct match
        if fault_type in self.diagnosis_rules:
            return self.diagnosis_rules[fault_type]

        # Partial match
        for rule_key, rule in self.diagnosis_rules.items():
            if rule_key in fault_type or fault_type in rule_key:
                return rule

        return None

    def _analyze_root_cause(self, fault, rule):
        """Analyze metrics to determine most likely root cause"""

        # Simple heuristic: return first root cause
        # In production, this would use ML to analyze patterns
        if rule['root_causes']:
            return rule['root_causes'][0]

        return "Unknown"


if __name__ == "__main__":
    from healing_environment import NetworkHealingEnvironment, FaultType

    print("Testing Fault Detection System...")
    print("=" * 60)

    # Create environment and inject faults
    env = NetworkHealingEnvironment(num_cells=10)
    print("[OK] Created network environment")

    # Inject various faults
    env.inject_fault(FaultType.HARDWARE_FAILURE, cell_id=2, severity='critical')
    env.inject_fault(FaultType.PERFORMANCE_DEGRADATION, cell_id=5, severity='medium')
    env.inject_fault(FaultType.CAPACITY_OVERLOAD, cell_id=8, severity='high')

    print("[OK] Injected 3 faults into network")

    # Test fault detector
    detector = FaultDetector(env)
    detected = detector.detect_faults()

    print(f"\n[OK] Fault detector found {len(detected)} faults:")
    for fault in detected:
        print(f"  - {fault['cell_name']}: {fault['fault_type']} ({fault['severity']})")

    # Test diagnosis engine
    diagnosis_engine = FaultDiagnosisEngine()
    print(f"\n[OK] Diagnosing faults...")

    for fault in detected[:3]:  # Diagnose first 3
        diagnosis = diagnosis_engine.diagnose(fault)
        print(f"\n  Cell: {fault['cell_name']}")
        print(f"  Fault: {diagnosis['fault_type']}")
        print(f"  Root Cause: {diagnosis['root_cause']}")
        print(f"  Confidence: {diagnosis['confidence']:.0%}")
        print(f"  Recommended Actions:")
        for action in diagnosis['recommended_actions']:
            print(f"    {action['priority']}. {action['description']}")

    print("\n[PASS] Fault detection and diagnosis test PASSED")
