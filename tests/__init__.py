"""
ChipClaw Test Framework
Minimal testing framework compatible with both MicroPython and CPython
"""


class TestCase:
    """Base test case class"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def assert_equal(self, actual, expected, msg=None):
        """Assert two values are equal"""
        if actual != expected:
            error_msg = msg or f"Expected {expected}, got {actual}"
            self.errors.append(error_msg)
            self.failed += 1
            raise AssertionError(error_msg)
        self.passed += 1
    
    def assert_true(self, value, msg=None):
        """Assert value is True"""
        if not value:
            error_msg = msg or f"Expected True, got {value}"
            self.errors.append(error_msg)
            self.failed += 1
            raise AssertionError(error_msg)
        self.passed += 1
    
    def assert_false(self, value, msg=None):
        """Assert value is False"""
        if value:
            error_msg = msg or f"Expected False, got {value}"
            self.errors.append(error_msg)
            self.failed += 1
            raise AssertionError(error_msg)
        self.passed += 1
    
    def assert_not_none(self, value, msg=None):
        """Assert value is not None"""
        if value is None:
            error_msg = msg or "Expected non-None value"
            self.errors.append(error_msg)
            self.failed += 1
            raise AssertionError(error_msg)
        self.passed += 1
    
    def assert_in(self, item, container, msg=None):
        """Assert item is in container"""
        if item not in container:
            error_msg = msg or f"Expected {item} to be in {container}"
            self.errors.append(error_msg)
            self.failed += 1
            raise AssertionError(error_msg)
        self.passed += 1
    
    def assert_raises(self, exception_type, func, *args, **kwargs):
        """Assert function raises specific exception"""
        try:
            func(*args, **kwargs)
            error_msg = f"Expected {exception_type.__name__} to be raised"
            self.errors.append(error_msg)
            self.failed += 1
            raise AssertionError(error_msg)
        except exception_type:
            self.passed += 1
        except Exception as e:
            error_msg = f"Expected {exception_type.__name__}, got {type(e).__name__}"
            self.errors.append(error_msg)
            self.failed += 1
            raise AssertionError(error_msg)


def run_tests(test_module):
    """
    Run all test functions in a module
    Test functions should start with 'test_'
    """
    print(f"\n{'=' * 60}")
    print(f"Running tests in {test_module.__name__}")
    print('=' * 60)
    
    total_passed = 0
    total_failed = 0
    test_count = 0
    
    # Find all test functions
    test_functions = [
        (name, getattr(test_module, name))
        for name in dir(test_module)
        if name.startswith('test_') and callable(getattr(test_module, name))
    ]
    
    for test_name, test_func in test_functions:
        test_count += 1
        print(f"\n{test_name}...", end=' ')
        
        try:
            test_func()
            print("PASS")
            total_passed += 1
        except AssertionError as e:
            print(f"FAIL: {e}")
            total_failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            total_failed += 1
            import sys
            try:
                sys.print_exception(e)
            except:
                import traceback
                traceback.print_exc()
    
    # Print summary
    print(f"\n{'-' * 60}")
    print(f"Tests run: {test_count}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success rate: {(total_passed/test_count*100) if test_count > 0 else 0:.1f}%")
    print('=' * 60)
    
    return total_failed == 0
