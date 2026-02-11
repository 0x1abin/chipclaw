"""
ChipClaw Configuration Loader
"""
import json
import os
from .utils import file_exists


class Config:
    """Configuration manager with JSON loading and nested access"""
    
    DEFAULTS = {
        "agent": {
            "workspace": "/workspace",
            "data_dir": "/data",
            "model": "deepseek-chat",
            "max_tokens": 4096,
            "temperature": 0.7,
            "max_tool_iterations": 15,
            "max_session_messages": 20
        },
        "provider": {
            "api_key": "",
            "api_base": "https://api.deepseek.com/v1"
        },
        "channels": {
            "mqtt": {
                "enabled": False,
                "broker": "192.168.1.1",
                "port": 1883,
                "client_id": "chipclaw-01",
                "topic_in": "chipclaw/in",
                "topic_out": "chipclaw/out",
                "username": "",
                "password": ""
            },
            "uart": {
                "enabled": True,
                "uart_id": 1,
                "baudrate": 115200,
                "tx_pin": 17,
                "rx_pin": 18
            }
        },
        "hardware": {
            "led_pin": 2,
            "restrict_to_workspace": True
        },
        "wifi": {
            "ssid": "",
            "password": ""
        }
    }
    
    def __init__(self, config_path="/config.json"):
        """Load configuration from JSON file with defaults"""
        self.data = self._load_with_defaults(config_path)
    
    def _load_with_defaults(self, path):
        """Load JSON and deep-merge with defaults"""
        result = self._deep_copy(self.DEFAULTS)
        
        if file_exists(path):
            try:
                with open(path) as f:
                    user_config = json.load(f)
                result = self._deep_merge(result, user_config)
            except Exception as e:
                print(f"Warning: Error loading config from {path}: {e}")
        
        return result
    
    def _deep_copy(self, obj):
        """Deep copy a dict/list structure"""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj
    
    def _deep_merge(self, base, override):
        """Deep merge override dict into base dict"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, *keys, default=None):
        """Get nested value: config.get('agent', 'model') or config.get('agent', 'model', default='gpt-4')"""
        value = self.data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default
    
    @property
    def workspace(self):
        """Get workspace directory path"""
        return self.get("agent", "workspace", default="/workspace")
    
    @property
    def data_dir(self):
        """Get data directory path"""
        return self.get("agent", "data_dir", default="/data")
