"""
Master test runner for all API test suites
Runs tests for Adzuna, Arbeitnow, and Eurostat APIs
"""
import sys
import importlib.util

def run_test_module(module_path, module_name):
    """Dynamically import and run a test module"""
    print(f"\n{'=' * 70}")
    print(f"Running {module_name}")
    print('=' * 70)
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True
    except Exception as e:
        print(f"❌ Failed to run {module_name}: {e}")
        return False

def main():
    """Run all test modules"""
    print("=" * 70)
    print("EU JOB MARKET PULSE - COMPLETE API TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("test_adzuna.py", "Adzuna API Tests"),
        ("test_arbeitnow.py", "Arbeitnow API Tests"),
        ("test_eurostat.py", "Eurostat API Tests"),
    ]
    
    results = {}
    for test_file, test_name in tests:
        success = run_test_module(test_file, test_name)
        results[test_name] = success
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✓ COMPLETED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} test suites completed successfully")
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
