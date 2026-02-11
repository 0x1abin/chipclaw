#!/usr/bin/env python3
"""
ChipClaw Test Runner
Run all tests in the tests directory
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests import run_tests


def discover_and_run_tests():
    """Discover and run all test modules"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all test modules
    test_modules = []
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                # Convert file path to module path
                rel_path = os.path.relpath(os.path.join(root, file), test_dir)
                module_path = rel_path[:-3].replace(os.sep, '.')
                module_name = f"tests.{module_path}"
                test_modules.append(module_name)
    
    if not test_modules:
        print("No test modules found!")
        return False
    
    print(f"Discovered {len(test_modules)} test module(s)")
    print(f"Test modules: {', '.join(test_modules)}\n")
    
    all_passed = True
    for module_name in sorted(test_modules):
        try:
            module = __import__(module_name, fromlist=[''])
            passed = run_tests(module)
            if not passed:
                all_passed = False
        except ImportError as e:
            print(f"Failed to import {module_name}: {e}")
            all_passed = False
        except Exception as e:
            print(f"Error running tests in {module_name}: {e}")
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    success = discover_and_run_tests()
    sys.exit(0 if success else 1)
