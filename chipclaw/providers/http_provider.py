"""
ChipClaw HTTP LLM Provider
OpenAI-compatible API caller using urequests
"""
import json
import gc

try:
    import urequests as requests
except ImportError:
    import requests

from .base import LLMProvider, LLMResponse, ToolCallRequest


class HTTPProvider(LLMProvider):
    """HTTP-based LLM provider for OpenAI-compatible APIs"""
    
    def __init__(self, api_key, api_base):
        self.api_key = api_key
        self.api_base = api_base.rstrip('/')
    
    async def chat(self, messages, tools=None, model=None, max_tokens=4096, temperature=0.7):
        """
        Send chat completion request via HTTP
        
        Args:
            messages: List of message dicts
            tools: Optional list of tool definitions
            model: Model name (required)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            LLMResponse instance
        """
        if not model:
            raise ValueError("model parameter is required")
        
        # Collect garbage before making request
        gc.collect()
        
        # Build request body
        body = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if tools:
            body["tools"] = tools
        
        # Make HTTP request
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(
                url,
                data=json.dumps(body).encode('utf-8'),
                headers=headers
            )
            
            if response.status_code != 200:
                error_text = response.text if hasattr(response, 'text') else str(response.content)
                raise Exception(f"HTTP {response.status_code}: {error_text}")
            
            data = response.json()
            response.close()
            
            # Parse response
            choice = data["choices"][0]
            message = choice["message"]
            finish_reason = choice.get("finish_reason", "stop")
            usage = data.get("usage", {})
            
            # Extract content and tool calls
            content = message.get("content")
            tool_calls_data = message.get("tool_calls")
            
            tool_calls = None
            if tool_calls_data:
                tool_calls = []
                for tc in tool_calls_data:
                    tool_calls.append(ToolCallRequest(
                        id=tc["id"],
                        name=tc["function"]["name"],
                        arguments=json.loads(tc["function"]["arguments"])
                    ))
            
            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason=finish_reason,
                usage=usage
            )
        
        finally:
            # Collect garbage after request
            gc.collect()
