"""
Unit tests for chipclaw.utils module
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chipclaw.utils import (
    ensure_dir,
    today_date,
    timestamp,
    safe_filename,
    truncate_string,
    get_runtime_info,
    format_runtime_info
)


def test_safe_filename():
    """Test safe_filename sanitization"""
    assert safe_filename("test:file/name\\test") == "test_file_name_test"
    assert safe_filename("normal_file.txt") == "normal_file.txt"
    assert safe_filename("file:with:colons") == "file_with_colons"


def test_truncate_string():
    """Test string truncation"""
    short_string = "Hello"
    assert truncate_string(short_string, 10) == "Hello"
    
    long_string = "A" * 100
    truncated = truncate_string(long_string, 50)
    assert len(truncated) <= 65  # 50 + "...(truncated)"
    assert truncated.endswith("...(truncated)")


def test_today_date():
    """Test today_date format"""
    date = today_date()
    assert len(date) == 10  # YYYY-MM-DD
    assert date[4] == '-'
    assert date[7] == '-'
    
    # Validate it's a valid date format
    year, month, day = date.split('-')
    assert len(year) == 4
    assert len(month) == 2
    assert len(day) == 2


def test_timestamp():
    """Test timestamp returns a number"""
    ts = timestamp()
    assert isinstance(ts, (int, float))
    assert ts > 0


def test_get_runtime_info():
    """Test runtime info retrieval"""
    info = get_runtime_info()
    assert isinstance(info, dict)
    # Should have at least some info
    # In CPython we should get platform and version
    assert len(info) > 0


def test_format_runtime_info():
    """Test runtime info formatting"""
    formatted = format_runtime_info()
    assert isinstance(formatted, str)
    assert len(formatted) > 0


def test_ensure_dir():
    """Test directory creation"""
    import tempfile
    import shutil
    
    # Create a temp directory
    temp_dir = tempfile.mkdtemp()
    try:
        test_dir = os.path.join(temp_dir, "test_subdir")
        ensure_dir(test_dir)
        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)
        
        # Calling again should not raise error
        ensure_dir(test_dir)
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    from tests import run_tests
    import sys
    run_tests(sys.modules[__name__])
