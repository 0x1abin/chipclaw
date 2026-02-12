# ChipClaw Testing Framework

This directory contains the testing framework for ChipClaw, designed to work with both MicroPython and CPython.

## Directory Structure

```
tests/
├── __init__.py          # Test framework core (TestCase, run_tests)
├── test_runner.py       # Test discovery and runner script
├── unit/                # Unit tests
│   ├── test_config.py
│   ├── test_events.py
│   └── test_utils.py
└── integration/         # Integration tests (future)
```

## Running Tests

### Run All Tests

```bash
# From the project root
python tests/test_runner.py
```

### Run Individual Test Module

```bash
# Run a specific test module
python tests/unit/test_utils.py
```

### Run Tests on MicroPython (ESP32)

The test framework is compatible with MicroPython. To run tests on ESP32:

```bash
# Upload tests directory to ESP32
mpremote fs cp -r tests :tests

# Run tests on device
mpremote exec "import tests.test_runner"
```

## Writing Tests

### Basic Test Structure

Tests use a simple framework compatible with both MicroPython and CPython:

```python
"""
Test module for my_module
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from my_module import my_function


def test_my_function():
    """Test my_function behavior"""
    result = my_function(42)
    assert result == 84


def test_edge_case():
    """Test edge case"""
    result = my_function(0)
    assert result == 0


if __name__ == "__main__":
    from tests import run_tests
    import sys
    run_tests(sys.modules[__name__])
```

### Test Function Naming

- Test functions must start with `test_`
- Use descriptive names: `test_config_loading`, `test_message_creation`

### Available Assertions

The `TestCase` class provides basic assertions:

- `assert_equal(actual, expected, msg=None)` - Assert two values are equal
- `assert_true(value, msg=None)` - Assert value is True
- `assert_false(value, msg=None)` - Assert value is False
- `assert_not_none(value, msg=None)` - Assert value is not None
- `assert_in(item, container, msg=None)` - Assert item is in container
- `assert_raises(exception_type, func, *args, **kwargs)` - Assert function raises exception

However, for simplicity, you can also use plain Python `assert` statements:

```python
def test_example():
    assert 1 + 1 == 2
    assert "hello" in "hello world"
```

## Test Configuration

The `test_config.json` file provides a test-specific configuration that:
- Uses temporary directories (`/tmp/test_workspace`, `/tmp/test_data`)
- Disables hardware channels (MQTT, UART)
- Uses placeholder API credentials

## CI/CD Integration

Tests run automatically on GitHub Actions for:
- Every push to `main`, `master`, or `develop` branches
- Every pull request
- Manual workflow dispatch

The CI pipeline tests using MicroPython 1.21.0 (Unix port) to ensure compatibility with the target platform.

## Test Coverage

Current test coverage includes:
- ✅ `chipclaw.utils` - Utility functions
- ✅ `chipclaw.bus.events` - Message events
- ✅ `chipclaw.config` - Configuration loading

### Future Test Coverage

Planned tests:
- Message bus queue operations
- Session management
- Context builder
- Tool registry
- Provider interface

## MicroPython Compatibility

The test framework is designed to work with MicroPython's limited standard library:
- No `unittest` module dependency
- No `pytest` dependency
- Simple assertion-based testing
- Compatible with MicroPython's import system

## Development Workflow

1. Write your code changes
2. Write tests for your changes
3. Run tests locally: `python tests/test_runner.py`
4. Commit and push
5. CI will automatically run tests

## Troubleshooting

### Import Errors

If you get import errors, ensure the test file has the correct path setup:

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
```

### Module Not Found

Make sure you're running tests from the project root directory.

### MicroPython Memory Issues

If tests fail on ESP32 due to memory:
- Run fewer tests at once
- Call `gc.collect()` between tests
- Reduce test data sizes
