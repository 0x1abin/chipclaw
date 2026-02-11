"""
ChipClaw LLM Provider Base Classes
"""


class ToolCallRequest:
    """Represents a tool call request from the LLM"""
    
    def __init__(self, id, name, arguments):
        self.id = id                # Unique call ID (from LLM response)
        self.name = name            # Tool name
        self.arguments = arguments  # Dict of parameters
    
    def __repr__(self):
        return f"ToolCallRequest(id={self.id}, name={self.name}, arguments={self.arguments})"


class LLMResponse:
    """Response from LLM API"""
    
    def __init__(self, content, tool_calls=None, finish_reason=None, usage=None):
        self.content = content            # Response text (or None if tool_calls)
        self.tool_calls = tool_calls      # List of ToolCallRequest (or None)
        self.finish_reason = finish_reason # "stop" | "tool_calls" | "length"
        self.usage = usage or {}          # Token usage dict
    
    @property
    def has_tool_calls(self):
        """Check if response contains tool calls"""
        return self.tool_calls is not None and len(self.tool_calls) > 0
    
    def __repr__(self):
        return f"LLMResponse(content={self.content[:50] if self.content else None}..., tool_calls={len(self.tool_calls) if self.tool_calls else 0}, finish_reason={self.finish_reason})"


class LLMProvider:
    """Base class for LLM providers (not using ABC for MicroPython compatibility)"""
    
    async def chat(self, messages, tools=None, model=None, max_tokens=4096, temperature=0.7):
        """
        Send chat completion request
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}, ...]
            tools: Optional list of tool definitions
            model: Model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            LLMResponse instance
        """
        raise NotImplementedError("Subclass must implement chat()")
