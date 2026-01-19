"""
Quick Test Script for Network Healing POC
Run this to verify everything works before launching web demo
"""

import sys
import os

# Simple ASCII markers for Windows compatibility
CHECK = "[OK]"
CROSS = "[X]"

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from healing_environment import NetworkHealingEnvironment, FaultType
from fault_detector import FaultDetector, FaultDiagnosisEngine
from healing_agent import NetworkHealingAgent, HealingComparison

def test_healing_environment():
    """Test healing environment with fault injection"""
    print("\n" + "="*60)
    print("TEST 1: Healing Environment")
    print("="*60)

    env = NetworkHealingEnvironment(num_cells=10)
    print(f"[OK] Created environment with {env.num_cells} cells")

    # Check initial health
    health = env.get_network_health()
    print(f"[OK] Initial network health: {health['average_health']:.2f}")
    print(f"[OK] All cells operational: {health['operational_cells']}/{env.num_cells}")

    # Inject faults
    fault1 = env.inject_fault(FaultType.HARDWARE_FAILURE, cell_id=0, severity='critical')
    fault2 = env.inject_fault(FaultType.PERFORMANCE_DEGRADATION, cell_id=3, severity='medium')
    print(f"[OK] Injected 2 faults")

    # Check health after faults
    health = env.get_network_health()
    print(f"[OK] Network health after faults: {health['average_health']:.2f}")
    print(f"[OK] Active faults: {health['active_faults']}")

    # Heal faults
    success1 = env.heal_fault(fault1['id'], {'type': 'restart', 'description': 'Restart cell'})
    success2 = env.heal_fault(fault2['id'], {'type': 'optimize_parameters', 'description': 'Optimize'})
    print(f"[OK] Healed faults: {int(success1) + int(success2)}/2 successful")

    # Check final health
    health = env.get_network_health()
    print(f"[OK] Final health: {health['average_health']:.2f}")

    print("\n[PASS] Environment test PASSED")
    return True

def test_fault_detection():
    """Test fault detection system"""
    print("\n" + "="*60)
    print("TEST 2: Fault Detection")
    print("="*60)

    # Create environment with faults
    env = NetworkHealingEnvironment(num_cells=10)
    env.inject_fault(FaultType.HARDWARE_FAILURE, cell_id=2, severity='critical')
    env.inject_fault(FaultType.CAPACITY_OVERLOAD, cell_id=5, severity='high')
    env.inject_fault(FaultType.INTERFERENCE_SPIKE, cell_id=8, severity='medium')

    print("[OK] Injected 3 faults")

    # Test detector
    detector = FaultDetector(env)
    detected = detector.detect_faults()

    print(f"[OK] Detector found {len(detected)} faults")

    if len(detected) > 0:
        print(f"[OK] Detection working correctly")
    else:
        print(f"[X] Detection failed - no faults found")
        return False

    print("\n[PASS] Fault detection test PASSED")
    return True

def test_diagnosis_engine():
    """Test diagnosis engine"""
    print("\n" + "="*60)
    print("TEST 3: Diagnosis Engine")
    print("="*60)

    # Create environment with faults
    env = NetworkHealingEnvironment(num_cells=10)
    env.inject_fault(FaultType.HARDWARE_FAILURE, cell_id=2, severity='critical')

    # Detect faults
    detector = FaultDetector(env)
    detected = detector.detect_faults()

    print(f"[OK] Detected {len(detected)} faults")

    # Test diagnosis
    diagnosis_engine = FaultDiagnosisEngine()
    diagnosis = diagnosis_engine.diagnose(detected[0])

    print(f"[OK] Diagnosis completed")
    print(f"  - Root cause: {diagnosis['root_cause']}")
    print(f"  - Confidence: {diagnosis['confidence']:.0%}")
    print(f"  - Actions: {len(diagnosis['recommended_actions'])}")

    if diagnosis['recommended_actions']:
        print(f"[OK] Recommendations generated")
    else:
        print(f"[X] No recommendations generated")
        return False

    print("\n[PASS] Diagnosis engine test PASSED")
    return True

