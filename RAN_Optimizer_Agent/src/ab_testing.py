"""
A/B Testing System to validate changes before full deployment
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict
import json
from datetime import datetime


@dataclass
class TestResult:
    """A/B test result"""
    test_id: str
    group_a_metrics: Dict
    group_b_metrics: Dict
    improvement: Dict
    is_significant: bool
    confidence: float
    recommendation: str
    timestamp: str


class ABTestingSystem:
    """
    A/B Testing System

    Splits cells into two groups:
    - Group A: Apply new changes
    - Group B: No change (control)

    Then measures the difference and decides if change is successful
    """

    def __init__(self, min_sample_size=10, confidence_threshold=0.05):
        """
        Args:
            min_sample_size: Minimum sample size
            confidence_threshold: Confidence threshold (p-value)
        """
        self.min_sample_size = min_sample_size
        self.confidence_threshold = confidence_threshold
        self.test_history = []

    def create_test_groups(self, cells, test_ratio=0.5):
        """
        Split cells into two groups

        Args:
            cells: List of cells
            test_ratio: Ratio for Group A (default 50%)

        Returns:
            group_a, group_b: Two lists of cells
        """

        # Random shuffle
        shuffled_cells = cells.copy()
        np.random.shuffle(shuffled_cells)

        # Split
        split_idx = int(len(shuffled_cells) * test_ratio)
        group_a = shuffled_cells[:split_idx]
        group_b = shuffled_cells[split_idx:]

        print(f"Created test groups:")
        print(f"  Group A (test): {len(group_a)} cells")
        print(f"  Group B (control): {len(group_b)} cells")

        return group_a, group_b

    def run_test(self, env, agent, num_steps=50, test_name="test"):
        """
        Run A/B test

        Args:
            env: RAN environment
            agent: Intelligent agent
            num_steps: Number of steps for testing
            test_name: Test name

        Returns:
            TestResult: Test result
        """

        print(f"\nStarting A/B test: {test_name}")
        print("="*60)

        # Split cells
        group_a, group_b = self.create_test_groups(env.cells)

        # Save original settings
        original_settings_a = [self._save_cell_settings(c) for c in group_a]
        original_settings_b = [self._save_cell_settings(c) for c in group_b]

        # Measure initial performance
        initial_metrics_a = self._measure_group_performance(group_a, env)
        initial_metrics_b = self._measure_group_performance(group_b, env)

        print("\nInitial performance:")
        print(f"  Group A: {initial_metrics_a}")
        print(f"  Group B: {initial_metrics_b}")

        # Apply changes to Group A only
        print(f"\nApplying optimizations to Group A...")

        state = env.reset()
        for step in range(num_steps):
            # Agent optimizes only Group A cells
            if env.current_cell_idx < len(group_a):
                action = agent.act(state, training=False)
                state, reward, done, info = env.step(action)
            else:
                # Group B: no change
                state, reward, done, info = env.step(13)  # Action "no change"

            if done:
                state = env.reset()

        # Measure performance after changes
        final_metrics_a = self._measure_group_performance(group_a, env)
        final_metrics_b = self._measure_group_performance(group_b, env)

        print("\nFinal performance:")
        print(f"  Group A: {final_metrics_a}")
        print(f"  Group B: {final_metrics_b}")

        # Analyze results
        result = self._analyze_results(
            test_name,
            initial_metrics_a, final_metrics_a,
            initial_metrics_b, final_metrics_b
        )

        # Save result
        self.test_history.append(result)

        # Display result
        self._print_result(result)

        return result

    def _save_cell_settings(self, cell):
        """Save cell settings"""
        return {
            'tx_power': cell['tx_power'],
            'antenna_tilt': cell['antenna_tilt'],
            'handover_threshold': cell['handover_threshold']
        }

    def _restore_cell_settings(self, cell, settings):
        """Restore cell settings"""
        cell['tx_power'] = settings['tx_power']
        cell['antenna_tilt'] = settings['antenna_tilt']
        cell['handover_threshold'] = settings['handover_threshold']

    def _measure_group_performance(self, cells, env):
        """Measure performance of a group of cells"""
        metrics = {
            'avg_throughput': np.mean([c['throughput'] for c in cells]),
            'avg_drop_rate': np.mean([c['drop_rate'] for c in cells]),
            'total_power': np.sum([c['power_consumption'] for c in cells]),
            'avg_satisfaction': np.mean([env._calculate_satisfaction(c) for c in cells])
        }
        return metrics

    def _analyze_results(self, test_name, initial_a, final_a, initial_b, final_b):
        """
        Analyze test results

        Calculates:
        - Improvement in Group A
        - Improvement in Group B (should be small)
        - Difference between them
        - Is the difference statistically significant?
        """

        # Calculate improvement
        improvement_a = {
            'throughput': ((final_a['avg_throughput'] - initial_a['avg_throughput']) /
                          initial_a['avg_throughput'] * 100),
            'drop_rate': ((initial_a['avg_drop_rate'] - final_a['avg_drop_rate']) /
                         initial_a['avg_drop_rate'] * 100),
            'satisfaction': ((final_a['avg_satisfaction'] - initial_a['avg_satisfaction']) /
                           initial_a['avg_satisfaction'] * 100),
            'power': ((initial_a['total_power'] - final_a['total_power']) /
                     initial_a['total_power'] * 100)
        }

        improvement_b = {
            'throughput': ((final_b['avg_throughput'] - initial_b['avg_throughput']) /
                          initial_b['avg_throughput'] * 100),
            'drop_rate': ((initial_b['avg_drop_rate'] - final_b['avg_drop_rate']) /
                         initial_b['avg_drop_rate'] * 100),
            'satisfaction': ((final_b['avg_satisfaction'] - initial_b['avg_satisfaction']) /
                           initial_b['avg_satisfaction'] * 100),
            'power': ((initial_b['total_power'] - final_b['total_power']) /
                     initial_b['total_power'] * 100)
        }

        # Calculate relative improvement
        relative_improvement = {
            key: improvement_a[key] - improvement_b[key]
            for key in improvement_a.keys()
        }

        # Test significance (simplified)
        # In practice, use t-test or z-test
        avg_relative_improvement = np.mean(list(relative_improvement.values()))
        is_significant = abs(avg_relative_improvement) > 5  # More than 5% improvement

        confidence = min(abs(avg_relative_improvement) / 10 * 100, 99)  # Simulated

        # Recommendation
        if is_significant and avg_relative_improvement > 0:
            recommendation = "EXCELLENT! Apply changes to entire network"
        elif avg_relative_improvement > 0:
            recommendation = "WARNING: Slight improvement, apply with caution"
        else:
            recommendation = "FAIL: Do not apply - changes are not beneficial"

        return TestResult(
            test_id=f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            group_a_metrics=final_a,
            group_b_metrics=final_b,
            improvement=relative_improvement,
            is_significant=is_significant,
            confidence=confidence,
            recommendation=recommendation,
            timestamp=datetime.now().isoformat()
        )

    def _print_result(self, result: TestResult):
        """Display test result"""
        print("\n" + "="*60)
        print("A/B Test Result")
        print("="*60)
        print(f"Test ID: {result.test_id}")
        print(f"Time: {result.timestamp}")
        print()

        print("Relative improvement (A vs B):")
        for key, value in result.improvement.items():
            symbol = "UP" if value > 0 else "DOWN"
            print(f"  [{symbol}] {key}: {value:+.2f}%")

        print()
        print(f"Statistically significant: {'YES' if result.is_significant else 'NO'}")
        print(f"Confidence level: {result.confidence:.1f}%")
        print()
        print(f"Recommendation: {result.recommendation}")
        print("="*60)

    def get_best_test(self):
        """Get best test result"""
        if not self.test_history:
            return None

        # Sort by average improvement
        sorted_tests = sorted(
            self.test_history,
            key=lambda t: np.mean(list(t.improvement.values())),
            reverse=True
        )

        return sorted_tests[0]

    def export_results(self, filepath):
        """Export results to JSON file"""
        results = []
        for test in self.test_history:
            # Convert numpy types to native Python types for JSON serialization
            results.append({
                'test_id': test.test_id,
                'group_a_metrics': {k: float(v) for k, v in test.group_a_metrics.items()},
                'group_b_metrics': {k: float(v) for k, v in test.group_b_metrics.items()},
                'improvement': {k: float(v) for k, v in test.improvement.items()},
                'is_significant': bool(test.is_significant),
                'confidence': float(test.confidence),
                'recommendation': test.recommendation,
                'timestamp': test.timestamp
            })

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"Results saved to: {filepath}")


if __name__ == "__main__":
    # Test A/B Testing system
    from ran_environment import RANEnvironment
    from agent import RANOptimizationAgent

    print("Testing A/B Testing System...")

    # Create environment
    env = RANEnvironment(num_cells=20)

    # Create agent
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    agent = RANOptimizationAgent(state_size, action_size)

    # Create A/B testing system
    ab_system = ABTestingSystem()

    # Run test
    result = ab_system.run_test(
        env, agent,
        num_steps=30,
        test_name="test_power_optimization"
    )

    print("\nTest complete!")
