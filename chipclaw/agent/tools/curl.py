"""
ChipClaw Curl Tool
MicroPython-compatible HTTP client based on urequests,
replacing curl command for LLM common use cases.
"""
import gc

try:
    import ujson as json
except ImportError:
    import json

try:
    import urequests as requests
except ImportError:
    import requests

from .base import Tool
from ...utils import truncate_string


class CurlTool(Tool):
    """HTTP request tool supporting GET, POST, PUT, DELETE, PATCH methods"""

    name = "curl"
    description = (
        "Perform HTTP requests (like curl). "
        "Supports GET, POST, PUT, DELETE, PATCH methods with custom headers and JSON body."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Request URL"
            },
            "method": {
                "type": "string",
                "description": "HTTP method: GET, POST, PUT, DELETE, PATCH (default: GET)",
                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]
            },
            "headers": {
                "type": "object",
                "description": "Custom HTTP headers as key-value pairs, e.g. {\"Authorization\": \"Bearer token\", \"Content-Type\": \"application/json\"}"
            },
            "data": {
                "type": "string",
                "description": "Request body as string. For JSON, pass a JSON-encoded string."
            }
        },
        "required": ["url"]
    }

    def execute(self, url, method="GET", headers=None, data=None):
        """
        Execute an HTTP request.

        Args:
            url: Request URL
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            headers: Dict of HTTP headers
            data: Request body string

        Returns:
            Formatted response string with status, headers and body
        """
        gc.collect()

        method = method.upper()
        if method not in ("GET", "POST", "PUT", "DELETE", "PATCH"):
            return "Error: Unsupported HTTP method: {}".format(method)

        try:
            # Build request keyword arguments
            kwargs = {}
            if headers:
                kwargs["headers"] = headers
            if data is not None:
                kwargs["data"] = data

            # Dispatch by method
            if method == "GET":
                response = requests.get(url, **kwargs)
            elif method == "POST":
                response = requests.post(url, **kwargs)
            elif method == "PUT":
                response = requests.put(url, **kwargs)
            elif method == "DELETE":
                response = requests.delete(url, **kwargs)
            elif method == "PATCH":
                response = requests.patch(url, **kwargs)

            # Read status
            status_code = response.status_code
            reason = response.reason if hasattr(response, "reason") else ""

            # Read response headers
            resp_headers = {}
            if hasattr(response, "headers"):
                h = response.headers
                if hasattr(h, "items"):
                    for k, v in h.items():
                        resp_headers[k] = v
                elif isinstance(h, dict):
                    resp_headers = h

            # Read body
            if hasattr(response, "text"):
                body = response.text
            else:
                body = response.content.decode("utf-8", errors="ignore")

            response.close()

            # Truncate body to 4KB
            body = truncate_string(body, max_len=4096)

            # Format output
            lines = []
            lines.append("HTTP {} {}".format(status_code, reason))
            if resp_headers:
                for k, v in resp_headers.items():
                    lines.append("{}: {}".format(k, v))
            lines.append("")
            lines.append(body)

            gc.collect()

            return "\n".join(lines)

        except Exception as e:
            gc.collect()
            return "Error: HTTP request failed: {}".format(e)