def test_healing_agent():
    """Test autonomous healing agent"""
    print("\n" + "="*60)
    print("TEST 4: Autonomous Healing Agent")
    print("="*60)

    # Create environment
    env = NetworkHealingEnvironment(num_cells=10)

    # Inject faults
    env.inject_fault(FaultType.HARDWARE_FAILURE, cell_id=2, severity='critical')
    env.inject_fault(FaultType.PERFORMANCE_DEGRADATION, cell_id=5, severity='high')
    env.inject_fault(FaultType.CAPACITY_OVERLOAD, cell_id=8, severity='medium')

    print("[OK] Injected 3 faults")

    # Create healing agent
    detector = FaultDetector(env)
    diagnosis_engine = FaultDiagnosisEngine()
    agent = NetworkHealingAgent(env, detector, diagnosis_engine)

    print("[OK] Created healing agent")

    # Check initial health
    initial_health = env.get_network_health()
    print(f"[OK] Initial health: {initial_health['average_health']:.2f}")

    # Run one healing cycle
    result = agent.run_healing_cycle()

    print(f"[OK] Healing cycle completed")
    print(f"  - Faults detected: {result['faults_detected']}")
    print(f"  - Healing attempts: {result['healing_attempts']}")
    print(f"  - Successful heals: {result['successful_heals']}")

    # Check final health
    final_health = env.get_network_health()
    print(f"[OK] Final health: {final_health['average_health']:.2f}")

    if final_health['average_health'] > initial_health['average_health']:
        print(f"[OK] Network health improved")
    else:
        print(f"[X] Network health did not improve")
        return False

    print("\n[PASS] Healing agent test PASSED")
    return True

def test_comparison():
    """Test full comparison (this takes ~15 seconds)"""
    print("\n" + "="*60)
    print("TEST 5: Healing Comparison (This takes ~15 seconds)")
    print("="*60)

    comparison = HealingComparison.run_comparison(num_cells=10, num_faults=5, num_cycles=10)

    print("\n[OK] Comparison completed")

    print("\nWITHOUT Autonomous Healing:")
    print(f"  - Final health: {comparison['without_healing']['final_health']:.2f}")
    print(f"  - Active faults: {comparison['without_healing']['active_faults']}")
    print(f"  - Failed cells: {comparison['without_healing']['failed_cells']}")

    print("\nWITH Autonomous Healing:")
    print(f"  - Final health: {comparison['with_healing']['final_health']:.2f}")
    print(f"  - Active faults: {comparison['with_healing']['active_faults']}")
    print(f"  - Failed cells: {comparison['with_healing']['failed_cells']}")
    print(f"  - Successful heals: {comparison['with_healing']['total_heals']}")
    print(f"  - Success rate: {comparison['with_healing']['success_rate']:.1f}%")

    print("\nIMPROVEMENT:")
    print(f"  - Health: {comparison['improvement']['health']:+.1f}%")
    print(f"  - Faults reduced: {comparison['improvement']['active_faults_reduced']}")

    if comparison['with_healing']['final_health'] > comparison['without_healing']['final_health']:
        print(f"[OK] Healing agent shows clear improvement")
    else:
        print(f"[X] Healing agent did not improve outcomes")
        return False

    print("\n[PASS] Comparison test PASSED")
    return True

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("NETWORK HEALING POC - AUTOMATED TEST SUITE")
    print("="*60)

    tests = [
        ("Healing Environment", test_healing_environment),
        ("Fault Detection", test_fault_detection),
        ("Diagnosis Engine", test_diagnosis_engine),
        ("Healing Agent", test_healing_agent),
        ("Full Comparison", test_comparison)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[FAIL] {test_name} test FAILED: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS] PASSED" if result else "[FAIL] FAILED"
        print(f"{test_name}: {status}")

    print("\n" + "="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED! Healing POC is ready to demo!")
        print("\nNext step: Run the web demo:")
        print("  streamlit run healing_demo.py")
    else:
        print("\n[WARNING] Some tests failed. Please fix issues before demo.")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
