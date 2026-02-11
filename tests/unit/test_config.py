"""
Unit tests for chipclaw.config module
"""
import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chipclaw.config import Config


def test_config_defaults():
    """Test default configuration values"""
    # Use non-existent path to test defaults
    config = Config(config_path="/nonexistent_test_config.json")
    
    # Check some default values
    assert config.get("agent", "model") == "deepseek-chat"
    assert config.get("agent", "max_tokens") == 4096
    assert config.get("channels", "uart", "enabled") is True
    assert config.get("channels", "mqtt", "enabled") is False


def test_config_workspace_property():
    """Test workspace property"""
    config = Config(config_path="/nonexistent_test_config.json")
    assert config.workspace == "/workspace"


def test_config_data_dir_property():
    """Test data_dir property"""
    config = Config(config_path="/nonexistent_test_config.json")
    assert config.data_dir == "/data"


def test_config_nested_get():
    """Test nested configuration access"""
    config = Config(config_path="/nonexistent_test_config.json")
    
    # Test multiple levels of nesting
    mqtt_enabled = config.get("channels", "mqtt", "enabled")
    assert mqtt_enabled is False
    
    uart_baudrate = config.get("channels", "uart", "baudrate")
    assert uart_baudrate == 115200


def test_config_get_with_default():
    """Test configuration get with default value"""
    config = Config(config_path="/nonexistent_test_config.json")
    
    # Non-existent key should return default
    value = config.get("nonexistent", "key", default="default_value")
    assert value == "default_value"
    
    # Existing key should return actual value
    value = config.get("agent", "model", default="fallback_model")
    assert value == "deepseek-chat"


def test_config_from_file():
    """Test loading configuration from file"""
    # Create temporary config file
    temp_dir = tempfile.mkdtemp()
    try:
        config_path = os.path.join(temp_dir, "test_config.json")
        test_config = {
            "agent": {
                "model": "custom-model",
                "max_tokens": 2048
            },
            "provider": {
                "api_key": "test-key-123"
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Load config
        config = Config(config_path=config_path)
        
        # Check merged values
        assert config.get("agent", "model") == "custom-model"
        assert config.get("agent", "max_tokens") == 2048
        assert config.get("provider", "api_key") == "test-key-123"
        
        # Check that defaults are still present for unspecified values
        assert config.get("agent", "temperature") == 0.7
        assert config.get("channels", "uart", "enabled") is True
        
    finally:
        shutil.rmtree(temp_dir)


def test_config_deep_merge():
    """Test deep merge of configuration"""
    temp_dir = tempfile.mkdtemp()
    try:
        config_path = os.path.join(temp_dir, "test_config.json")
        test_config = {
            "channels": {
                "mqtt": {
                    "enabled": True,
                    "broker": "test.broker.com"
                }
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        config = Config(config_path=config_path)
        
        # Overridden values
        assert config.get("channels", "mqtt", "enabled") is True
        assert config.get("channels", "mqtt", "broker") == "test.broker.com"
        
        # Default values should still be present
        assert config.get("channels", "mqtt", "port") == 1883
        assert config.get("channels", "uart", "enabled") is True
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    from tests import run_tests
    import sys
    run_tests(sys.modules[__name__])
