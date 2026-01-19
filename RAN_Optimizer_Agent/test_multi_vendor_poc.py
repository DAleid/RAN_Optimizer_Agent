"""
Quick Test Script for Multi-Vendor POC
Run this to verify everything works before launching web demo
"""

import sys
import os

# Simple ASCII checkmarks for Windows compatibility
CHECK = "[OK]"
CROSS = "[X]"

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from multi_vendor_environment import MultiVendorEnvironment
from vendor_ai_simulator import IndependentVendorSimulation, VendorAI
from coordination_agent import MultiVendorCoordinationAgent, CoordinationComparison

def test_environment():
    """Test multi-vendor environment"""
    print("\n" + "="*60)
    print("TEST 1: Multi-Vendor Environment")
    print("="*60)

    env = MultiVendorEnvironment(num_cells=12)

    print(f"[OK] Created environment with {env.num_cells} cells")

    # Check vendor distribution
    for vendor in ['ericsson', 'nokia', 'huawei']:
        cells = env.get_cells_by_vendor(vendor)
        print(f"[OK] {vendor.capitalize()}: {len(cells)} cells")

    # Test cross-vendor neighbors
    neighbors = env.get_cross_vendor_neighbors(0)
    print(f"[OK] Cell 0 has {len(neighbors)} cross-vendor neighbors")

    # Test network stats
    stats = env.get_network_stats()
    print(f"[OK] Network stats calculated: Avg throughput = {stats['avg_throughput']:.2f} Mbps")

    print("\n[PASS] Environment test PASSED")
    return True

def test_vendor_ais():
    """Test vendor AI simulators"""
    print("\n" + "="*60)
    print("TEST 2: Vendor AI Simulators")
    print("="*60)

    env = MultiVendorEnvironment(num_cells=12)

    for vendor in ['ericsson', 'nokia', 'huawei']:
        ai = VendorAI(vendor, env)
        actions = ai.optimize()
        print(f"[OK] {vendor.capitalize()} AI generated {len(actions)} actions")

    # Test independent simulation
    sim = IndependentVendorSimulation(env)
    result = sim.run_one_step()

    print(f"[OK] Independent simulation step completed")
    print(f"  - Actions: {len(result['actions'])}")
    print(f"  - Conflicts detected: {len(result['conflicts'])}")

    print("\n[PASS] Vendor AI test PASSED")
    return True

def test_coordination_agent():
    """Test coordination agent"""
    print("\n" + "="*60)
    print("TEST 3: Coordination Agent")
    print("="*60)

    env = MultiVendorEnvironment(num_cells=12)
    vendor_ais = {
        'ericsson': VendorAI('ericsson', env),
        'nokia': VendorAI('nokia', env),
        'huawei': VendorAI('huawei', env)
    }

    coordinator = MultiVendorCoordinationAgent(env, vendor_ais)

    # Test conflict detection
    conflicts = coordinator.detect_conflicts()
    print(f"[OK] Conflict detection works: {len(conflicts)} conflicts found")

    # Test coordination step
    result = coordinator.coordinate_step()
    print(f"[OK] Coordination step completed")
    print(f"  - Mode: {result['mode']}")
    print(f"  - Conflicts: {len(result['conflicts_detected'])}")

    print("\n[PASS] Coordination agent test PASSED")
    return True

def test_comparison():
    """Test full comparison"""
    print("\n" + "="*60)
    print("TEST 4: Full Comparison (This takes ~10 seconds)")
    print("="*60)

    comparison = CoordinationComparison.run_comparison(num_cells=12, num_steps=5)

    print("\n[OK] Comparison completed")

    print("\nWITHOUT Coordination:")
    stats_without = comparison['without_coordination']['stats']
    print(f"  - Throughput: {stats_without['avg_throughput']:.2f} Mbps")
    print(f"  - Conflicts: {comparison['without_coordination']['conflicts']}")

    print("\nWITH Coordination:")
    stats_with = comparison['with_coordination']['stats']
    print(f"  - Throughput: {stats_with['avg_throughput']:.2f} Mbps")
    print(f"  - Conflicts resolved: {comparison['with_coordination']['conflicts_resolved']}")

    print("\nIMPROVEMENTS:")
    for metric, value in comparison['improvement'].items():
        print(f"  - {metric.capitalize()}: {value:+.1f}%")

    print("\n[PASS] Comparison test PASSED")
    return True

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("MULTI-VENDOR POC - AUTOMATED TEST SUITE")
    print("="*60)

    tests = [
        ("Environment", test_environment),
        ("Vendor AIs", test_vendor_ais),
        ("Coordination Agent", test_coordination_agent),
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
        print("\n[SUCCESS] ALL TESTS PASSED! POC is ready to demo!")
        print("\nNext step: Run the web demo:")
        print("  streamlit run multi_vendor_demo.py")
    else:
        print("\n[WARNING] Some tests failed. Please fix issues before demo.")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
