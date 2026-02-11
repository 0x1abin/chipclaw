"""
ChipClaw HTTP Fetch Tool
"""
from .base import Tool
from ...utils import truncate_string

try:
    import urequests as requests
except ImportError:
    import requests


class HTTPFetchTool(Tool):
    """HTTP GET request tool"""
    
    name = "http_fetch"
    description = "Fetch content from a URL via HTTP GET"
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to fetch"
            }
        },
        "required": ["url"]
    }
    
    def execute(self, url):
        """Fetch URL and return response body"""
        import gc
        
        gc.collect()
        
        try:
            response = requests.get(url)
            
            if response.status_code != 200:
                return f"HTTP {response.status_code}: {response.reason if hasattr(response, 'reason') else 'Error'}"
            
            # Get response text
            if hasattr(response, 'text'):
                content = response.text
            else:
                content = response.content.decode('utf-8', errors='ignore')
            
            response.close()
            
            # Truncate to 4KB to save RAM
            result = truncate_string(content, max_len=4096)
            
            gc.collect()
            
            return result
        
        except Exception as e:
            gc.collect()
            return f"Error fetching URL: {e}"
