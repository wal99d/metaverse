import unittest
import sys
import os
from colorama import init, Fore, Style

def run_test_suite():
    """Run all test suites and return results."""
    # Initialize colorama for Windows color support
    init()

    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print(f"{Fore.CYAN}Test Summary:{Style.RESET_ALL}")
    print(f"Ran {result.testsRun} tests")
    print(f"{Fore.GREEN}Passed: {result.testsRun - len(result.failures) - len(result.errors)}{Style.RESET_ALL}")
    if result.failures:
        print(f"{Fore.RED}Failed: {len(result.failures)}{Style.RESET_ALL}")
    if result.errors:
        print(f"{Fore.RED}Errors: {len(result.errors)}{Style.RESET_ALL}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_test_suite()
    sys.exit(0 if success else 1)